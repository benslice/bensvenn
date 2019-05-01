#!/usr/bin/env python3 

import discord
import random
import asyncio
import vennsteam as vs
import tokens


class MyClient(discord.Client):
   async def on_ready(self):
      print('Logged in as ' + self.user.name)
      print('ID is ' + str(self.user.id))
      print('------')


   async def on_message(self, message):
      # we do not want the bot to reply to itself
      if message.author.id == self.user.id:
         return

      if message.content.startswith('$guess'):
         await message.channel.send('Guess a number between 1 and 10.')

         def is_correct(m):
            return m.author == message.author and m.content.isdigit()

         answer = random.randint(1, 10)

         try:
            guess = await self.wait_for('message', check=is_correct, timeout=5.0)
         except asyncio.TimeoutError:
            return await message.channel.send('Sorry, you took too long it was {}.'.format(answer))

         if int(guess.content) == answer:
            await message.channel.send('You are right!')
         else:
            await message.channel.send('Oops. It is actually {}.'.format(answer))

      elif message.content.startswith('?bensvenn'):
         # parse command to get target channel, defaut to General
         target_channel = message.content[len('?bensvenn'):].strip()
         target_handle = None
         steamids = []

         if target_channel == '':
            target_channel = 'General'

          # find a handle to target_channel
         for c in client.get_all_channels():
            if c.name == target_channel:
               target_handle = c
               break

         # check channel and population
         if target_handle is None:
            await message.channel.send('no such voice channel %s' % target_channel)
            return

         if len(target_handle.members) == 0:
            await message.channel.send("nobody's home in %s!" % target_channel)
            return

         # convert discord ids to steam ids
         for usr in target_handle.members:
            usr_id = str(usr.id)
            if usr_id in dis_to_stm:
               steamids.append(dis_to_stm[usr_id])
            else:
               await message.channel.send('No steamID registered for %s' % usr.name)
               continue

         # currently no on is in the mapping that's not my friend, but that could change
         for sid in steamids:
            if sid not in my_friends:
               steam_nick = vs.get_names(steam_id=str(sid))
               steamids.remove(sid)
               await message.channel.send('%s not steam-friends with WhileTrueGame' % steam_nick[sid])
               continue


         if len(steamids) < len(target_handle.members):
            await message.channel.send('(Only got games for %d people)' % len(steamids))

         if len(steamids) > 0:
            gameset = vs.venn_games(steam_ids=','.join(steamids), app_names=app_names)

            report_all = 'Games everyone in %s has:\n' %target_channel 
            report_all += '\n'.join(gameset[len(steamids)])

            if len(report_all) > 2000:
               await message.channel.send('Character limit exceeded, this list will be abridged')
               report_all = report_all[:2000]

            await message.channel.send(report_all)


      elif message.content.startswith('?debug'):
         print('enter debug')
         import ipdb; ipdb.set_trace()

         print('exit debug')


   def dump_guild(self):
      G = self.guilds[0]
      fid = open('guild_dump.tsv', 'w')
      fields = ('Member id', 'name', 'discriminator', 'nick')
      print('%s\t%s\t%s\t%s' % fields, file=fid)

      for m in G.members:
         fields = (m.id, m.name, m.discriminator, m.nick)
         print('%s\t%s\t%s\t%s' % fields, file=fid)

      fid.close()




# </Class definition>

# try loading some global lookup tables here ---------------

# discord to steam name map, make them all strings
dis_to_stm = {}
with open('user_database.tsv', 'r') as fid:
   for line in fid.readlines():
      discord_id, steam_id = line.strip().split('\t')
      dis_to_stm[discord_id] = steam_id


# steam name to steam id map
my_friends = vs.get_my_friends()

# appid to game name map
app_names = vs.get_app_list()

# Loaded. Ready. Run!   ------------------------------------


client = MyClient()
client.run(tokens.vennbot_token)
