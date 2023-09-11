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

daysDict = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6, "all": 8}

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
        # if not word.isalpha():
        #     await ctx.send("I can define words that consist of letters only, silly!")
        #     return

        # Check if word is in DB, if not, return message saying no
        if self.words.find_in_db(word):  
            word_info = self.words.fetch_from_db(word)['data']
        else:
            word_info = await self.request_word_info(word)
            if type(word_info) == dict:
                await ctx.send(f"**{word}** isn't a word! :nerd:")
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
                if "example" in j.keys() and j['example']:
                    embed.add_field(name = f'**Example:**', value= f'{j["example"]}', inline=True)
                else:
                    embed.add_field(name = f'‎', value= f'', inline=True) # An invisible character is used as a placeholder for name
                embed.add_field(name = f'', value= f'', inline=True)

        
        await ctx.send(ctx.author.mention)
        await ctx.send(embed = embed)

    #We didn't figure out global error handling in time so most commands have their own error handler
    @define.error
    async def define_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}` :nerd:")

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
    async def adduser(self, ctx, time = "10:00:00", UTC = "-7"):
        """Add user to task loop for daily word; default pacific coast time

        Args:
            time (str): military time in format "HH:MM:SS"; add all zeros as applicable, default 10AM Pacific
            UTC (str): UTC timezone, defaults to -7.
        """
        if self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f"{ctx.author.mention} You're already registered! LOL! If you want to modify your time, use **!changetime** instead. {random_emoji()}")
            return
        if ":" != time[2] or ":" != time[5] or not time[:2].isdigit() or not time[3:5].isdigit() or not time[6:].isdigit():
            await ctx.send(f'{ctx.author.mention} Um atshually, **{time}** does not conform with military time style format, which is "HH:MM:SS".  :nerd:')
            return
        if not UTC.lstrip("-").isdigit():
            await ctx.send(f'{ctx.author.mention} Um akshually, **{UTC}** is not a valid UTC value, which is an integer. :nerd:')
            return
        
        hour = str((int(time[:2]) - int(UTC)) % 24)
        minute = time[3:5]
        second = time[6:]
        timeDict = {"Hour": hour, "Minutes": minute, "Seconds": second, "_id": str(ctx.message.author.id), "Study": [], "WeekDay": 8, "Reminders": []}
        self.users.store_in_db(str(ctx.message.author.id), timeDict)
        
        user_times.append(datetime.time(hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone.utc))
        self.daily_word.restart()
        
        await ctx.send(f'{ctx.author.mention} Congratulations! You got registered! Enjoy your words {random_emoji()}')
    
    @adduser.error
    async def adduser_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}` :nerd:")

    @commands.command(usage="<time> <UTC>")
    async def changetime(self, ctx, time, UTC = "-7"):
        """Change user's time to receive daily word; default pacific coast time

        Args:
            time (str): military time in format "HH:MM:SS"; add all zeros as applicable
            UTC (str): UTC timezone, defaults to -7.
        """
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f"{ctx.author.mention} You're not registered! LOL! If you want to add your time, use **!adduser** instead. {random_emoji()}")
            return
        if ":" != time[2] or ":" != time[5] or not time[:2].isdigit() or not time[3:5].isdigit() or not time[6:].isdigit():
            await ctx.send(f'{ctx.author.mention} Um atshually, **{time}** does not conform with military time style format, which is "HH:MM:SS".  :nerd:')
            return
        if not UTC.lstrip("-").isdigit():
            await ctx.send(f'{ctx.author.mention} Um akshually, **{UTC}** is not a valid UTC value, which is an integer. :nerd:')
            return
        old = self.users.fetch_from_db(str(ctx.message.author.id))
        old_hour = int(old['data']['Hour'])
        old_minute = int(old['data']['Minutes'])
        old_second = int(old['data']['Seconds'])

        hour = str((int(time[:2]) - int(UTC)) % 24)
        minute = time[3:5]
        second = time[6:]
        timeDict = {"Hour": hour, "Minutes": minute, "Seconds": second, "_id": str(ctx.message.author.id), "Study": [], "WeekDay": 8}
        self.users.replace_in_db(str(ctx.message.author.id), timeDict)
        
        user_times.remove(datetime.time(hour=old_hour, minute=old_minute, second=old_second, tzinfo=timezone.utc))
        user_times.append(datetime.time(hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone.utc))
        self.daily_word.restart()
        await ctx.send(f'{ctx.author.mention} Fine! Your time has been changed to {time} for UTC {UTC}. {random_emoji()}')
    
    @changetime.error
    async def changetime_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}`")

    @commands.command()
    async def unregister(self, ctx) -> None:
        """Removes user from task loop for daily word
        """
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f"{ctx.author.mention} You're not registered! LOL! If you want to add your time, use **!adduser** instead.")
            return
        document = self.users.fetch_from_db(str(ctx.message.author.id))
        self.users.delete_from_db(str(ctx.message.author.id))
        
        hour = int(document['data']['Hour']) 
        minute = int(document['data']['Minutes'])
        second = int(document['data']['Seconds'])
        user_times.remove(datetime.time(hour=hour, minute=minute, second=second, tzinfo=timezone.utc))
        self.daily_word.restart()
        await ctx.send(f'{ctx.author.mention} Bye! If you ever want to reregister, use !adduser. {random_emoji()}') 
    
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

        #1/100 change to not give a word, LOL!
        if(random.randint(1, 100) == 100):
            await ctx.send(f"Sorry, no word for you! Humor these days is randomly generated! {random_emoji()}")
        else:
            await ctx.send(word["_id"])

    @commands.command(usage="<N>")
    async def rollvs(self, ctx, N = 6) -> None:
        """Can you beat the Nerd in an N-sided dice roll?

        Args:
            N (int): Number of sides of the dice to roll. Default 6, must be greater than 1.
        """

        if N <= 1: 
            await ctx.send("The dice must have more than 1 side!")
            return
        
        playerRoll = random.randint(1, N)
        nerdRoll = random.randint(1, N)
        
        #Nerd magic happens here
        for i in range(1, 4):
            if random.randint(1, 10) > 6:
                nerdRoll += 1

        if nerdRoll > N:
            nerdRoll = N

        await ctx.send(f"You :vs: Nerd")
        await ctx.send(f"Your roll: {playerRoll}")
        await ctx.send(f"Nerd's roll: {nerdRoll}")

        if nerdRoll == playerRoll:
            await ctx.send("It's a tie!")
        elif nerdRoll < playerRoll: 
            await ctx.send("You win!")
        else:
            await ctx.send("You lose! :nerd:")

        return

    @rollvs.error
    async def rollvs_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument): #this case should not happen because N has a default value
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("Your argument should be an integer! Usage: " + f"`!{ctx.command.name} {ctx.command.usage}`")

    @commands.command()
    async def flashcard(self, ctx):
        """Given a definition, can you guess the word?
        """
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f"{ctx.author.mention} You're not registered! LOL! If you want to study, use **!adduser** instead.")
            return

        user = self.users.fetch_from_db(str(ctx.message.author.id))
        studyList = user['data']['Study']

        if len(studyList) == 0:
            await ctx.send(f"Your study list is empty! Add new words to study with !study <word>")
            return

        word = studyList[random.randint(0, len(studyList) - 1)]

        word_info = self.words.fetch_from_db(word)['data']
        if type(word_info) == list:
            word_info = word_info[0]

        
        meaning = word_info['meanings'][random.randint(0, len(word_info['meanings']) - 1)]
    
        definition = meaning['definitions'][random.randint(0, len(meaning['definitions']) - 1)]['definition']

        await ctx.send(f"Enter the word being defined by: {definition}")        

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check)

        #Output based on if user input matches the defined word
        if msg.content.lower() == word:
            await ctx.send("Correct! You are smart just like :nerd:")
        else:
            await ctx.send(f"Wrong! The correct word was {word}")

    @commands.command(usage="<word>")
    async def study(self, ctx, word):
        """Add a word to your study list.
        """
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f"{ctx.author.mention} You're not registered! LOL! If you want to study, use **!adduser** instead.")
            return
        
        # Check if word is in DB, if not, return message saying no
        if not self.words.find_in_db(word):  
            word_info = await self.request_word_info(word)
            if type(word_info) == dict:
                await ctx.send(f"**{word}** isn't a word! :nerd:")
                return
            self.words.store_in_db(word, word_info)
        
        user = self.users.fetch_from_db(str(ctx.message.author.id))
        newData = user['data']
        studyList = newData['Study']

        if word.lower() not in studyList:

            studyList.append(word.lower())
            newData['Study'] = studyList
            self.users.replace_in_db(str(ctx.message.author.id), newData)

            await ctx.send(f"{word} successfully added to your study list!")

        else:
            await ctx.send("You're already studying this word! :book:")

    @study.error
    async def study_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}` :nerd:")

    @commands.command(usage="<word>")
    async def unstudy(self, ctx, word):
        """Remove a word to your study list.
        """
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f"{ctx.author.mention} You're not registered! LOL! If you want to study, use **!adduser** instead.")
            return
        
        # Check if word is in DB, if not, return message saying no
        if not self.words.find_in_db(word):  
            word_info = await self.request_word_info(word)
            if type(word_info) == dict:
                await ctx.send(f"**{word}** isn't a word! :nerd:")
                return
            self.words.store_in_db(word, word_info)

        user = self.users.fetch_from_db(str(ctx.message.author.id))
        newData = user['data']
        studyList = newData['Study']

        if word.lower() in studyList:

            studyList.remove(word.lower())
            newData['Study'] = studyList
            self.users.replace_in_db(str(ctx.message.author.id), newData)

            await ctx.send(f"{word} successfully removed from your study list!")

        else:
            await ctx.send("You aren't studying this word!")

    @unstudy.error
    async def unstudy_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Um, ackshually, you should try this instead: " + f"`!{ctx.command.name} {ctx.command.usage}` :nerd:")

    @commands.command(usage="<weekday>")
    async def setWeekday(self, ctx, weekday):
        """Sets the day of week to be reminded.

        Args:
            weekday (str): the day of the week, or "All" to be reminded daily
        """
        if not self.users.find_in_db(str(ctx.message.author.id)):
            await ctx.send(f"{ctx.author.mention} You're not registered! LOL! If you want reminders, use **!adduser** instead.")
            return
        
        user = self.users.fetch_from_db(str(ctx.message.author.id))
        newData = user['data']
        day = daysDict.get(weekday.lower())

        if day == None:
            await ctx.send(f"{weekday} is not a valid day!")
            return
        
        newData['WeekDay'] = day
        self.users.replace_in_db(str(ctx.message.author.id), newData)
        await ctx.send("Reminder day successfully set to "+f"{weekday}!")
        
        


    # @tasks.loop(time = user_times)
    @tasks.loop(minutes = 0.5)
    async def daily_word(self):
        now = datetime.datetime.utcnow()
        year = now.year
        month = now.month
        day = now.day
        dayOfWeek = now.weekday()
        prevDayOfWeek = (dayOfWeek + 6) % 7
        users = self.users.fetch_all_from_db()
        users = [i for i in users]
        new_users = []
        for i in users:
            h = i['data']
            hour = int(h['Hour'])
            minute = int(h['Minutes'])
            second = int(h['Seconds'])
            weekday = int(h["WeekDay"])
            if(weekday != 8 and weekday != dayOfWeek and weekday != prevDayOfWeek):
                continue
            if abs(now - datetime.datetime(year, month, day, hour, minute, second)) > datetime.timedelta(minutes = 0.25):
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
        embed.set_author(name=f"Word of the Day! ({month}-{day}-{year}) 📓")
        for i in word_info["meanings"]:
            embed.add_field(name = f'**{i["partOfSpeech"]}**', value= f'', inline=False)
            embed.add_field(name = f'', value= f'', inline=False)
            for j in i["definitions"]:
                embed.add_field(name = f'**Definition:**', value= f'{j["definition"]}', inline=True)
                if "example" in j.keys() and j['example']:
                    embed.add_field(name = f'**Example:**', value= f'{j["example"]}', inline=True)
                else:
                    embed.add_field(name = f'‎', value= f'', inline=True) # An invisible character is used as a placeholder for name
                embed.add_field(name = f'', value= f'', inline=True)
    
        for i in users:
            user_connec = await self.bot.fetch_user(int(i['_id']))
            weekday = int(i["data"]["WeekDay"])
            ctx = user_connec.dm_channel
            if ctx is None:
                ctx = await user_connec.create_dm()

            if weekday == dayOfWeek or weekday == 8:
                #await ctx.send(f"<@{i['_id']}> You now have a daily word of the day!!!! {random_emoji()}")
                #await ctx.send(embed = embed)
                await ctx.send(f"<@{i['_id']}> u good lil bro? {random_emoji()}")

            elif weekday == prevDayOfWeek:
                await ctx.send(f"<@{i['_id']}> u good for tmrw lil bro? {random_emoji()}")


    
    @staticmethod
    async def daily_word_scraper():
        async with aiohttp.ClientSession() as session:
            url = f'https://www.merriam-webster.com/word-of-the-day'
            async with session.get(url) as resp:
                return await resp.text()
            
    @commands.command()
    async def randomemoji(self, ctx):
        """The Nerd shares a random emoji he likes.
        """

        await ctx.send(random_emoji())
            
def random_emoji():
    emoji_list = [':nerd:', ':disguised_face:', ':clown:', ":cold_face:", ":heart_eyes:", ":full_moon_with_face:", ":smiling_face_with_3_hearts:",
                  ":poop:", ":men_with_bunny_ears_partying:", ":skull:"]
    rand = random.randint(0, len(emoji_list) - 1)
    return emoji_list[rand]
    
        
async def setup(bot) -> None:
    await bot.add_cog(BotCommands(bot))

