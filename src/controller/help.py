# Módulo de ajuda aos comandos do bot.
from discord.ext import commands
from controller.misc import smoothen, split_args
from controller import daedalus_environment, daedalus_version


default_message = f"""Projeto Daedalus, versão {daedalus_version}, ambiente {daedalus_environment}.
---
Daedalus é um bot feito em Python 3.9.0 utilizando em grande parte os módulos
discord.py e SQLAlchemy.

O propósito desse bot é servir de memes e sei lá o quê, mas mais importante é
servir como uma espécie de agenda e/ou catálogo de matérias e provas para
estudantes de Ciência da Computação do Centro Universitário Carioca (UniCarioca).

Para ajuda em um comando específico, digite `>>dhelp comando`.
Esse bot também conta com o módulo de ajuda padrão do discord.py!
  -> Para utilizá-lo, digite `>>help comando` ou `>>help categoria`.
"""


class DaedalusHelp(commands.Cog, name='Daedalus Help'):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command('dhelp')
    async def cmd_parser(self, ctx: commands.Context):
        arguments = split_args(ctx.message.content)
        global default_message
        msg = default_message
        if not arguments or arguments[0].title() in self.bot.cogs.keys():
            pass
        else:
            for cogname, cog in self.bot.cogs.items():
                if arguments[0].lower() == cogname.lower() or (str(cogname).lower().endswith(f': {arguments[0].lower()}')):
                    try:
                        if arguments[1].lower() in cog.cmds.keys():
                            msg = cog.cog_info(arguments[1].lower())
                        else:
                            msg = cog.cog_info()
                    except IndexError:
                        msg = cog.cog_info()
                    finally:
                        break
        await ctx.send('Ajuda: ```%s```' % (msg.replace('`', "'")))
