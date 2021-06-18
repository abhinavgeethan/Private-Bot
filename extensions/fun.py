import os
import discord
import json
import requests
import asyncio
from discord.ext import commands
from jokeapi import Jokes
from main import botPrefix
import random
from utils import send_embed
import praw
import prawcore

#-------------------------------------------------------------External API Calls--------------------------------------------------------#
def get_cnjoke():
  response=requests.get("https://api.chucknorris.io/jokes/random")
  joke=json.loads(response.text)
  return joke['value']

def get_regjoke(category):
  j=Jokes()
  joke = j.get_joke(category=["Any" if category==None else category])  # Retrieve a random joke
  return joke
  
def get_yomamajoke():
  response=requests.get("https://api.yomomma.info/")
  joke=json.loads(response.text)
  return joke['joke']

#async def async_get_meme(subreddit_name):
#  superset=[]
#  reddit=asyncpraw.Reddit(client_id=os.environ['reddit_client_id'],client_secret=os.environ['reddit_client_secret'],user_agent='Private Bot')
#  reddit.read_only=True
#  subreddit=await reddit.subreddit(subreddit_name,fetch=True)
#  #top=subreddit.top(limit=25)
#  async for submission in subreddit.hot(limit=25):
#    superset.append(submission)
#  choice=random.choice(superset)
#  await reddit.close()
#  #i=0
#  #while choice.over18 and i<25:
#  #  choice=random.choice(superset)
#  #  i=i+1
#  #if not choice.over18:
#  return choice.title,choice.url
#  #else:
#  #  return None,None

def get_meme(subreddit_name):
  superset=[]
  reddit=praw.Reddit(client_id=os.environ['reddit_client_id'],client_secret=os.environ['reddit_client_secret'],username=os.environ['reddit_username'],password=os.environ['reddit_password'],user_agent='Private Bot')
  subreddit=reddit.subreddit(subreddit_name)
  try:
    if not subreddit.over18:
      top=subreddit.hot(limit=10)
      for submission in top:
        superset.append(submission)
      choice=random.choice(superset)
      return choice.title,choice.url
    else:
      return None,None
  except prawcore.exceptions.NotFound:
    return -1,-1
  except prawcore.exceptions.Forbidden:
    return 0,0
  except:
    return 1,1
  
#--------------------------------------------------------Cog Class Definition-----------------------------------------------------------#
class fun(commands.Cog):
  
  def __init__(self,client):
    self.client=client

  #cnjoke command
  @commands.command(help="Returns a Chuck Norris Joke")
  async def cnjoke(self,ctx):
    print("CN Joke Triggered.")
    msg=await ctx.send("Ringing `Chuck Norris` now. He's 81, it won't take him long though")
    joke=get_cnjoke()
    await ctx.send(joke)
    await msg.delete()

  #joke command
  @commands.command(help="Returns a Joke. Type dark/programming/pun/spooky if you'd like one of a specific kind.",enabled=True)
  async def joke(self,ctx,*,category=None):
    print("Joke triggered.")
    choices=['any','misc','programming','dark','pun','spooky','christmas']
    if category==None:
      pass
    elif category.lower() in choices:
      pass
    else:
      await send_embed(
        ctx.channel,
        '',
        f"`{category}` is not a valid category.\nTry `Any`, `Misc`, `Programming`, `Dark`, `Pun`, `Spooky` or `Christmas`.",
        discord.Colour.red(),
        footer='clear'
        )
      return
    #print("Category= "+category)
    msg= await ctx.send("Retreiving jokes from the Interwebs.")
    joke=get_regjoke(category)
    if joke["type"] == "single": # Print the joke
      await ctx.send("`"+joke["joke"]+"`")
      await msg.delete()
    else:
      await ctx.send("`"+joke["setup"]+"`")
      await msg.delete()
      print("Waiting for Delivery")
      calctime=(len(joke["setup"])*1/10)
      waittime=2.5 if calctime>2.5 else calctime
      print(waittime)
      await asyncio.sleep(waittime)
      await ctx.send("`"+joke["delivery"]+"`")


  @commands.command(help="Returns a Yo Mama Joke")
  async def yomama(self,ctx):
    print("YoMama Joke Triggered.")
    msg=await ctx.send("Ringing `Yo Mama` now.")
    joke=get_yomamajoke()
    await ctx.send(joke)
    await msg.delete()

  #rps command
  @commands.command(help="Plays Rock, Paper Scissors")
  async def rps(self,ctx,choice):
    print("RPS Triggered.")
    p_choices=['r','rock','p','paper','s','scissors','scissor','scisors','sissior','scisorss','sissors','scisser','sissors','sissor']
    if choice.lower() in p_choices:
      vals={'p':1,'s':2,'r':3}
      uVal=vals[choice[0].lower()]
      b_choices=['**Rock**', '**Paper**', '**Scissors**']
      bChoice=random.choice(b_choices)
      bVal=vals[bChoice[2].lower()]
      if uVal==bVal:
        res="It's a **tie**!"
      elif uVal>bVal:
        if not (uVal==3 and bVal==1):
          posResponse=["**You beat me!**","**Oh no! You've beaten me**.","**You've Won**!"]
          res=random.choice(posResponse)
        else:
          res="Haha! **I win**."
      else:
          if not (uVal==1 and bVal==3):
            res="You lose! **I win**!"
          else:
            posResponse=["**You beat me!**","**Oh no! You've beaten me**.","**You've Won**!"]
            res=random.choice(posResponse)  

      await ctx.send(f"I chose {bChoice}.")
      await ctx.send(res)

    elif choice==None:
      await ctx.send(f"The format is: `{botPrefix} rps <choice>`.\nYou must enter either **Rock**, **Paper** *or* **Scissors** in place of `<choice>`.")
    else:
      await ctx.send("That seems like a wrong choice. Try again with either **Rock**, **Paper** *or* **Scissors**.")

  #rickroll command
  @commands.command(help='Rickrolls the mentioned user anonymously.')
  async def rickroll(self,ctx,member: discord.Member):
    if bool(random.getrandbits(1)):
      try:
        #names=['Felix','Sean','Jack']
        prompt=['Link','Cats','Dogs','Cyberpunk','Discord Bots']
        #if bool(random.getrandbits(1)):
        embed=await send_embed(ctx.channel,title=" ",description=f"You should check this out: [{random.choice(prompt)}](https://youtu.be/dQw4w9WgXcQ?t=43)",send=False,footer='clear')
        await member.send(embed=embed)
        #else:
        #  await member.send('|| https://tenor.com/view/rick-roll-rick-astley-never-gonna-give-you-up-gif-13662086 ||')
        await ctx.send(f"`{member.name}` has been rickrolled lol.")
      except:
        await ctx.send(f"`{member.name}` has their DM's closed. You can try sending them this: `https://youtu.be/dQw4w9WgXcQ?t=43`.\n Or... *Get a Life*.")
    else:
      await ctx.send('Instead, *Get a Life* maybe?\nOr just *try again* ;)')
  

  @commands.command(help="Calculates your compatibility with the mentioned person.")
  async def match(self,ctx,member: discord.Member):
    if bool(random.getrandbits(1)):
      vals=['93','82','87','95','99','89','90','80','97']
      posResponse=random.choice(['Get a room you guys.','Want me to help set up a Date?'])
      await ctx.send(f"{ctx.author.mention}, you are **{random.choice(vals)}%** compatible with {member.mention}. ❤!\n*{posResponse}* Just click on the Template voice channel ;).")
    else:
      vals=['13','22','47','35','29','19','30','50','37']
      negResponse=random.choice(['Ouch.','Sheesh!'])
      await ctx.send(f"{ctx.author.mention}, you are **{random.choice(vals)}%** compatible with {member.mention}. 💙.\n*{negResponse}*")

  
  @commands.command(help="Gets a meme from the specified subreddit.",aliases=['meme'])
  async def reddit(self,ctx,*,subreddit='memes'):
    msg=await ctx.send(f"Awaiting response from `r/{subreddit}`. Reddit can get really slow.")
    title,image_url=get_meme(subreddit)
    await msg.delete()
    if title==None and image_url==None:
      await ctx.send(f"`r/{subreddit}` is flagged NSFW and I cannot display memes from it.")
    elif title==-1 and image_url==-1:
      await ctx.send(f"`r/{subreddit}` was not found.")
    elif title==0 and image_url==0:
      await ctx.send(f"`r/{subreddit}` is member-only.")
    elif title==1 and image_url==1:
      await ctx.send("An unknown error occurred.")
    else:
      await send_embed(ctx.channel,"","**"+title+"**",image_url=image_url,author=f"r/{subreddit}",footer=f'Slow/Missing media content is usually caused from Discord\'s end. If it is a persistent issue do report it using {botPrefix} support.')


  @commands.command(help="Insults the mentioned person.")
  async def insult(self,ctx,target: discord.Member=None):
    if not target:
      target=ctx.author
    try:
      response=requests.get('https://evilinsult.com/generate_insult.php')
      insult=response.text.replace('&quot;','\"').replace("&gt;","")
      await ctx.send(f"{target.mention}, "+(insult[0].lower() if not insult.startswith("I ") else insult[0])+insult[1:])
    except:
      await ctx.send("Get a life.")

def setup(client):
  client.add_cog(fun(client))
