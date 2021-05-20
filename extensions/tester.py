import discord
from discord.ext import commands

class tester(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Pings channel")
  async def ping(self,ctx):
    await ctx.send(f'Pong! Server-Bot latency is {round(self.client.latency * 1000)}ms')

def setup(client):
  client.add_cog(tester(client))