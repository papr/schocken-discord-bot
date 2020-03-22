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

    def emoji_by_name(self, name):
        emoji = get(self.guild.emojis, name=name)
        return str(emoji)

    def name_to_member(self, name):
        member = get(self.guild.members, name=name)
        return member

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
                        # old state of the game
                        state_0 = self.game.state
                        if command in self.game.zulaessige_befehle:
                            player = msg_author.name
                            if state_0 == "Einwerfen":
                                self.game.perform_action(player, command)
                                out_str = f"{message.author.mention} hat eine {self.emoji_by_name(self._wuerfel_emoji_names[self.game.last_roll])} gewürfelt."
                                spieler_liste = self.game.spieler_liste
                                stecher_liste = self.game.stecher_liste

                                if len(stecher_liste) > 1:
                                    out_str += "\n" + (
                                        ", ".join(
                                            [
                                                self.name_to_member(pl.name).mention
                                                for pl in stecher_liste
                                            ]
                                        )
                                        + f" haben eine {self.emoji_by_name(self._wuerfel_emoji_names[spieler_liste[0].einwurf])} geworfen.\n"
                                    )
                                    out_str += "`!stechen` um zu stechen."

                                elif len(stecher_liste) == 1 and len(spieler_liste) > 1:
                                    out_str += f"\n{self.name_to_member(spieler_liste[0].name).mention} hat mit einer {self.emoji_by_name(self._wuerfel_emoji_names[spieler_liste[0].einwurf])} den niedrigsten Wurf."
                                    out_str += "\n`!würfeln` um das Spiel zu beginnen."


                                await self.print_to_channel(channel, out_str)

                            elif state_0 == "Stechen":
                                if len(stecher_liste) > 1:
                                    self.game.perform_action(player,command)
                                    stecher_liste = self.game.stecher_liste
                                    out_str = f"{message.author.mention} hat eine {self.emoji_by_name(self._wuerfel_emoji_names[self.game.last_roll])} gestochen."
                                    out_str+= f"\n" +(
                                                      ", ".join([self.name_to_member(pl.name).mention for pl in stecher_liste]) + " müssen noch `!stechen`")

                                else:
                                    raise NotImplementedError
                        else:
                            raise FalscherSpielBefehl

                        # output = self.game.parse_input(message)
                        # await self.print_to_channel(channel,output)

                except NotImplementedError:
                    msg = "Das geht leider noch nicht."
                    await self.print_to_channel(channel, msg)

                except SpielLäuftNicht:
                    msg = f"Gerade läuft kein Spiel. `!{self._start_game_cmd}` zum starten"
                    await self.print_to_channel(channel, msg)

                except FalscherSpielBefehl:
                    zulaessig = self.game.zulaessige_befehle
                    msg = "Das geht leider nicht. Zulässig sind:\n"
                    msg += "\n".join(["`" + bef + "`" for bef in zulaessig])
                    await self.print_to_channel(channel, msg)

                except FalscherSpieler:
                    msg = "Das darfst du gerade nicht."
                    await self.print_to_channel(channel, msg)

                except FalscheAktion:
                    msg = "Das darfst du gerade nicht."
                    await self.print_to_channel(channel, msg)



            else:
                pass

    async def print_to_channel(self, channel, text):
        return await channel.send(text)
