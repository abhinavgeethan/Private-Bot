import os
import discord
from discord.ext import commands
from utils import config_dict

# TODO: Remove after Dev
from dotenv import load_dotenv
load_dotenv()

token=os.environ['TOKEN']
intents=discord.Intents.all()
bot=commands.Bot(command_prefix=config_dict['botPrefix'],intents=intents)

@bot.event
async def on_ready():
    print(f'We are logged in as {bot.user}')

bot.run(token)
