import os
import discord
from discord.ext import commands
from utils import send_embed
from main import field,botName
import requests
import aiohttp
from aiohttp import ClientSession

class tester(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Pings channel")
  async def ping(self,ctx):
    await ctx.send(f'Pong! Server-Bot latency is {round(self.client.latency * 1000)}ms')

  @commands.command(help='Checks server status.')
  async def status(self,ctx):
    msg=await ctx.send('Requesting for Status')
    async with ClientSession() as session:
      response = await session.request(
        method="POST",
        url="https://api.uptimerobot.com/v2/getMonitors",
        data=f"api_key={os.environ['uptime_api_key']}&format=json&logs=0&response_times=1",
        headers={
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
        }
      )
      data=await response.json()
    # response = requests.request(
    #   "POST",
    #   "https://api.uptimerobot.com/v2/getMonitors",
    #   data=f"api_key={os.environ['uptime_api_key']}&format=json&logs=0&response_times=1",
    #   headers={
    #   'content-type': "application/x-www-form-urlencoded",
    #   'cache-control': "no-cache"
    #   }
    # )
    try:
      # data=await response.json()
      status=data['monitors'][0]['status']
      response_time=data['monitors'][0]['response_times'][0]['value']
      avg=round(float(data['monitors'][0]['average_response_time']))
      if status==2:
        await send_embed(ctx.channel,f"{botName} Server Status",'The Server is UP.',discord.Colour.green(),footer='clear',fields=[field("Discord API",f"{round(self.client.latency * 1000)} ms",True),field("Round-Trip Response",f"{response_time}"+(" ms" if response_time!='Unavailable' else '')+f"\nAverage: {avg}"+(" ms" if avg!='Unavailable' else ''),True)])
      else:
        await send_embed(ctx.channel,f"{botName} Server Status",'The monitoring server is malfunctioning. {botName} is up and running.',discord.Colour.orange(),footer='clear')
    except:
      await send_embed(ctx.channel,f"{botName} Server Status",'The monitoring server is malfunctioning. {botName} is up and running.',discord.Colour.orange(),footer='clear')
    await msg.delete()

def setup(client):
  client.add_cog(tester(client))