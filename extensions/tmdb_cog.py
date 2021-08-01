import os
import discord
from aiohttp import ClientSession
from discord.ext import commands
from tmdbv3api import TMDb, Movie
from utils import send_embed
from main import field,botPrefix
import json

tmdb = TMDb()
tmdb.api_key = os.environ['tbdbv3_token']
tmdb.language = 'en'

def get_movie(movie):
    mov=Movie()
    search=mov.search(movie)
    movie=search[0]
    return movie

async def parse_anime_data(response):
  try:
    root=response['data']['Page']['media'][0]
  except IndexError:
    return -1
  title=root['title']['english'] if root['title']['english']!=None else ""
  image_url=root['coverImage']['extraLarge']
  fields=[]
  #Field 0
  fields.append(field("Status",root['status'].title()+"\n",True))
  content_type=root['type']
  #Field 1
  if content_type=="ANIME":
    fields.append(field("Episodes",str(root['episodes'])+"\n",True))
  elif content_type=="MANGA":
    fields.append(field("Volumes",str(root['volumes'])+"\n",True))
  
  #Field 2
  fields.append(field("Starting Date",str(root['startDate']['day'])+"/"+str(root['startDate']['month'])+"/"+str(root['startDate']['year'])+"\n",True))
  #Field 3
  if root['status']=="FINISHED":
    fields.append(field("Ending Date",str(root['endDate']['day'])+"/"+str(root['endDate']['month'])+"/"+str(root['endDate']['year'])+"\n",True))

  studio_names=""
  for edge in root['studios']['edges']:
    studio_names+=edge['node']['name']+"\n"
  
  #Field 4
  if studio_names!="":
    fields.append(field("Studio",studio_names+"\n",True))

  #Field 5
  if root['countryOfOrigin']=="JP":
    fields.append(field("Origin Country","Japan"+"\n",True))
  elif root['countryOfOrigin']=="CN":
    fields.append(field("Origin Country","China"+"\n",True))
  elif root['countryOfOrigin']=="KR":
    fields.append(field("Origin Country","Korea"+"\n",True))

  genres=""
  for genre in root['genres']:
    genres+=genre+", "
  
  #Field 6
  fields.append(field("Genres",genres[0:-2]+"\n",True))
  
  #Field 7
  fields.append(field("Content Origin",root['source'].title()+"\n",True))

  poster_colour=root['coverImage']['color'][1:]
  
  try:  
    if root['trailer']['site']=='youtube':
      t_url='https://www.youtube.com/watch?v='+root['trailer']['id']
    elif root['trailer']['site']=='dailymotion':
      t_url='https://www.dailymotion.com/video/'+root['trailer']['id']
    else:
      t_url=None
  except TypeError:
    t_url=None

  description=content_type.title()+" "+(root['title']['native'] if root['title']['native']!='null'else"")
  description+="\n\n"+"**Description:**\n*"+(root['description'].replace('<br>','').replace('<i>','').replace('</i>','')if root['description']!=None else "Unavailable")
  if description[-1]==" "or description[-1]=="\n":
    description=description[:-1]
  description+="*\n"+(f"Link to Trailer:[{root['trailer']['site'].title()}]({t_url})" if t_url != None else "")
  
  embed=await send_embed(None,title,description,colour=discord.Color(int(poster_colour,16)),image_url=image_url,fields=fields,send=False,footer=f"To report any bugs or to suggest a feature use {botPrefix} support")
  return embed

async def get_anime(term,type):
  query="""
    query ($search: String,$type: MediaType){
  Page(page: 1, perPage: 1) {
    pageInfo {
      perPage
    }
    media(search: $search, isAdult: false, type: $type, sort:[STATUS,SEARCH_MATCH, TRENDING_DESC, POPULARITY_DESC, TYPE]) {
      id
      type
      #trending
      countryOfOrigin
      title {
        english
        native
      }
      source
      volumes
      episodes
      format
      description(asHtml: false),
      trailer {
        id
        site
      }
      coverImage {
        extraLarge
        color
      }
      genres
      characters {
        edges{
          node{
            name {
              full
            }
          }
        }
      }
      studios(isMain:true) {
        edges{
          node{
            name
          }
        }
      }
      status
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
    }
  }
  }
  """
  variables={
    'search':f"{term}",
    'type':f"{type}"
  }
  url = 'https://graphql.anilist.co'
  async with ClientSession() as session:
    response=await session.post(url,json={'query':query,'variables':variables})
    response=await response.json()
  return await parse_anime_data(response)


class tmdb_cog(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Displays Details about Movie from TMDB")
  async def movie(self,ctx,*,movie):
    #print(rt.API_KEY)
    msg=await ctx.send(f'Awaiting response from TMDB for: {movie}')
    try:
      movie=get_movie(movie)
      await msg.delete()
      print(f"Movie discovered: {movie.title}, id = {movie.id}")
      rating=[field(f"TMDB Rating: {movie.vote_average}","**Poster:**")]  if movie.vote_average != None else None
      await send_embed(ctx.message.channel,movie.title,"**Synopsis**\n"+'*'+movie.overview+'*',image_url='http://image.tmdb.org/t/p/original/'+movie.poster_path,fields=rating)
    except:
      await msg.delete()
      await ctx.send(f"{movie} could not be found.")

  @commands.command(help="Retreives information about specified Anime.")
  async def anime(self,ctx,*,term):
    embed=await get_anime(term,"ANIME")
    if embed!=-1:
      await ctx.send(embed=embed)
    else:
      await send_embed(ctx.channel,'',f"Anime:`{term}` was not found.",discord.Colour.red(),footer='clear')

  #@anime.error
  #async def on_anime_error(self,ctx,error):
  #  await send_embed(ctx.channel,"Error",f"An unexpected error occurred. Use `{botPrefix} commands` to verify your syntax.",discord.Color.red(),footer=f'Alternatively, try again later; if the issue persists use {botPrefix} support to report the issue.')
  #  raise error
  
  @commands.command(help="Retreives information about specified Manga.")
  async def manga(self,ctx,*,term):
    embed=await get_anime(term,"MANGA")
    if embed!=-1:
      await ctx.send(embed=embed)
    else:
      await send_embed(ctx.channel,'',f"Manga:`{term}` was not found.",discord.Colour.red(),footer='clear')

  #@manga.error
  #async def on_manga_error(self,ctx,error):
  #  await send_embed(ctx.channel,"Error",f"An unexpected error occurred. Use `{botPrefix} commands` to verify your syntax.",discord.Color.red(),footer=f'Alternatively, try again later; if the issue persists use {botPrefix} support to report the issue.')
  #  raise error
    
def setup(client):
  client.add_cog(tmdb_cog(client))