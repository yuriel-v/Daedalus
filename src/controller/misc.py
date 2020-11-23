# Módulo de sei lá o quê. Utilidades em geral. E memes.
from typing import Iterable
from discord.ext import commands
from sys import getsizeof

debug = True


def split_args(arguments):
    arguments = arguments.split(' ')
    if arguments[0] == 'Roger ':
        arguments.pop(0)
    arguments.pop(0)
    return arguments


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


def dprint(message):
    if debug:
        print(message)


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Texto com ÊNFASE!!
    @commands.command()
    async def emphasize(self, ctx):
        start = 1
        if ctx.prefix == 'Roger ':
            start = 2
        await ctx.send(f"**{' '.join(ctx.message.content.split(' ')[start::]).upper()}!!**")

    # Texto em código
    @commands.command(name='code')
    async def text_code(self, ctx):
        start = 1
        if ctx.prefix == 'Roger ':
            start = 2
        reply = []
        reply.extend([
            "```\n",
            ' '.join(ctx.message.content.split(' ')[start::]),
            "\n```"
        ])
        reply = ''.join(reply)
        await ctx.send(reply)

    # Tamanho em bytes do valor digitado
    @commands.command('sizeof')
    async def sizeof_value(self, ctx):
        args = split_args(ctx.message.content)
        if len(args) == 0:
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
