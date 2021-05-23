import os
import discord
from discord.ext import commands
from discord.utils import get
#import requests
import json
from utils import send_embed, get_channel_by_name, get_category_by_name, create_text_channel, create_voice_channel, get_quote, initial_catalog, get_catalog_size, data_catalog

token = os.environ['TOKEN']

#customize
botPrefix = 'pb'
templateChannel = 'Template'
specialServers=[844544300053430282,832994908973170769,838532330741039105]

client = commands.Bot(command_prefix=botPrefix+" ",intents=discord.Intents().all())


class field:
  def __init__(self,name,value,inline=False):
    self.name=name
    self.value=value
    self.inline=inline
    

#edit before deployment
def unload_cogs():
  #for filename in os.listdir('./extensions'):
  #  if filename.endswith('.py'):
  client.unload_extension(f'extensions.tester')
  client.unload_extension(f'extensions.tmdb_cog')
  client.unload_extension(f'extensions.fun')

#edit before deployment
def load_cogs():
  #for filename in os.listdir('./extensions'):
  #if filename.endswith('.py'):
  client.load_extension('extensions.tester')
  client.load_extension('extensions.tmdb_cog')
  client.load_extension(f'extensions.fun')


async def send_on_pvt_channel_creation(channel):
    await channel.send("Hello There!")
    title="Welcome to your Private Text Channel"
    description="Once your friends have joined the channel you may be able to lock it and chat without interruptions.\n\u200b"
    colour=discord.Colour.green()
    #For Links: [Movie Link](https://www.youtube.com/)
    fields = [field(
        "To Lock the Channel click on :lock:",
        "**To Unlock the Channel click on :unlock:**"
        ),
      field(
        "To invite someone into your channel",
        f"Type: `{botPrefix} pvtinvite @username`"
        ),
      field(
        "To kick an unwanted person from the channel",
        f"Type: `{botPrefix} votekick @username`"
        )
      ]
    message=await send_embed(channel,title,description,colour,fields=fields)
    return message


@client.event
async def on_ready():
    print('We are logged in as {0.user}'.format(client))


@client.event
async def on_raw_reaction_add(payload):
  if payload.member.bot==0:
    #lock pvt room
    if payload.emoji.name=='\U0001F512':
      channel= client.get_channel(payload.channel_id)
      if channel.name.endswith('-channel'):
        for role in payload.member.roles:
          if role.name.endswith('channel member'):
            vChannel=get_channel_by_name(client.get_guild(payload.guild_id),channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
        permsMember = vChannel.overwrites_for(role)
        permsMember.connect=True
        await vChannel.set_permissions(role, overwrite=permsMember)
        permsEveryone = vChannel.overwrites_for(client.get_guild(payload.guild_id).default_role)
        permsEveryone.connect=False
        await vChannel.set_permissions(client.get_guild(payload.guild_id).default_role, overwrite=permsEveryone)
            

    #Unlock Pvt Room
    if payload.emoji.name=='\U0001F513':
      tGuild=client.get_guild(payload.guild_id)
      tMember=tGuild.get_member(payload.user_id)
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

    #Carousel control
    buttons=['\u23ea','\u25c0','\u25b6','\u23e9']
    if payload.emoji.name in buttons:
      #is Carousel
      if payload.guild_id in specialServers:
        #is AV or Test Server
        channel = client.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        #print(msg)
        embed=msg.embeds[0]
        if embed != None:
          if embed.description.startswith('**Movie Synopsis**'):
            #is a Movie catalog
            index=int(embed.title[0])
            cat_size=get_catalog_size()
            print(f"Initial Given Index= {index}")
            if index==1:
              if embed.title[1].isdigit():
                index=(index*10)+int(embed.title[1])
                print(f'Given Index= {index}')
            elif index==0:
              print("Index is 0.")
              return
            index=index-1
            print(f"Normalised Index= {index}")
            prev_index=index
            if payload.emoji.name==buttons[0]:
              index=0
              print(f"SeekStart, index={index}")
            elif payload.emoji.name==buttons[1]:
              if index != 0:
                index=index-1
                print(f"Prev, index={index}")
            elif payload.emoji.name==buttons[2]:
              if index != (cat_size-1):
                index=index+1
                print(f"Next, index={index}")
            else:
              index=(cat_size-1)
              print(f"SeekEnd, index={index}")
            print(index)
            if index!=prev_index:
              title,description,image_url,link,fields=data_catalog(index)
              embed=await send_embed(channel,title,description,image_url=image_url,fields=[field(fields[0],fields[1])],send=False)
              await msg.edit(embed=embed)
              print("Display Updated")
              await msg.remove_reaction(payload.emoji.name,payload.member)
            else:
              print("Nothing to Update")
              await msg.remove_reaction(payload.emoji.name,payload.member)

        


    #vote to kick in pvt room
    if payload.emoji.name=='\U00002705':
      channel= client.get_channel(payload.channel_id)
      if channel.name.endswith('-channel'):
        print(channel.name)
        print(payload.member.roles)
        for role in payload.member.roles:
          print(role.name)
          if role.name.endswith('channel member'):
            vChannel=get_channel_by_name(client.get_guild(payload.guild_id),channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            print(role.name)
            break
        print(role)
        msg = await channel.fetch_message(payload.message_id)
        reaction = get(msg.reactions, emoji='\U00002705')
        if reaction and reaction.count > (round(len(payload.member.voice.channel.members)/2)):
          print(reaction.count)
          embed=msg.embeds[0]
          superset=client.get_all_members()
          target=str(embed.description[0:-59])
          for person in superset:
            if person.name==target:
              target=person
              break
          await target.move_to(None)
          print("Target Disconnected.")
          print (role.id)
          await target.remove_roles(role)
          print("Target's Role Removed.")
          await msg.delete()
          await channel.send(f"{target.name} has been kicked.")


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
@client.command(help='Returns an inspirational quote from the interwebs.')
async def inspire(ctx):
  quote=get_quote()
  await ctx.send("`"+quote+"`")


#hello command
@client.command(help="Says Hello.")
async def hello(ctx):
  await ctx.send("Hello There!")


#refresh command
@client.command(help="Reloads all Cogs.")
async def refresh(ctx):
  unload_cogs()
  load_cogs()
  await ctx.send("All cogs reloaded.")


#votekick command
@client.command(help="Initialises vote to Kick member of Private Voice Channel.")
async def votekick(ctx, member: discord.Member):
  #error if person not connected to a channel, handle errors
  if ctx.author.voice.channel==member.voice.channel:
    fields=[
      field(
        f"To Kick {member.name}:",
        f"Click on :white_check_mark: to kick `{member.name}` from the private channel.\n `{member.name}` will only be kicked if majority votes to."
        ),
      field(
        f"To Keep {member.name}:",
        "Click on :negative_squared_cross_mark:"
        )
      ]
    msg= await send_embed(ctx.message.channel,"Vote to Kick",f'`{member.name}` will be kicked from the private channel if majority votes.',discord.Color.red(),fields=fields)
    await msg.add_reaction('\U00002705')
    await msg.add_reaction('\U0000274E')
  else:
    ctx.send(f"{member.name} doesn't appear to be connected to your private Voice Channel")


#pvtinvite to pvt channel command
@client.command(help="Invites mentioned user to private voice channel.")
async def pvtinvite(ctx,member: discord.Member):
  if ctx.message.channel.name.endswith('-channel'):
    for roles in ctx.author.roles:
      if roles.name.endswith('channel member'):
        role=roles
    await member.add_roles(role)
    await member.send(f"`{ctx.author.name}` has invited you to join a private channel: {ctx.message.channel.mention} on the server: `{ctx.message.guild.name}`.\nYou should also probably join the Voice Channel with the same name. \nCheers!")
    await ctx.send(f"`{member.name}` has been invited to join this private channel.")


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
                await message.add_reaction('\U0001F513')
                if after.channel.guild.id in specialServers:
                  await pvt_text_channel.send("`Here is AV Club's curated Movie Catalog for the Month:`")
                  title,description,image_url,link,fields=initial_catalog()
                  msg=await send_embed(pvt_text_channel,title,description,image_url=image_url,fields=[field(fields[0],fields[1])])
                  buttons=['\u23ea','\u25c0','\u25b6','\u23e9']
                  for button in buttons:
                    await msg.add_reaction(button)
        elif after.channel.category.id == get_category_by_name(after.channel.guild,"Private Channels").id:
           pvtRole=discord.utils.get(after.channel.guild.roles, name=((after.channel.name)[0:-10]+" channel member"))
           print(pvtRole)
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


load_cogs()
client.run(token)
