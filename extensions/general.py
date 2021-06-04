import discord
import json
from discord.ext import commands
from utils import send_embed
from main import botPrefix, botName,field

class general(commands.Cog):

  def __init__(self,client):
    self.client=client

  @commands.command(help="Clears the last message(s).")
  async def clear(self,ctx,limit=1):
    await ctx.channel.purge(limit=limit+1)

  @commands.command(help="Suggest a feature or report a bug.",aliases=['suggest','bug'])
  async def support(self,ctx):
    await send_embed(ctx.channel,"Private Bot Suggestion/Bug Report.",'Please click the following link: [Support](https://discord.gg/JYWVf7MFUt)\nYou could also directly contact abhinavgeethan#1933',footer='clear')
  
  @commands.command(help=f"Displays Bot Commands and syntax. Alternative to {botPrefix} help")
  async def commands(self,ctx):
    fields=[]
    f=open('Commands.json','r')
    comm_list=json.load(f)
    f.close()
    for i in comm_list:
      fields.append(field(comm_list[i]['name'],"Syntax: "+comm_list[i]['syntax']+"\n\u200b\n*"+comm_list[i]['description']+"*\n\u200b\n",inline=True))

    await send_embed(ctx.channel,f"{botName} Commands","Use them wisely.\n\u200b\n",fields=fields,footer='Arguments inside [] are optional and those inside <> are necessary.')

def setup(client):
  client.add_cog(general(client))