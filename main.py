import os
import discord
from discord.ext import commands
from discord.utils import get
import requests
import json

token = os.environ['TOKEN']

#customize
botPrefix = 'pb'
templateChannel = 'Template'

client = commands.Bot(command_prefix=botPrefix+" ",intents=discord.Intents().all())


class field:
  def __init__(self,name,value,inline=False):
    self.name=name
    self.value=value
    self.inline=inline
    

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


def get_channel_by_name(guild, channel_name):
    channel = None
    for c in guild.channels:
        if c.name == channel_name.lower():
            channel = c
            break
    return channel


def get_category_by_name(guild, category_name):
    category = None
    for c in guild.categories:
        if c.name == category_name:
            category = c
            break
    return category


async def create_text_channel(guild, channel_name, category_name):
    category = get_category_by_name(guild, category_name)
    channel = await guild.create_text_channel(channel_name, category=category)
    #channel=get_channel_by_name(guild, channel_name)
    return channel, guild


async def create_voice_channel(guild,channel_name,category_name="VOICECHANNELS",user_limit=None):
    category = get_category_by_name(guild, category_name)
    await guild.create_voice_channel(channel_name,category=category,user_limit=user_limit)
    channel = get_channel_by_name(guild, channel_name)
    return channel


async def send_on_pvt_channel_creation(channel):
    await channel.send("Hello There!")
    title="Welcome to your Private Text Channel"
    description="Once your friends have joined the channel you may be able to lock it in the future haha."
    colour=discord.Colour.green()
    fields=[field("Movie 1","[Movie Link](https://www.youtube.com/)"),field("Movie 2", "[Movie Link](https://www.youtube.com/)")]
    message=await send_embed(channel,title,description,colour,fields=fields)
    return message


async def send_embed(channel,title,description,colour=discord.Colour.blue(),image_url=None,thumbnail_url=None,fields=None):
  embed=discord.Embed(title=title,description=description,colour=colour)
  embed.set_footer(text='This is sent by a bot under development by abhinavgeethan#1933. Excuse any bugs.')
  if image_url != None:
    embed.set_image(url=image_url)
  if thumbnail_url != None:
    embed.set_thumbnail(url=thumbnail_url)
  for field in fields:
    embed.add_field(name=field.name, value=field.value, inline=field.inline)
  message=await channel.send(embed=embed)
  return message


#async def reactRole(message,emoji, role: discord.Role=None):
  #await message.add_reaction(emoji)
  #with open('pvtRoles.json') as json_file:
  #  data=json.load(json_file)
  #  newRole={
  #    'roleName':role.name,
  #    'roleId':role.id,
  #    'emoji':emoji,
  #    'messageId':message.id
  #  }
  #  data.append(newRole)
  #with open('pvtRoles.json','w') as j:
  #  json.dump(data,j,indent=4)


@client.event
async def on_ready():
    print('We are logged in as {0.user}'.format(client))


@client.event
async def on_raw_reaction_add(payload):
  if payload.member.bot==0:
    if payload.emoji.name=='\U0001F512':
      channel= client.get_channel(payload.channel_id)
      if '-channel' in channel.name:
        for role in payload.member.roles:
          if 'channel member' in role.name:
            vChannel=get_channel_by_name(client.get_guild(payload.guild_id),channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
        permsMember = vChannel.overwrites_for(role)
        permsMember.connect=True
        await vChannel.set_permissions(role, overwrite=permsMember)
        permsEveryone = vChannel.overwrites_for(client.get_guild(payload.guild_id).default_role)
        permsEveryone.connect=False
        await vChannel.set_permissions(client.get_guild(payload.guild_id).default_role, overwrite=permsEveryone)


@client.event
async def on_raw_reaction_remove(payload):
  tGuild=client.get_guild(payload.guild_id)
  tMember=tGuild.get_member(payload.user_id)
  if tMember.bot==0:
    if payload.emoji.name=='\U0001F512':
      channel= client.get_channel(payload.channel_id)
      if '-channel' in channel.name:
        for role in tMember.roles:
          if 'channel member' in role.name:
            vChannel=get_channel_by_name(client.get_guild(payload.guild_id),channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
        permsMember = vChannel.overwrites_for(role)
        permsMember.connect=None
        await vChannel.set_permissions(role, overwrite=permsMember)
        permsEveryone = vChannel.overwrites_for(client.get_guild(payload.guild_id).default_role)
        permsEveryone.connect=None
        await vChannel.set_permissions(client.get_guild(payload.guild_id).default_role, overwrite=permsEveryone)


#inspire command
@client.command()
async def inspire(ctx):
  quote=get_quote()
  await ctx.send(quote)


#hello command
@client.command()
async def hello(ctx):
  await ctx.send("Hello There!")


@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    #join channel
    if not before.channel:
        print(f'{member.name} joined {after.channel.name}')

    #left channel
    if before.channel and not after.channel:
        print(f'{member.name} left {before.channel.name}')

    #switch channel
    if before.channel and after.channel:
        if before.channel.id != after.channel.id:
            print(
                f'{member.name} switched channels and is now in {after.channel.name}.'
            )
        elif member.voice.self_mute:
            print(f'{member.name} muted self.')
        elif member.voice.self_deaf:
            print(f'{member.name} deafened  self.')
        elif member.voice.self_stream:
            print(f'{member.name} started streaming.')
        else:
            print("Something else happened.")

    #creating channels
    if after.channel is not None:
        if after.channel.name == templateChannel:
            #print("Transfer")
            pvt_text_channel, pvt_text_channel_guild = await create_text_channel(after.channel.guild,f'{member.name}-channel'.lower(),category_name="Private Channels")
            channel = await create_voice_channel(after.channel.guild,f'{member.name}\'s Channel'.lower(),category_name="Private Channels",user_limit=None)
            if channel is not None:
                await member.move_to(channel)
                message=await send_on_pvt_channel_creation(pvt_text_channel)
                newRole=await pvt_text_channel_guild.create_role(
                  name=f'{member.name} channel member',
                  hoist=False,
                  mentionable=False,
                  reason='Created Pvt Channel'
                  )
                await member.add_roles(newRole)
                await message.add_reaction('\U0001F512')
                #await reactRole(message,'\U0001F512')

        elif after.channel.category.id == get_category_by_name(before.channel.guild,"Private Channels").id:
          pvtRole=get(after.channel.guild.roles, name=str(before.channel.name)[0:-10]+" channel member")
          await member.add_roles(pvtRole)

    #deleteting pvt channels once empty
    if before.channel is not None:
        if before.channel.category.id == get_category_by_name(before.channel.guild,"Private Channels").id:
            pvtRole=get(before.channel.guild.roles, name=str(before.channel.name)[0:-10]+" channel member")
            await member.remove_roles(pvtRole)
            if len(before.channel.members) == 0:
                txtchannelName=str(before.channel.name)[0:-10]+"-channel"
                #Delete VC
                await before.channel.delete()
                #Delete TC
                channel = get_channel_by_name(before.channel.guild,txtchannelName)
                await channel.delete()
                await pvtRole.delete()


client.run(token)
