import discord
import asyncio
import os
import random
import re
import unicodedata
import datetime
from easter_eggs import *

from discord.ext import commands
bot = commands.Bot(command_prefix='!', description="Hi, I'm Ninjabot\n"
+ "I manage permissions to private channels, giving access to them on demand (commands join and leave)\n"
+ "I can roll dice and make basic operations on them (command roll)\n"
+ "I can help with your polls\n")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)

################################################################################
# Channel access management #
################################################################################

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
    """ Gives permission to access requested channel. """
    await join_g(ctx.message)


async def leave_g(msg):
    """
    General function for leave commands.
    For each line of the message msg corresponding to a leave command (!leave [channel_name]),
    the bot looks for the corresponding channel and suppresses all permission overwrites for the user who sent this message.
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
    """Suppress permission overwrites for requested channel (cancels a join command)."""
    await leave_g(ctx.message)


################################################################################
# Radio feature for a particular GN #
################################################################################

radio_is_on = False
radio_timelapse = 8*60+34

@bot.command(pass_context = True)
async def radio_on(ctx):
    """Turns a channel into a GN "radio" : half of the time, all members can speak through it, the other half they are muted.
    Permissions alternate in regular intervals given by radio_timelapse, default 8min34."""
    global radio_is_on
    radio_is_on = True
    msg = ctx.message
    chan_name = normalize_name(msg.content[10:])
    target_channel = discord.utils.find(lambda c: normalize_name(c.name) == chan_name, msg.guild.voice_channels)
    await msg.channel.send("{0.author.mention}, c'est noté ! ".format(msg)+\
    "Le salon vocal {0.name} est désormais en communication alternée.".format(target_channel))
    speak_permission = True
    while radio_is_on:
        people = target_channel.members
        for player in people:
            overwrite = target_channel.overwrites_for(player)
            overwrite.speak = speak_permission
            await target_channel.set_permissions(player, overwrite=overwrite)
            await player.move_to(target_channel)
        speak_permission = not(speak_permission)
        await asyncio.sleep(radio_timelapse)

@bot.command(pass_context = True)
async def radio_off(ctx):
    """Stops alternating permissions on current GN "radio" channel."""
    global radio_is_on
    radio_is_on = False
    await ctx.message.channel.send("{0.author.mention}, c'est noté ! ".format(ctx.message)+\
    "J'arrête de travailler.")

@bot.command(pass_context = True)
async def change_time(ctx):
    """Modifies the duration of intervals between permission changes for a "radio" channel."""
    global radio_timelapse
    radio_timelapse = int(ctx.message.content[12:])
    await ctx.message.channel.send("{0.author.mention}, c'est noté ! ".format(ctx.message)+\
    "L'intervalle de communication a été changé à {0} secondes.".format(radio_timelapse))


################################################################################
# Dice roll and easter eggs #
################################################################################

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
    c = c.lower()
    select_dice = re.search("max|min", c)
    if select_dice:
        c = c[:select_dice.start()] + c[select_dice.end():]
    c2 = re.split("d|D", c)
    try:
        if len(c2) != 2:
            raise(ValueError)
        if c2[0] == '':
            nb_of_dices = 1
        else:
            nb_of_dices = int(c2[0])
        add_value = 0
        operation = re.match("(.*)([+-])(.*)", c2[1])
        if operation:
            value_of_dices = int(operation.group(1))
            factor = 1
            if operation.group(2) == "-":
                factor = -1
            add_value = factor*int(operation.group(3))
        else:
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
        if not(operation):
            await msg.channel.send("{0.author.mention} vous avez obtenu un ".format(msg) + "**" + str(sum(results)) + "**" + ".")
        else:
            total = sum(results) + add_value
            to_say = "{0.author.mention} vous avez obtenu un ".format(msg) +\
            "** {0} ** ({1} {2} {3}).".format(total, sum(results), operation.group(2), abs(add_value), )
            await msg.channel.send(to_say)
    else:
        concat = " , " if select_dice else " + "
        inter = "(" + str(results[0])
        for value in results[1:]:
            inter = inter + concat + str(value)
        if operation:
            inter += " avec un bonus aux dés de " + str(add_value)
        inter = inter + ")"
        if select_dice:
            if select_dice.group(0) == "min":
                await msg.channel.send("{0.author.mention} vous avez obtenu un ".format(msg) + "**" + str(min(results) + add_value) + "** " + inter + ".")
            else: #=="max"
                await msg.channel.send("{0.author.mention} vous avez obtenu un ".format(msg) + "**" + str(max(results) + add_value) + "** " + inter + ".")
        else:
            await msg.channel.send("{0.author.mention} vous avez obtenu un ".format(msg) + "**" + str(sum(results)+add_value*len(results)) + "** " + inter + ".")

@bot.command(pass_context = True,
description = "This command allows the user to roll one or several dice, using the syntax:\n"
+ "!roll [number of dice][d|D][max value of the dice] (+/- value to add)")
async def roll(ctx):
    """ Draws one or more random numbers from 1 to a specified value. """
    await roll_g(ctx.message, 4)

@bot.command(pass_context = True)
async def r(ctx):
    """ Alias for roll. """
    await roll_g(ctx.message, 1)


################################################################################
# Poll making #
################################################################################

async def poll_g(msg, length):
    """
    General function for poll commands.
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


################################################################################
# Emotional security checking #
################################################################################

check_dict = {}

@bot.command(pass_context=True)
async def check(ctx):
    """ Regularly checks on player emotional state and gives a feedback to the GM """
    global check_dict
    msg = ctx.message
    guild = msg.guild
    chan = msg.channel
    key = guild.id, chan.id
    check_dict[key] = msg.author #personne à contacter
    interval = re.search("[0-9]+m", msg.content)
    duration = re.search("[0-9]+h", msg.content)
    role_list = msg.role_mentions
    if len(role_list) > 1 :
        await msg.channel.send("{0.author.mention}, veuillez préciser un unique rôle à suivre (au plus).".format(msg))
    if not(interval):
        await msg.channel.send("{0.author.mention}, précisez la durée entre deux checks (en minutes, par ex \"10m\").".format(msg))
    else:
        interval = interval.group(0)
        interval = int(interval[:-1])#en minutes !
        answer_time_limit = min(interval*60*0.15, 2*60)#en secondes
        if duration:
            duration = duration.group(0)
            duration = int(duration[:-1])
            nb_check = (duration*60)//interval
        else:
            nb_check = 100 #this way, the bot will not keep going forever if someone forgets to stop the checks
            #it is limited to 100 checks
        message = await msg.channel.send("{0.author.mention}, c'est noté ! Le premier ok-check aura lieu dans {1}m".format(msg,interval))
        await asyncio.sleep(interval*60)
        for i in range(nb_check-1):
            if key not in check_dict:
                break
            message = await msg.channel.send(":ok_hand: :grey_question:")
            await message.add_reaction("👍")
            await message.add_reaction("🤏")
            await message.add_reaction("👎")
            if role_list == []:
                await asyncio.sleep(interval*60) #pour l'instant en secondes, plus tard en minutes
            else:
                role = role_list[0]
                liste_joueurs = role.members
                await asyncio.sleep(answer_time_limit)
                message_updated = await message.channel.fetch_message(message.id)
                liste_reaction = message_updated.reactions
                for joueur in liste_joueurs:
                    found = False #teste si le joueur a réagi au message du bot
                    for reac in liste_reaction:
                        if found:
                            break
                        async for u in reac.users():
                            if u.id == joueur.id:
                                found = True
                                break
                    if not found and str(joueur.status) != "offline":
                        await msg.author.send("{0} n'a toujours pas répondu au check après {1}m.".format(joueur, answer_time_limit/60))
                await asyncio.sleep(interval*60 - answer_time_limit)


@bot.command(pass_context=True)
async def stop(ctx):
    """Cancels emotional checks to come in this channel."""
    global check_dict
    msg = ctx.message
    guild = msg.guild
    chan = msg.channel
    key = guild.id, chan.id
    if key in check_dict:
        del check_dict[key]
        await msg.channel.send("{0.author.mention}, je mets fin aux contrôles ici.".format(msg))


################################################################################
# Divers #
################################################################################

@bot.listen()
async def on_message(msg):
    """ Detects and automatically erases Ninja emojis in messages (after 10s).
    Detects Michel's messages from Le Grand Méchant Renard and react with Michel. """
    react = re.search("(B|b)onjour (M|m)ada(a)+me", msg.content)
    if react:
        await msg.add_reaction("🐥")
    if bot.user.mentioned_in(msg):
        ninja_emote = discord.utils.find(lambda e: e.name == "Ninja", msg.guild.emojis)
        await msg.channel.send(ninja_emote)
    if ':Ninja:' in msg.content and msg.author != bot.user:
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
    """ Detect and automatically erase Ninja emojis in reactions (after 5s).
    Detects emotional status reactions to the checks. """
    global check_dict
    if 'Ninja' in str(reaction.emoji) or 'ninja' in str(reaction.emoji):
        await asyncio.sleep(5)
        await reaction.message.remove_reaction(reaction.emoji, user)
    elif (str(reaction.emoji) == "👎" or str(reaction.emoji) == "🤏")\
    and reaction.message.author == bot.user\
    and reaction.message.content == ":ok_hand: :grey_question:"\
    and user != bot.user: #sent by bot and contains ok_hand :question:
        msg = reaction.message
        guild = msg.guild
        chan = msg.channel
        key = guild.id, chan.id
        if key in check_dict:
            to_contact = check_dict[key]
            await to_contact.send("Attention, {0} a répondu avec {1}.".format(user, str(reaction.emoji)))


################################################################################
# Pad Change Tracking #
################################################################################

import requests
import imgkit
import difflib
import io
from contextlib import redirect_stdout

class NullIO(io.StringIO):
    def write(self, txt):
        pass

def silent(f):
    """Decorator to silence functions. To keep an empty console for Heroku."""
    def silent_f(*args, **kwargs):
        with redirect_stdout(NullIO()):
            return f(*args, **kwargs)
    return silent_f


from redis_dict import RedisDict
tracking_dict = RedisDict(namespace='bar') #global variable for managing emotional security checks
#for tests : https://pads.aliens-lyon.fr/p/XVnOAJ0LZMtTudweskBZ
@bot.command(pass_context=True)
async def track(ctx, arg):
    """Tracks changes in given pad, and upload image of diffs when detected.
    Usage : !track url_to_pad """
    global tracking_dict
    msg = ctx.message
    guild = msg.guild
    chan = msg.channel
    url = arg
    if url[-1] == "/":
        url = url[:-1]
    key = str(chan.id) + "+" + url

    if key in tracking_dict:
        await msg.channel.send("{0.author.mention}, ".format(msg, url) +\
        "je tracke déjà ici le pad à l'url {}".format(url))
    else:
        try:
            rq = requests.get(url + "/export/txt")
        except:
            await msg.channel.send("{0.author.mention}, ceci n'est pas un url valide.".format(msg, url))
        else:
            #Errors and forbidden demands (we want only track a PAD)
            if rq.status_code != 200:
                await msg.channel.send("{0.author.mention}, ".format(msg) +\
                "je ne peux pas accéder à {}. Code {} ({}).\n".format(url, rq.status_code, rq.reason))
            elif rq.text.startswith("<!DOCTYPE html>"):
                await msg.channel.send("{0.author.mention}, ".format(msg) +\
                "La requête /export/txt de cet url renvoie vers une page html au lieu d'une chaîne de caractères.\n" + \
                "Est ce bien l'url d'un pad ? Son /export/txt se comporte-t-il comme attendu ?")
            else:
                tracking_dict[key] = rq.text
                await msg.channel.send("{0.author.mention}, c'est noté !\n".format(msg, url) +\
                "A partir de maintenant, j'indiquerai ici les changements détectés sur le pad à l'url {}".format(url))

async def end_track_aux(key, chan):
    global tracking_dict
    if key in tracking_dict:
        del tracking_dict[key]
        await chan.send("{0.author.mention}, j'arrête de tracker le pad à l'url {1}".format(msg, url))
    else:
        await chan.send("{0.author.mention}, ".format(msg) +\
        "je ne trackais pas ici le pad à l'url {0}".format(url))

@bot.command(pass_context=True)
async def end_track(ctx, arg):
    """Puts an end to the tracking of changes in given pad.
    Usage : !end_track url_to_pad"""
    msg = ctx.message
    guild = msg.guild
    chan = msg.channel
    url = arg
    if url[-1] == "/":
        url = url[:-1]
    key = str(chan.id) + "+" + url
    await end_track_aux(key, chan)

################################################################################
# Bot loop function (and happy new year feature) #
################################################################################

async def loop_function():
    global tracking_dict
    await bot.wait_until_ready()
    while not bot.is_closed():

        #new year wishing
        t = datetime.datetime.now()
        if t.month == 12 and t.day == 31 and t.hour == 23 and t.minute == 0:
            guild = discord.utils.find(lambda c: normalize_name(c.name) == "club-murder", bot.guilds)
            channel = discord.utils.find(lambda c: normalize_name(c.name) == "blabla", guild.channels)
            role = guild.default_role
            role.mentionable = True
            msg = "🐥 @everyone Bonne année ! 🐥"
            await channel.send(msg)
            await asyncio.sleep(61) #avoid wishing the new year twice

        #pad tracking
        for key in tracking_dict:
            infos = key.split("+")
            chan = bot.get_channel(int(infos[0]))
            url = infos[1]
            rq = requests.get(url + "/export/txt")
            #Errors and forbidden demands (we want only track a PAD)
            if rq.status_code != 200:
                await chan.send("Je ne peux plus accéder au pad à l'url {}. Code {} ({}).\n".format(url, rq.status_code, rq.reason) +\
                "J'arrête de tracker cet url.")
                await end_track_aux(key, chan)
            else:
                new_pad = rq.text
                old_pad = tracking_dict[key]
                if old_pad != new_pad:
                    #computes the diff between pads and builds string of a html file containing a readable table of diffs
                    d = difflib.HtmlDiff(tabsize=4, wrapcolumn=80)
                    differences = d.make_file(old_pad.split("\n"), new_pad.split("\n"), context = True, numlines=2)

                    fileObj = io.StringIO(differences) #turns differences (string of a HTML file) into a valid file object
                    config = imgkit.config(wkhtmltoimage='./bin/wkhtmltoimage')
                    img = silent(imgkit.from_file)(fileObj, False, config=config) #turns html file into an image
                    await chan.send("Changement détecté sur le pad à l'url {} :".format(url))
                    await chan.send(file=discord.File(io.BytesIO(img), filename = "diff.png"))
                    tracking_dict[key] = new_pad

        await asyncio.sleep(10)

bot.loop.create_task(loop_function())

bot.run(os.getenv('BOT_TOKEN'))
