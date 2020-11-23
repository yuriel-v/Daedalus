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

# Imports de módulos customizados
from controller.misc import Misc, split_args, arg_types
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
bot.add_cog(Misc(bot))
bot.add_cog(Games(bot))
bot.add_cog(Roger(bot))
bot.add_cog(StudentController(bot))


@bot.command()
async def hello(ctx):
    """Hello, WARUDO!!"""
    await ctx.send(f"Hello, {ctx.author.name} - or should I call you {ctx.author.nick}? Either way, hello.")


@bot.command()
async def argcount(ctx):
    """Conta quantos argumentos foram passados (separados por espaço)"""
    arguments = split_args(ctx.message.content)
    await ctx.send(f"Arguments passed: {len(arguments)}\nArguments: {arg_types(arguments, repr=True)}")


@bot.command()
async def listroles(ctx):
    """Lista as roles do usuário."""
    await ctx.send(f"Suas roles: `{[r.name for r in ctx.author.roles if r.name != '@everyone']}`")

# Aqui é só a parte de rodar e terminar o bot.
bot.run(daedalus_token)
close_all_sessions()
print('Bye')
