# Módulo de sei lá o quê. Utilidades em geral. E memes.
from typing import Iterable, Union
from discord.ext import commands
from sys import getsizeof

debug = True


def split_args(arguments: str, prefixed=False, islist=True):
    arguments = arguments.split(' ')
    if arguments[0] == 'Roger':
        arguments.pop(0)

    if (arguments[0].endswith('st') or arguments[0].endswith('mt')) and prefixed:
        arguments.pop(1)

    arguments.pop(0)
    if islist:
        return arguments
    else:
        return ' '.join(arguments)


def arg_types(arguments: Iterable, repr=False):
    arg_with_types = {0: [], 1: [], 2: []}
    for x in arguments:
        x = str(x)
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
    if debug:
        print(message)


def smoothen(message: Iterable, complement=False):
    if isinstance(message, Union[list, tuple, set].__args__):
        message = [str(x) for x in message]
        dashes = len(max(message, key=len))
    elif isinstance(message, dict):
        message = [str(x) for x in message.values()]
        dashes = len(max(message, key=len))
    else:
        message = str(message)
        dashes = len(message)
    dashes += 2

    formatted_message = (lambda: f'\n+{"-" * dashes}+\n' if not complement else "")()
    if isinstance(message, str):
        formatted_message += f'| {message} |\n'
    else:
        for string in message:
            formatted_message += f'| {string}{" " * (dashes - 1 - len(string))}|\n'

    formatted_message += f'\n+{"-" * dashes}+\n'
    return formatted_message


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Texto com ÊNFASE!!
    @commands.command()
    async def emphasize(self, ctx):
        await ctx.send(f"**{split_args(ctx.message.content, islist=False).upper()}!!**")

    # Texto em código
    @commands.command(name='code')
    async def text_code(self, ctx):
        reply = ''.join([
            "```\n",
            split_args(ctx.message.content, islist=False),
            "\n```"
        ])
        await ctx.send(reply)

    # Tamanho em bytes do valor digitado
    @commands.command('sizeof')
    async def sizeof_value(self, ctx):
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
