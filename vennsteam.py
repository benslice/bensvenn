import json
import requests
import tokens

api_url_base = 'http://api.steampowered.com/'


def dump_friends():
   """ dump a list of all my friends, their IDs and their alias to a flat file"""

   friend_list = get_my_friends()

   fid = open('steam_friend_dump.tsv', 'w')
   fields = ('steamid', 'steamnick')
   print('%s\t%s' % fields, file=fid)
   for id, nick in friend_list.items():
      print('%s\t%s' % (id, nick), file=fid)

   fid.close()



def get_my_friends():
   """ 
   Return a dict of all my friends steamID -> handles
   BOTH are STRINGS
   """

   steam_id = tokens.benny

   friends_list_url = api_url_base + 'ISteamUser/GetFriendList/v0001/?'
   friends_list_url += 'key=' + tokens.steam_api_token + '&'
   friends_list_url += 'steamid=' + steam_id + '&'
   friends_list_url += 'format=json'

   response = requests.get(friends_list_url)
   if not response.ok:
      print('error with request:')
      print(response.content.decode('utf-8'))
      return None

   rdict = json.loads(response.content.decode('utf-8'))

   # unpack the list of steam ids
   friends = [x['steamid'] for x in rdict['friendslist']['friends']]

   # add myself to the list
   friends.append(tokens.benny)

   # lookup the name for each
   steamid_to_name = get_names(steam_id = ','.join(friends))

   return steamid_to_name 


def get_names(steam_id=None):
   """ return a dict of steam_ids -> names 
      steam_id can be a comma delimited string
      the API takes such a string
   """
   # lookup steam handles from steam ids
   # pass in a string
   # can also be a comma delimited string-list
   # output is a dict of handle -> steam id

   if steam_id is None:
      steam_id = tokens.matty
      steam_id += ',' + tokens.benny

   profile_list_url = api_url_base + 'ISteamUser/GetPlayerSummaries/v0002/?' 
   profile_list_url += 'key=' + tokens.steam_api_token + '&'
   profile_list_url += 'steamids=' + steam_id + '&'
   profile_list_url += 'format=json'
   response = requests.get(profile_list_url)

   if not response.ok:
      print('error with request:')
      print(response.content.decode('utf-8'))
      return None

   rdict = json.loads(response.content.decode('utf-8'))

   steamid_to_name = {}
   for p in rdict['response']['players']:
      steamid_to_name[p['steamid']] = p['personaname']

   return steamid_to_name


def get_games(steam_id=None):
   # get list of appids owned by single steamid
   if steam_id is None:
      steam_id = tokens.matty

   game_list_url = api_url_base + 'IPlayerService/GetOwnedGames/v0001/?' 
   game_list_url += 'key=' + tokens.steam_api_token + '&'
   game_list_url += 'steamid=' + steam_id + '&'
   game_list_url += 'format=json'

   response = requests.get(game_list_url)
   if not response.ok:
      print('error with request:')
      print(response.content.decode('utf-8'))
      return None

   rdict = json.loads(response.content.decode('utf-8'))
   games = [x['appid'] for x in rdict['response']['games']]
   return games


def get_app_list():
   # get the whole list so we can map appids to names
   #  http://api.steampowered.com/ISteamApps/GetAppList/v0002/
   # returns { appid (int)  -> name dict }
   app_list_url = api_url_base + 'ISteamApps/GetAppList/v0002/?'
   app_list_url += 'format=json'

   response = requests.get(app_list_url)
   if not response.ok:
      print('error with request:')
      print(response.content.decode('utf-8'))
      return None

   rdict = json.loads(response.content.decode('utf-8'))
   app_names = {}

   for app in rdict['applist']['apps']:
       app_names[app['appid']] = app['name']


   return app_names


def venn_games(steam_ids=None, app_names=None, exclude=None):
   # take in a comma sep list of ids, 
   # returns a game set dict
   # keys are ints (how many players own)
   # values are each a list of games

   if steam_ids is None:
      steam_ids = '76561197961737526' # benny
      steam_ids += ',76561197970805046' # matty

   if exclude is not None:
      for e in eclude.split(','):
         if e in steam_ids:
            steam_ids.remove(e)

   if app_names is None:
      app_names = get_app_list()

   appid_list = []
   for id in steam_ids.split(','):
      appid_list.extend(get_games(steam_id=id))

   appid_set = list(set(appid_list))
   appid_count = [appid_list.count(x) for x in appid_set]

   game_set_dict = {}
   for app,score in zip(appid_set, appid_count):
      if score not in game_set_dict:
         game_set_dict[score] = [app_names[app]]
      else:
         game_set_dict[score].append(app_names[app])

   return game_set_dict

