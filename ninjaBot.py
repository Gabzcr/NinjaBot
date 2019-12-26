import discord
import asyncio
import os
import random
import re
import unicodedata
from easter_eggs import *

from discord.ext import commands
bot = commands.Bot(command_prefix='!', description="Ninjabot, at your service.\n"
+ "I can give you access to the channel of your choice. (join)\n"
+ "But I don't like those sneaky Ninjas, so I don't let them alive more than 5s or 10s on this server.\n"
+ "I can roll dice for you. Just ask ! (roll)\n"
+ "I can also prepare a poll message for you by reacting with appropriate emojis so that no one has to find them in the list. (poll)")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)


def normalize_name(name):
    """ Transform the string name according to a norm ignoring punctuation and accents.
    The new string must be able to match channel names, hence the spaces are replaced with hyphens."""
    res = name.lower()
    to_replace = {"a":["à", "â"], "e":["é","è", "ê", "ë"], "i":["î", "ï"], "o":["ô"], "-":[" ","'", "_"], "":["?", "!", ",", ":"]}
    for c1 in to_replace:
        for c2 in to_replace[c1]:
            res = res.replace(c2, c1)
    res = res.replace("--", "-")
    if res[-1] == "-":
        res = res[:-1]
    return(res)


async def join_g(msg):
    """
    General function for join commands.
    For each line of the message msg corresponding to a join command (!join [channel_name]), the bot looks for the corresponding channel
    and overwrites the permissions of the user who sent this message to grant him the rights to read and send messages in this channel.
    The bot answers to the user when finished, with the result of the command.
    """
    queries = msg.content.split("\n")
    messages = []
    for q in queries:
        if q[:6] != "!join ":
            continue
        #find corresponding channel
        chan_name = normalize_name(q[6:])
        channel = discord.utils.find(lambda c: normalize_name(c.name) == chan_name, msg.guild.channels)
        if channel:
            if not(channel.category) or normalize_name(channel.category.name[:6]) != "murder":
                #restrict joinable channels to a "murder" list category
                message = await msg.channel.send("{0.author.mention}, ce channel n'est pas joignable ".format(msg) + channel.name)
            else:
                #adapt permissions
                overwrite = channel.overwrites_for(msg.author)
                overwrite.read_messages = True
                overwrite.send_messages = True
                await channel.set_permissions(msg.author, overwrite=overwrite)
                message = await msg.channel.send("{0.author.mention}, vous avez désormais accès au channel ".format(msg) + channel.name)
        else:
            message = await msg.channel.send("{0.author.mention}, je ne reconnais pas ce channel ".format(msg) + chan_name)
        messages.append(message)
    #clean every command message and automated answer after five minutes
    await asyncio.sleep(5*60)
    for message in messages:
        await message.delete()
    await msg.delete()

@bot.command(pass_context=True)
async def join(ctx):
    """ Gives permission to access asked channel. """
    await join_g(ctx.message)


async def leave_g(msg):
    """
    General function for leave commands.
    For each line of the message msg corresponding to a leave command (!leave [channel_name]),
    the bot looks for the corresponding channel and suppress all permission overwrites for the user who sent this message.
    The bot answers to the user when finished, with the result of the command.
    """
    queries = msg.content.split("\n")
    messages = []
    for q in queries:
        if q[:7] != "!leave ":
            continue
        #find corresponding channel
        chan_name = normalize_name(q[7:])
        channel = discord.utils.find(lambda c: normalize_name(c.name) == chan_name, msg.guild.channels)
        if channel:
            await channel.set_permissions(msg.author, overwrite=None)
            message = await msg.channel.send("{0.author.mention}, vous n'avez plus accès spécifiquement au channel ".format(msg) + channel.name)
        else:
            message = await msg.channel.send("{0.author.mention}, je ne reconnais pas ce channel ".format(msg) + chan_name)
        messages.append(message)
    #clean every command message and automated answer after five minutes
    await asyncio.sleep(5*60)
    for message in messages:
        await message.delete()
    await msg.delete()

@bot.command(pass_context=True)
async def leave(ctx):
    """Suppress permission overwrites for asked channel (cancels a join command)."""
    await leave_g(ctx.message)


async def roll_g(msg, l):
    """
    General function for roll commands.
    The bot checks if the given command corresponds to an easter egg via easter_eggs function from easter_eggs.py and reacts accordingly.
    If no easter egg found, it analyzes the dice rolling command. It generates random numbers according to asked number of dice and
    value of the dice, and sum them.
    The bot answers to the user with the obtained total and the detailed results of each dice (if not too many dice).
    """
    c = msg.content[l+2:]
    #looking for special easter egg message
    special = easter_eggs(c)
    if special:
        message = await msg.channel.send("{0.author.mention} ".format(msg) + special)
        await asyncio.sleep(15*60)
        await message.delete()
        await msg.delete()
        return()

    #parsing the dice rolling command
    c2 = re.split("d|D", c)
    try:
        if len(c2) != 2:
            raise(ValueError)
        if c2[0] == '':
            nb_of_dices = 1
        else:
            nb_of_dices = int(c2[0])
        value_of_dices = int(c2[1])
    except(ValueError):
        await msg.channel.send("{0.author.mention} je ne reconnais pas cette expression.".format(msg))
        return()
    results = []

    #checking for degenerate cases (invalid dice rolling command)
    if nb_of_dices <= 0:
        await msg.channel.send("{0.author.mention} vous devez lancer au moins un dé.".format(msg))
        return()
    if nb_of_dices > 4242:
        await msg.channel.send("{0.author.mention} vous devez lancer moins de 4242 dés.".format(msg))
        return()
    if value_of_dices <= 0:
        await msg.channel.send("{0.author.mention} les dés doivent avoir une valeur au moins égale à 1.".format(msg))
        return()
    if value_of_dices > 2**42:
        await msg.channel.send("{0.author.mention} les dés doivent avoir une valeur inférieure à 2 puissance 42.".format(msg))
        return()

    #generating random numbers for the dice results
    for dice in range(nb_of_dices):
        results.append(random.randint(1,value_of_dices))

    #answering (according to number of dice)
    if nb_of_dices == 1 or nb_of_dices > 100:
        await msg.channel.send("{0.author.mention} vous avez obtenu un ".format(msg) + "**" + str(sum(results)) + "**" + ".")
    else:
        inter = "(" + str(results[0])
        for value in results[1:]:
            inter = inter + " + " + str(value)
        inter = inter + ")"
        await msg.channel.send("{0.author.mention} vous avez obtenu un ".format(msg) + "**" + str(sum(results)) + "**" + " " + inter + ".")

@bot.command(pass_context = True,
description = "This command allows the user to roll one or several dice, using the syntax:\n"
+ "!roll [number of dice][d|D][max value of the dice]")
async def roll(ctx):
    """ Draws one or more random numbers from 1 to a specified value. """
    await roll_g(ctx.message, 4)

@bot.command(pass_context = True)
async def r(ctx):
    """ Alias for roll. """
    await roll_g(ctx.message, 1)


async def poll_g(msg, length):
    """
    General message for poll commands.
    The bot superficially analyzes the structure of the message to detect the offering of options to the user of the form
    1. or A- etc.
    It then parses the message to detect the emoji contained.
    The bot reacts to the poll message with all proposition labels and emojis found, in correct order.
    """
    lines = msg.content.split("\n")
    #analysis of the message structure to get letters or digits used to label a proposition
    if len(lines) >= 2:
        lines[0] = lines[0][length + 2:]
        for l in lines:
            start = re.match("([0-9]|[a-z]|[A-Z])( |\.|\-)", l)
            if not(start):
                continue
            start = start.group(0)[:-1]
            if len(start) != 1:
                continue
            if (48 <= ord(start) and ord(start) <= 57) or ():
                await msg.add_reaction(start + "\N{COMBINING ENCLOSING KEYCAP}")
            elif 65 <= ord(start) and ord(start) <= 90:
                await msg.add_reaction(unicodedata.lookup("REGIONAL INDICATOR SYMBOL LETTER " + start))
            elif 97 <= ord(start) and ord(start) <= 122:
                start = chr(ord(start) - 32)
                await msg.add_reaction(unicodedata.lookup("REGIONAL INDICATOR SYMBOL LETTER " + start))
    #looking for the presence of emojis
    for i in range(len(msg.content)):
        s = msg.content[i]
        if ord(s) > 160:
            try:
                await msg.add_reaction(s)
            except:
                if s == "\N{COMBINING ENCLOSING KEYCAP}":
                    await msg.add_reaction(msg.content[i-1] + s)
        elif s == "<":
            em = re.match("<:(.*?):(.*?)>", msg.content[i:])
            if em:
                id = int(em.group(2))
                await msg.add_reaction(bot.get_emoji(id))

@bot.command(pass_context=True)
async def poll(ctx):
    """ Automatically fills a poll message with appropriate emoji reactions. """
    await poll_g(ctx.message, 4)

@bot.command(pass_context=True)
async def sondage(ctx):
    """ (French alias for poll)
    Réagis automatiquement à un message de sondage avec les emojis appropriées. """
    await poll_g(ctx.message, 7)


@bot.listen()
async def on_message(msg):
    """ Detect and automatically erase Ninja emojis in messages (after 10s).
    Detect Michel's messages from Le Grand Méchant Renard and react with Michel. """
    react = re.search("(B|b)onjour (M|m)ada(a)+me", msg.content)
    if react:
        await msg.add_reaction("🐥")
    if ':Ninja:' in msg.content:
        await asyncio.sleep(10)
        await msg.delete()


@bot.listen()
async def on_message_edit(before, after):
    """ Applies appropriate function to edited message (new message analysis)."""
    await on_message(after)
    if after.content[:5] == "!poll":
        await poll_g(after, 4)
    elif after.content[:8] == "!sondage":
        await poll_g(after, 7)
    elif after.content[:5] == "!join":
        await join_g(after)
    elif after.content[:6] == "!leave":
        await leave_g(after)
    elif after.content[:5] == "!roll":
        await roll_g(after, 4)
    elif after.content[:2] == "!r":
        await roll_g(after, 1)


@bot.listen()
async def on_reaction_add(reaction, user):
    """ Detect and automatically erase Ninja emojis in reactions (after 5s)."""
    if 'Ninja' in str(reaction.emoji):
        await asyncio.sleep(5)
        await reaction.message.remove_reaction(reaction.emoji, user)

import datetime

async def alarm_message():
    await bot.wait_until_ready()
    while not bot.is_closed():
        for g in bot.guilds:
            print(normalize_name(g.name))
        guild = discord.utils.find(lambda c: normalize_name(c.name) == "test", bot.guilds)
        channel = discord.utils.find(lambda c: normalize_name(c.name) == "general", guild.channels)
        t = datetime.datetime.now()
        print(t)
        if t.month == 12 and t.day == 26 and t.hour == 17:
            messages = "Nous sommes le 26 décembre, et il est 17h{}".format(t.minute)
            await channel.send(messages)
            await asyncio.sleep(30)

bot.loop.create_task(alarm_message())

bot.run(os.getenv('BOT_TOKEN'))
