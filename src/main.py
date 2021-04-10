"""
Core para o bot Daedalus.

Comandos aqui são somente para fins de teste. Comandos mais sofisticados
deverão ser adicionados a um "cog", um conjunto de comandos separado e adicionado
ali embaixo com o comando "bot.add_cog(Cogname(bot))".
--
Autor: Leonardo Valim

Licenciado sob a MIT License.
Ou seja, faça o que bem entender, eu estou pouco me lixando.
Contanto que me dê o crédito, claro.
"""

# Essenciais
import asyncio

from os import getenv
from discord.errors import ConnectionClosed, GatewayNotFound, HTTPException, LoginFailure
from discord.ext import commands
from discord.flags import Intents
from sqlalchemy.orm import close_all_sessions
from db import engin, devengin, initialize_sql
from core.utils import Misc, arg_types, smoothen, print_exc, daedalus

# Imports de módulos customizados
from cogs import *

# Inicialização
bot = commands.Bot(
    command_prefix=['>>', 'Roger '],
    owner_id=int(getenv('DAEDALUS_OWNERID')),
    intents=Intents(messages=True, guilds=True, members=True, presences=True),
    help_command=None
)
initialize_sql(engin)
if daedalus['environment'] == "DEV" and devengin is not None:
    initialize_sql(devengin)

# Cogs
bot.add_cog(Misc(bot))
bot.add_cog(Games(bot))
bot.add_cog(RogerDotNet(bot))
bot.add_cog(DaedalusHelp(bot))
bot.add_cog(StudentController(bot))
bot.add_cog(SubjectController(bot))
bot.add_cog(ScheduleController(bot))

# Mensagem de inicialização
init = f"""
=========================================================================
Project Daedalus v{daedalus['version']} - {daedalus['environment']} environment
All systems go."""
init2 = """
Loaded cogs:
%s
========================================================================="""


@bot.listen('on_ready')
async def ready():
    print(init + init2 % (list_cogs()))


def list_cogs(guild_id: int = None):
    # if guild_id is None:
    #     coglist = (f'- {x}' for x in bot.cogs.keys())
    # else:
    #     coglist = (
    #         f'- {cogname}' for cogname, cog in bot.cogs.items()
    #         if 'ferozes' not in dir(cog) or ('ferozes' in dir(cog) and guild_id == ferozes)
    #     )
    return '\n'.join(f'- {cogname}' for cogname in bot.cogs.keys())


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
                bot.remove_cog(cog)
            for cog in cogs.values():
                bot.add_cog(cog)
            await ctx.send("Cogs atualizadas.")
        except Exception:
            await ctx.send("Algo deu errado. Consulte o log para detalhes.")


@bot.command('version')
async def show_version(ctx: commands.Context):
    await ctx.send("```" + smoothen(str(init + init2 % (list_cogs())).replace('=', '').strip()) + "```")


@bot.command()
async def hello(ctx: commands.Context):
    """Hello, WARUDO!!"""
    await ctx.send(f"Hello, {ctx.author.name} - or should I call you {ctx.author.nick}? Either way, hello.")


@bot.command()
async def argcount(ctx: commands.Context, *, arguments=''):
    arguments = arguments.split()
    await ctx.send(f"Arguments passed: {len(arguments)}\nArguments themselves: `{arguments}`\nArgument classes: {arg_types(arguments, repr=True)}")


@bot.command()
async def listroles(ctx: commands.Context):
    await ctx.send(f"Suas roles: `{[r.name for r in ctx.author.roles if r.name != '@everyone']}`")


@bot.command('log')
async def tolog(ctx: commands.Context, *, arguments):
    print(arguments)
    ctx.send("Logged message.")


@bot.command('fmt')
async def fmt(ctx: commands.Context, *, arguments):
    await ctx.send(f"```{smoothen(arguments)}```")


# Loop principal
def main(*args, **kwargs):
    global bot
    loop = asyncio.get_event_loop()

    async def run_bot():
        try:
            await bot.start(*args, **kwargs)
        finally:
            if not bot.is_closed():
                bot.close()

    asyncio.ensure_future(run_bot(), loop=loop)
    try:
        loop.run_forever()
    except GatewayNotFound as e:
        print_exc(f"Gateway wasn't found, likely a Discord API error.", e)
    except ConnectionClosed as e:
        print_exc(f"Connection closed by Discord.", e)
    except LoginFailure as e:
        print_exc(f"You gave me the wrong credentials, so Discord didn't let me log in.", e)
    except HTTPException as e:
        print_exc(f"Some weird HTTP error happened. More details below.", e)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print_exc(f"Something else went wrong and I'm not sure what. More details below.", e)


# Aqui é só a parte de rodar e terminar o bot.
if __name__ == "__main__":
    # bot.run(daedalus_token)
    main(daedalus['token'])
    close_all_sessions()
    print('Bye')
