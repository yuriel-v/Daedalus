# Módulo de ajuda aos comandos do bot.
from discord.ext import commands
from controller.misc import split_args
from controller import daedalus_environment, daedalus_version


default_message = f"""Projeto Daedalus, versão {daedalus_version}, ambiente {daedalus_environment}.
---
Daedalus é um bot feito em Python 3.9.0 utilizando em grande parte os módulos
discord.py e SQLAlchemy.

O propósito desse bot é servir de memes e sei lá o que, mas mais importante é
servir como uma espécie de agenda e/ou catálogo de matérias e provas para
estudantes de Ciência da Computação do Centro Universitário Carioca (UniCarioca).

Para ajuda em um comando ou cog específico, digite `>>dhelp comando|cog`.
Esse bot também conta com o módulo de ajuda padrão do discord.py!
  -> Para utilizá-lo, digite `>>help comando` ou `>>help categoria`.
"""


class DaedalusHelp(commands.Cog, name='Daedalus Help'):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command('dhelp')
    async def cmd_parser(self, ctx: commands.Context):
        """Comando de ajuda específico para o bot Daedalus."""
        arguments = split_args(ctx.message.content)
        nl = '\n'
        global default_message
        msg = default_message + f'\nCogs ativos:\n{nl.join([f"- {x}" for x in self.bot.cogs.keys()])}'
        msg += "\n\nP.S. Se você pediu ajuda para algum comando ou cog em específico, ele não foi encontrado."
        if not arguments:
            pass
        else:
            found = False
            # check if first word is a cog
            for cogname, cog in self.bot.cogs.items():
                if arguments[0].lower() == cogname.lower() or (str(cogname).lower().endswith(f': {arguments[0].lower()}')):
                    found = True
                    try:
                        if arguments[1].lower() in cog.cmds.keys():
                            msg = cog.cog_info(arguments[1].lower())
                        else:
                            msg = cog.cog_info()
                    except IndexError:
                        msg = cog.cog_info()
                    except Exception as e:
                        print(f'Uncaught exception: {e}')
                    finally:
                        break

            # check if the first word is a command instead
            if not found:
                for cmd in self.bot.commands:
                    cmd: commands.Command
                    if str(cmd.name).lower() == arguments[0].lower():
                        msg = cmd.help
                        break
        await ctx.send('Ajuda: ```%s```' % (msg.replace('`', "'")))
