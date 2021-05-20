import discord

async def send_embed(channel,title,description,colour=discord.Colour.blue(),image_url=None,thumbnail_url=None,fields=None):
  embed=discord.Embed(title=title,description=description,colour=colour)
  embed.set_footer(text='This is sent by a bot under development by abhinavgeethan#1933. Excuse any bugs.')
  if image_url != None:
    embed.set_image(url=image_url)
  if thumbnail_url != None:
    embed.set_thumbnail(url=thumbnail_url)
  if fields != None:
    for field in fields:
      embed.add_field(name=field.name, value=field.value, inline=field.inline)
  message=await channel.send(embed=embed)
  return message