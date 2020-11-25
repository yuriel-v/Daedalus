# Módulo de controle de matérias.
# Nota: Somente o proprietário do bot pode invocar esses comandos!
from os import getenv
from controller.misc import split_args, dprint
from discord.ext import commands
from dao.subjectdao import SubjectDao


class SubjectController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sbdao = SubjectDao()

    @commands.command('mt')
    async def subject_controller(self, ctx: commands.Context):
        if ctx.author.id != getenv("DAEDALUS_OWNERID"):
            await ctx.send("Só o proprietário do bot pode utilizar os comandos iniciados por `mt`.")
