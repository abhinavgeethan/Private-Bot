import discord
import requests
import json
import os
from typing import Optional

#__all__=["send_embed","get_channel_by_name","get_category_by_name","create_text_channel","create_voice_channel","get_quote","initial_catalog","get_catalog_size","data_catalog","check_conn_perms","update_lock_status","check_vis_perms","update_visibility_status","if_owner","get_bot_status"]

with open("./Config.json") as config_file:
  config_dict=json.load(config_file)

class field:
  def __init__(self,name,value,inline=False):
    self.name=name
    self.value=value
    self.inline=inline
  
  def to_text(self):
    return f"Name: {self.name}, Value: {self.value}, Inline: {self.inline}"

async def send_embed(channel,title,description,colour=discord.Colour.blue(),image_url=None,thumbnail_url=None,fields=None,send=True,author=None,timestamp=None,footer='default',isInteractionResponse:bool=False,view:Optional[discord.ui.View]=None):
  if timestamp==None:
    embed=discord.Embed(title=title,description=description,colour=colour)
  else:
    embed=discord.Embed(title=title,description=description,colour=colour,timestamp=timestamp)
  if footer=='default':
    embed.set_footer(text='This is sent by a bot under development by abhinavgeethan#1933. Excuse any bugs.')
  elif footer=='clear':
    pass
  else:
    embed.set_footer(text=footer)
  if image_url != None:
    embed.set_image(url=image_url)
  if thumbnail_url != None:
    embed.set_thumbnail(url=thumbnail_url)
  if author!= None:
    embed.set_author(name=author)
  if fields != None:
    if len(fields)>1:
      for field in fields:
        embed.add_field(name=field.name, value=field.value, inline=field.inline)
    else:
      field=fields[0]
      embed.add_field(name=field.name, value=field.value, inline=field.inline)
  if not send or isInteractionResponse:
    return embed
  message=await channel.send(embed=embed,view=view)
  return message


def get_channel_by_name(guild, channel_name):
  channel = None
  for c in guild.channels:
    if c.name == channel_name.lower():
      channel = c
      break
  return channel


def get_category_by_name(guild, category_name):
    category = None
    for c in guild.categories:
        if c.name == category_name:
            category = c
            break
    return category


async def create_text_channel(guild, channel_name, category_name):
    category = get_category_by_name(guild, category_name)
    channel = await guild.create_text_channel(channel_name, category=category)
    return channel, guild


async def create_voice_channel(guild,channel_name,category_name="VOICECHANNELS",user_limit=None):
    category = get_category_by_name(guild, category_name)
    channel = await guild.create_voice_channel(channel_name,category=category,user_limit=user_limit)
    #channel = get_channel_by_name(guild, channel_name)
    return channel


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)

def initial_catalog():
  with open('AV_Catalog.json','r') as f:
    data=json.load(f)
  f.close
  title='1. '+data[0]['name']
  description='**Movie Synopsis**\n*'+data[0]['synopsis']+'*'
  image_url=data[0]['image_url']
  link=data[0]['link']
  fields=["Click the Link below to watch the movie:",f"[{data[0]['name']} Link]({link})"]
  return title,description,image_url,link,fields

def get_catalog_size():
  with open('AV_Catalog.json','r') as f:
    data=json.load(f)
  f.close
  return len(data)

def data_catalog(index):
  with open('AV_Catalog.json','r') as f:
    data=json.load(f)
  f.close
  author='AV Club\'s SNL'
  thumbnail_url='https://instagram.ffjr1-2.fna.fbcdn.net/v/t51.2885-19/s150x150/30590396_163613307799664_9089326030237204480_n.jpg?tp=1&_nc_ht=instagram.ffjr1-2.fna.fbcdn.net&_nc_ohc=GppUZ8OOmQYAX8ArS8i&edm=ABfd0MgBAAAA&ccb=7-4&oh=b9f0d6377eae12d363e92b4ffd4a127c&oe=60B4CDD2&_nc_sid=7bff83'
  title=str(index+1)+'. '+data[index]['name']
  description='**Movie Synopsis**\n*'+data[index]['synopsis']+'*'
  image_url=data[index]['image_url']
  link=data[index]['link']
  fields=["Click the below Link to watch the movie",f"[{data[index]['name']} Link]({link})"]
  return title,description,image_url,link,fields,author,thumbnail_url

def check_conn_perms(channel,guild):
  permsEveryone = channel.overwrites_for(guild.default_role)
  #print(permsEveryone)
  #print(permsEveryone.connect)
  if permsEveryone.connect!=None:
    locked=True
    #print(locked)
  else:
    locked=False
    #print(locked)
  return locked


async def update_lock_status(channel,message,guild):
  embed=message.embeds[0]
  embed=embed.to_dict()
  #print (embed)
  if check_conn_perms(channel,guild):
    if embed!= None:
      #print(embed['fields'][3]['value'])
      embed['fields'][3]['value']='Locked'
  else:
    if embed!= None:
      #print(embed['fields'][3]['value'])
      embed['fields'][3]['value']='Unlocked'
  embed=discord.Embed.from_dict(embed)
  await message.edit(embed=embed)


def check_vis_perms(channel,guild):
  permsEveryone = channel.overwrites_for(guild.default_role)
  #print(permsEveryone)
  print(permsEveryone.view_channel)
  if permsEveryone.view_channel==True or permsEveryone.view_channel==None:
    visible=True
    #print(locked)
  else:
    visible=False
    #print(locked)
  return visible


async def update_visibility_status(channel,message,guild):
  embed=message.embeds[0]
  embed=embed.to_dict()
  #print (embed)
  if check_vis_perms(channel,guild):
    if embed!= None:
      #print(embed['fields'][3]['value'])
      embed['fields'][4]['value']='Visible'
  else:
    if embed!= None:
      #print(embed['fields'][3]['value'])
      embed['fields'][4]['value']='Invisible'
  embed=discord.Embed.from_dict(embed)
  await message.edit(embed=embed)


async def if_owner(guild,member):
  vChannel_name=member.name+'\'s channel'
  vChannel=get_channel_by_name(guild,vChannel_name)
  if vChannel==None:
    return False
  else:
    return True

def get_bot_status():
  url = "https://api.uptimerobot.com/v2/getMonitors"          
  try:
    payload = f"api_key={os.environ['uptime_api_key']}&format=json&noJsonCallback=1&monitors=788254326&response_times=1&response_times_limit=1&limit=1"
  except:
    return "Unavailable","Unavailable",None
  headers = {
      'content-type': "application/x-www-form-urlencoded",
      'cache-control': "no-cache"
      }            
  response = requests.request("POST", url, data=payload, headers=headers)
  try:
    response=json.loads(response.text)
    response_time=response['monitors'][0]['response_times'][0]['value']
    avg_response_time=round(float(response['monitors'][0]['average_response_time']))
    status=response['monitors'][0]['status']
    return response_time,avg_response_time,status
  except:
    return "Unavailable","Unavailable",None