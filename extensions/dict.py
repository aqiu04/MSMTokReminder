import discord
from discord.ext import commands, tasks

import aiohttp
import asyncio

times = [] # hold datetime info for each user

# GENERAL PURPOSE STUFF
class Define(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.printer.start()
        self.index = 0

    @commands.command()
    async def define(self, ctx, word: str) -> None:
        # Check if word is in DB, if not, return message saying no
        
        # word_in_DB = True
        
        # if not word_in_DB:
        #     await ctx.send(ctx.author.mention)
        #     await ctx.send(f"{word} is not defined in the dictionary. Maybe check your spelling?")
        #     return
            
        # If so, find defintion in db
        
        word_info = await self.request_word_info(word)
        word_info = word_info[0]
        
        # Return definition
        
        embed = discord.Embed(
        title=f"word",
        url=f"https://www.merriam-webster.com/dictionary/{word}",
        color=discord.Colour.blue())
        embed.set_author(name="Daily-Word")
        # embed.set_thumbnail(url="https://imgur.com/a/4RU7r8k")
        for i in word_info["meanings"]:
            embed.add_field(name = f'**{i["partOfSpeech"]}**', value= f'', inline=False)
            embed.add_field(name = f'', value= f'', inline=False)
            for j in i["definitions"]:
                embed.add_field(name = f'**Definition:**', value= f'{j["definition"]}', inline=True)
                if "example" in j.keys():
                    embed.add_field(name = f'**Example:**', value= f'{j["example"]}', inline=True)
                else:
                    embed.add_field(name = f'**Example:**', value= f'', inline=True)
                embed.add_field(name = f'', value= f'', inline=True)

        
        await ctx.send(ctx.author.mention)
        await ctx.send(embed = embed)
        
    @staticmethod
    async def request_word_info(word: str):
        """Gets word information from dictionary.com api

        Args:
            word (str): word to query
        """
        
        async with aiohttp.ClientSession() as session:
            url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
            async with session.get(url) as resp:
                return await resp.json()
            
    @tasks.loop(seconds=1.0)
    async def printer(self):
        print(self.index)
        self.index += 1
        
    @tasks.loop(time = times)
    async def daily_word(self):
        pass
                
                
async def setup(bot) -> None:
    await bot.add_cog(Define(bot))