import discord
import requests
import json

async def send_embed(channel,title,description,colour=discord.Colour.blue(),image_url=None,thumbnail_url=None,fields=None,send=True):
  embed=discord.Embed(title=title,description=description,colour=colour)
  embed.set_footer(text='This is sent by a bot under development by abhinavgeethan#1933. Excuse any bugs.')
  if image_url != None:
    embed.set_image(url=image_url)
  if thumbnail_url != None:
    embed.set_thumbnail(url=thumbnail_url)
  if fields != None:
    if len(fields)>1:
      for field in fields:
        embed.add_field(name=field.name, value=field.value, inline=field.inline)
    else:
      field=fields[0]
      embed.add_field(name=field.name, value=field.value, inline=field.inline)
  if not send:
    return embed
  message=await channel.send(embed=embed)
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
  fields=["Click the below Link to watch the movie",f"[{data[0]['name']} Link]({link})"]
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
  title=str(index+1)+'. '+data[index]['name']
  description='**Movie Synopsis**\n*'+data[index]['synopsis']+'*'
  image_url=data[index]['image_url']
  link=data[index]['link']
  fields=["Click the below Link to watch the movie",f"[{data[index]['name']} Link]({link})"]
  return title,description,image_url,link,fields