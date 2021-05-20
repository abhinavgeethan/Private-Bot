import os
import discord
import requests
from discord.ext import commands
import rtsimple as rt


rt.API_KEY = os.environ['rt_token']

class rt_cog(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Displays Details about Movie from RottenTomatoes")
  async def movie(self,ctx,movie):
    print(rt.API_KEY)
    msg=await ctx.send(f'Awaiting response from RottenTomatoes for: {movie}')
    mov=rt.Movies()
    response=mov.search(q=movie)
    if len(mov.movies)>1:
      await msg.delete()
      await ctx.send("These are the movies I've found:")
      for m in mov.movies:
        await ctx.send (f"{m['title']}")
    else:
      await msg.delete()
      await ctx.send(f"I found {mov.movies[0]['title']}")

def setup(client):
  client.add_cog(rt_cog(client))