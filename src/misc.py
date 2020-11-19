# Módulo de sei lá o quê. Memes? Memes.
from discord.ext import commands


def split_args(arguments):
    arguments = arguments.split(' ')
    if arguments[0] == 'Roger ':
        arguments.pop(0)
    arguments.pop(0)
    return arguments


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
