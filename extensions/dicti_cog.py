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
  if len(defs)!=0:
    print("Urban Dictionary: "+defs[0].word)
    fields=[field("Example:",defs[0].example.replace('[','').replace(']',''),True)]
    embed=await send_embed(channel,"Search: "+defs[0].word,"**Definition:**\n*"+defs[0].definition.replace('[','').replace(']','')+"*",author="Urban Dictionary",fields=fields,send=False,thumbnail_url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/UD_logo-01.svg/220px-UD_logo-01.svg.png')
    return embed
  else:
    return -1

async def get_def(channel,term):
  url='https://api.dictionaryapi.dev/api/v2/entries/en_US/'
  response=requests.get(url+term)
  response=json.loads(response.text)
  try:
    if response['title']=="No Definitions Found":
      return -1
  except TypeError:
    embeds=[]
    for i in range(len(response)):
      pronounciations=''
      for pron in response[i]['phonetics']:
        if pron['text']!="":
          pronounciations+="`"+pron['text']+"` "
      fields=[]
      try:
        for item in response[i]['meanings']:
          for j in range(len(item['definitions'])):
            try:
              fields.append(field("Part of Speech: "+item['partOfSpeech'] if item['partOfSpeech']!=None else "Noun",item['definitions'][j]['definition']+"\n\nExample: *"+item['definitions'][j]['example']+"*"))
            except KeyError:
              fields.append(field("Part of Speech: "+item['partOfSpeech'] if item['partOfSpeech']!=None else "Noun",item['definitions'][j]['definition']))
        embeds.append(await send_embed(
          channel,
          "Defining: "+response[i]['word'].title(),
          pronounciations,
          fields=fields,
          send=False
        ))
      except:
        continue
    return embeds
  

class dicti(commands.Cog):
  def __init__(self,client):
    self.client=client
  
  @commands.command(help="Retreives definition from Urban Dictionary.")
  async def urban(self,ctx,*,term=None):
    msg=await ctx.send(f"Grabbing definition for `{term}` from Urban Dictionary.")
    embed=await get_udef(ctx.channel,term)
    if embed!=-1:
      await ctx.send(embed=embed)
    else:
      await send_embed(ctx.channel,'',f"Term `{term}` was not found.",discord.Colour.red(),footer='clear')
    await msg.delete()

  @commands.command(help="Retreives Definition.")
  async def define(self,ctx,*,term):
    msg=await ctx.send(f"Grabbing definition for `{term}`")
    embeds=await get_def(ctx.channel,term)
    if embeds!=-1:
      for embed in embeds:
        await ctx.send(embed=embed)
    else:
      await send_embed(ctx.channel,'',f"Term `{term}` was not found.",discord.Colour.red(),footer='clear')
    await msg.delete()

def setup(client):
  client.add_cog(dicti(client))