# Controlador para registro de matrículas em matérias e suas atividades.

from controller.misc import split_args, dprint, smoothen
from controller import stdao, sbdao, scdao
from discord.ext import commands
from model.student import Student
from model.subject import Subject


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
            elif command == "nota":
                await self.update_grade(ctx, student)
            elif command == "sts" or command == "status":
                await self.update_status(ctx, student)
            else:
                await ctx.send("Comando inválido. Sintaxe: `>>sc comando argumentos`")

    async def sign_up(self, ctx: commands.Context, student: Student):
        arguments = split_args(ctx.message.content, prefixed=True)
        if not arguments:
            await ctx.send("Sintaxe inválida. Exemplo: `>>sc matricular mt1 mt2 ...`")
        else:
            arguments = list(filter(lambda x: len(x) == 3, arguments))
            if len(arguments) > 8:
                arguments = arguments[0:7:1]  # up to 8 at once only, uni rules
            subjects = sbdao.find_by_code(arguments)
            subjects = {x for x in subjects if x is not None}
            subj_names = [f"-> {str(x.code)}: {str(x.fullname)}" for x in subjects]

            if not subjects:
                await ctx.send("Matéria(s) inexistente(s).\nUse o comando `>>mt todas` ou `>>mt buscar` para verificar o código da(s) matéria(s) desejada(s).")
            else:
                stdao.expunge(student)
                for subj in subjects:
                    sbdao.expunge(subj)
                res = scdao.register(student=student, subjects=subjects)
                if res == 0:
                    await ctx.send(f"Matrícula registrada nas matérias a seguir:\n```{smoothen(subj_names)}```")
                else:
                    await ctx.send("Algo deu errado. Consulte o log para mais detalhes.")

    async def update_grade(self, ctx: commands.Context, student: Student):
        arguments = split_args(ctx.message.content, prefixed=True)
        invalid_syntax = "Sintaxe: `>>sc nota codigo trabalho novanota antigo?` - 'antigo' é opcional: sim ou não.\nExemplo: `>>sc nota AL1 AV1 9.5`"
        invalid_syntax += "\nSe tentar mudar a nota para uma matéria de um semestre anterior, terá que especificar 'sim' em antigo."
        grade_too_high = "A nota especificada é mais alta que o permitido:"
        if len(arguments) < 3:
            await ctx.send(invalid_syntax)
        else:
            exam_types = ('AV1', 'APS1', 'AV2', 'APS2', 'AV3')
            max_grades = (7.0, 3.0, 8.0, 2.0, 10.0)
            try:
                arguments[0] = arguments[0].upper()
                arguments[1] = exam_types.index(arguments[1].upper()) + 1

                # grade constraints
                arguments[2] = abs(float(arguments[2]))
                if arguments[2] > max_grades[arguments[1] - 1]:
                    raise SyntaxError("Grade is too high")

                if len(arguments) > 4:
                    arguments = arguments[0:3:1]
                if len(arguments) == 4:
                    arguments[3] == bool(arguments[3].lower() == 'sim')
                else:
                    arguments.append(False)
                if len(arguments[0]) != 3:
                    raise SyntaxError("Subject code length is not 3")
            except Exception as e:
                if 'Grade' in str(e) and isinstance(e, SyntaxError):
                    await ctx.send(f"{grade_too_high} `{arguments[2]} > {max_grades[arguments[1] - 1]}`")
                else:
                    await ctx.send(invalid_syntax)
                return

            sbj: Subject = sbdao.find_one_by_code(arguments[0])
            res = scdao.update(student=student, subject=sbj, exam_type=arguments[1], newval=arguments[2], current=arguments[3], grade=True)
            responses = (
                f"Nota alterada: ```{smoothen(f'{sbj.fullname} | {exam_types[arguments[1] - 1]}: {round(arguments[2], 1)}')}```",
                "Algo deu errado. Consulte o log para mais detalhes.",
                invalid_syntax,
                "O trabalho para a matéria especificada não foi encontrado.",
                "Você não pode alterar a nota para um trabalho que não foi entregue ainda."
            )
            if res not in range(len(responses)):
                await ctx.send(responses[1])
            else:
                await ctx.send(responses[res])

    async def update_status(self, ctx: commands.Context, student: Student):
        arguments = split_args(ctx.message.content, prefixed=True)
        invalid_syntax = "Sintaxe: `>>sc status codigo trabalho novostatus`.\nExemplo: `>>sc status AL1 AV1 OK`"
        if len(arguments) < 3:
            await ctx.send(invalid_syntax)
        else:
            try:
                statuses = ('OK', 'EPN', 'PND')
                exam_types = ('AV1', 'APS1', 'AV2', 'APS2', 'AV3')
                arguments[0] = arguments[0].upper()
                arguments[1] = exam_types.index(arguments[1].upper()) + 1
                if len(arguments) >= 4:
                    if ' '.join(arguments[2:4:]).lower() == 'envio pendente':
                        arguments[2] = 2
                if not isinstance(arguments[2], int):
                    if arguments[2] == 'pendente':
                        arguments[2] = 3
                    else:
                        arguments[2] = statuses.index(arguments[2].upper()) + 1
            except Exception:
                await ctx.send(invalid_syntax)
                return

            sbj: Subject = sbdao.find_one_by_code(arguments[0])
            res = scdao.update(student=student, subject=sbj, exam_type=arguments[1], newval=arguments[2], grade=False)
            responses = (
                f"Status alterado: ```{smoothen(f'{sbj.fullname} | {exam_types[arguments[1] - 1]}: {statuses[arguments[2] - 1]}')}```",
                "Algo deu errado. Consulte o log para mais detalhes.",
                invalid_syntax,
                "O trabalho para a matéria especificada não foi encontrado."
            )
            if res not in range(len(responses)):
                await ctx.send(responses[1])
            else:
                await ctx.send(responses[res])
