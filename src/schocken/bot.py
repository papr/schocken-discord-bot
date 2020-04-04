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
from . import wurf
from discord.utils import get
from copy import deepcopy
import random


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
            "beiseite": "beiseite legen",
            "umdrehen": "umdrehen",
        }

        self.game_to_discord_cmd_dict = {
            v: k for k, v in self.discord_to_game_cmd_dict.items()
        }

        self._halbzeit_state_names = {
            1: "halbzeit_erste",
            2: "halbzeit_zweite",
            3: "finale",
        }

    def emoji_by_name(self, name):
        emoji = get(self.guild.emojis, name=name)
        return str(emoji)

    def name_to_member(self, name):
        member = get(self.guild.members, name=name)
        return member

    def wurf_to_emoji(self, wuerfe):
        out = " ".join(
            [self.emoji_by_name(self._wuerfel_emoji_names[wurf]) for wurf in wuerfe]
        )
        return out

    def discord_to_game_cmd(self, discord_cmd):
        try:
            game_cmd = self.discord_to_game_cmd_dict[discord_cmd]
            return game_cmd
        except KeyError:
            raise FalscherSpielBefehl

    def spieler_by_name(self, name, spielerliste):
        spieler = next(sp for sp in spielerliste if sp.name == name)
        return spieler

    def replace_names_by_mentions(self, string):
        for name in self._all_member_names:
            member = self.name_to_member(name)
            string = string.replace(name, member.mention)
        return string

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
            handlers = self.game.leaf_state.handlers.keys()
            game_handlers = [
                handle for handle in handlers if handle != "enter" and handle != "exit"
            ]
            print(game_handlers)

            cmds = [
                f"`!{self.game_to_discord_cmd_dict[hdlr]}`" for hdlr in game_handlers
            ]
            msg = "Diesen Befehl gibt es nicht. Versuch's mal mit einem von diesen:\n"
            msg += ", ".join(cmds)
            await self.print_to_channel(channel, msg)

        except FalscherSpieler as e:
            if str(e):
                msg = self.replace_names_by_mentions(str(e))
            else:
                msg = "Das darfst du gerade nicht (Falsche Spielerin)."
            await self.print_to_channel(channel, msg)

        except ZuOftGeworfen as e:
            if str(e):
                msg = self.replace_names_by_mentions(str(e))
            else:
                msg = "Du darfst nicht nochmal!"
            await self.print_to_channel(channel, msg)

        except FalscheAktion as e:
            if str(e):
                msg = self.replace_names_by_mentions(str(e))
            else:
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

        # freeze old game state. some properties are needed for the bot
        game_old = deepcopy(self.game)
        # run game state machine
        game_cmd = self.discord_to_game_cmd(command)
        if game_cmd not in self.game.leaf_state.handlers.keys():
            raise FalscherSpielBefehl
        self.game.command_to_event(spieler_name, game_cmd)
        state_new = self.game.state.leaf_state.name

        if state_new == "einwerfen":
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
                    anfaenger = self.game.einwerfen.stecher_liste[0]
                    out_str += f"\n{self.name_to_member(anfaenger.name).mention} hat mit einer {self.emoji_by_name(self._wuerfel_emoji_names[anfaenger.augen])} den niedrigsten Wurf und darf anfangen."
                    out_str += "\n`!wuerfeln` um das Spiel zu beginnen oder auf weiteres `!einwerfen` warten."
            await self.print_to_channel(channel, out_str)

        elif state_new == "stechen":
            spieler = self.spieler_by_name(
                spieler_name, self.game.einwerfen.spieler_liste
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

        elif state_new == "wuerfeln":

            # in welcher halbzeit sind wir gerade?
            stack_list = list(self.game.state_stack.deque)
            stack_names = [st.name for st in stack_list]
            num_halbzeit = stack_names.count("Halbzeit") + 1

            # entsprechend halbzeit_erste oder halbzeit_zweite oder finale aus
            # game holen
            halbzeit = getattr(self.game, self._halbzeit_state_names[num_halbzeit])

            spieler_liste = halbzeit.spieler_liste
            spieler = self.spieler_by_name(spieler_name, spieler_liste)

            # get old state information
            state_old = game_old.state.leaf_state.name
            stack_list_old = list(game_old.state_stack.deque)
            stack_names_old = [st.name for st in stack_list_old]
            num_halbzeit_old = stack_names_old.count("Halbzeit") + 1
            halbzeit_old = getattr(
                game_old, self._halbzeit_state_names[num_halbzeit_old]
            )

            try:
                spieler_liste_old = halbzeit_old.spieler_liste
                spieler_old = self.spieler_by_name(spieler_name, spieler_liste_old)

            except AttributeError:
                # nur im allerersten wurf einer halbzeit!
                spieler_liste_old = spieler_liste[:1] + spieler_liste[1:]
                pass

            is_neue_halbzeit = (
                state_old in ["einwerfen", "stechen"]
                or num_halbzeit_old != num_halbzeit
            )

            if is_neue_halbzeit:
                out_str0 = f"Halbzeit {num_halbzeit} beginnt. Die Reihenfolge ist:\n"
                out_str0 += ", ".join(
                    [self.name_to_member(pl.name).mention for pl in spieler_liste_old]
                )
                await self.print_to_channel(channel, out_str0)

            if not is_neue_halbzeit:
                hoch, tief = halbzeit.rdm.hoch_und_tief()

            if command == "wuerfeln":
                # Generiere Output in abhängigkeit des wurfes
                if is_neue_halbzeit:
                    out_str = self.handle_augen_output(message, spieler)
                else:
                    out_str = self.handle_augen_output(message, spieler, hoch, tief)

                if halbzeit.rdm.num_maximale_wuerfe == 1:
                    schon_geworfen = 1
                else:
                    schon_geworfen = spieler.anzahl_wuerfe

            elif command == "weiter":
                out_str = f"{message.author.mention} lässt liegen."
                # wenn weiter gecalled wird, ist spieler.anzahl_wuerfe==0,
                # aber ist egal, da es bei weiter nicht gebraucht wird
                schon_geworfen = 0

            # Zug vorbei, print Information
            if (
                schon_geworfen == halbzeit.rdm.num_maximale_wuerfe
                or game_cmd == "weiter"
            ):
                naechster = self.name_to_member(halbzeit.aktiver_spieler.name)
                out_str += f"\nAls nächstes ist {naechster.mention} an "
                out_str += f"der Reihe. Bitte `!wuerfeln`\n"
                # TODO figure out how to get high/low aus dem letzten durchgang
                hoch_spieler = hoch.spieler
                tief_spieler = tief.spieler
                hoch_augen = hoch.spieler.augen
                tief_augen = tief.spieler.augen
                out_str += f"Hoch ist {self.name_to_member(hoch_spieler.name).mention} "
                out_str += f"mit: {self.wurf_to_emoji(hoch_augen)}\n"
                out_str += f"Tief ist {self.name_to_member(tief_spieler.name).mention} "
                out_str += f"mit: {self.wurf_to_emoji(tief_augen)}"
            await self.print_to_channel(channel, out_str)

    def handle_augen_output(self, message, spieler, hoch=None, tief=None):
        augen = spieler.augen
        wurf_emoji = self.wurf_to_emoji(augen)
        # besonderer wurf?
        augen_name = str(wurf.welcher_wurf(augen))
        if hoch is None and tief is None:
            # erster Wurf der Runde
            out_str = f"{message.author.mention} legt vor: "
            is_erster_wurf = True
        else:
            out_str = f"{message.author.mention} wirft "
            is_erster_wurf = False
            reicht = tief.spieler.name != spieler.name
        out_str += wurf_emoji + "."

        comment_choices = [" "]
        if "Gemuese" in augen_name:
            if augen[0] < 5:
                comment_choices = [
                    "Gar nicht mal so gut...",
                    "Schlechtes Gemüse...",
                    "Das kannst du besser!",
                    "Wow.",
                ]
                reicht_choices = {
                    "reicht": [" Aber reicht sogar.",],
                    "reichtnicht": [" Und reicht nicht mal.",],
                }

            elif augen[0] == 5:
                comment_choices = [
                    "Solides Gemüse.",
                    "Das kann man noch schlagen.",
                    "Ausbaufähig...",
                ]
                reicht_choices = {
                    "reicht": [" Und reicht sogar.",],
                    "reichtnicht": [" Aber reicht gar nicht.",],
                }

            elif augen[0] == 6:
                comment_choices = [
                    "Hohes Gemüse.",
                    "Nicht schlecht!",
                ]
                reicht_choices = {
                    "reicht": [" Und reicht sogar.",],
                    "reichtnicht": [" Aber reicht gar nicht.",],
                }

        elif "General" in augen_name:
            comment_choices = ["Kann man liegen lassen.", "General."]
            reicht_choices = {
                "reicht": [" Reicht ja.",],
                "reichtnicht": [" Aber reicht gar nicht.",],
            }

        elif "Schock" in augen_name:
            if "out" in augen_name:
                comment_choices = [
                    "Nice.",
                    "Random Schock Out.",
                    "Würde ich liegen lassen.",
                ]
                reicht_choices = {
                    "reicht": [" Reicht.",],
                    "reichtnicht": [" Aber reicht ja nicht mal.",],
                }
            else:
                comment_choices = ["Schöner Schock."]
                reicht_choices = {
                    "reicht": [" Reicht auch.",],
                    "reichtnicht": [" Aber reicht gar nicht.",],
                }

        elif "Herrenwurf" in augen_name:
            comment_choices = ["Herrenwurf. Verliert nicht."]
            reicht_choices = {
                "reicht": [" Und reicht sogar.",],
                "reichtnicht": [" ...aber vielleicht schon.",],
            }

        elif "Jule" in augen_name:
            comment_choices = ["Schöne Jule."]
            reicht_choices = {
                "reicht": [" Und sie reicht.",],
                "reichtnicht": [" Aber reicht leider nicht.",],
            }

        out_str += "\n" + random.choice(comment_choices)
        if not is_erster_wurf:
            if reicht:
                out_str += random.choice(reicht_choices["reicht"])
            else:
                out_str += random.choice(reicht_choices["reichtnicht"])

        return out_str
