import discord
from discord.ext import commands
from main import botPrefix, botName,field
from utils import send_embed
import json

class tester(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Pings channel")
  async def ping(self,ctx):
    await ctx.send(f'Pong! Server-Bot latency is {round(self.client.latency * 1000)}ms')

  
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
  client.add_cog(tester(client))