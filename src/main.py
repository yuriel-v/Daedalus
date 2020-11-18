# Controllers para o bot Daedalus.

import sqlalchemy as sqla
import discord

from games import *
from discord.ext import commands
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
from secret import daedalus_token

# engine = create_engine('sqlite:///database/data.db', echo=True)
# Session = sessionmaker(bind=engine)
# session = Session()
bot = commands.Bot(command_prefix=['>>', 'Roger '])


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}.")


@bot.command(name='8ball')
async def magic_eight_ball(ctx):
    await ctx.send(f"{ctx.message.author.mention}: {eight_ball()}")

bot.run(daedalus_token)
