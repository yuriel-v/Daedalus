# Módulo de controle de estudantes.
import time
from controller.misc import split_args, dprint, smoothen
from controller import stdao, scdao
from discord.ext import commands
from model.student import Student


class StudentController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('st')
    async def student_controller(self, ctx: commands.Context):
        command = next(iter(split_args(ctx.message.content)), "").lower()

        if command == "cadastrar":
            await self.add_student(ctx)
        elif command == "buscar":
            await self.check_student(ctx)
        elif command == "existe":
            await self.student_exists(ctx)
        elif command == "ver":
            await self.view_self(ctx)
        elif command == "editar":
            await self.edit_student(ctx)
        elif command == "excluir":
            await self.delete_student(ctx)
        else:
            dprint(f"Ignoring unknown command: '{command}'")

    async def add_student(self, ctx: commands.Context):
        """
        Cadastra o usuário que invocou o comando.

        Sintaxe: `st cadastrar matricula nome completo`

        Ex.: `st cadastrar 2020123456 Celso Souza`

        O sistema não permite o cadastro de um usuário já cadastrado.
        """

        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) < 2 or not str(arguments[0]).isnumeric():
            await ctx.send("Sintaxe inválida. Exemplo: `>>st cadastrar 2020123456 Celso Souza`.")

        else:
            re = stdao.insert(name=' '.join(arguments[1::]), registry=arguments[0], discord_id=ctx.author.id)
            if re == 0:
                await ctx.send("Cadastro realizado com sucesso.")
            elif re == 1:
                await ctx.send("Sintaxe inválida. Exemplo: `>>st cadastrar 2020123456 Celso Souza`.")
            elif re == 2:
                await ctx.send("Você já está cadastrado.")
            else:
                await ctx.send("Algo deu errado - cadastro não realizado.")

    async def check_student(self, ctx: commands.Context):
        """
        Busca os dados de um estudante.
        O 'filtro' pode ser uma matrícula (numérica) ou um nome (string).

        Sintaxe: `st buscar filtro`

        Ex.: `st buscar 2019123456`
        """

        arguments = split_args(ctx.message.content, prefixed=True, islist=False)
        if len(arguments) == 0:
            await ctx.send("Sintaxe inválida. Exemplo: `>>st buscar 2019123456` (matrícula) ou `>>st buscar João Carlos`.")
            return

        q = None
        comedias = False
        roger = False

        if "roger" in arguments.lower():
            roger = True
        if arguments.lower().startswith("comédia"):
            q = stdao.find_all()
            comedias = True
        elif arguments.lower() == "todos":
            q = stdao.find_all()
        else:
            q = stdao.find(arguments)

        if len(q) == 0:
            await ctx.send("Estudante não encontrado.")
            return
        else:
            results = ""
            if comedias:
                results = "Os comédia dessa porra:"
            elif roger:
                results = "O divino meme em charme e osso:"
            else:
                results = "Encontrado(s):"
            await ctx.send(f"{results}```{smoothen(q)}```")

    async def student_exists(self, ctx: commands.Context):
        """
        Verifica se um ID Discord existe no banco de dados ou não.

        Sintaxe: `existe 263169934543028225`
        """
        disc_id = split_args(ctx.message.content, prefixed=True, islist=False)
        try:
            exists = stdao.find_by_discord_id(int(disc_id))

            if exists:
                await ctx.send("ID existente.")
            else:
                await ctx.send("ID não existente.")
        except Exception:
            await ctx.send("ID não existente.")

    async def view_self(self, ctx: commands.Context):
        """
        Verifica se a pessoa que invocou o comando está cadastrada no banco de dados.
        Se sim, então os dados da pessoa são mostrados.
        """
        cur_student: Student = stdao.find_by_discord_id(ctx.author.id)
        if cur_student is None:
            await ctx.send("Você não está cadastrado.")
        else:
            command = next(iter(split_args(ctx.message.content, prefixed=True)), None)
            if command is not None:
                command = command.lower()
            start = time.time()
            cur_subjects = scdao.find(cur_student, exams=True)
            # parse to strings afterward
            cur_strings = []
            for reg in cur_subjects:
                composite = str(reg.subject.code) + ' | '
                composite += ' | '.join([f"{exam.show_type()}: {exam.show_status()}" for exam in reg.eager_exams])
                cur_strings.append(composite)

            composite_message = f"Seus dados: ```{smoothen(str(cur_student))}```"
            if cur_strings:
                composite_message += f"Suas matérias: ```{smoothen(cur_strings)}```"
            await ctx.send(composite_message)
            dprint(f"------------------ Time taken: {round(time.time() - start, 2)} sec ------------------")

    async def edit_student(self, ctx: commands.Context):
        """
        Edita o cadastro do usuário que invocou o comando.
        O 'campo' pode ser 'nome' ou 'mtr' (matrícula).

        Sintaxe: `editar campo novo valor`
        """

        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) < 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>st editar mtr 2019246852` ou `>>st editar nome Carlos Eduardo`.")
            return

        res = None

        if str(arguments[0]).lower() == 'nome':
            res = stdao.update(ctx.author.id, name=' '.join(arguments[1::]))

        elif str(arguments[0]).lower() == 'mtr':
            res = stdao.update(ctx.author.id, registry=int(arguments[1]))

        else:
            await ctx.send("Campo inválido - o campo pode ser `nome` ou `mtr`.")
            return

        if res != 0:
            await ctx.send("Você não está cadastrado.")

        else:
            reply = "Dados alterados."
            cur_student = stdao.find_by_discord_id(ctx.author.id)
            reply += f"```{smoothen(str(cur_student))}```"
            await ctx.send(reply)

    async def delete_student(self, ctx: commands.Context):
        if stdao.delete(ctx.author.id) == 0:
            await ctx.send("O seu cadastro foi excluído com sucesso.")
        else:
            await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
