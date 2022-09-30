import discord
import json
from discord.ext import commands
from utils import send_embed,field,config_dict
from aiohttp import ClientSession
import os

botPrefix=config_dict['botPrefix']
botName=config_dict['botName']
class general(commands.Cog):

  def __init__(self,client):
    self.client=client

  @commands.command(help="Clears the last message(s).")
  async def clear(self,ctx,limit=1):
    await ctx.channel.purge(limit=limit+1)

  @commands.command(help="Suggest a feature or report a bug.",aliases=['suggest','bug'])
  async def support(self,ctx):
    await send_embed(ctx.channel,"Private Bot Suggestion/Bug Report.",'Please click the following link: [Support](https://discord.gg/JYWVf7MFUt)\nYou could also directly contact abhinavgeethan#1933',footer='clear')
  
  @commands.command(help='Bot information.')
  async def info(self,ctx):
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
    try:
      response_time=data['monitors'][0]['response_times'][0]['value']
      avg=round(float(data['monitors'][0]['average_response_time']))
    except:
      response_time="Unavailable"
      avg="Unavailable"
    f=open('Commands.json','r')
    comm_list=json.load(f)
    f.close()
    comms=len(comm_list)
    fields=[
      field(
        "Developer",
        "abhinavgeethan#1933",
        True
      ),
      field(
        "Commands",
        str(comms),
        True
      ),
      field(
        "Guilds",
        str(len(self.client.guilds)),
        True
      ),
      field(
        "Support Server",
        "[Invite](https://discord.gg/JYWVf7MFUt)",
        True
      ),
      field(
        "Version",
        "2.0.0",
        True
      ),
      field(
        "Discord API version",
        "8",
        True
      ),
      field(
        "Discord-Py version",
        "1.7.3",
        True
      ),
      field(
        "Latency",
        f"{round(self.client.latency * 1000)} ms",
        True
        ),
      field(
        "Monitor Response",
        f"{response_time}"+(" ms" if response_time!='Unavailable' else '')+f"\nAverage: {avg}"+(" ms" if avg!='Unavailable' else ''),
        True
        )
      ]
    await send_embed(
      ctx.channel,
      f"{botName} Info",
      "A Discord bot with your privacy in mind.",
      fields=fields,
      footer='clear'
    )

  @commands.command(help=f"Displays Bot Commands and syntax. Alternative to {botPrefix} help")
  async def commands(self,ctx):
    fields=[]
    f=open('Commands.json','r')
    comm_list=json.load(f)
    f.close()
    for i in comm_list:
      fields.append(field(comm_list[i]['name'],"Syntax: "+comm_list[i]['syntax']+"\n\u200b\n*"+comm_list[i]['description']+"*\n\u200b\n",inline=True))

    await send_embed(ctx.channel,f"{botName} Commands","Use them wisely.\n\u200b\n",fields=fields,footer='Arguments inside [] are optional and those inside <> are necessary.')

async def setup(client):
  await client.add_cog(general(client))