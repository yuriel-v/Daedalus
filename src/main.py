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
from os import getenv
from discord.ext import commands
from discord.flags import Intents
from sqlalchemy.orm import close_all_sessions
from db import engin, devengin, initialize_sql
from core.utils import daedalus_version, daedalus_environment, daedalus_token, ferozes
from core.utils import Misc, arg_types, smoothen

# Imports de módulos customizados
from cogs import Games, RogerDotNet, DaedalusHelp, StudentController, ScheduleController, SubjectController

# Inicialização
bot = commands.Bot(
    command_prefix=['>>', 'Roger '],
    owner_id=int(getenv('DAEDALUS_OWNERID')),
    intents=Intents(messages=True, guilds=True, members=True, presences=True)
)
initialize_sql(engin)
if daedalus_environment == "DEV":
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
Project Daedalus v{daedalus_version} - {daedalus_environment} environment
All systems go."""
init2 = """
Loaded cogs:
%s
========================================================================="""


@bot.listen('on_ready')
async def ready():
    print(init + init2 % (list_cogs()))


def list_cogs(guild_id: int = None):
    if guild_id is None:
        coglist = (f'- {x}' for x in bot.cogs.keys())
    else:
        coglist = (
            f'- {cogname}' for cogname, cog in bot.cogs.items()
            if 'ferozes' not in dir(cog) or ('ferozes' in dir(cog) and guild_id == ferozes)
        )
    return '\n'.join(coglist)


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
    string = str(init + init2 % (list_cogs(ctx.guild.id))).split('\n')[2:-1:]
    await ctx.send("```" + smoothen(string) + "```")


@bot.command()
async def hello(ctx):
    """Hello, WARUDO!!"""
    await ctx.send(f"Hello, {ctx.author.name} - or should I call you {ctx.author.nick}? Either way, hello.")


@bot.command()
async def argcount(ctx, *, arguments: str):
    arguments = arguments.split()
    await ctx.send(f"Arguments passed: {len(arguments)}\nArguments themselves: `{arguments}`\nArgument classes: {arg_types(arguments, repr=True)}")


@bot.command()
async def listroles(ctx):
    await ctx.send(f"Suas roles: `{[r.name for r in ctx.author.roles if r.name != '@everyone']}`")


@bot.command('log')
async def tolog(ctx, *, arguments):
    print(arguments)


@bot.command('fmt')
async def fmt(ctx, *, arguments):
    await ctx.send(f"```{smoothen(arguments)}```")

# Aqui é só a parte de rodar e terminar o bot.
bot.run(daedalus_token)
close_all_sessions()
print('Bye')
