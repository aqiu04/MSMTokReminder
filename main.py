from typing import Union

import discord
from discord.ext import commands, tasks

import logging

intents = discord.Intents.default()
intents.members = True
description = 'Description'
DailyWordBot = commands.Bot(command_prefix='?', description=description, intents=intents, help_command=None)

logging.basicConfig(level=logging.INFO, filename="logging.log", datefmt='%m/%d/%Y %H:%M:%S',
                    format='%(levelname)s: %(module)s: %(message)s; %(asctime)s')


# GENERAL PURPOSE STUFF
class GeneralMaintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await DailyWordBot.change_presence(activity=discord.Game("Jstris, ?help"))
        print(f'Logged in as {DailyWordBot.user} (ID: {DailyWordBot.user.id})')
        print('------')

    @commands.command()
    async def help(self, ctx) -> None:
        logging.info("Executing help")
        await ctx.send("https://docs.google.com/document/d/"
                       "1D54qjRTNmkOBXcvff1vpiph5E5txnd6J6R2oI9e6ZMM/edit?usp=sharing")
        logging.info("Finish help")


if __name__ == "__main__":
    DailyWordBot.add_cog(GeneralMaintenance(DailyWordBot))

    with open('token.txt', 'r') as r:
        token = r.readline()
        DailyWordBot.run(token)
    