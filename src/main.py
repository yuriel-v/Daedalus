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
from controller.subject import SubjectController
from dao import engin
from model import initialize_sql
# from dao.studentdao import StudentDao
# from dao.subjectdao import SubjectDao
# from dao.schedulerdao import SchedulerDao

# Imports de módulos customizados
from controller.misc import Misc, split_args, arg_types, smoothen
from controller.games import Games
from controller.student import StudentController
from controller.roger import Roger

# Por alguma causa, motivo, razão ou circunstância, se esses imports não
# forem feitos, o sistema não mapeia os objetos.
from model.student import Student
from model.subject import Subject
from model.assigned import Assigned
from model.registered import Registered

# Inicialização
daedalus_token = getenv("DAEDALUS_TOKEN")
bot = commands.Bot(command_prefix=['>>', 'Roger '])
daedalus_version = '0.4.3'
daedalus_environment = getenv("DAEDALUS_ENV")
# stdao = StudentDao()
# sbdao = SubjectDao()
# scdao = SchedulerDao()
initialize_sql(engin)

# Cogs
bot.add_cog(Misc(bot))
bot.add_cog(Games(bot))
bot.add_cog(Roger(bot))
bot.add_cog(StudentController(bot))
bot.add_cog(SubjectController(bot))


@bot.command('version')
async def show_version(ctx):
    await ctx.send(f"Project Daedalus v{daedalus_version} ({daedalus_environment})")


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
