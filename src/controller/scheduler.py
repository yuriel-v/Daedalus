# Controlador para registro de matrículas em matérias e suas atividades.

from controller.misc import split_args, dprint, smoothen
from dao import stdao, sbdao, scdao
from discord.ext import commands


class ScheduleController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('sc')
    async def select_command(self, ctx):
        command = next(iter(split_args(ctx.message.content)), "").lower()
        if not command:
            await ctx.send("Sintaxe: `>>sc comando argumentos`")
        elif not stdao.find(ctx.author.id, exists=True):
            await ctx.send("Você não está cadastrado. Use o comando `>>st cadastrar` para isso.")
        else:
            if command == "matricular":
                pass
            elif command == "trancar":
                pass
            else:
                await ctx.send("Comando inválido. Sintaxe: `>>sc comando argumentos`")
