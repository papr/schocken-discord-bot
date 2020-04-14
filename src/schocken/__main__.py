import os

import discord
from discord.utils import get
from dotenv import load_dotenv

from schocken import __version__
from schocken.exceptions import FalscherServer
from schocken.bot import SchockenBot


def run_bot():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD = os.getenv("DISCORD_GUILD")
    client = discord.Client()

    is_initial_start = True

    # when connecting
    @client.event
    async def on_ready():
        nonlocal is_initial_start
        # check if server is correct:
        for guild in client.guilds:
            if guild.name != client.bot.valid_guild_name:
                raise FalscherServer("Dieser Bot darf nur ins Café A")

        if is_initial_start:
            client.bot = SchockenBot(client)
            ch = client.get_channel(690929770355097610)  # schocktresen
            await ch.send(f"Schocken (v{__version__}) kann jetzt losgehen. :muscle:")
            print("Success")
            is_initial_start = False

    # when a message is read by the bot
    @client.event
    async def on_message(message):
        try:
            await client.bot.parse_input(message)
        except AttributeError:
            msg_text = message.content
            author = message.author.mention
            ch = client.get_channel(694603857950539887)  # errorland
            await ch.send(
                f"Dropping message because bot was not initialized yet.\n"
                f"{author} said:\n"
                f"> {msg_text}"
            )

    @client.event
    async def on_error(error, *args, **kwargs):
        import traceback

        ch = client.get_channel(694603857950539887)  # errorland
        trace = traceback.format_exc()
        await ch.send(f"Error: {error}({args}, {kwargs})\n```\n{trace}\n```")
        return

    client.run(TOKEN)


if __name__ == "__main__":
    run_bot()
