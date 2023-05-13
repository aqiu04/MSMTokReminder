import discord
from discord.ext import commands

# GENERAL PURPOSE STUFF
class Define(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def define(self, ctx, word: str) -> None:
        # Check if word is in DB, if not, return message saying no
        
        word_in_DB = True
        
        if not word_in_DB:
            await ctx.send(ctx.author.mention)
            await ctx.send(f"{word} is not defined in the dictionary. Maybe check your spelling?")
            return
            
        # If so, find defintion in db
        
        definition = "sample def"
        
        # Return definition
        
        embed = discord.Embed(
        title=word,
        url=f"https://www.merriam-webster.com/dictionary/{word}",
        color=discord.Colour.blue())
        embed.set_author(name="Daily-Word")
        embed.set_thumbnail(url="https://imgur.com/a/4RU7r8k")
        embed.add_field(name = f'**Definition:**', value= f"{definition}", inline=True )
        
        await ctx.send(ctx.author.mention)
        await ctx.send(embed = embed)
                
async def setup(bot) -> None:
    await bot.add_cog(Define(bot))