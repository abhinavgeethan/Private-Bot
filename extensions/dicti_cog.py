import discord
import json
import requests
from discord.ext import commands
from udpy import AsyncUrbanClient
from utils import send_embed
from main import field

async def get_udef(channel,term):
  uClient=AsyncUrbanClient()
  if term!=None:
    defs=await uClient.get_definition(term)
  else:
    defs=await uClient.get_random_definition()
  await uClient.session.close()
  print("Urban Dictionary: "+defs[0].word)
  fields=[field("Example:",defs[0].example.replace('[','').replace(']',''),True)]
  embed=await send_embed(channel,"Search: "+defs[0].word,"**Definition:**\n*"+defs[0].definition.replace('[','').replace(']','')+"*",author="Urban Dictionary",fields=fields,send=False,thumbnail_url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/UD_logo-01.svg/220px-UD_logo-01.svg.png')
  return embed

async def get_def(channel,term):
  url='https://api.dictionaryapi.dev/api/v2/entries/en_US/'
  response=requests.get(url+term)
  response=json.loads(response.text)
  #print(response)
  embeds=[]
  for i in range(len(response)):
    pronounciations=''
    for pron in response[i]['phonetics']:
      pronounciations+="`"+pron['text']+"` "
    fields=[]
    for item in response[i]['meanings']:
      for j in range(len(item['definitions'])):
        try:
          fields.append(field("Part of Speech: "+item['partOfSpeech'],item['definitions'][j]['definition']+"\n\nExample: *"+item['definitions'][j]['example']+"*"))
        except KeyError:
          fields.append(field("Part of Speech: "+item['partOfSpeech'],item['definitions'][j]['definition']))
    
    embeds.append(await send_embed(
      channel,
      "Defining: "+response[i]['word'].title(),
      pronounciations,
      fields=fields,
      send=False
    ))
  return embeds

class dicti(commands.Cog):
  def __init__(self,client):
    self.client=client
  
  @commands.command(help="Retreives definition from Urban Dictionary.")
  async def urban(self,ctx,*,term=None):
    embed=await get_udef(ctx.channel,term)
    await ctx.send(embed=embed)

  @commands.command(help="Retreives Definition.")
  async def define(self,ctx,*,term):
    embeds=await get_def(ctx.channel,term)
    for embed in embeds:
      await ctx.send(embed=embed)

def setup(client):
  client.add_cog(dicti(client))