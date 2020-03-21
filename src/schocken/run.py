import os

import discord
from discord.utils import get
from dotenv import load_dotenv

from schocken.exceptions import FalscherServer
from schocken.schocken_bot import SchockenBot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
client = discord.Client()
bot = SchockenBot()

# when connecting
@client.event
async def on_ready():
    #check if server is correct:
    for guild in client.guilds:
        if guild.name != bot.valid_guild_name:
            raise FalscherServer("Dieser Bot darf nur ins Café A")
    print("Success")
    #read emojis from server
    bot.init_emojis(client.guilds[0])

# when a message is read by the bot
@client.event
async def on_message(message):
    await bot.parse_input(message)

    return


client.run(TOKEN)
