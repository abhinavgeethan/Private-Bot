import os
import discord
from discord.ext import commands
from utils import send_embed
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
    status=data['monitors'][0]['status']
    if status==2:
      await send_embed(ctx.channel,"Private Bot Server Status",'The Server is UP.',discord.Colour.green())
    else:
      await send_embed(ctx.channel,"Private Bot Server Status",'The monitoring server is malfunctioning. Private Bot is up and running.',discord.Colour.orange())
    await msg.delete()
  

def setup(client):
  client.add_cog(tester(client))