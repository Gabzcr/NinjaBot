#!/usr/bin/env python3

import discord
import asyncio
import time
from discord.ext import commands
bot = commands.Bot(command_prefix='!', description='your description')

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

def find_channel(channels, name):
    for chan in channels:
        if normalize_name(chan.name) == name:
            return(chan)
    return(None)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)


@bot.command(pass_context=True)
async def join(ctx):
    queries = ctx.message.content.split("\n")
    messages = []
    for q in queries:
        if q[:6] != "!join ":
            continue
        chan_name = normalize_name(q[6:])
        channel = find_channel(ctx.message.server.channels, chan_name)
        if channel:
            overwrite = channel.overwrites_for(ctx.message.author)
            overwrite.read_messages = True
            overwrite.send_messages = True
            await bot.edit_channel_permissions(channel, ctx.message.author, overwrite)
            message = await bot.say("{0.author.mention}, vous avez désormais accès au channel ".format(ctx.message) + channel.name)
        else:
            message = await bot.say("{0.author.mention}, je ne connais pas ce channel ".format(ctx.message) + chan_name)
        messages.append(message)
    await asyncio.sleep(5)
    for msg in messages:
        await bot.delete_message(msg)
    await bot.delete_message(ctx.message)


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
    if reaction.emoji.name == "Ninja":
        await asyncio.sleep(5)
        await bot.remove_reaction(reaction.message, reaction.emoji, user)


bot.run('process.env.BOT_TOKEN')
