"""
startup - Inicialização

Módulo encarregado de inicializar o bot corretamente, junto com a conexão com
o banco de dados via SQLAlchemy.
"""

import asyncio

import cogs

from os import getenv

from discord.errors import ConnectionClosed, GatewayNotFound, HTTPException, LoginFailure
from discord.ext import commands
from discord.flags import Intents
from discord.member import Member

from db import engin, devengin, initialize_sql
from .utils import arg_types, smoothen, print_exc, daedalus


# Inicialização
bot = commands.Bot(
    command_prefix=[">>", "Roger "],
    owner_id=int(getenv("DAEDALUS_OWNERID")),
    intents=Intents(messages=True, guilds=True, members=True, presences=True),
    help_command=None
)
initialize_sql(devengin if (daedalus["environment"] == "DEV" and devengin is not None) else engin)

# Mensagem de inicialização
init = f"""
=========================================================================
Project Daedalus v{daedalus['version']} - {daedalus['environment']} environment
All systems go."""
init2 = """
Loaded cogs:
%s
========================================================================="""

# Cogs
all_cogs = dict([(name, cls) for name, cls in cogs.__dict__.items() if isinstance(cls, type) and not name.startswith('_')])
for cog in all_cogs.values():
    bot.add_cog(cog(bot))


# Funções
def list_cogs(bot: commands.Bot):
    return '\n'.join(f'- {cogname}' for cogname in bot.cogs.keys())


def main(*args, **kwargs):
    global bot
    loop = asyncio.get_event_loop()  # TODO: Fix this maybe, apparently there is no more current event loop

    async def run_bot():
        try:
            await bot.start(*args, **kwargs)
        finally:
            if not bot.is_closed():
                await bot.close()

    asyncio.ensure_future(run_bot(), loop=loop)
    try:
        loop.run_forever()
    except GatewayNotFound:
        print_exc(f"Gateway wasn't found, likely a Discord API error.")
    except ConnectionClosed:
        print_exc(f"Connection closed by Discord.")
    except LoginFailure:
        print_exc(f"You gave me the wrong credentials, so Discord didn't let me log in.")
    except HTTPException:
        print_exc(f"Some weird HTTP error happened. More details below.")
    except KeyboardInterrupt:
        pass
    except Exception:
        print_exc(f"Something else went wrong and I'm not sure what. More details below.")


# Comandos
@bot.listen('on_ready')
async def ready():
    print(init + init2 % (list_cogs(bot)))


# doesn't work as intended, simply detatches and reattaches cogs
# TODO reattach new, fresh instances of the same cogs
@bot.command('reload')
async def reload_cogs(ctx: commands.Context):
    if not await bot.is_owner(ctx.author):
        await ctx.send("Só o proprietário pode fazer isso.")
    else:
        try:
            cogs = {x: y for x, y in dict(bot.cogs).items()}
            for cog in cogs.keys():
                await bot.remove_cog(cog)
            for cog in cogs.values():
                await bot.add_cog(cog)
            await ctx.send("Cogs atualizadas.")
        except Exception:
            await ctx.send("Algo deu errado. Consulte o log para detalhes.")


@bot.command('version')
async def show_version(ctx: commands.Context):
    await ctx.send("```" + smoothen(str(init + init2 % (list_cogs(bot))).replace('=', '').strip()) + "```")


@bot.command()
async def hello(ctx: commands.Context):
    """Hello, WARUDO!!"""
    msg = f"Hello, {ctx.author.name}"
    if isinstance(ctx.author, Member) and ctx.author.nick is not None:
        msg += f" - or should I call you {ctx.author.nick}? Either way, hello"
    msg += '.'
    await ctx.send(msg)


@bot.command()
async def argcount(ctx: commands.Context, *, arguments=''):
    arguments = arguments.split()
    await ctx.send(f"Arguments passed: {len(arguments)}\nArguments themselves: `{arguments}`\nArgument classes: {arg_types(arguments, repr=True)}")


@bot.command()
async def listroles(ctx: commands.Context):
    if isinstance(ctx.author, Member):
        await ctx.send(f"Your roles: `{[r.name for r in ctx.author.roles if r.name != '@everyone']}`")
    else:
        await ctx.send(f"There are no roles in direct messages!")


@bot.command('log')
async def tolog(ctx: commands.Context, *, arguments):
    print(arguments)
    await ctx.send("Logged message.")


@bot.command('fmt')
async def fmt(ctx: commands.Context, *, arguments):
    await ctx.send(f"```{smoothen(arguments)}```")
