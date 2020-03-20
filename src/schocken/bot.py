import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")


class SchockenBot:
    def __init__(self):
        self.valid_commands = [
            "start",
        ]
        self.schock_channel_name = "programmierbereich"
        self.game_running = False

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
                    output = game.parse_input(message)
                    await self.print_to_channel(output)
        else:
            pass

    async def print_to_channel(self, channel, text):
        return await channel.send(text)


# @client.event
# async def on_ready():

client = discord.Client()
bot = SchockenBot()


@client.event
async def on_message(message):
    channel = message.channel
    if bot.correct_channel(channel.name):
        await bot.parse_input(message)

    return


client.run(TOKEN)
