import discord
import asyncio
import os
import random
import re
from easter_eggs import *

from discord.ext import commands
bot = commands.Bot(command_prefix='!', description="Ninjabot, at your service.\n"
+ "I can give you access to the channel of your choice. (join)\n"
+ "But I don't like those sneaky Ninjas, so I don't let them alive more than 5s on this server.\n"
+ "I can also roll dice for you. Just ask ! (roll)")

def normalize_name(name):
    res = name.lower()
    to_replace = {"a":["à", "â"], "e":["é","è", "ê", "ë"], "i":["î", "ï"], "o":["ô"], "-":[" ","'", "_"], "":["?", "!", ",", ":"]}
    for c1 in to_replace:
        for c2 in to_replace[c1]:
            res = res.replace(c2, c1)
    res = res.replace("--", "-")
    if res[-1] == "-":
        res = res[:-1]
    return(res)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)


@bot.command(pass_context=True)
async def join(ctx):
    """ Gives permission to access given channel. """
    queries = ctx.message.content.split("\n")
    messages = []
    for q in queries:
        if q[:6] != "!join ":
            continue
        chan_name = normalize_name(q[6:])
        channel = discord.utils.find(lambda c: normalize_name(c.name) == chan_name, ctx.message.server.channels)
        if channel:
            print(channel.type)
            print([c.name for c in ctx.message.server.channels])
            overwrite = channel.overwrites_for(ctx.message.author)
            overwrite.read_messages = True
            overwrite.send_messages = True
            await bot.edit_channel_permissions(channel, ctx.message.author, overwrite)
            message = await bot.say("{0.author.mention}, vous avez désormais accès au channel ".format(ctx.message) + channel.name)
        else:
            message = await bot.say("{0.author.mention}, je ne connais pas ce channel ".format(ctx.message) + chan_name)
        messages.append(message)
    await asyncio.sleep(5*60)
    for msg in messages:
        await bot.delete_message(msg)
    await bot.delete_message(ctx.message)


async def roll_g(ctx, l):
    c = ctx.message.content[l+2:]
    special = easter_eggs(c)
    if special:
        await bot.say("{0.author.mention}, ".format(ctx.message) + special)
        return()
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
        await bot.say("{0.author.mention}, je ne reconnais pas cette expression.".format(ctx.message))
        return()
    results = []
    if nb_of_dices <= 0:
        await bot.say("{0.author.mention}, vous devez lancer au moins un dé.".format(ctx.message))
        return()
    if nb_of_dices > 4242:
        await bot.say("{0.author.mention}, vous devez lancer moins de 4242 dés.".format(ctx.message))
        return()
    if value_of_dices <= 0:
        await bot.say("{0.author.mention}, les dés doivent avoir une valeur au moins égale à 1.".format(ctx.message))
        return()
    if value_of_dices > 2**42:
        await bot.say("{0.author.mention}, les dés doivent avoir une valeur inférieure à 2 puissance 42.".format(ctx.message))
        return()
    for dice in range(nb_of_dices):
        results.append(random.randint(1,value_of_dices))
    if nb_of_dices == 1 or nb_of_dices > 100:
        await bot.say("{0.author.mention}, vous avez obtenu un ".format(ctx.message) + "**" + str(sum(results)) + "**" + ".")
    else:
        inter = "(" + str(results[0])
        for value in results[1:]:
            inter = inter + " + " + str(value)
        inter = inter + ")"
        await bot.say("{0.author.mention}, vous avez obtenu un ".format(ctx.message) + "**" + str(sum(results)) + "**" + " " + inter + ".")

@bot.command(pass_context = True,
description = "This command allows the user to roll one or several dice, using the syntax:\n"
+ "!roll [number of dice][d|D][max value of the dice]")
async def roll(ctx):
    """ Draws one or more random numbers from 1 to a specified value. """
    await roll_g(ctx, 4)

@bot.command(pass_context = True)
async def r(ctx):
    """ Alias for roll. """
    await roll_g(ctx, 1)


@bot.listen()
async def on_message(msg):
    if ':Ninja:' in msg.content:
        await asyncio.sleep(5)
        await bot.delete_message(msg)

@bot.listen()
async def on_message_edit(before, after):
    await on_message(after)

@bot.listen()
async def on_reaction_add(reaction, user):
    if 'Ninja' in str(reaction.emoji):
        await asyncio.sleep(5)
        await bot.remove_reaction(reaction.message, reaction.emoji, user)

bot.run(os.getenv('BOT_TOKEN'))
