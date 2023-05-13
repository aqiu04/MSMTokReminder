from discord.ext import commands
import discord

intents = discord.Intents.all()
description = 'Description'
DailyWordBot = commands.Bot(command_prefix='!', description=description, intents=intents, help_command=None)
extensions = ("extensions.example",)


@DailyWordBot.event
async def setup_hook() -> None:
    for extension in extensions:
        await DailyWordBot.load_extension(extension)

with open('token.txt', 'r') as r:
        token = r.readline()
        DailyWordBot.run(token)
