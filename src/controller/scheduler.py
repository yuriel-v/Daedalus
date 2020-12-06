# Controlador para registro de matrículas em matérias e suas atividades.

from controller.misc import split_args, dprint, smoothen
from controller import stdao, sbdao  # , scdao
from discord.ext import commands
from model.student import Student


class ScheduleController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('sc')
    async def select_command(self, ctx):
        command = next(iter(split_args(ctx.message.content)), "").lower()
        if not command:
            await ctx.send("Sintaxe: `>>sc comando argumentos`")
        else:
            student = stdao.find_by_discord_id(ctx.author.id)
            if student is None:
                await ctx.send("Você não está cadastrado. Use o comando `>>st cadastrar` para isso.")
            elif command == "matricular":
                await self.sign_up(ctx, student)
            elif command == "trancar":
                pass
            else:
                await ctx.send("Comando inválido. Sintaxe: `>>sc comando argumentos`")

    async def sign_up(self, ctx, student: Student):
        pass
        # arguments = split_args(ctx.message.content, prefixed=True)
        # if not arguments:
        #     await ctx.send("Sintaxe inválida. Exemplo: `>>sc matricular mt1 mt2 ...`")
        # else:
        #     arguments = list(filter(lambda x: len(x) == 3, arguments))
        #     if len(arguments) > 8:
        #         arguments = arguments[0:7:1]  # up to 8 at once only, uni rules
        #     subjects = sbdao.find_by_code(arguments)
        #     subjects = {x for x in subjects if x is not None}
        #     subj_names = [f"-> {str(x.code)}: {str(x.fullname)}" for x in subjects]

        #     if not subjects:
        #         await ctx.send("Matéria(s) inexistente(s).\nUse o comando `>>mt todas` ou `>>mt buscar` para verificar o código da(s) matéria(s) desejada(s).")
        #     else:
        #         stdao.expunge(student)
        #         for subj in subjects:
        #             sbdao.expunge(subj)
        #         res = scdao.register(student=student, subjects=subjects)
        #         if res == 0:
        #             await ctx.send(f"Matrícula registrada nas matérias a seguir:\n```{smoothen(subj_names)}```")
        #         else:
        #             await ctx.send("Algo deu errado. Consulte o log para mais detalhes.")
