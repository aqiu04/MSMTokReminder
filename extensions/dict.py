import discord
from discord.ext import commands, tasks

import aiohttp
import asyncio
from extensions.dbCollection import dbCollection

from bs4 import BeautifulSoup
from datetime import datetime, tzinfo, timezone, timedelta

times = [] # hold datetime info for each user

# GENERAL PURPOSE STUFF
class Define(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.index = 0
        
        self.words = dbCollection('words')
        self.users = dbCollection('users')

    @commands.command()
    async def define(self, ctx, word: str) -> None:
        # Check if word is in DB, if not, return message saying no
        if self.words.find_in_db(word):  
            word_info = self.words.fetch_from_db(word)['data']
        else:
            word_info = await self.request_word_info(word)
            if 'title' in word_info[0].keys():
                await ctx.send(f'"**{word}**" is not a valid word according to dictionary.com. Please recheck your spelling.')
                return
            self.words.store_in_db(word.lower(), word_info)
        if type(word_info) == list:
            word_info = word_info[0]

        # Return definition
                
        embed = discord.Embed(
        title=f"{word}",
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
            
    @commands.command()
    async def adduser(self, ctx, time, UTC = "-7"):
        """Add user to task loop for daily word; default pacific coast time

        Args:
            time (str): military time in format "HH:MM:SS"; add all zeros as applicable
            UTC (str): UTC timezone, defaults to -7.
        """
        if self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f'{ctx.author.mention} Your user is already registered for a certain time. If you want to modify your time, use "!changetime" instead.')
            return
        if ":" != time[2] and ":" != time[5] and not time[:2].isdigit() and not time[3:5].isdigit() and not time[6:].isdigit():
            await ctx.send(f'{ctx.author.mention} **{time}** does not conform with military time style format, which is "HH:MM:SS". Please modify your input.')
            return
        if not UTC.lstrip("-").isdigit():
            await ctx.send(f'{ctx.author.mention} **{UTC}** is not a valid UTC value, which is an integer. Please modify your input.')
            return
        timeDict = {"Hour": time[:2], "Minutes": time[3:5], "Seconds": time[6:]}
        
        self.users.store_in_db(str(ctx.message.author.id), timeDict)
        await ctx.send(f'{ctx.author.mention} You have been registered for the Daily Word of the Day for the time {time} at UTC {UTC}. If you want to change your time, use !changetime.')
            
    # @tasks.loop(seconds=1.0)
    # async def printer(self):
    #     print(self.index)
    #     self.index += 1
        
    # @tasks.loop(time = times)
    # async def daily_word(self):
    #     # check which time and user is applicable
        
    #     # mention that user and send the definition of the word
    #     pass
                
async def setup(bot) -> None:
    await bot.add_cog(Define(bot))