# Módulo de sei lá o quê. Utilidades em geral. E memes.
import traceback
import inspect

from discord.ext import commands
from discord import Member
from os import getenv
from ruamel.yaml import YAML
from sys import getsizeof
from typing import Iterable, Union

daedalus = {
    'token': getenv("DAEDALUS_TOKEN"),
    'version': '0.787657',
    'environment': getenv("DAEDALUS_ENV").upper()
}
debug = bool(daedalus['environment'] == "DEV")
yaml = YAML(typ='safe')


def ferozes():
    async def predicate(ctx: commands.Context):
        return ctx.guild.id == 567817989806882818
    return commands.check(predicate)


def print_exc(msg=''):
    if not msg:
        msg = f'Exception caught at {inspect.stack()[1][0].f_locals["self"].__class__.__name__}.{inspect.stack()[1][0].f_code.co_name}():'
    print(f"{msg}")
    traceback.print_exc()


def nround(number: float, decimals=1):
    """Round, só que normalizado. nround(0.5) = 1"""
    number = str(number)
    # if decimal places <= decimals
    if len(number[number.index('.')::]) <= decimals + 1:
        return float(number)
    if number[-1] == '5':
        number = number[:-1:] + '6'
    return round(float(number), decimals)


def avg(items: Union[list, tuple, set]):
    """Média entre itens de um iterável."""
    return sum(items) / len(items)


def uni_avg(av1: float, aps1: float, av2: float, aps2: float, av3: float):
    """
    Médias de provas, de acordo com os padrões estabelecidos pelo Centro Universitário Carioca (UniCarioca).
    - A prova de menor nota é descartada, e a média é feita entre as duas que sobrarem.
    """
    items = [av1 + aps1, av2 + aps2, av3]
    items.remove(min(items))
    return nround(avg(items), 1)


def split_args(arguments='', prefixed=False, islist=True) -> Union[list[str], str]:
    """
    Separa os argumentos passados num comando em uma lista de strings, ou em uma string só, caso `islist = False`.
    - Use `prefixed = True` quando um comando for separado por espaço, ex.: `st cadastrar mtr nome = ['mtr', 'nome']`.

    DEPRECADO: Argumentos "keyword-only" trazem todos os argumentos de um comando, independente do prefixo.
    """
    arguments = arguments.split(' ')
    if arguments[0] == 'Roger':
        arguments.pop(0)

    # for commands like >>st ver, so 'ver' doesn't get treated as an argument
    if prefixed:
        arguments.pop(1)

    arguments.pop(0)
    if islist:
        return arguments
    else:
        return ' '.join(arguments)


def arg_types(arguments: Union[list, tuple, set], repr=False):
    """Separa argumentos passados em strings, floats ou ints."""
    arg_with_types = {0: [], 1: [], 2: []}
    for x in arguments:
        x = str(x)
        # if one dot and string without dots is numeric = float
        if x.count('.') == 1 and x.replace('.', '').isnumeric():
            arg_with_types[0].append(x)
        elif x.isnumeric():
            arg_with_types[1].append(x)
        else:
            arg_with_types[2].append(x)
    if not repr:
        return arg_with_types
    else:
        return f"{{\n  Strings: `{arg_with_types.get(2)}`\n  Integers: `{arg_with_types.get(1)}`\n  Floats: `{arg_with_types.get(0)}`\n}}"


def dprint(message: str):
    """Print para log, só quando `debug = True`."""
    if debug:
        print(message)


def smoothen(message: Iterable):
    """
    Recebe um iterável e o formata numa caixinha.
    - Feito para lidar especialmente com strings ou listas/tuplas/conjuntos/dicionários de strings.
    - Para dicionários, somente os valores, convertidos para string, são 'encaixados'.
    """
    if isinstance(message, Union[list, tuple, set].__args__):
        message = tuple([str(x) for x in message])
        dashes = len(max(message, key=len))
    elif isinstance(message, dict):
        message = tuple([str(x) for x in message.values()])
        dashes = len(max(message, key=len))
    else:
        message = tuple(str(message).split('\n'))
        dashes = len(max(message, key=len))
    dashes += 2

    formatted_message = f'\n+{"-" * dashes}+\n'
    if len(message) == 1:
        formatted_message += f'| {message[0]} |\n'
    else:
        for string in message:
            if string == len(string) * '-':
                formatted_message += '|' + '-'.ljust(dashes, '-') + '|\n'
            else:
                formatted_message += '| ' + string.ljust(dashes - 2) + ' |\n'

    formatted_message += f'+{"-" * dashes}+\n'
    return formatted_message


class Misc(commands.Cog, name='Misc'):
    def __init__(self, bot):
        self.bot = bot
        self.cmds = {
            'emphasize': self.emphasize,
            'code': self.text_code,
            'sizeof': self.sizeof_value
        }

    def ferozes():
        async def predicate(ctx: commands.Context):
            return (ctx.guild.id == ferozes) and (ctx.prefix == 'Roger ')
        return commands.check(predicate)

    @commands.Cog.listener(name='on_member_join')
    @ferozes()
    async def auto_blacksmith(self, member: Member):
        """Automaticamente torna novos membros ferreiros."""
        await member.add_roles(member.guild.get_role(583789334797352970))

    @commands.command()
    async def emphasize(self, ctx):
        """Texto com ÊNFASE!!"""
        await ctx.send(f"**{split_args(ctx.message.content, islist=False).upper()}!!**")

    @commands.command(name='code')
    async def text_code(self, ctx):
        """Texto em código."""
        reply = ''.join([
            "```\n",
            split_args(ctx.message.content, islist=False),
            "\n```"
        ])
        await ctx.send(reply)

    @commands.command('sizeof')
    async def sizeof_value(self, ctx):
        """Tamanho em bytes do valor digitado."""
        args = split_args(ctx.message.content)
        if not args:
            await ctx.send("Sintaxe: `>>sizeof numero`")
        elif not str(args[0]).isnumeric():
            await ctx.send("Sintaxe: `>>sizeof numero`")
        else:
            numba = None
            if '.' in str(args[0]):
                numba = float(args[0])
            else:
                numba = int(args[0])

            await ctx.send(f"Tamanho de `{numba}`: {getsizeof(numba)} bytes.")

    def cog_info(self, command=None) -> str:
        if command is not None and str(command).lower() in self.cmds.keys():
            reply = f'-- {str(command).lower()} --\n' + self.cmds[str(command)].help
        else:
            nl = '\n'
            reply = f"""
            Misc
            Esse módulo contém funções utilitárias ou de manutenção.\n
            Comandos incluem:
            {nl.join([f'- {x}' for x in self.cmds.keys()])}
            """
            reply = '\n'.join([x.strip() for x in reply.split('\n')]).strip()

        return reply
