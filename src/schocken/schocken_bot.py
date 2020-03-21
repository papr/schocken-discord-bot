from .exceptions import SpielLäuft, SpielLäuftNicht
from .schockenrunde import SchockenRunde
from discord.utils import get

class SchockenBot:
    def __init__(self, client):
        self.client = client
        # bot will never run on any other server than Café A
        self.guild = client.guilds[0]
        self.schock_channel_name = "programmierbereich"
        self.valid_guild_name = "Café A"
        self.game_running = False
        self._start_game_cmd = "schocken"
        self._end_game_cmd = "beenden"

    def emoji_by_name(self, name):
        emoji = get(message.guild.emojis, name = name)
        return str(emoji)

    async def parse_input(self, message):
        # all messages from channels with read permissions are read
        msg_text = message.content
        channel = message.channel
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
                            msg = f"{message.author.name} will Schocken. `!einwerfen` zum mitmachen"
                            await self.print_to_channel(channel, msg)

                    elif command == self._end_game_cmd:
                        if self.game_running:
                            msg = f"{message.author.name} hat das Spiel beendet"
                            self.game_running = False()
                            await self.print_to_channel(channel, msg)
                        else:
                            raise SpielLäuftNicht 
                    else:
                        if not self.game_running:
                            raise SpielLäuftNicht
                        #actual game
                        #TODO Fix Logic
                        output = self.game.parse_input(message)
                        await self.print_to_channel(channel,output)

                except NotImplementedError:
                    msg = "Das geht leider noch nicht."
                    await self.print_to_channel(channel,msg)

                except SpielLäuftNicht:
                    msg = f"Gerade läuft kein Spiel. `!{self._start_game_cmd}` zum starten"
                    await self.print_to_channel(channel,msg)
            else:
                pass

    async def print_to_channel(self, channel, text):
        return await channel.send(text)
