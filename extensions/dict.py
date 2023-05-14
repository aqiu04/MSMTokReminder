import discord
from discord.ext import commands, tasks

import aiohttp
import asyncio
from extensions.dbCollection import dbCollection

import datetime
from bs4 import BeautifulSoup
import datetime
from datetime import timezone, timedelta

import random

intents = discord.Intents.all()
client = discord.Client(intents=intents)

user_times = []
all_user_times = dbCollection('users').fetch_all_from_db()
for document in all_user_times:
    hour = int(document['data']['Hour']) 
    minute = int(document['data']['Minutes'])
    second = int(document['data']['Seconds'])
    user_times.append(datetime.time(hour=hour, minute=minute, second=second, tzinfo=timezone.utc))

# GENERAL PURPOSE STUFF
class BotCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.words = dbCollection('words')
        self.users = dbCollection('users')
        
        self.bot = bot
        self.daily_word.start()

    @commands.command(description="Gives the definition of any word in the dictionary.", name="define", usage="<word>")
    async def define(self, ctx, word: str = commands.parameter(description=": the word which is being defined")) -> None:
        """Gives the dictionary definition of any word

        Args:
            word (str): the word to be defined
        """
        if not word.isalpha():
            await ctx.send("I can define words that consist of letters only, silly!")
            return

        # Check if word is in DB, if not, return message saying no
        if self.words.find_in_db(word):  
            word_info = self.words.fetch_from_db(word)['data']
        else:
            word_info = await self.request_word_info(word)
            if 'title' in word_info[0].keys():
                await ctx.send(f'"**{word}**" is not a valid word according to dictionary.com. Please recheck your spelling.')
                return
            self.words.store_in_db(word, word_info)
        if type(word_info) == list:
            word_info = word_info[0]

        # Return definition
                
        embed = discord.Embed(
        title=f"{word}",
        url=f"https://www.dictionary.com/browse/{word}",
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

    @define.error
    async def define_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}`")

    # @commands.command()
    # async def help(self, ctx):
    #     embed = discord.Embed()
    #     embed.set_author(name=f"Help Menu")
    #     embed.add_field(name = '**!define**', value= f'Gives the definition of a word.', inline=True)
    #     embed.add_field(name = '**Example:**', value= f'!define <word>', inline=True)

    #     await ctx.send(ctx.author.mention)
    #     await ctx.send(embed = embed)

    # @commands.command()
    # async def synonym(self, ctx, word: str):

    #     if self.words.find_in_db(word):  
    #         word_info = self.words.fetch_from_db(word)['data']
    #     else:
    #         word_info = await self.request_word_info(word)
    #         if 'title' in word_info[0].keys():
    #             await ctx.send(f'"**{word}**" is not a valid word according to dictionary.com. Please recheck your spelling.')
    #             return
    #         self.words.store_in_db(word.lower(), word_info)
    #     if type(word_info) == list:
    #         word_info = word_info[0]

    #     embed = discord.Embed()
    #     embed.set_author(name=f"Synonyms for {word}:")

    #     for i in word_info["meanings"]:
    #         for j in i["synonyms"]:
    #             embed.add_field(name = f'{j}', value= f'', inline=True)
                

    #     await ctx.send(ctx.author.mention)
    #     await ctx.send(embed = embed)
        
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
            
    @commands.command(aliases = ['register'], usage="<time> <UTC>")
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
        timeDict = {"Hour": hour, "Minutes": minute, "Seconds": second, "_id": str(ctx.message.author.id)}
        self.users.store_in_db(str(ctx.message.author.id), timeDict)
        
        self.daily_word.restart()
        user_times.append(datetime.time(hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone.utc))
        
        await ctx.send(f'{ctx.author.mention} You have been registered for the Word of the Day at time {time} for UTC {UTC}. If you want to change your time, use !changetime. If you want to unregister, use !unregister.')
    
    @adduser.error
    async def adduser_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}`")

    @commands.command(usage="<time> <UTC>")
    async def changetime(self, ctx, time, UTC = "-7"):
        """Change user's time to receive daily word; default pacific coast time

        Args:
            time (str): military time in format "HH:MM:SS"; add all zeros as applicable
            UTC (str): UTC timezone, defaults to -7.
        """
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
        timeDict = {"Hour": hour, "Minutes": minute, "Seconds": second, "_id": str(ctx.message.author.id)}
        self.users.replace_in_db(str(ctx.message.author.id), timeDict)
        
        self.daily_word.restart()
        user_times.append(datetime.time(hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone.utc))
        await ctx.send(f'{ctx.author.mention} Your daily Word of the Day time has been changed to {time} for UTC {UTC}.')
    
    @changetime.error
    async def changetime_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}`")

    @commands.command()
    async def unregister(self, ctx) -> None:
        """Removes user from task loop for daily word
        """
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f'{ctx.author.mention} Your user is not registered for a certain time. If you want to add your time, use "!adduser" instead.')
            return
        document = self.users.fetch_from_db(str(ctx.message.author.id))
        self.users.delete_from_db(str(ctx.message.author.id))
        
        hour = int(document['data']['Hour']) 
        minute = int(document['data']['Minutes'])
        second = int(document['data']['Seconds'])
        self.daily_word.restart()
        user_times.remove(datetime.time(hour=hour, minute=minute, second=second, tzinfo=timezone.utc))
        await ctx.send(f'{ctx.author.mention} You have been unregistered from word of the Day. If you ever want to reregister, use !adduser.') 
    
    @commands.command(aliases = ['random', 'rmword'])
    async def randomword(self, ctx) -> None:
        """The Nerd will pull a random word from his lexicon!
        """
        db = self.words.fetch_all_from_db()

        words = [i for i in db]

        size = len(words)

        if size == 0:
            return

        rand = random.randint(0, size - 1)

        word = words[rand]

        if(random.randint(1, 100) == 100):
            await ctx.send("Sorry, no word for you! Humor these days is randomly generated!")
        else:
            await ctx.send(word["_id"])

    @commands.command(usage="<N>")
    async def rollvs(self, ctx, N: int = commands.parameter(default=6)) -> None:
        """Can you beat the Nerd in an N-sided dice roll?

        Args:
            N (int): Number of sides of the dice to roll. Default 6, must be greater than 1.
        """
        if N <= 1: 
            await ctx.send("The dice must have more than 1 side!")
            return
        
        return

    @rollvs.error
    async def rollvs_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("Your argument should be an integer! Usage: " + f"`!{ctx.command.name} {ctx.command.usage}`")


        
    # @tasks.loop(time = user_times)
    @tasks.loop(minutes = 5)
    async def daily_word(self):
        now = datetime.datetime.utcnow()
        year = now.year
        month = now.month
        day = now.day
        users = self.users.fetch_all_from_db()
        users = [i for i in users]
        new_users = []
        for i in users:
            h = i['data']
            hour = int(h['Hour'])
            minute = int(h['Minutes'])
            second = int(h['Seconds'])
            if abs(now - datetime.datetime(year, month, day, hour, minute, second)) > datetime.timedelta(minutes=5):
                continue
            new_users.append(i)
        users = new_users
        
        html_content = await self.daily_word_scraper()
        soup = BeautifulSoup(html_content, 'html.parser')
        daily_word = soup.find('h2', 'word-header-txt').text
        
        word_info = await self.request_word_info(daily_word)
        if not self.words.find_in_db(daily_word):
            self.words.store_in_db(daily_word, word_info)
        if type(word_info) == list:
            word_info = word_info[0]

        # Return definition
                
        embed = discord.Embed(
        title=f"{daily_word}",
        url=f"https://www.dictionary.com/browse/{daily_word}",
        color=discord.Colour.blue())
        embed.set_author(name="Daily-Word")
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
    
        for i in users:
            user_connec = await self.bot.fetch_user(int(i['_id']))
            ctx = user_connec.dm_channel
            if ctx is None:
                ctx = await user_connec.create_dm()
            await ctx.send(f"<@{i['_id']}> You now have a daily word of the day!!!!")
            await ctx.send(embed = embed)
    
    @staticmethod
    async def daily_word_scraper():
        async with aiohttp.ClientSession() as session:
            url = f'https://www.merriam-webster.com/word-of-the-day'
            async with session.get(url) as resp:
                return await resp.text()
        
async def setup(bot) -> None:
    await bot.add_cog(BotCommands(bot))

