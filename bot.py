import os
import discord
import random
import bs4
import re

from botData import hangmanPics, hangmanWords, jokes
from dotenv import load_dotenv
from discord.ext import commands
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup

# intialize bot for desired server
intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix='!')

# randomly sends a joke from an array of jokes
@bot.command(name='joke', help='Responds with a witty one-liner')
async def joke(ctx):
    response = random.choice(jokes)
    await ctx.send(response)

# simulates dice rolling, arg1 (optional) = number of dice to roll, arg2 (optional) = number of sides on each dice
@bot.command(name='roll_dice', help='Simulates rolling dice. After !roll_dice type # of dice to roll and the # of sides on each dice i.e. !roll_dice 2 3')
async def roll(ctx, *args):
    dice = []

    if(len(args) >= 2):
        for i in range(int(args[0])):
            dice.append(str(random.choice(range(1, int(args[1]) + 1))))
    elif(len(args) == 1):
        for i in range(int(args[0])):
            dice.append(str(random.choice(range(1, 7))))
    else:
        dice.append(str(random.choice(range(1, 7))))

    await ctx.send(', '.join(dice))

# sends a gif of the infamous Rick Astley music video
@bot.command(name='rickroll', help="Just Try It")
async def rickRoll(ctx):
    await ctx.send("https://media.giphy.com/media/lgcUUCXgC8mEo/giphy.gif")

# scrapes tenor.com for a relvant gif and sends it, arg1 = the search term with spaces replaced by _
@bot.command(name='gif', help="After !gif type what you want a gif of making sure to replace spaces with _ i.e. !gif call_of_duty" +
             "\n You may also include a number to see a different related gif i.e. !gif call_of_duty 6")
async def searchTenorGif(ctx, *args):

    searchTerm = args[0].replace('_', '-')
    num = 1
    if(len(args) == 2):
        num = int(args[1])

    my_url = "https://tenor.com/search/" + searchTerm
    uClient = urlopen(my_url)
    page_html = uClient.read()
    uClient.close()
    soupp = soup(page_html, "html.parser")

    container = soupp.find_all('div', {'class': 'Gif'})

    if(num >= len(container)):
        await ctx.send("There are not that many gifs!")
        return

    for gif in container[num-1].find_all('img'):
        gifSource = gif.get('src')
        if(gifSource[-3:] != "gif"):
            continue
        else:
            await ctx.send(gifSource)
            return

# scrapes tenor.com for a relvant sticker (transparent gif) and sends it, arg1 = the search term with spaces replaced by _
@bot.command(name='sticker', help="After !sticker type what you want a sticker of making sure to replace spaces with _ i.e. !sticker call_of_duty" +
             "\n You may also include a number to see a different related sticker i.e. !sticker call_of_duty 6")
async def searchTenorSticker(ctx, *args):

    searchTerm = args[0].replace('_', '-')
    num = 1
    if(len(args) >= 2):
        num = int(args[1])

    my_url = "https://tenor.com/search/" + searchTerm
    uClient = urlopen(my_url)
    page_html = uClient.read()
    uClient.close()
    soupp = soup(page_html, "html.parser")

    container = soupp.find_all('div', {'class': 'Sticker'})

    if(num >= len(container)):
        await ctx.send("There are not that many stickers!")
        return

    for sticker in container[num-1].find_all('img'):
        stickerSource = sticker.get('src')
        if(stickerSource[-3:] != "gif"):
            continue
        else:
            await ctx.send(stickerSource)
            return


@bot.event
async def on_message(message):

    # prevent bot from responding to itself
    if message.author == bot.user:
        return

    # wishs a happy birthday
    if "happy birthday" in message.content.lower():
        await message.channel.send('Happy Birthday! - Soap Bot')
        return

    # reacts to praise
    if message.content == "good bot":
        await message.add_reaction('\N{HEAVY BLACK HEART}')
        return

    # reacts to criticism
    if message.content == "bad bot":
        await message.add_reaction('😢')
        return

    await bot.process_commands(message)

# traverses wikipedia by following the first link on each page until the Wikipedia Page for Philosphy is found
@bot.command(name='wiki', help="Traverses Wikipedia by clicking on the first link on each page until Philosophy is reached. After !wiki enter the Wikipedia page you would like to start from, make sure the page exists and is formatted correctly i.e. " +
             "if you wanted to start at https://en.wikipedia.org/wiki/Sonic_the_Hedgehog you would type !wiki sonic_the_hedgehog")
async def findPhilosophy(ctx, startingURL):

    def findNextLink(wikiURL, visited, forbiddenLinks, forbiddenComponents):

        soupp = getHTML(wikiURL)
        container = soupp.find_all('p')
        urlStub = "https://en.wikipedia.org"

        for paragraph in container:
            links = paragraph.find_all('a')
            for link in links:
                if validStub(str(link), forbiddenComponents):
                    startIndex = str(link).find("href")
                    link = re.findall(r'["](.*?)["]', str(link)[startIndex:])
                    fullURL = str(urlStub) + str(link[0])
                    if validURL(fullURL, visited, forbiddenLinks):
                        return fullURL

    def getHTML(wikiURL):
        uClient = urlopen(wikiURL)
        page_html = uClient.read()
        uClient.close()
        return soup(page_html, "html.parser")

    def validStub(stub, forbiddenComponents):
        for component in forbiddenComponents:
            if component in stub:
                return False
        if "href=\"/wiki/" not in stub:
            return False
        return True

    def validURL(fullURL, visited, forbiddenLinks):
        if fullURL not in visited and fullURL not in forbiddenLinks:
            return True
        else:
            return False

    startingURL = "https://en.wikipedia.org/wiki/" + startingURL
    pageName = [startingURL[30:]]
    visited = [startingURL]
    forbiddenLinks = ["https://en.wikipedia.org/wiki/Wikipedia:NOTRS",
                      "https://en.wikipedia.org/wiki/Wikipedia:No_original_research"]
    forbiddenComponents = ["Help:", "img", "#", "Coordinates", "Wikipedia:"]

    while visited[len(visited)-1] != "https://en.wikipedia.org/wiki/Philosophy":
        newURL = findNextLink(
            visited[len(visited)-1], visited, forbiddenLinks, forbiddenComponents)
        visited.append(newURL)
        pageName.append(newURL[30:])

    visitedString = ", ".join(pageName)
    await ctx.send("THE PATH TO PHILOSOPHY: " + visitedString)


# ASCII art came courtesy of chrishorton on github, https://gist.github.com/chrishorton/8510732aa9a80a03c829b09f12e20d9c
# Play hangman against the bot, intialize game by calling command with no argument, make guesses by calling game with argument
@bot.command(name='hm', help="To play hang man: 1.) !hm 2.) !hm letter/guess")
async def playHM(ctx, *args):

    global word, guesses, revealed, numIncorrect, numCorrect

    # initialize new game
    if(len(args) == 0):
        guesses = []
        word = random.choice(hangmanWords).lower()
        revealed = []
        numIncorrect = 0
        numCorrect = 0
        await ctx.send(hangmanPics[0] + '\nWord: ' + '—' * len(word))
        return

    # checks if the letter/word has already been guessed
    guess = args[0].lower()
    if guess in guesses:
        await ctx.send("You already guessed that letter")
        return

    # if guess is a letter
    if len(guess) == 1:
        if guess in word.lower():
            numCorrect = numCorrect + word.count(guess)
            if numCorrect == len(word):
                await ctx.send("YOU WIN!")
                return
            revealed.append(guess)
            guesses.append(guess)
        else:
            numIncorrect = numIncorrect + 1
            if numIncorrect == 6:
                await ctx.send(hangmanPics[6] + "\nYOU LOSE!")
                return
            guesses.append(guess)

    # if guess is a word
    if len(guess) != 1:
        if guess == word:
            await ctx.send("YOU WIN!")
            return
        else:
            numIncorrect = numIncorrect + 1
            guesses.append(guess)

    # construct string representing current game state
    message = hangmanPics[numIncorrect] + '\nWord: '
    for letter in word:
        if letter in revealed:
            message = message + letter
        else:
            message = message + '—'
    message = message + '\nGuesses: ' + (', '.join(guesses))

    await ctx.send(message)
    return

bot.run(TOKEN)
