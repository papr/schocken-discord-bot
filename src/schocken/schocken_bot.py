from .exceptions import SpielLäuft, SpielLäuftNicht, FalscherSpielBefehl, FalscheAktion
from .deckel_management import FalscherSpieler
from .schockenrunde import SchockenRunde
from discord.utils import get


class SchockenBot:
    def __init__(self, client):
        self.client = client
        # bot will never run on any other server than Café A
        self.guild = client.guilds[0]
        self.schock_channel_name = "schocktresen"
        self.valid_guild_name = "Café A"
        self.game_running = False
        self._start_game_cmd = "schocken"
        self._end_game_cmd = "beenden"
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
        except KeyError:
            raise FalscherSpielBefehl

    async def parse_input(self, message):
        # all messages from channels with read permissions are read
        msg_text = message.content
        channel = message.channel
        msg_author = message.author
        # check if message is in the correct channel
        if channel.name == self.schock_channel_name:
            # check if message is a command
            if msg_text.startswith("!"):
                try:
                    command = msg_text.split("!")[-1]
                    if command == self._start_game_cmd:
                        if self.game_running:
                            raise SpielLäuft
                        else:
                            self.game_running = True
                            self.game = SchockenRunde()
                            msg = f"{message.author.mention} will Schocken. `!einwerfen` zum mitmachen"
                            await self.print_to_channel(channel, msg)

                    elif command == self._end_game_cmd:
                        if self.game_running:
                            msg = f"{message.author.mention} hat das Spiel beendet"
                            self.game_running = False
                            await self.print_to_channel(channel, msg)
                        else:
                            raise SpielLäuftNicht

                    else:
                        if not self.game_running:
                            raise SpielLäuftNicht
                        # actual game
                        await self.handle_game(message)

                except NotImplementedError:
                    msg = "Das geht leider noch nicht. (Nicht implementiert)"
                    await self.print_to_channel(channel, msg)

                except SpielLäuftNicht:
                    msg = f"Gerade läuft kein Spiel. `!{self._start_game_cmd}` zum starten"
                    await self.print_to_channel(channel, msg)

                except SpielLäuft:
                    msg = (
                        f"Es läuft bereits ein Spiel, schau, ob du `!einwerfen` kannst."
                    )
                    await self.print_to_channel(channel, msg)

                except FalscherSpielBefehl:
                    msg = "Das geht leider nicht."
                    # msg += "\n".join(["`" + bef + "`" for bef in zulaessig])
                    await self.print_to_channel(channel, msg)

                except FalscherSpieler:
                    msg = "Das darfst du gerade nicht (Falsche Spielerin)."
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

        old_state = self.game.state
        game_cmd = self.discord_to_game_cmd(command)
        self.game.command_to_event(spieler_name, command)
        new_state = self.game.state

        state_changed = old_state != new_state
        if new_state == "einwerfen":
            spieler = [
                sp
                for sp in self.game.einwerfen.spieler_liste
                if sp.name == spieler_name
            ][0]
            if command == "einwerfen":
                out_str = f"{message.author.mention} hat eine {self.emoji_by_name(self._wuerfel_emoji_names[spieler.augen])} gewürfelt."
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
                        out_str += f"\n{self.name_to_member(anfaenger.name).mention} hat mit einer {self.emoji_by_name(self._wuerfel_emoji_names[anfaenger.augen])} den niedrigsten Wurf."
                        out_str += "\n`!würfeln` um das Spiel zu beginnen oder auf weiteres `!einwerfen` warten."
                await self.print_to_channel(channel, out_str)
            elif new_state == "stechen":

                await self.print_to_channel(channel, out_str)
            # einwerfen is the initial state, no need to check for changes

            # if state_0 == "Einwerfen":
            # self.game.perform_action(player, command)
            # if state_0 != self.game.state:
            # return await self.parse_input(message)
            # out_str = f"{message.author.mention} hat eine {self.emoji_by_name(self._wuerfel_emoji_names[self.game.letzter_wurf])} gewürfelt."
            # spieler_liste = self.game.spieler_liste
            # stecher_liste = self.game.stecher_liste

            # if len(stecher_liste) > 1:
            # out_str += "\n" + (
            # ", ".join(
            # [
            # self.name_to_member(pl.name).mention
            # for pl in stecher_liste
            # ]
            # )
            # + f" haben eine {self.emoji_by_name(self._wuerfel_emoji_names[spieler_liste[0].augen])} geworfen.\n"
            # )
            # out_str += "`!stechen` um zu stechen."

            # if (
            # len(self.game.spieler_liste) > 1
            # and len(self.game.stecher_liste) == 1
            # ):
            # out_str += f"\n{self.name_to_member(self.game.aktiver_spieler.name).mention} hat mit einer {self.emoji_by_name(self._wuerfel_emoji_names[self.game.aktiver_spieler.augen])} den niedrigsten Wurf."
            # out_str += "\n`!würfeln` um das Spiel zu beginnen oder weiter `!einwerfen`."

            # await self.print_to_channel(channel, out_str)

            # if state_0 == "Runde":
            # print("RUNDE BEGINNT")
            # self.game.perform_action(player, command)
            # print(self.game.letzter_wurf)
