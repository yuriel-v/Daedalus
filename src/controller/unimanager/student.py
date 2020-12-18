# Módulo de controle de estudantes.
from time import time
from discord.message import Message
from controller.ferozes import ferozes
from controller.misc import split_args, dprint, smoothen, uni_avg, avg, nround
from dao.unimanager.schedulerdao import SchedulerDao
from dao.unimanager.studentdao import StudentDao
from discord.ext import commands
from model.unimanager.student import Student


class StudentController(commands.Cog, name='Student Controller: st'):
    def __init__(self, bot):
        self.bot = bot
        self.stdao = StudentDao()
        self.scdao = SchedulerDao()

        self.cmds = {
            'cadastrar': self.add_student,
            'buscar': self.check_student,
            'existe': self.student_exists,
            'ver': self.view_self,
            'editar': self.edit_student,
            'excluir': self.delete_student
        }

    def ferozes():
        async def predicate(ctx):
            return ctx.guild.id == ferozes
        return commands.check(predicate)

    async def cog_after_invoke(self, ctx):
        self.stdao.sclear()
        self.scdao.sclear()

    @commands.command('st')
    @ferozes()
    async def select_command(self, ctx: commands.Context):
        """
        Comando mestre para o cog Student Controller.
        """
        command = next(iter(split_args(ctx.message.content)), "").lower()

        if command in self.cmds.keys():
            await self.cmds[command](ctx)
        else:
            await ctx.send("Comando inválido. Sintaxe: `>>st comando argumentos`")

    async def add_student(self, ctx: commands.Context):
        """
        Cadastra o usuário que invocou o comando.
        - O sistema não permite o cadastro de um usuário já cadastrado.
        - Sintaxe: `st cadastrar matricula nome completo`
          - Exemplo: `st cadastrar 2020123456 Celso Souza`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) < 2 or not str(arguments[0]).isnumeric():
            await ctx.send("Sintaxe inválida. Exemplo: `>>st cadastrar 2020123456 Celso Souza`.")
            return

        msg: Message = await ctx.send('Cadastrando...')
        try:
            statuses = (
                "Cadastro realizado com sucesso.",
                "Algo deu errado - cadastro não realizado. Consulte o log para mais detalhes.",
                "Sintaxe inválida. Exemplo: `>>st cadastrar 2020123456 Celso Souza`.",
                "Você já está cadastrado."
            )
            re = self.stdao.insert(name=' '.join(arguments[1::]), registry=arguments[0], discord_id=ctx.author.id)
            student = str(self.stdao.find_by_discord_id(ctx.author.id))
            await msg.edit(content=f'{statuses[re]} ```{smoothen(student)}```')
        except Exception as e:
            print(f'Exception caught at searching student: {e}\n Stack trace: {e.__traceback__}')
            await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    async def check_student(self, ctx: commands.Context):
        """
        Busca os dados de um estudante.
        - O 'filtro' pode ser uma matrícula (numérica) ou um nome (string).
        - Sintaxe: `st buscar filtro`
          - Exemplos: `st buscar 2019123456` ou `st buscar Silva`
        """
        arguments = split_args(ctx.message.content, prefixed=True, islist=False)
        if len(arguments) == 0:
            await ctx.send("Sintaxe inválida. Exemplo: `>>st buscar 2019123456` (matrícula) ou `>>st buscar João Carlos`.")
            return

        q = None
        comedias = False
        roger = bool("roger" in arguments.lower())
        msg: Message = await ctx.send('Buscando estudantes...')

        try:
            if arguments.lower().startswith("comédia"):
                q = self.stdao.find_all()
                comedias = True
            elif arguments.lower() == "todos":
                q = self.stdao.find_all()
            else:
                q = self.stdao.find(arguments)

            if len(q) == 0:
                await msg.edit(content="Estudante(s) não encontrado(s).")
                return
            else:
                if comedias:
                    results = "Os comédia dessa porra:"
                elif roger:
                    results = "O divino meme em charme e osso:"
                else:
                    results = "Encontrado(s):"
                await msg.edit(content=f"{results}```{smoothen(q)}```")
        except Exception as e:
            print(f'Exception caught at searching student: {e}\n Stack trace: {e.__traceback__}')
            await msg.edit(content='Algo deu errado. Consulte o log para detalhes.')

    async def student_exists(self, ctx: commands.Context):
        """
        Verifica se um ID Discord existe no banco de dados ou não.
        - Sintaxe: `existe numeroid`
          - Exemplo: `existe 263169934543028225`
        """
        disc_id = split_args(ctx.message.content, prefixed=True, islist=False)
        msg: Message = await ctx.send('Buscando estudante...')
        try:
            exists = self.stdao.find_by_discord_id(int(disc_id))

            if exists:
                await msg.edit(content="ID existente.")
            else:
                await msg.edit(content="ID não existente.")
        except Exception:
            await msg.edit(content="ID não existente.")

    async def view_self(self, ctx: commands.Context):
        """
        Verifica se a pessoa que invocou o comando está cadastrada no banco de dados.
        - Se sim, então os dados da pessoa são mostrados, juntamente com suas provas e respectivos status.
        - Aceita um argumento, sendo este o tipo de exibição das matérias:
          - `completo`: mostra trabalhos como `TRB: STS (nota)`
          - `notas`: mostra trabalhos como `TRB: nota`
          - `médias` ou `medias`: ao invés de trabalhos, mostra a média atual da matéria.
            - Caso a AV2 já tenha sido marcada como OK, mostra também um status "aprovado" ou "reprovado", dependendo da média.
          - Nada ou qualquer outra coisa além dos já citados: mostra trabalhos como o padrão, `TRB: STS`
        - Sintaxe: `st ver exibicao`
          - Exemplo: `st ver notas`
        """
        msg: Message = await ctx.send('Buscando...')
        cur_student: Student = self.stdao.find_by_discord_id(ctx.author.id)
        if cur_student is None:
            await msg.edit(content="Você não está cadastrado.")
        else:
            start = time()
            command = next(iter(split_args(ctx.message.content, prefixed=True)), None)
            if command is not None:
                command = command.lower()

            try:
                enrollments = self.scdao.find_enrollments(cur_student.id)
                # parse to strings afterward, if applicable
                cur_strings = []
                if enrollments:
                    semester_avg = []
                    av2_delivered = []
                    for reg in enrollments:
                        composite = str(reg.subject.code) + ' | '
                        if command == 'completo':  # MT1 | AV1: STS (10.0) | APS1: STS (10.0) | AV2: STS (10.0) | APS2: STS (10.0) | AV3: STS (10.0)
                            composite += ' | '.join([f"{exam.show_type()}: {exam.show_status()} ({exam.show_grade()})" for exam in reg.exams])

                        elif command == 'notas':  # MT1 | AV1: 10.0 | APS1: 10.0 | AV2: 10.0 | APS2: 10.0 | AV3: 10.0
                            composite += ' | '.join([f"{exam.show_type()}: {exam.show_grade()}" for exam in reg.exams])

                        elif command == 'médias' or command == 'medias':  # MT1 | Média: 10.0 | Status: Aprovado (se AV2 OK)
                            average = uni_avg(*[exam.grade for exam in reg.exams])
                            semester_avg.append(average)
                            composite += ' | '.join([f"Média {average}"])
                            finished = False
                            for exam in reg.exams:
                                if exam.exam_type == 2 and exam.status == 1:
                                    composite += f" | Status: { (lambda: 'Aprovado' if average >= 7 else 'Reprovado')() }"
                                    finished = True
                                    break
                            av2_delivered.append(finished)

                        else:  # MT1 | AV1: STS | APS1: STS | AV2: STS | APS2: STS | AV3: STS
                            composite += ' | '.join([f"{exam.show_type()}: {exam.show_status()}" for exam in reg.exams])
                        cur_strings.append(composite)
                    enrollments.clear()
                    if command == 'médias' or command == 'medias':
                        semester_avg = nround(avg(semester_avg), 2)
                        savg_msg = f"CR do semestre: {semester_avg}"
                        cur_strings.extend(('---', savg_msg))

                final_msg = [str(cur_student), '---']
                if cur_strings:
                    final_msg.extend(cur_strings)
                else:
                    final_msg.append('-- aluno não matriculado em nenhuma matéria --')
                final_msg = tuple(final_msg)
            except Exception as e:
                final_msg = 'Algo deu errado. Consulte o log para detalhes.'
                print(f'Exception caught at viewing self: {e}\n Stack trace: {e.__traceback__}')
            else:
                final_msg = f"Seus dados: ```{smoothen(final_msg)}```"
            finally:
                end = round(time() - start, 2)
                await msg.edit(content=final_msg + f"Tempo de execução: {end} seg.")
                dprint(f"------------------ Time taken: {end} sec ------------------")

    async def edit_student(self, ctx: commands.Context):
        """
        Edita o cadastro do usuário que invocou o comando.
        - Sintaxe: `editar campo novo valor`, onde campo pode ser:
          - `nome`: Edita o nome do estudante;
          - `mtr`: Edita a matrícula do estudante.
          - Exemplos: `st editar nome Carlos Eduardo` ou `st editar mtr 2020048596`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) < 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>st editar mtr 2019246852` ou `>>st editar nome Carlos Eduardo`.")
            return

        msg: Message = await ctx.send('Editando...')
        try:
            res = None
            student = self.stdao.find_by_discord_id(ctx.author.id)

            if str(arguments[0]).lower() == 'nome':
                await msg.edit(content='Editando nome...')
                res = self.stdao.update(student, name=' '.join(arguments[1::]))

            elif str(arguments[0]).lower() == 'mtr':
                await msg.edit(content='Editando matrícula...')
                res = self.stdao.update(student, registry=int(arguments[1]))

            else:
                await msg.edit(content="Campo inválido - o campo pode ser `nome` ou `mtr`.")
                return

            statuses = (
                f'Dados alterados. ```{smoothen(str(student))}```',
                'Algo deu errado. Consule o log para detalhes.',
                'Você não está cadastrado.',
                'Nenhuma modificação a fazer.'
            )
            await msg.edit(content=statuses[res])
        except Exception as e:
            await msg.edit(content='Algo deu errado. Consule o log para detalhes.')
            print(f'Exception caught at editing self: {e}\n Stack trace: {e.__traceback__}')

    async def delete_student(self, ctx: commands.Context):
        """
        Exclui o estudante que chamou o comando.
        - Uma confirmação deve ser dada para o comando efetivar a exclusão, sendo esta dada pela afirmação `tenho cerveja` após o comando em si.
        """
        confirm = split_args(ctx.message.content, prefixed=True)

        if len(confirm) < 2 or ' '.join(confirm[0:3:1]).lower() != 'tenho cerveja':
            tem_cerveja = "Você tem cerveja disso? Isso irá apagar todas as suas matrículas e dados associados a elas!\n"
            tem_cerveja += "Se realmente tem cerveja disso, então use `st excluir tenho cerveja`. Não diga que não avisei!"
            await ctx.send(tem_cerveja)

        elif self.stdao.delete(ctx.author.id) == 0:
            await ctx.send("O seu cadastro foi excluído com sucesso.")
        else:
            await ctx.send("Algo deu errado. Consulte o log para detalhes.")

    def cog_info(self, command=None) -> str:
        if command is not None and str(command).lower() in self.cmds.keys():
            reply = f'-- st {str(command).lower()} --\n' + self.cmds[str(command)].__doc__
        else:
            nl = '\n'
            reply = f"""
            st: Student Controller
            Este módulo gerencia cadastros gerais de estudantes.\n
            Comandos incluem:
            {nl.join([f'- {x}' for x in self.cmds.keys()])}
            """

        return '\n'.join([x.strip() for x in reply.split('\n')]).strip()
