class SchockenBot:
    def __init__(self):
        self.valid_commands = [
            "start",
        ]
        self.schock_channel_name = "programmierbereich"
        self.valid_guild_name = "Café A"
        self.game_running = False

    def init_emojis(self, guild):
        self.emojis = guild.emojis

    def emoji_by_name(self, name):
        return [em for em in self.emojis if em.name==name][0]

    def check_if_valid_command(self, command):
        if command in self.valid_commands:
            return True
        else:
            return False

    def correct_channel(self, channel_name):
        if channel_name == self.schock_channel_name:
            return True
        else:
            return False

    async def parse_input(self, message):
        msg_text = message.content
        channel = message.channel
        if msg_text.startswith("!"):
            command = msg_text.split("!")[-1]
            if not self.check_if_valid_command(command):
                await self.print_to_channel(
                    channel, "Kein zulässiger Befehl: !" + command
                )
            else:
                if command == "start":
                    if self.game_running:
                        await self.print_to_channel(
                            channel, "Es läuft bereits eine Runde"
                        )
                    else:
                        game = SchockenRunde()
                else:
                    try:
                        output = game.parse_input(message)
                        await self.print_to_channel(output)
                    except NotImplementedError:
                        msg = "Das geht leider noch nicht."
                        await self.print_to_channel(msg)
        else:
            pass

    async def print_to_channel(self, channel, text):
        return await channel.send(text)
