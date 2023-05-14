from discord.ext import commands
import discord

intents = discord.Intents.all()
description = 'Description'
help_cmd = commands.DefaultHelpCommand(show_parameter_descriptions=False)
DailyWordBot = commands.Bot(command_prefix='!', description=description, intents=intents, help_command=help_cmd)
extensions = ("extensions.init", "extensions.dict")


@DailyWordBot.event
async def setup_hook() -> None:
    for extension in extensions:
        await DailyWordBot.load_extension(extension)

#Must have a discord bot token pasted into a file named token.txt
with open('token.txt', 'r') as r:
        token = r.readline()
        DailyWordBot.run(token)
