import discord
from discord.ext import commands

# GENERAL PURPOSE STUFF
class GeneralMaintenance(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.change_presence(activity=discord.Game("Dictionary, !help"))
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print('------')

    @commands.command(aliases = ['loll'])
    async def lol(self, ctx) -> None:
        await ctx.send("https://docs.google.com/document/d/"
                       "1D54qjRTNmkOBXcvff1vpiph5E5txnd6J6R2oI9e6ZMM/edit?usp=sharing")
        
async def setup(bot) -> None:
    await bot.add_cog(GeneralMaintenance(bot))