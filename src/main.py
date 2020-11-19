"""
Controller para o bot Daedalus.

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
import discord

# Imports parciais de essenciais
from discord.ext import commands
from secret import daedalus_token

# Imports de módulos customizados
from misc import Misc, split_args
from games import Games
from uni_reminder import UniReminder

# Inicialização
bot = commands.Bot(command_prefix=['>>', 'Roger '])
bot.add_cog(Misc(bot))
bot.add_cog(Games(bot))
bot.add_cog(UniReminder(bot))


# Hello, WARUDO!!
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}.")


# Contar quantos argumentos foram passados
@bot.command()
async def argcount(ctx):
    arguments = split_args(ctx.message.content)
    await ctx.send(f"Arguments passed: {len(arguments)}\nArguments: {arguments}")

# Aqui é só a parte de rodar e terminar o bot.
bot.run(daedalus_token)
print('Bye')
