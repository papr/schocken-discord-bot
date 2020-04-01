import os
import signal

from .exceptions import (
    SpielLaeuft,
    SpielLaeuftNicht,
    FalscherSpielBefehl,
    FalscheAktion,
    PermissionError,
    FalscherSpieler,
    ZuOftGeworfen,
)
from .spiel import SchockenSpiel
from discord.utils import get
import os
import signal


class SchockenBot:
    def __init__(self, client):
        self.client = client
        # bot will never run on any other server than Café A
        self.guild = client.guilds[0]
        self.schock_channel_name = "schocktresen"
        self.valid_guild_name = "Café A"
        self.game_running = False
        self._all_member_names = [member.name for member in self.guild.members]
        self._start_game_cmd = "schocken"
        self._end_game_cmd = "beenden"
        self._restart_cmd = "neustart"
        self._wuerfel_emoji_names = dict(
            [
                (1, "wuerfel_1"),
                (2, "wuerfel_2"),
                (3, "wuerfel_3"),
                (4, "wuerfel_4"),
                (5, "wuerfel_5"),
                (6, "wuerfel_6"),
            ]
        )
        self.discord_to_game_cmd_dict = {
            "einwerfen": "einwerfen",
            "wuerfeln": "wuerfeln",
            "stechen": "stechen",
            "weiter": "weiter",
            "beiseite legen": "beiseite legen",
        }

    def emoji_by_name(self, name):
        emoji = get(self.guild.emojis, name=name)
        return str(emoji)

    def name_to_member(self, name):
        member = get(self.guild.members, name=name)
        return member

    def discord_to_game_cmd(self, discord_cmd):
        try:
            game_cmd = self.discord_to_game_cmd_dict[discord_cmd]
            return game_cmd
        except KeyError:
            raise FalscherSpielBefehl

    def spieler_by_name(self, name, spielerliste):
        spieler = next(sp for sp in spielerliste if sp.name == name)
        return spieler

    def command_in_schock_channel(self, message):
        msg_text = message.content
        channel = message.channel
        correct_channel = channel.name == self.schock_channel_name
        is_command = msg_text.startswith("!")
        is_not_restart = self._restart_cmd not in msg_text
        return correct_channel and is_command and is_not_restart

    def restart_issued(self, message):
        msg_text = message.content
        return msg_text == f"!{self._restart_cmd}"

    async def parse_input(self, message):
        # all messages from channels with read permissions are read
        msg_text = message.content
        channel = message.channel
        msg_author = message.author
        try:
            if self.command_in_schock_channel(message):
                command = msg_text.split("!")[-1]
                if command == self._start_game_cmd:
                    # TODO Status auf Spiel läuft setzten
                    if self.game_running:
                        raise SpielLaeuft
                    else:
                        self.game_running = True
                        self.game = SchockenSpiel()
                        msg = f"{message.author.mention} will schocken. `!einwerfen` zum mitmachen"
                        await self.print_to_channel(channel, msg)

                elif command == self._end_game_cmd:
                    # TODO Status auf Spiel beendet setzten
                    if self.game_running:
                        msg = f"{message.author.mention} hat das Spiel beendet"
                        self.game_running = False
                        await self.print_to_channel(channel, msg)
                    else:
                        raise SpielLaeuftNicht

                elif command == "ICH WILL UNREAL TOURNAMENT SPIELEN":
                    msg = "Dann geh doch"
                    await self.print_to_channel(channel, msg)
                    link = "https://tenor.com/view/unreal-tournament-kid-unreal-unreal-kid-rage-gif-16110833"
                    await self.print_to_channel(channel, link)

                else:
                    if not self.game_running:
                        raise SpielLaeuftNicht
                    # actual game
                    await self.handle_game(message)

            elif self.restart_issued(message):
                role_strs = [str(role) for role in message.author.roles]
                if "developer" not in role_strs:
                    raise PermissionError
                msg = f"👋 Bis gleich! :wave:"
                await self.print_to_channel(channel, msg)
                await self.client.logout()
                os.kill(os.getpid(), signal.SIGINT)

        except NotImplementedError:
            msg = "Das geht leider noch nicht. (Nicht implementiert)"
            msg += "\n Spiel wird beendet."
            await self.print_to_channel(channel, msg)
            self.game_running = False
            del self.game

        except PermissionError:
            msg = f"Das darfst du nicht, DU HURENSOHN! {self.emoji_by_name('king')}"
            await self.print_to_channel(channel, msg)

        except SpielLaeuftNicht:
            msg = f"Gerade läuft kein Spiel. `!{self._start_game_cmd}` zum starten"
            await self.print_to_channel(channel, msg)

        except SpielLaeuft:
            msg = f"Es läuft bereits ein Spiel, schau, ob du `!einwerfen` kannst."
            await self.print_to_channel(channel, msg)

        except FalscherSpielBefehl:
            msg = "Das geht leider nicht."
            # msg += "\n".join(["`" + bef + "`" for bef in zulaessig])
            await self.print_to_channel(channel, msg)

        except FalscherSpieler as e:
            if str(e):
                msg = str(e)
            else:
                msg = "Das darfst du gerade nicht (Falsche Spielerin)."
            await self.print_to_channel(channel, msg)

        except ZuOftGeworfen as e:
            if str(e):
                msg = str(e)
            else:
                msg = "Du darfst nicht nochmal!"
            await self.print_to_channel(channel, msg)

        except FalscheAktion:
            msg = "Das darfst du gerade nicht. (Falsche Aktion)"
            await self.print_to_channel(channel, msg)

    async def print_to_channel(self, channel, text):
        return await channel.send(text)

    async def handle_game(self, message):
        msg_text = message.content
        channel = message.channel
        msg_author = message.author
        command = msg_text.split("!")[-1]
        spieler_name = msg_author.name

        old_state = self.game.state.leaf_state.name
        game_cmd = self.discord_to_game_cmd(command)
        if game_cmd not in self.game.leaf_state.handlers.keys():
            raise FalscheAktion

        self.game.command_to_event(spieler_name, command)
        new_state = self.game.state.leaf_state.name

        state_changed = old_state != new_state
        if new_state == "einwerfen":
            # einwerfen is the initial state, no need to check for changes
            spieler = self.spieler_by_name(
                spieler_name, self.game.einwerfen.spieler_liste
            )
            out_str = f"{message.author.mention} hat eine {self.emoji_by_name(self._wuerfel_emoji_names[spieler.augen])} geworfen."
            # stechen oder nicht?
            if self.game.einwerfen.stecher_count > 1:
                out_str += "\n" + (
                    ", ".join(
                        [
                            self.name_to_member(pl.name).mention
                            for pl in self.game.einwerfen.stecher_liste
                        ]
                    )
                    + f" haben eine {self.emoji_by_name(self._wuerfel_emoji_names[self.game.einwerfen.spieler_liste[0].augen])} geworfen.\n"
                )
                out_str += (
                    "`!stechen` um zu stechen oder auf weiteres `!einwerfen` warten"
                )
            else:
                if len(self.game.einwerfen.spieler_liste) > 1:
                    anfaenger = self.game.einwerfen.spieler_liste[0]
                    out_str += f"\n{self.name_to_member(anfaenger.name).mention} hat mit einer {self.emoji_by_name(self._wuerfel_emoji_names[anfaenger.augen])} den niedrigsten Wurf und darf anfangen."
                    out_str += "\n`!wuerfeln` um das Spiel zu beginnen oder auf weiteres `!einwerfen` warten."
            await self.print_to_channel(channel, out_str)

        elif new_state == "stechen":
            spieler = next(
                sp
                for sp in self.game.einwerfen.spieler_liste
                if sp.name == spieler_name
            )
            noch_stechen = [
                sp
                for sp in self.game.einwerfen.stecher_liste
                if sp not in self.game.einwerfen.gestochen_liste
            ]
            out_str = f"{message.author.mention} sticht mit einer {self.emoji_by_name(self._wuerfel_emoji_names[spieler.augen])}."
            if len(noch_stechen) > 1:
                out_str += "\n" + (
                    ", ".join(
                        [self.name_to_member(pl.name).mention for pl in noch_stechen]
                    )
                    + f" müssen `!stechen`."
                )
            elif len(noch_stechen) == 1 and len(self.game.einwerfen.stecher_liste) > 1:
                out_str += f"\n {self.name_to_member(noch_stechen[0].name).mention} muss noch `!stechen`."
            else:
                anfaenger = self.game.einwerfen.spieler_liste[0]
                out_str += f"\n{self.name_to_member(anfaenger.name).mention} hat mit einer {self.emoji_by_name(self._wuerfel_emoji_names[anfaenger.augen])} den niedrigsten Wurf und darf anfangen."
                out_str += "\n`!wuerfeln` um das Spiel zu beginnen."

            await self.print_to_channel(channel, out_str)

        elif new_state == "wuerfeln":
            stack_list = list(self.game.state_stack.deque)
            stack_names = [st.name for st in stack_list]
            halbzeit_no = stack_names.count("Halbzeit") + 1
            halbzeit_names = {1: "halbzeit_erste", 2: "halbzeit_zweite", 3: "finale"}

            halbzeit = getattr(self.game, halbzeit_names[halbzeit_no])
            spieler = halbzeit.aktiver_spieler

            # Halbzeit beginnt
            if old_state in ["einwerfen", "stechen"] or halbzeit_no != 1:
                new_spieler_liste = halbzeit.spieler_liste
                old_spieler_liste = new_spieler_liste[:1] + new_spieler_liste[1:]
                # Erster wurf nach einwerfen. Print reihenfolge
                out_str0 = f"Halbzeit {halbzeit_no} beginnt. Die Reihenfolge ist:\n"
                out_str0 += ", ".join(
                    [self.name_to_member(pl.name).mention for pl in old_spieler_liste]
                )
                await self.print_to_channel(channel, out_str0)

            # handle wuerfeln
            wuerfe = spieler.augen
            anzahl_wuerfe = spieler.anzahl_wuerfe
            # erster wurf (immer drei)
            wurf_emoji = "".join(
                [self.emoji_by_name(self._wuerfel_emoji_names[wurf]) for wurf in wuerfe]
            )
            out_str = f"{message.author.mention} wirft "
            out_str += wurf_emoji + "."
            await self.print_to_channel(channel, out_str)
