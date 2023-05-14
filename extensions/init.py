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
        
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.change_presence(activity=discord.Game("Word Oracle, ?help"))
        
async def setup(bot) -> None:
    await bot.add_cog(GeneralMaintenance(bot))