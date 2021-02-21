# Controlador para registro de matrículas em matérias e suas atividades.
from core.utils import print_exc, smoothen, nround
from db.dao import *
from db.model import Student
from discord import Message
from discord.ext import commands
registered_students = None


def refresh_student_registry(dao: StudentDao, disposable_dao=False):
    if not dao.active():
        dao.create()

    global registered_students
    registered_students = dao.find_all_ids()

    if disposable_dao:
        dao.destroy()


class ScheduleController(commands.Cog, name='Schedule Controller: sc'):
    def __init__(self, bot):
        self.bot = bot
        self.stdao = StudentDao()
        self.scdao = SchedulerDao()
        refresh_student_registry(self.stdao)
        self.cmds = {
            'matricular': self.enroll,
            'trancar': self.lock_enrollment,
            'nota': self.update_grade,
            'status': self.update_status
        }

    def cadastrado():
        async def predicate(ctx: commands.Context):
            global registered_students
            if ctx.author.id not in registered_students:
                refresh_student_registry(StudentDao(), True)
            return ctx.author.id in registered_students
        return commands.check(predicate)

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Você não está cadastrado. Use o comando `>>st cadastrar` para usar os subcomandos de `sc`.")
        else:
            print_exc(f"Exception raised:", error)

    async def cog_after_invoke(self, ctx):
        # no, i don't think i will.

        # if self.stdao.active():
        #     self.stdao.destroy()
        # if self.scdao.active():
        #     self.scdao.destroy()

        # if another thread is using the dao while an earlier one finishes,
        # the dao gets destroyed before the last thread can do its thing.
        pass

    @commands.group(name='sc')
    @cadastrado()
    async def scheduler(self, ctx: commands.Context, *, arguments: str):
        """
        Comando mestre para o cog Schedule Controller.
        - P.S. Somente estudantes cadastrados têm acesso a esse cog!
        """
        if ctx.invoked_subcommand is None:
            if not arguments:
                await ctx.send("Sintaxe: `>>sc comando argumentos`")
            else:
                await ctx.send("Comando inválido. Sintaxe: `>>sc comando argumentos`")

    @scheduler.command(name='matricular')
    async def enroll(self, ctx: commands.Context, *, arguments: str):
        """
        Matricula um estudante numa matéria.
        - Se essa matéria for uma matéria trancada, ela é reativada.
        - Se essa matéria for uma matéria antiga, ela é atualizada e todos os seus trabalhos redefinidos para o padrão.
        """
        arguments: list = arguments.split()
        if not arguments:
            await ctx.send("Sintaxe inválida. Exemplo: `>>sc matricular mt1 mt2 ...`")
        else:
            msg: Message = await ctx.send('Efetuando matrícula...')
            try:
                arguments = list(filter(lambda x: len(x) == 3, arguments))
                if len(arguments) > 8:
                    arguments = arguments[0:7:1]  # up to 8 at once only, uni rules

                result = self.scdao.register(student=ctx.author.id, subjects=arguments)
                if 'err' in result.keys():
                    if result['err'] == 3:
                        await msg.edit(content="Matéria(s) inexistente(s).\nUse o comando `>>mt todas` ou `>>mt buscar` para verificar o código da(s) matéria(s) desejada(s).")
                    elif result['err'] == 2:
                        await msg.edit(content="Sintaxe inválida. Exemplo: `>>sc matricular mt1 mt2 ...`")
                    else:
                        msg.edit(content="Algo deu errado. Consulte o log para mais detalhes.")
                else:
                    await msg.edit(content=f"Matrícula registrada nas matérias a seguir:\n```{smoothen(tuple([f'{x}: {y}' for x, y in result.items()]))}```")
            except Exception as e:
                print_exc(f'(ScheduleController) Exception caught at enrolling student:', e)
                await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    @scheduler.command(name='nota')
    async def update_grade(self, ctx: commands.Context, student: Student, *, arguments: str):
        """
        Atualiza a nota de uma matéria em específico.
        - O comando rejeita trabalhos pendentes - somente trabalhos com status `OK` são alterados!
        - Sintaxe: `sc nota codigo trabalho novanota [antigo]`
          - Se `antigo = 'sim'` então o comando altera a nota de uma matéria de um semestre anterior, ou de alguma matéria trancada.
          - Senão, o comando só vai alterar notas de matérias ativas do semestre atual.
          - Exemplo: `sc nota AL1 AV1 9.5 sim`
        """
        arguments: list = arguments.split()
        invalid_syntax = "Sintaxe: `>>sc nota codigo trabalho novanota antigo?` - 'antigo' é opcional: sim ou não.\nExemplo: `>>sc nota AL1 AV1 9.5`"
        invalid_syntax += "\nSe tentar mudar a nota para uma matéria de um semestre anterior, terá que especificar 'sim' em antigo."
        if len(arguments) < 3:
            await ctx.send(invalid_syntax)
        else:
            exam_grades = {'AV1': [8.0, 1], 'APS1': [2.0, 2], 'AV2': [8.0, 3], 'APS2': [2.0, 4], 'AV3': [10.0, 5]}
            msg: Message = await ctx.send('Atualizando nota...')
            try:
                if len(arguments) > 4:
                    arguments = arguments[0:3:1]
                if len(arguments) == 4:
                    current = not bool(arguments[3].lower() == 'sim')
                else:
                    current = True
                sbj_code = arguments[0].upper()
                assignment = arguments[1].upper()
                grade = abs(float(arguments[2]))

                if exam_grades.get(assignment) is None:
                    await msg.edit(content=f'*Trabalho inválido!*\n{invalid_syntax}')
                    return

                if grade > exam_grades.get(assignment)[0]:
                    await msg.edit(content=f"*A nota especificada é mais alta que o permitido:* `{exam_grades.get(assignment)[0]}`")
                    return

                result = self.scdao.update(
                    student=ctx.author.id,
                    subject=sbj_code,
                    exam_type=exam_grades.get(assignment)[1],
                    newval=grade,
                    grade=True,
                    current=current,
                    active=current
                )
                err_responses = (
                    "Algo deu errado. Consulte o log para mais detalhes.",
                    invalid_syntax,
                    "O trabalho para a matéria especificada não foi encontrado.",
                    "Você não pode alterar a nota para um trabalho que não foi entregue ainda."
                )

                if 'err' in result.keys():
                    await msg.edit(content=err_responses[result.get('err') - 1])
                else:
                    msg = f"Nota alterada: ```{smoothen(f'{tuple(result.keys())[0]} | {assignment}: {nround(grade, 1)}')}```"
                    await msg.edit(content=msg)

            except Exception as e:
                print_exc('(ScheduleController) Exception caught at updating grade:', e)
                await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    @scheduler.command(name='status')
    async def update_status(self, ctx: commands.Context, student: Student, *, arguments: str):
        """
        Altera o status de um trabalho. Também reconhecido como o comando `sts`.
        - Sintaxe: `sc status codigo_materia trabalho novostatus`; onde `novostatus` pode ser:
          - OK;
          - PND (pendente);
          - EPN (envio/entrega pendente).
          - Exemplo: `sc status AL1 AV1 OK`
        """
        arguments: list = arguments.split()
        invalid_syntax = "Sintaxe: `>>sc status codigo trabalho novostatus`.\nExemplo: `>>sc status AL1 AV1 OK`"
        if len(arguments) < 3:
            await ctx.send(invalid_syntax)
        else:
            msg: Message = await ctx.send('Atualizando status...')
            statuses = ('OK', 'EPN', 'PND')
            exam_types = ('AV1', 'APS1', 'AV2', 'APS2', 'AV3')

            sbj_code = arguments[0].upper()
            assignment = arguments[1].upper()
            status = arguments[2].upper()

            if assignment not in exam_types:
                await msg.edit(content=invalid_syntax)
                return
            else:
                assignment = exam_types.index(assignment)

            if status not in statuses:
                await msg.edit(content=invalid_syntax)
                return

            if len(arguments) >= 4 and ' '.join(arguments[2:4:]).lower() in ('envio pendente', 'entrega pendente'):
                status = 2
            elif status == 'pendente':
                status = 3
            else:
                status = statuses.index(status) + 1

            try:
                result = self.scdao.update(
                    student=ctx.author.id,
                    subject=sbj_code,
                    exam_type=assignment,
                    newval=status,
                    grade=False
                )
                err_responses = (
                    "Algo deu errado. Consulte o log para mais detalhes.",
                    invalid_syntax,
                    "O trabalho para a matéria especificada não foi encontrado."
                )

                if 'err' in result.keys():
                    await msg.edit(content=err_responses[result.get('err') - 1])
                else:
                    msg = f"Status alterado: ```{smoothen(f'{tuple(result.keys())[0]} | {assignment}: {status}')}```"
                    await msg.edit(content=msg)

            except Exception as e:
                print_exc('Exception caught at updating status:', e)
                await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    @scheduler.command(name='trancar')
    async def lock_enrollment(self, ctx: commands.Context, student: Student, *, arguments: str):
        """
        Tranca uma, várias ou todas as matérias matriculadas pelo estudante que chamar o comando.
        - Sintaxe: `sc trancar mt1 mt2 ...`
          - Exemplo: `sc trancar POO CGR TCP`
          - `mt1`, `mt2` etc. são códigos de matérias a ser trancadas. Case insensitive, mas precisam necessariamente ter comprimento 3.
          - Caso `mt1 = 'todas'`, todas as matérias matriculadas são trancadas.
        """
        arguments: list = arguments.split()
        invalid_syntax = "Sintaxe: `>>sc trancar mt1 mt2 ...` - caso `mt1 = 'todas'`, todas as matérias ativas do estudante serão trancadas."
        if not arguments:
            await ctx.send(invalid_syntax)
        else:
            msg: Message = await ctx.send('Trancando matrículas...')
            try:
                if arguments[0] == 'todas':
                    lock_all = True
                else:
                    lock_all = False

                result = self.scdao.lock(ctx.author.id, arguments, lock_all=lock_all)

                msgs = (
                    "Você trancou todas as suas matrículas.",
                    "Algo deu errado. Consulte o log para mais detalhes.",
                    "Nenhuma matéria válida fornecida. Nada foi trancado."
                )
                if 'err' not in result.keys():
                    if not lock_all:
                        await msg.edit(content=f"Matrículas trancadas com sucesso: ```{smoothen([f'-> {x}' for x in result.get(0)])}```")
                    else:
                        await msg.edit(content=msgs[0])
                else:
                    await msg.edit(content=msgs[result.get('err')])
            except Exception as e:
                print_exc('Exception caught during enrollment locking:', e)
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
