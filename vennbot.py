#!/usr/bin/env python3

import discord
from discord.ext import commands
import tokens
import vennsteam as vs
import json


    #  usr = ctx.message.author
    # channel is ctx.message.channel.name
    # server is ctx.message.server.name
    # print([x.name for x in client.get_all_members()])

bot_prefix = '?'
client = commands.Bot(command_prefix=bot_prefix)

# Register event handlers     ------------------------------
@client.event
async def on_ready():
    print('Bot Online!')
    print('Name: {}'.format(client.user.name))
    print('ID: {}'.format(client.user.id))


## COMMANDS -
@client.command(pass_context=True)
async def ping(ctx):
    '''
    HelloWorld for two players.

    This command is just to see if bensvenn is listening in.
    '''
    await client.say('pong!')


#  @client.command(pass_context=True)
#  async def register(ctx):
    #  '''register   <steamnick>
            #  teach bensvenn your steam name
            #  you have to be steam-friends with WhileTrueGame 
            #  for bensvenn to see your games.
    #  '''
    #  await client.say('pong!')


@client.command(pass_context=True)
async def bensvenn(ctx, channel_name='General'):
    '''
    show steam games owned by everyone

    usage:
    bensvenn channel_name
       
       If you leave channel_name blank:
       the default is General.
    
       Only works for voice channels.
       
       Don't use in the #general text channel.
       This is just to limit spam, you can 
       create a new channel or use #venndev.
       
    '''

    channels = client.get_all_channels()
    voice_gen = None
    steamids = []

    # don't spam the general text channel
    if ctx.message.channel.name == 'general':
        await client.say('Please use a different text channel for bensvenn.')
        return

    # find a handle to the General voice-channel
    for c in client.get_all_channels():
        if c.name == channel_name:
            voice_gen = c
            break

    # check channel and population
    if voice_gen is None:
        await client.say('no such voice channel %s' % channel_name)
        return

    if len(voice_gen.voice_members) == 0:
        await client.say("nobody's home in %s!" % channel_name)
        return

    for usr in voice_gen.voice_members:
        if usr.name not in dis_to_stm:
            await client.say('No steam handle for %s' % usr.name)
            continue

        steam_usr = dis_to_stm[usr.name]
        if steam_usr not in my_friends:
            await client.say('%s not steam-friends with WhileTrueGame' % steam_usr)
            continue

        steamids.append(my_friends[steam_usr])
        #  await client.say('%s is %s (%s)' % (usr.name, steam_usr, steam_id))

    if len(steamids) < len(voice_gen.voice_members):
        await client.say('(Only got games for %d people)' % len(steamids))

    if len(steamids) > 0:
        gameset = vs.venn_games(steam_ids=','.join(steamids), app_names=app_names)

        report_all = 'Games everyone in %s has:\n' % channel_name
        report_all += '\n'.join(gameset[len(steamids)])

        await client.say(report_all)

# try loading some global lookup tables here ---------------

# discord to steam name map
with open('user_database.json') as fid:
    data = fid.readlines()
data = [x.strip() for x in data]
data = ''.join(data)
dis_to_stm = json.loads(data)

# steam name to steam id map
my_friends = vs.get_all_friends_names()

# appid to game name map
app_names = vs.get_app_list()

# Loaded. Ready. Run!    ------------------------------------
client.run(tokens.vennbot_token)

