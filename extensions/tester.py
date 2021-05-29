import os
import discord
from discord.ext import commands
from main import botPrefix, botName,field
from utils import send_embed
import json
import requests

class tester(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Pings channel")
  async def ping(self,ctx):
    await ctx.send(f'Pong! Server-Bot latency is {round(self.client.latency * 1000)}ms')

  
  @commands.command(help='Checks server status.')
  async def status(self,ctx):
    msg=await ctx.send('Requesting for Status')
    response = requests.request(
      "POST",
      "https://api.uptimerobot.com/v2/getMonitors",
      data=f"api_key={os.environ['uptime_api_key']}&format=json&logs=0",
      headers={
      'content-type': "application/x-www-form-urlencoded",
      'cache-control': "no-cache"
      }
    )
    data=response.json()
    #print(response.text)
    status=data['monitors'][0]['status']
    if status==2:
      await send_embed(ctx.channel,"Private Bot Server Status",'The Server is UP.',discord.Colour.green())
    else:
      await send_embed(ctx.channel,"Private Bot Server Status",'The monitoring server is malfunctioning. Private Bot is up and running.',discord.Colour.orange())
    await msg.delete()

  
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
  client.add_cog(tester(client))