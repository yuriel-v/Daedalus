# Controlador para registro de matrículas em matérias e suas atividades.
from controller.misc import split_args, smoothen
from controller.ferozes import ferozes
from discord import Message
from discord.ext import commands
from dao.unimanager.schedulerdao import SchedulerDao
from dao.unimanager.studentdao import StudentDao
from dao.unimanager.subjectdao import SubjectDao
from model.unimanager.student import Student
from model.unimanager.subject import Subject


class ScheduleController(commands.Cog, name='Schedule Controller: sc'):
    def __init__(self, bot):
        self.bot = bot
        self.stdao = StudentDao()
        self.sbdao = SubjectDao()
        self.scdao = SchedulerDao()
        self.reg_students = self.stdao.find_all_ids()
        self.stdao.sclear()

        self.cmds = {
            'matricular': self.enroll,
            'trancar': self.lock_enrollment,
            'nota': self.update_grade,
            'status': self.update_status,
            'sts': self.update_status
        }

    def ferozes():
        async def predicate(ctx):
            return ctx.guild.id == ferozes
        return commands.check(predicate)

    async def cog_after_invoke(self, ctx):
        self.stdao.sclear()
        self.sbdao.sclear()
        self.scdao.sclear()

    @commands.command('sc')
    @ferozes()
    async def select_command(self, ctx: commands.Context):
        """
        Comando mestre para o cog Schedule Controller.
        - P.S. Somente estudantes cadastrados têm acesso a esse cog!
        """
        command = next(iter(split_args(ctx.message.content)), "").lower()
        if not command:
            await ctx.send("Sintaxe: `>>sc comando argumentos`")
        else:
            registered = True
            if ctx.author.id not in self.reg_students:
                self.reg_students = self.stdao.find_all_ids()
                registered = ctx.author.id in self.reg_students
            if not registered:
                await ctx.send("Você não está cadastrado. Use o comando `>>st cadastrar` para isso.")
            else:
                if command in self.cmds.keys():
                    await self.cmds[command](ctx, self.stdao.find_by_discord_id(ctx.author.id))
                else:
                    await ctx.send("Comando inválido. Sintaxe: `>>sc comando argumentos`")

    async def enroll(self, ctx: commands.Context, student: Student):
        """
        Matricula um estudante numa matéria.
        - Se essa matéria for uma matéria trancada, ela é reativada.
        - Se essa matéria for uma matéria antiga, ela é atualizada e todos os seus trabalhos redefinidos para o padrão.
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        if not arguments:
            await ctx.send("Sintaxe inválida. Exemplo: `>>sc matricular mt1 mt2 ...`")
        else:
            msg: Message = await ctx.send('Efetuando matrícula...')
            try:
                arguments = list(filter(lambda x: len(x) == 3, arguments))
                if len(arguments) > 8:
                    arguments = arguments[0:7:1]  # up to 8 at once only, uni rules
                subjects = self.sbdao.find_by_code(arguments)
                subjects = {x.code: x for x in subjects if x is not None}
                subj_names = tuple([f"-> {x}: {y.fullname}" for x, y in subjects.items()])

                if not subjects:
                    await msg.edit(content="Matéria(s) inexistente(s).\nUse o comando `>>mt todas` ou `>>mt buscar` para verificar o código da(s) matéria(s) desejada(s).")
                else:
                    self.stdao.expunge(student)
                    for subj in subjects.values():
                        self.sbdao.expunge(subj)
                    res = self.scdao.register(student=student, subjects=subjects)
                    if res == 0:
                        await msg.edit(content=f"Matrícula registrada nas matérias a seguir:\n```{smoothen(subj_names)}```")
                    else:
                        msg.edit(content="Algo deu errado. Consulte o log para mais detalhes.")
            except Exception as e:
                print(f'Exception caught at enrolling student: {e}\n Stack trace: {e.__traceback__}')
                await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    async def update_grade(self, ctx: commands.Context, student: Student):
        """
        Atualiza a nota de uma matéria em específico.
        - O comando rejeita trabalhos pendentes - somente trabalhos com status `OK` são alterados!
        - Sintaxe: `sc nota codigo trabalho novanota antigo?` -> antigo é opcional.
          - Se `antigo = 'sim'` então o comando altera a nota de uma matéria de um semestre anterior.
          - Senão, o comando só vai alterar notas de matérias do semestre atual.
          - Exemplo: `sc nota AL1 AV1 9.5 sim`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        invalid_syntax = "Sintaxe: `>>sc nota codigo trabalho novanota antigo?` - 'antigo' é opcional: sim ou não.\nExemplo: `>>sc nota AL1 AV1 9.5`"
        invalid_syntax += "\nSe tentar mudar a nota para uma matéria de um semestre anterior, terá que especificar 'sim' em antigo."
        grade_too_high = "A nota especificada é mais alta que o permitido:"
        if len(arguments) < 3:
            await ctx.send(invalid_syntax)
        else:
            exam_types = ('AV1', 'APS1', 'AV2', 'APS2', 'AV3')
            max_grades = (7.0, 3.0, 8.0, 2.0, 10.0)
            msg: Message = await ctx.send('Atualizando nota...')
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
                    await msg.edit(content=f"{grade_too_high} `{arguments[2]} > {max_grades[arguments[1] - 1]}`")
                else:
                    await msg.edit(content=invalid_syntax)
                return

            try:
                sbj: Subject = self.sbdao.find_one_by_code(arguments[0])
                res = self.scdao.update(student=student, subject=sbj.id, exam_type=arguments[1], newval=arguments[2], current=arguments[3], grade=True)
                responses = (
                    f"Nota alterada: ```{smoothen(f'{sbj.fullname} | {exam_types[arguments[1] - 1]}: {round(arguments[2], 1)}')}```",
                    "Algo deu errado. Consulte o log para mais detalhes.",
                    invalid_syntax,
                    "O trabalho para a matéria especificada não foi encontrado.",
                    "Você não pode alterar a nota para um trabalho que não foi entregue ainda."
                )
                if res not in range(len(responses)):
                    await msg.edit(content=responses[1])
                else:
                    await msg.edit(content=responses[res])
            except Exception as e:
                print(f'Exception caught at updating grade: {e}\n Stack trace: {e.__traceback__}')
                await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    async def update_status(self, ctx: commands.Context, student: Student):
        """
        Altera o status de um trabalho. Também reconhecido como o comando `sts`.
        - Sintaxe: `sc status codigo_materia trabalho novostatus`; onde `novostatus` pode ser:
          - OK;
          - PND (pendente);
          - EPN (envio/entrega pendente).
          - Exemplo: `sc status AL1 AV1 OK`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        invalid_syntax = "Sintaxe: `>>sc status codigo trabalho novostatus`.\nExemplo: `>>sc status AL1 AV1 OK`"
        if len(arguments) < 3:
            await ctx.send(invalid_syntax)
        else:
            msg: Message = await ctx.send('Atualizando status...')
            try:
                statuses = ('OK', 'EPN', 'PND')
                exam_types = ('AV1', 'APS1', 'AV2', 'APS2', 'AV3')
                arguments[0] = arguments[0].upper()
                arguments[1] = exam_types.index(arguments[1].upper()) + 1
                if len(arguments) >= 4:
                    if ' '.join(arguments[2:4:]).lower() in ('envio pendente', 'entrega pendente'):
                        arguments[2] = 2
                if not isinstance(arguments[2], int):
                    if arguments[2] == 'pendente':
                        arguments[2] = 3
                    else:
                        arguments[2] = statuses.index(arguments[2].upper()) + 1
            except Exception:
                await msg.edit(content=invalid_syntax)
                return

            try:
                sbj: Subject = self.sbdao.find_one_by_code(arguments[0])
                print(f'newval = {arguments[2]}')
                res = self.scdao.update(student=student, subject=sbj.id, exam_type=arguments[1], newval=arguments[2], grade=False)
                responses = (
                    f"Status alterado: ```{smoothen(f'{sbj.fullname} | {exam_types[arguments[1] - 1]}: {statuses[arguments[2] - 1]}')}```",
                    "Algo deu errado. Consulte o log para mais detalhes.",
                    invalid_syntax,
                    "O trabalho para a matéria especificada não foi encontrado."
                )
                if res not in range(len(responses)):
                    await msg.edit(content=responses[1])
                else:
                    await msg.edit(content=responses[res])
            except Exception as e:
                print(f'Exception caught at updating status: {e}\n Stack trace: {e.__traceback__}')
                await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    async def lock_enrollment(self, ctx: commands.Context, student: Student):
        """
        Tranca uma, várias ou todas as matérias matriculadas pelo estudante que chamar o comando.
        - Sintaxe: `sc trancar mt1 mt2 ...`
          - Exemplo: `sc trancar POO CGR TCP`
          - `mt1`, `mt2` etc. são códigos de matérias a ser trancadas. Case insensitive, mas precisam necessariamente ter comprimento 3.
          - Caso `mt1 = 'todas'`, todas as matérias matriculadas são trancadas.
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        invalid_syntax = "Sintaxe: `>>sc trancar mt1 mt2 ...` - caso `mt1 = 'todas'`, todas as matérias ativas do estudante serão trancadas."
        if not arguments:
            await ctx.send(invalid_syntax)
        else:
            msg: Message = await ctx.send('Trancando matrículas...')
            try:
                subjects = None
                if arguments[0] == 'todas':
                    lock_all = True
                    ret = self.scdao.lock(student, [], True)
                else:
                    lock_all = False
                    subjects = {x.code: x.fullname for x in self.sbdao.find_by_code(arguments)}
                    print(f"Subjects: {subjects}")
                    ret = self.scdao.lock(student, subjects.keys())

                statuses = (
                    "Você trancou todas as suas matrículas.",
                    "Algo deu errado. Consulte o log para mais detalhes.",
                    invalid_syntax
                )
                if not lock_all and ret == 0:
                    await msg.edit(content=f"Matrículas trancadas com sucesso: ```{smoothen([f'-> {x}' for x in subjects.values()])}```")
                else:
                    await msg.edit(content=statuses[ret])
            except Exception as e:
                print(f'Exception caught during enrollment locking: {e}\n Stack trace: {e.__traceback__}')
                await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    def cog_info(self, command=None) -> str:
        if command is not None and str(command).lower() in self.cmds.keys():
            reply = f'-- sc {str(command).lower()} --\n' + self.cmds[str(command)].__doc__
        else:
            nl = '\n'
            reply = f"""
            sc: Schedule Controller
            Este módulo foi criado para auxiliar na matrícula e controle de status/notas de provas matriculadas.
            Somente usuários matriculados pelo módulo 'st' podem utilizar as funções desse módulo!\n
            Comandos incluem:
            {nl.join([f'- {x}' for x in self.cmds.keys()])}
            """

        return '\n'.join([x.strip() for x in reply.split('\n')]).strip()
