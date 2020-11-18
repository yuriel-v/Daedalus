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
import sqlalchemy as sqla
import discord

# Imports parciais de essenciais
from discord.ext import commands
from secret import daedalus_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Imports de módulos customizados
from misc import Misc
from games import Games

# Inicialização
engine = create_engine('sqlite:///database/data.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

bot = commands.Bot(command_prefix=['>>', 'Roger '])
bot.add_cog(Misc(bot))
bot.add_cog(Games(bot))


# Hello, WARUDO!!
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}.")


# Aqui é só a parte de rodar e terminar o bot.
bot.run(daedalus_token)
print('Bye')
