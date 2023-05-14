import discord
from discord.ext import commands, tasks

import aiohttp
import asyncio
from extensions.dbCollection import dbCollection

from bs4 import BeautifulSoup
import datetime
from datetime import timezone

intents = discord.Intents.all()
client = discord.Client(intents=intents)

user_times = []
all_user_times = dbCollection('users').fetch_all_from_db()
for document in all_user_times:
    hour = int(document['data']['Hour']) 
    minute = int(document['data']['Minutes'])
    second = int(document['data']['Seconds'])
    user_times.append(datetime.time(hour=hour, minute=minute, second=second, tzinfo=timezone.utc))

print(user_times)

# GENERAL PURPOSE STUFF
class Define(commands.Cog):
    def __init__(self, bot) -> None:
        self.words = dbCollection('words')
        self.users = dbCollection('users')
        
        self.bot = bot
        self.daily_word.start()

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
            
    @commands.command(aliases = ['register'])
    async def adduser(self, ctx, time, UTC = "-7"):
        """Add user to task loop for daily word; default pacific coast time

        Args:
            time (str): military time in format "HH:MM:SS"; add all zeros as applicable
            UTC (str): UTC timezone, defaults to -7.
        """
        if self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f'{ctx.author.mention} Your user is already registered for a certain time. If you want to modify your time, use "!changetime" instead.')
            return
        if ":" != time[2] or ":" != time[5] or not time[:2].isdigit() or not time[3:5].isdigit() or not time[6:].isdigit():
            await ctx.send(f'{ctx.author.mention} **{time}** does not conform with military time style format, which is "HH:MM:SS". Please modify your input.')
            return
        if not UTC.lstrip("-").isdigit():
            await ctx.send(f'{ctx.author.mention} **{UTC}** is not a valid UTC value, which is an integer. Please modify your input.')
            return
        
        hour = str((int(time[:2]) - int(UTC)) % 24)
        minute = time[3:5]
        second = time[6:]
        timeDict = {"Hour": hour, "Minutes": minute, "Seconds": second}
        print(timeDict)
        self.users.store_in_db(str(ctx.message.author.id), timeDict)
        
        self.daily_word.restart()
        user_times.append(datetime.time(hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone.utc))
        
        await ctx.send(f'{ctx.author.mention} You have been registered for the Word of the Day at time {time} for UTC {UTC}. If you want to change your time, use !changetime. If you want to unregister, use !unregister.')
        
    @commands.command()
    async def changetime(self, ctx, time, UTC = "-7"):
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f'{ctx.author.mention} Your user is not registered for a certain time. If you want to add your time, use "!adduser" instead.')
            return
        if ":" != time[2] or ":" != time[5] or not time[:2].isdigit() or not time[3:5].isdigit() or not time[6:].isdigit():
            await ctx.send(f'{ctx.author.mention} **{time}** does not conform with military time style format, which is "HH:MM:SS". Please modify your input.')
            return
        if not UTC.lstrip("-").isdigit():
            await ctx.send(f'{ctx.author.mention} **{UTC}** is not a valid UTC value, which is an integer. Please modify your input.')
            return
        hour = str((int(time[:2]) - int(UTC)) % 24)
        minute = time[3:5]
        second = time[6:]
        timeDict = {"Hour": hour, "Minutes": minute, "Seconds": second}
        self.users.replace_in_db(str(ctx.message.author.id), timeDict)
        
        self.daily_word.restart()
        user_times.append(datetime.time(hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone.utc))
        await ctx.send(f'{ctx.author.mention} Your daily Word of the Day time has been changed to {time} for UTC {UTC}.')
        
    @commands.command()
    async def unregister(self, ctx) -> None:
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f'{ctx.author.mention} Your user is not registered for a certain time. If you want to add your time, use "!adduser" instead.')
            return
        time_to_delete = self.users.fetch_from_db(str(ctx.message.author.id))
        self.users.delete_from_db(str(ctx.message.author.id))
        
        hour = int(document['data']['Hour']) 
        minute = int(document['data']['Minutes'])
        second = int(document['data']['Seconds'])
        self.daily_word.restart()
        user_times.remove(datetime.time(hour=hour, minute=minute, second=second, tzinfo=timezone.utc))
        await ctx.send(f'{ctx.author.mention} You have been unregistered from word of the Day. If you ever want to reregister, use !adduser.') 
        
    @tasks.loop(time = user_times)
    async def daily_word(self):
        print("laksdjflkadsj")
        now = datetime.datetime.utcnow()
        users = []
        for i in user_times:
            if now - i > datetime.timedelta(minutes=1):
                continue
            timeDict = {"Hour": str(i.hour), "Minutes": str(i.minute), "Seconds": str(i.second)}
            users.append(self.users.find_in_db(timeDict, "data"))
        
        for i in users:
            ctx = client.get_user(int(i['_id']))
            await ctx.send(f"@{i['_id']} You now have a daily word of the day!!!!")
                
        
async def setup(bot) -> None:
    await bot.add_cog(Define(bot))