import dis
import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import json
# from keep_alive import keep_alive #Uncomment
from utils import *
from asyncio import run as AsyncRun

# Dev Only
from dotenv import load_dotenv
load_dotenv() 

token = os.environ['TOKEN']

#-----------------------------------------Customize for Unique Implementations-----------------------------------------------#
config=config_dict
botPrefix=config['botPrefix']
specialServers=[832994908973170769]
masterGuild=config['masterGuild']
updateChannel=config['updateChannel']
reaction_emojis=[
        "\U0001F512",
        "\U0001F513",
        "\U0001F441",
        "\u23ea",
        "\u25c0",
        "\u25b6",
        "\u23e9",
        "\U00002705",
        "\U0001f7e5",
        "\U0001f7e6",
        "\U0001f7e7",
        "\U0001f7e8",
        "\U0001f7e9",
        "\U0001f7ea",
        "\U0001f7eb",
        "\U00002b1b",
        "\U00002b1c"
    ],
monitorName='private bot monitor'
# client = commands.Bot(command_prefix=config['botPrefix']+" ",intents=discord.Intents().all(),case_insensitive=True, description=description, owner_id=710430416045080656)
#-------------------------------------------Important Customizable Functions-------------------------------------------------#

async def load_cogs(client):
  await client.load_extension('extensions.tester')
  await client.load_extension('extensions.tmdb_cog')
  await client.load_extension('extensions.fun')
  await client.load_extension('extensions.general')
  await client.load_extension('extensions.dicti_cog')
  # await client.load_extension('extensions.tourney')
  # await client.load_extension('extensions.rxnrole')
  await client.load_extension('extensions.games')
  print("Loaded Cogs")

async def unload_cogs(client):
  await client.unload_extension('extensions.tester')
  await client.unload_extension('extensions.tmdb_cog')
  await client.unload_extension('extensions.fun')
  await client.unload_extension('extensions.general')
  await client.unload_extension('extensions.dicti_cog')
  # await client.unload_extension('extensions.tourney')
  # await client.unload_extension('extensions.rxnrole')
  await client.unload_extension('extensions.games')
  print("Unloaded Cogs")

async def reload_cogs(client):
  await client.reload_extension('extensions.tester')
  await client.reload_extension('extensions.tmdb_cog')
  await client.reload_extension('extensions.fun')
  await client.reload_extension('extensions.general')
  await client.reload_extension('extensions.dicti_cog')
  # await client.reload_extension('extensions.tourney')
  # await client.reload_extension('extensions.rxnrole')
  await client.reload_extension('extensions.games')
  print("Reloaded Cogs")

# client=commands.Bot(command_prefix=config['botPrefix']+' ', description=config['description'], intents=discord.Intents.all(), case_insensitive=True,owner_id=config['owner_id'])

class MyClient(commands.Bot):
  def __init__(self, config) -> None:
    myIntents=discord.Intents.all()
    super().__init__(command_prefix=config['botPrefix']+' ', description=config['description'], intents=myIntents, case_insensitive=True,owner_id=config['owner_id'])
  
  async def setup_hook(self):
    await load_cogs(self)
    comms=await self.tree.sync()
    print(f'Synced {len(comms)} app_commands.')

client=MyClient(config)

def is_me(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 710430416045080656

async def send_on_pvt_channel_creation(channel):
    await channel.send("Hello There!")
    title="Welcome to your Private Text Channel"
    description="Once your friends have joined the channel you may be able to lock it and chat without interruptions.\n\u200b"
    colour=discord.Colour.green()
    fields = [
      field(
        "To Lock the Channel click on :lock:",
        "**To Unlock the Channel click on :unlock:**\n**To Toggle the Channel visibility click on :eye:**"
        ),
      field(
        "To invite someone into your channel",
        f"Type: `{botPrefix} pvtinvite @username`"
        ),
      field(
        "To kick an unwanted person from the channel",
        f"Type: `{botPrefix} votekick @username`"
        ),
      field(
        "Lock Status",
        "Unlocked",
        True
      ),
      field(
        "Channel Visibility",
        "Visible",
        True
      ),
      field(
        'Use `pb commands` to see full list of commands.',
        "\u200b"
      )
      ]
    view=ChannelControls()
    message=await send_embed(channel,title,description,colour,fields=fields,footer=botPrefix.upper()+"PVT"+str(channel.id)[-5:],view=view)
    return message

#-------------------------------------------------------General Commands-----------------------------------------------------#
#inspire command
@client.hybrid_command(name='inspire',help='Returns an inspirational quote from the interwebs.')
async def inspire(ctx):
  quote=get_quote()
  await ctx.send("`"+quote+"`")


#hello command
@client.command(help="Says Hello.")
async def hello(ctx):
  await ctx.send("Hello There!")

#----------------------------------------------------Developer Command-------------------------------------------------------#
#refresh command
@client.hybrid_command(name='refresh',help="Reloads all Cogs. Dev-only Command",hidden=True)
@app_commands.check(is_me)
async def refresh(ctx):
  if ctx.author.id==710430416045080656:
    await reload_cogs(client)
    await ctx.send("All cogs reloaded.")
  else:
    await ctx.send("You do not have sufficient permissions to invoke this command at the moment.")

@refresh.error
async def is_me_error(ctx,error):
  if isinstance(error,commands.errors.CheckFailure):
    response_embed=await send_embed(ctx.channel,"Error","You do not have sufficient permissions to invoke this command at the moment.",discord.Color.red(),isInteractionResponse=True)
    await ctx.interaction.response.send_message(embed=response_embed)

#sync command
@client.tree.command(name='sync',description="Sync all app_commands. Dev-only Command")
@app_commands.check(is_me)
async def _sync(interaction:discord.Interaction):
  comms=await client.tree.sync()
  print(f"Synced {len(comms)} app_commands.")
  await interaction.response.send_message(content=f"{len(comms)} app commands synced with all guilds.")

@_sync.error
async def sync_error(interaction,error):
  if isinstance(error,app_commands.errors.CheckFailure):
    response_embed=await send_embed(interaction.channel,"Error","You do not have sufficient permissions to invoke this command at the moment.",discord.Color.red(),isInteractionResponse=True)
    await interaction.response.send_message(embed=response_embed)
  else:
    raise


#------------------------------------------------Private Channel Commands----------------------------------------------------#
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
    msg= await send_embed(ctx.message.channel,"Vote to Kick",f'`{member.name}` will be kicked from the private channel if majority votes.',discord.Color.red(),fields=fields,footer=botPrefix.upper()+"VKE"+str(ctx.message.channel.id)[-5:])
    await msg.add_reaction('\U00002705')
    await msg.add_reaction('\U0000274E')
  else:
    ctx.send(f"{member.name} doesn't appear to be connected to your private Voice Channel")


#pvtinvite to pvt channel command
@client.hybrid_command(help="Invites mentioned user to private voice channel.")
async def pvtinvite(ctx,member: discord.Member):
  if ctx.message.channel.name.endswith('-channel'):
    for roles in ctx.author.roles:
      if roles.name.endswith('channel member'):
        role=roles
    await member.add_roles(role)
    try:
      await member.send(f"`{ctx.author.name}` has invited you to join a private channel: {ctx.message.channel.mention} on the server: `{ctx.message.guild.name}`.\nYou should also probably join the Voice Channel with the same name. \nCheers!")
      await ctx.send(f"`{member.name}` has been invited to join this private channel.")
    except:
      await ctx.send(f"`{member.name}` has their DM's closed. Nevertheless, I have given them access to your channel.")


#------------------------------------------------------Event Listeners-------------------------------------------------------#
@client.event
async def on_ready():
    print('We are logged in as {0.user}'.format(client))
    # TODO: Uncomment for Prod
    # channel=client.get_channel(updateChannel)
    # await channel.purge(limit=3,check=is_me)
    # response_time,avg,status=get_bot_status()
    # if status==2:
    #   print("UptimeRobot reports the bot to be UP.")
    # else:
    #   print("UptimeRobot does not give an accurate report.")
    # await send_embed(channel,"Status",f"**{config['botName']} is now online and operational.**",discord.Color.green(),timestamp=datetime.now(),footer='clear',fields=[field("Discord API",f"{round(client.latency * 1000)} ms",True),field("Round-Trip Response",f"{response_time}"+(" ms" if response_time!='Unavailable' else '')+f"\nAverage: {avg}"+(" ms" if avg!='Unavailable' else ''),True)])
    # await send_embed(channel,"","It can take upto **4** minutes to confirm that the bot is down.",footer='If you encounter an undetected downtime head over to #bug-report.')

#Reaction Listeners
@client.event
async def on_raw_reaction_add(payload):
  if payload.member.bot!=0:
    return
  if not payload.emoji.name in reaction_emojis:
    return
  channel=payload.member.guild.get_channel(payload.channel_id)
  message=await channel.fetch_message(payload.message_id)
  embed=message.embeds[0]
  if not embed.footer:
    return
  id=embed.footer.text[0:10]
  if not id.lower().startswith(botPrefix.lower()):
    return
  if not id[-5:]==str(payload.channel_id)[-5:]:
    print("Rxn: Channel Error",id[-5:],str(payload.channel_id)[-5:])
    return
  if id[2:].startswith("RR"):
    #ReactionRole
    for em_pxy in embed.fields:
      if em_pxy.name.startswith(payload.emoji.name):
        role_name=em_pxy.name[len(payload.emoji.name)+3:]
        break
    if role_name:
      for r in payload.member.guild.roles:
        if r.name==role_name:
          role=r
          break
      if role:
        try:
          await payload.member.add_roles(role,reason=f"Reacted on {config['botName']}'s Reaction Role post with id: {id}")
        except:
          print("RR: Role Assign Failed due to:")
          await channel.send(f"{payload.member.mention}, I could not give you the {role.mention} role.")
          raise
      else:
        print(f"RR: Couldnt find role with rolename: {role_name} on guild: {payload.guild.name}")
    else:
      print("RR: Couldnt find rolename in RR embed.")
      return
  elif id[2:].startswith("PVT"):
    #lock pvt room
    if payload.emoji.name=='\U0001F512':
      # channel= client.get_channel(payload.channel_id)
      guild=payload.member.guild
      if channel.name.endswith('-channel'):
        for role in payload.member.roles:
          if role.name.endswith('channel member'):
            vChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
        #voicechannel
        permsMember = vChannel.overwrites_for(role)
        permsMember.connect=True
        await vChannel.set_permissions(role, overwrite=permsMember)
        permsEveryone = vChannel.overwrites_for(guild.default_role)
        permsEveryone.connect=False
        await vChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
        msg=await channel.fetch_message(payload.message_id)
        #txtchannel
        # txtChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+"-channel")
        txtChannel=channel
        permsMember = txtChannel.overwrites_for(role)
        permsMember.send_messages=True
        await txtChannel.set_permissions(role, overwrite=permsMember)
        permsEveryone = txtChannel.overwrites_for(guild.default_role)
        permsEveryone.send_messages=False
        await txtChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
        #updation
        # msg=await channel.fetch_message(payload.message_id)
        await update_lock_status(vChannel,message,guild)
        await message.remove_reaction(payload.emoji.name,payload.member)
        

    #Unlock Pvt Room
    if payload.emoji.name=='\U0001F513':
      guild=payload.member.guild
      # channel= client.get_channel(payload.channel_id)
      if '-channel' in channel.name:
        for role in payload.member.roles:
          if 'channel member' in role.name:
            vChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
        #vChannel
        permsMember = vChannel.overwrites_for(role)
        permsMember.connect=None
        await vChannel.set_permissions(role, overwrite=permsMember)
        permsEveryone = vChannel.overwrites_for(guild.default_role)
        permsEveryone.connect=None
        await vChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
        #txtchannel
        # txtChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+"-channel")
        txtChannel=channel
        permsMember = txtChannel.overwrites_for(role)
        permsMember.send_messages=None
        await txtChannel.set_permissions(role, overwrite=permsMember)
        permsEveryone = txtChannel.overwrites_for(guild.default_role)
        permsEveryone.send_messages=None
        await txtChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
        #updation
        # msg=await channel.fetch_message(payload.message_id)
        await update_lock_status(vChannel,message,guild)
        await message.remove_reaction(payload.emoji.name,payload.member)


    #Toggle Visibility
    if payload.emoji.name=='\U0001F441':
      guild=payload.member.guild
      # channel= client.get_channel(payload.channel_id)
      if '-channel' in channel.name:
        for role in payload.member.roles:
          if 'channel member' in role.name:
            vChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
        curr=check_vis_perms(vChannel,guild)
        if curr:
          permsMember = vChannel.overwrites_for(role)
          permsMember.view_channel=True
          await vChannel.set_permissions(role, overwrite=permsMember)
          permsEveryone = vChannel.overwrites_for(guild.default_role)
          permsEveryone.view_channel=False
          await vChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
          #txtchannel
          # txtChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+"-channel")
          txtChannel=channel
          permsMember = txtChannel.overwrites_for(role)
          permsMember.view_channel=True
          await txtChannel.set_permissions(role, overwrite=permsMember)
          permsEveryone = txtChannel.overwrites_for(guild.default_role)
          permsEveryone.view_channel=False
          await txtChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
          #updation
          # msg=await channel.fetch_message(payload.message_id)
          await update_visibility_status(vChannel,message,guild)
          await message.remove_reaction(payload.emoji.name,payload.member)
        else:
          permsMember = vChannel.overwrites_for(role)
          permsMember.view_channel=True
          await vChannel.set_permissions(role, overwrite=permsMember)
          permsEveryone = vChannel.overwrites_for(guild.default_role)
          permsEveryone.view_channel=None
          await vChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
          #txtchannel
          # txtChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+"-channel")
          txtChannel=channel
          permsMember = txtChannel.overwrites_for(role)
          permsMember.view_channel=True
          await txtChannel.set_permissions(role, overwrite=permsMember)
          permsEveryone = txtChannel.overwrites_for(guild.default_role)
          permsEveryone.view_channel=None
          await txtChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
          #updation
          # msg=await channel.fetch_message(payload.message_id)
          await update_visibility_status(vChannel,message,guild)
          await message.remove_reaction(payload.emoji.name,payload.member)
  elif id[2:].startswith("AVC"):
    #Carousel control
    buttons=['\u23ea','\u25c0','\u25b6','\u23e9']
    if payload.emoji.name in buttons:
      #is Carousel
      if payload.guild_id in specialServers:
        #is AV or Test Server
        # channel = client.get_channel(payload.channel_id)
        # msg = await channel.fetch_message(payload.message_id)
        #print(msg)
        # embed=msg.embeds[0]
        if embed != None:
          if embed.description.startswith('**Movie Synopsis**'):
            #is a Movie catalog
            index=int(embed.title[0])
            cat_size=get_catalog_size()
            #print(f"Initial Given Index= {index}")
            if index==1:
              if embed.title[1].isdigit():
                index=(index*10)+int(embed.title[1])
                #print(f'Given Index= {index}')
            elif index==0:
              #print("Index is 0.")
              return
            index=index-1
            #print(f"Normalised Index= {index}")
            prev_index=index
            if payload.emoji.name==buttons[0]:
              index=0
              #print(f"SeekStart, index={index}")
            elif payload.emoji.name==buttons[1]:
              if index != 0:
                index=index-1
                #print(f"Prev, index={index}")
            elif payload.emoji.name==buttons[2]:
              if index != (cat_size-1):
                index=index+1
                #print(f"Next, index={index}")
            else:
              index=(cat_size-1)
              #print(f"SeekEnd, index={index}")
            #print(index)
            if index!=prev_index:
              title,description,image_url,link,fields,author,thumbnail_url=data_catalog(index)
              embed=await send_embed(channel,title,description,image_url=image_url,fields=[field(fields[0],fields[1])],send=False,author=author,thumbnail_url=thumbnail_url,footer=botPrefix.upper()+"AVC"+str(channel.id)[-5:]+'Use the Arrow icons below to navigate through the catalog.')
              await message.edit(embed=embed)
              #print("Display Updated")
              await message.remove_reaction(payload.emoji.name,payload.member)
            else:
              print("Nothing to Update")
              await message.remove_reaction(payload.emoji.name,payload.member)
  elif id[2:].startswith("VKE"):
    #vote to kick in pvt room
    if payload.emoji.name=='\U00002705':
      # channel= client.get_channel(payload.channel_id)
      if channel.name.endswith('-channel'):
        #print(channel.name)
        #print(payload.member.roles)
        for role in payload.member.roles:
          #print(role.name)
          if role.name.endswith('channel member'):
            guild=payload.member.guild
            vChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            #print(role.name)
            break
        #print(role)
        # msg = await channel.fetch_message(payload.message_id)
        #opp_reaction=get(msg.reactions, emoji='\U0000274E')
        #opp_reactors=await opp_reaction.users().flatten()
        #if payload.member.name in opp_reactors:
        #  await msg.remove_reaction(opp_reaction.emoji,payload.member)
        reaction = get(message.reactions, emoji='\U00002705')
        if reaction and reaction.count > (round(len(payload.member.voice.channel.members)/2)):
          #print(reaction.count)
          # embed=msg.embeds[0]
          #superset=client.get_all_members()
          targetName=embed.description[1:-60]
          #for person in superset:
          #  if person.name==target:
          #    target=person
          #    break
          print(targetName)
          target=guild.get_member_named(targetName)
          if target==payload.member:
            await channel.send(f"Why kick yourself {payload.member.mention}?")
          else:
            await target.move_to(None)
            #print("Target Disconnected.")
            #print (role.id)
            await target.remove_roles(role)
            #print("Target's Role Removed.")
            await message.delete()
            await channel.send(f"{target.name} has been kicked.")

@client.event
async def on_raw_reaction_remove(payload):
#  tGuild=client.get_guild(payload.guild_id)
#  tMember=tGuild.get_member(payload.user_id)
#  if tMember.bot==0:
#    if payload.emoji.name=='\U0001F441':
#      #guild=client.get_guild(payload.guild_id)
#      channel= client.get_channel(payload.channel_id)
#      if '-channel' in channel.name:
#        for role in tMember.roles:
#          if 'channel member' in role.name:
#            vChannel=get_channel_by_name(tGuild,channel_name=str(role.name)[0:-15]+'\'s Channel')
#            role=role
#            break
#        permsMember = vChannel.overwrites_for(role)
#        permsMember.view_channel=True
#        await vChannel.set_permissions(role, overwrite=permsMember)
#        permsEveryone = vChannel.overwrites_for(tGuild.default_role)
#        permsEveryone.view_channel=None
#        await vChannel.set_permissions(tGuild.default_role, overwrite=permsEveryone)
#        msg=await channel.fetch_message(payload.message_id)
#        await update_visibility_status(vChannel,msg,tGuild)
#        #await msg.remove_reaction(payload.emoji.name,payload.member)

#    if payload.emoji.name=='\U0001F512':
#      channel= client.get_channel(payload.channel_id)
#      if '-channel' in channel.name:
#        for role in tMember.roles:
#          if 'channel member' in role.name:
#            vChannel=get_channel_by_name(client.get_guild(payload.guild_id),channel_name=str(role.name)[0:-15]+'\'s Channel')
#            role=role
#            break
#        permsMember = vChannel.overwrites_for(role)
#        permsMember.connect=None
#        await vChannel.set_permissions(role, overwrite=permsMember)
#        permsEveryone = vChannel.overwrites_for(client.get_guild(payload.guild_id).default_role)
#        permsEveryone.connect=None
#        await vChannel.set_permissions(client.get_guild(payload.guild_id).default_role, overwrite=permsEveryone)
  pass

class ChannelControls(discord.ui.View):
  def __init__(self):
    super().__init__()

  @discord.ui.button(label='Lock',emoji='🔒')
  async def lock_channel(self, interaction:discord.Interaction,button: discord.ui.Button):
    guild=interaction.guild
    txtChannel=interaction.channel
    for role in interaction.user.roles:
          if role.name.endswith('channel member'):
            vChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
    # Voice Channel
    permsMember = vChannel.overwrites_for(role)
    permsMember.connect=True
    await vChannel.set_permissions(role, overwrite=permsMember)
    permsEveryone = vChannel.overwrites_for(guild.default_role)
    permsEveryone.connect=False
    await vChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
    # Text Channel
    permsMember = txtChannel.overwrites_for(role)
    permsMember.send_messages=True
    await txtChannel.set_permissions(role, overwrite=permsMember)
    permsEveryone = txtChannel.overwrites_for(guild.default_role)
    permsEveryone.send_messages=False
    await txtChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
    button.disabled=True

  @discord.ui.button(label='Unlock',emoji='🔓')
  async def unlock_channel(self, interaction:discord.Interaction,button: discord.ui.Button):
    guild=interaction.guild
    txtChannel=interaction.channel
    for role in interaction.user.roles:
          if role.name.endswith('channel member'):
            vChannel=get_channel_by_name(guild,channel_name=str(role.name)[0:-15]+'\'s Channel')
            role=role
            break
    # Voice Channel
    permsMember = vChannel.overwrites_for(role)
    permsMember.connect=None
    await vChannel.set_permissions(role, overwrite=permsMember)
    permsEveryone = vChannel.overwrites_for(guild.default_role)
    permsEveryone.connect=None
    await vChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
    # Text Channel
    permsMember = txtChannel.overwrites_for(role)
    permsMember.send_messages=None
    await txtChannel.set_permissions(role, overwrite=permsMember)
    permsEveryone = txtChannel.overwrites_for(guild.default_role)
    permsEveryone.send_messages=None
    await txtChannel.set_permissions(guild.default_role, overwrite=permsEveryone)
    button.disabled=True

#Voice State Listeners
@client.event
async def on_voice_state_update(member, before, after):
  if member.bot:
      return
  #join channel
  if not before.channel:
      #print(f'{member.name} joined {after.channel.name}')
      pass

  #left channel
  if before.channel and not after.channel:
      #print(f'{member.name} left {before.channel.name}')
      pass

  #switch channel
  if before.channel and after.channel:
      if before.channel.id != after.channel.id:
          #print(f'{member.name} switched channels and is now in {after.channel.name}.')
          pass
      elif member.voice.self_mute:
          #print(f'{member.name} muted self.')
          pass
      elif member.voice.self_deaf:
          #print(f'{member.name} deafened  self.')
          pass
      elif member.voice.self_stream:
          #print(f'{member.name} started streaming.')
          pass
      else:
          print("Something else happened.")

  #creating channels
  if after.channel is not None:
    if after.channel.name == config['templateChannel']:
        #print("Transfer")
        guild=after.channel.guild
        check=await if_owner(guild,member)
        if not check:
          pvt_text_channel, pvt_text_channel_guild = await create_text_channel(guild,f'{member.name}-channel'.lower(),category_name="Private Channels")
          channel = await create_voice_channel(guild,f'{member.name}\'s Channel'.lower(),category_name="Private Channels",user_limit=None)
          if channel is not None:
              await member.move_to(channel)
              message=await send_on_pvt_channel_creation(pvt_text_channel)
              newRole=await pvt_text_channel_guild.create_role(
                name=f'{member.name} channel member'.lower(),
                hoist=False,
                mentionable=False,
                reason='Created Pvt Channel'
                )
              await member.add_roles(newRole)
              await message.add_reaction('\U0001F512')
              await message.add_reaction('\U0001F513')
              await message.add_reaction('\U0001F441')
              await message.pin()
              if guild.id in specialServers:
                await pvt_text_channel.send("`Watch F.R.I.E.N.D.S: The Reunion as a part of AV Club's SNL here:`")
                title,description,image_url,link,fields=initial_catalog()
                thumbnail_url='https://instagram.ffjr1-2.fna.fbcdn.net/v/t51.2885-19/s150x150/30590396_163613307799664_9089326030237204480_n.jpg?tp=1&_nc_ht=instagram.ffjr1-2.fna.fbcdn.net&_nc_ohc=GppUZ8OOmQYAX8ArS8i&edm=ABfd0MgBAAAA&ccb=7-4&oh=b9f0d6377eae12d363e92b4ffd4a127c&oe=60B4CDD2&_nc_sid=7bff83'
                author='AV Club\'s SNL'
                msg=await send_embed(pvt_text_channel,title,description,image_url=image_url,fields=[field(fields[0],fields[1])],thumbnail_url=thumbnail_url,author=author,footer=botPrefix.upper()+"AVC"+str(pvt_text_channel.id)[-5:]+' For assistance use pb support or contact a server admin with @Admin.')
                #buttons=['\u23ea','\u25c0','\u25b6','\u23e9']
                #for button in buttons:
                #  await msg.add_reaction(button)
        else:
          #print("Channel Exists, Moved.")
          await member.move_to(get_channel_by_name(guild,member.name+'\'s channel'))

    elif after.channel.category.id == get_category_by_name(after.channel.guild,"Private Channels").id:
        roleName=after.channel.name[0:-10]+' channel member'
        print(roleName)
        pvtRole=discord.utils.get(after.channel.guild.roles, name=roleName)
        print(pvtRole)
        await member.add_roles(pvtRole)

    #deleteting pvt channels once empty
  if before.channel is not None:
    guild=before.channel.guild
    if before.channel.category.id == get_category_by_name(guild,"Private Channels").id:
      roleName=str(before.channel.name)[0:-10]+" channel member"
      print(roleName+" to remove from user for leaving.")
      pvtRole=get(guild.roles, name=roleName)
      print(pvtRole)
      await member.remove_roles(pvtRole)
      if len(before.channel.members) == 0:
          txtchannelName=str(before.channel.name)[0:-10]+"-channel"
          #Delete VC
          await before.channel.delete()
          #Delete TC
          channel = get_channel_by_name(guild,txtchannelName)
          await channel.delete()
          await pvtRole.delete()

@client.event
async def on_command_error(ctx,error):
  if isinstance(error,commands.MissingRequiredArgument):
    comm=ctx.command.name
    f=open('Commands.json','r')
    comm_list=json.load(f)
    f.close()
    for i in comm_list:
      if comm_list[i]['identifier']==comm:
        syntax=comm_list[i]['syntax']
        break
    await send_embed(ctx.channel,"",'One or more required inputs weren\'t provided.',discord.Colour.red(),fields=[field('The correct syntax is:',f"{syntax}")],footer='clear')
  elif isinstance(error,commands.DisabledCommand):
    await send_embed(ctx.channel,'',f"`{botPrefix} {ctx.command.name}` is temporarily disabled.",discord.Colour.red(),footer='clear')
  elif isinstance(error,commands.MemberNotFound):
    await send_embed(ctx.channel,'',f"User: `{error.argument}` was not found in this server.",discord.Colour.red(),footer='clear')
  elif isinstance(error,commands.RoleNotFound):
    await send_embed(ctx.channel,'',f"Role: `{error.argument}` was not found in this server.",discord.Colour.red(),footer='clear')
  elif isinstance(error,commands.MissingRole):
    await send_embed(ctx.channel,'',f"Role: `{error.missing_role}` is required to invoke that command.",discord.Colour.red(),footer='clear')
  elif isinstance(error,commands.CommandNotFound):
    pass
  elif isinstance(error,commands.errors.CheckFailure):
    pass
  else:
    await send_embed(ctx.channel,"Error",f"An unexpected error occurred. Use `{botPrefix} commands` to verify your syntax.",discord.Color.red(),footer=f'Alternatively, try again later; if the issue persists use {botPrefix} support to report the issue.')
    raise error

# keep_alive() # TODO: Uncomment for Prod
client.run(token)