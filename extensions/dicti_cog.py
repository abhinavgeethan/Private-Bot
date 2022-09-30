import discord
import json
from aiohttp import ClientSession
from discord import app_commands
from discord.ext import commands
from udpy import AsyncUrbanClient
from utils import send_embed,field
from typing import Optional

async def get_udef(channel,term):
  uClient=AsyncUrbanClient()
  if term!=None:
    defs=await uClient.get_definition(term)
  else:
    defs=await uClient.get_random_definition()
  await uClient.session.close()
  if len(defs)!=0:
    fields=[field("Example:",defs[0].example.replace('[','').replace(']',''),True)]
    embed=await send_embed(channel,"Search: "+defs[0].word,"**Definition:**\n*"+defs[0].definition.replace('[','').replace(']','')+"*",author="Urban Dictionary",fields=fields,send=False,thumbnail_url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/UD_logo-01.svg/220px-UD_logo-01.svg.png')
    return embed
  else:
    return -1

async def get_def(channel,term):
  url='https://api.dictionaryapi.dev/api/v2/entries/en_US/'
  async with ClientSession() as session:
    response=await session.get(url+term)
    response=await response.json()
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
              fields.append(field("Part of Speech: "+item['partOfSpeech'].title() if item['partOfSpeech']!=None else "Noun",item['definitions'][j]['definition']+"\n\nExample: *"+item['definitions'][j]['example']+"*"))
            except KeyError:
              fields.append(field("Part of Speech: "+item['partOfSpeech'].title() if item['partOfSpeech']!=None else "Noun",item['definitions'][j]['definition']))
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

  @app_commands.command(name='urban',description="Retreives definition from Urban Dictionary.")
  @app_commands.describe(term='Term to search for, leave empty for random word.')
  async def _urban(self,interaction: discord.Interaction,term:Optional[str]):
    embed=await get_udef(interaction.channel,term)
    if embed!=-1:
      await interaction.response.send_message(embed=embed)
    else:
      response_embed=await send_embed(interaction.channel,'',f"Term `{term}` was not found.",discord.Colour.red(),footer='clear')
      await interaction.response.send_message(embed=response_embed)

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

  @app_commands.command(name='define',description="Retreives definition.")
  @app_commands.describe(term='Term to search for')
  async def _define(self,interaction: discord.Interaction,term:str):
    embeds=await get_def(interaction.channel,term)
    if embeds!=-1:
      await interaction.response.send_message(embeds=embeds)
    else:
      response_embed=await send_embed(interaction.channel,'',f"Term `{term}` was not found.",discord.Colour.red(),footer='clear')
      await interaction.response.send_message(embed=response_embed)

async def setup(client):
  await client.add_cog(dicti(client))