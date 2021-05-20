import os
import discord
import requests
from discord.ext import commands
from tmdbv3api import TMDb
from tmdbv3api import Movie
from utils import send_embed

tmdb = TMDb()
tmdb.api_key = os.environ['tbdbv3_token']
tmdb.language = 'en'

def get_movie(movie):
    mov=Movie()
    search=mov.search(movie)
    movie=search[0]
    return movie

class tmdb_cog(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Displays Details about Movie from TMDB")
  async def movie(self,ctx,movie):
    #print(rt.API_KEY)
    msg=await ctx.send(f'Awaiting response from TMDB for: {movie}')
    movie=get_movie(movie)
    await msg.delete()
    print(movie.id)
    await send_embed(ctx.message.channel,movie.title,'*'+movie.overview+'*',image_url='http://image.tmdb.org/t/p/original/'+movie.poster_path)
    

def setup(client):
  client.add_cog(tmdb_cog(client))