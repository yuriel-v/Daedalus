# Módulo de sei lá o quê. Memes? Memes.
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Texto com ÊNFASE!!
    @commands.command()
    async def emphasize(self, ctx):
        await ctx.send(f"**{' '.join(ctx.message.content.split(' ')[1::]).upper()}!!**")

    # Texto em código
    @commands.command(name='code')
    async def text_code(self, ctx):
        reply = []
        reply.extend([
            "```\n",
            ' '.join(ctx.message.content.split(' ')[1::]),
            "\n```"
        ])
        reply = ''.join(reply)
        await ctx.send(reply)
