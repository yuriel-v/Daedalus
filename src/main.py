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
from sqlalchemy.orm import close_all_sessions
from dao import engin, devengin
from controller import daedalus_version, daedalus_environment, daedalus_token
from model import initialize_sql

# Imports de módulos customizados
from controller.misc import Misc, split_args, arg_types, smoothen
from controller.games import Games
from controller.roger import Roger
from controller.help import DaedalusHelp
from controller.student import StudentController
from controller.scheduler import ScheduleController
from controller.subject import SubjectController

# Inicialização
bot = commands.Bot(command_prefix=['>>', 'Roger '], owner_id=int(getenv('DAEDALUS_OWNERID')))
initialize_sql(engin)
if daedalus_environment == "DEV":
    initialize_sql(devengin)

# Cogs
bot.add_cog(Misc(bot))
bot.add_cog(Games(bot))
bot.add_cog(Roger(bot))
bot.add_cog(DaedalusHelp(bot))
bot.add_cog(StudentController(bot))
bot.add_cog(SubjectController(bot))
bot.add_cog(ScheduleController(bot))

# Mensagem de inicialização
nl = '\n'
init = f"""
=========================================================================
Project Daedalus v{daedalus_version} - {daedalus_environment} environment
All systems go.
Loaded cogs:
{nl.join([f'- {x}' for x in bot.cogs.keys()])}
=========================================================================
"""


@bot.listen('on_ready')
async def ready():
    print(init)


@bot.command('version')
async def show_version(ctx):
    await ctx.send("```" + smoothen(init.split('\n')[2:-2:1]) + "```")


@bot.command()
async def hello(ctx):
    """Hello, WARUDO!!"""
    await ctx.send(f"Hello, {ctx.author.name} - or should I call you {ctx.author.nick}? Either way, hello.")


@bot.command()
async def argcount(ctx):
    arguments = split_args(ctx.message.content)
    await ctx.send(f"Arguments passed: {len(arguments)}\nArguments themselves: `{arguments}`\nArgument classes: {arg_types(arguments, repr=True)}")


@bot.command()
async def listroles(ctx):
    await ctx.send(f"Suas roles: `{[r.name for r in ctx.author.roles if r.name != '@everyone']}`")


@bot.command('log')
async def tolog(ctx):
    print(split_args(ctx.message.content, islist=False))


@bot.command('fmt')
async def fmt(ctx):
    await ctx.send(f"```{smoothen(split_args(ctx.message.content, islist=False))}```")

# Aqui é só a parte de rodar e terminar o bot.
bot.run(daedalus_token)
close_all_sessions()
print('Bye')
