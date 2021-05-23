import discord
import json
import requests
import time
from discord.ext import commands
from jokeapi import Jokes

def get_cnjoke():
  response=requests.get("https://api.chucknorris.io/jokes/random")
  joke=json.loads(response.text)
  return joke['value']

def get_regjoke(category):
  j=Jokes()
  joke = j.get_joke(category=["Any" if category==None else category])  # Retrieve a random joke
  return joke
  

class fun(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  @commands.command(help="Returns a Chuck Norris Joke")
  async def cnjoke(self,ctx):
    print("CN Joke Triggered.")
    joke=get_cnjoke()
    await ctx.send(joke)

  @commands.command(help="Returns a Joke. Type dark/programming/fun/spooky if you'd like one of a specific kind.")
  async def joke(self,ctx,*,category=None):
    print("Joke triggered.")
    print("Category= "+category)
    joke=get_regjoke(category)
    if joke["type"] == "single": # Print the joke
      await ctx.send("`"+joke["joke"]+"`")
    else:
      await ctx.send("`"+joke["setup"]+"`")
      print("Waiting for Delivery")
      calctime=(len(joke["setup"])*1/10)
      waittime=2.5 if calctime>2.5 else calctime
      print(waittime)
      time.sleep(waittime)
      await ctx.send("`"+joke["delivery"]+"`")
    

def setup(client):
  client.add_cog(fun(client))
