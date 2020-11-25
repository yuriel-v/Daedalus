# Módulo de controle de estudantes.
from controller.misc import split_args, dprint, smoothen
from dao.studentdao import StudentDao
from discord.ext import commands


class StudentController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stdao = StudentDao()

    @commands.command('st')
    async def student_controller(self, ctx: commands.Context):
        command = next(iter(split_args(ctx.message.content)), "")

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
        else:
            dprint(f"Ignoring unknown command: '{command}'")

    async def add_student(self, ctx: commands.Context):
        """
        Cadastra o usuário que invocou o comando.\n
        Sintaxe: >>st cadastrar matricula nome completo\n
        Ex.: >>st cadastrar 2020123456 Celso Souza

        O sistema não permite o cadastro de um usuário já cadastrado.
        """

        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) < 2 or not str(arguments[0]).isnumeric():
            await ctx.send("Sintaxe inválida. Exemplo: `>>st cadastrar 2020123456 Celso Souza`.")

        else:
            re = self.stdao.insert(name=' '.join(arguments[1::]), registry=arguments[0], discord_id=ctx.author.id)
            if re == 0:
                await ctx.send("Cadastro realizado com sucesso.")
            elif re == 1:
                await ctx.send("Sintaxe inválida. Exemplo: `>>cadastrar 2020123456 Celso Souza`.")
            elif re == 2:
                await ctx.send("Você já está cadastrado.")
            else:
                await ctx.send("Algo deu errado - cadastro não realizado.")

    async def check_student(self, ctx: commands.Context):
        """
        Busca os dados de um estudante.
        Sintaxe: >>st buscar filtro
        O 'filtro' pode ser uma matrícula (numérica) ou um nome (string).
        Ex.: >>st buscar 2019123456
        """

        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) == 0:
            await ctx.send("Sintaxe inválida. Exemplo: `>>st buscar 2019123456` (matrícula) ou `>>st buscar João Carlos`.")
            return

        q = self.stdao.find(arguments)

        if len(q) == 0:
            await ctx.send("Estudante não encontrado.")
            return
        else:
            results = "Encontrado(s): " + smoothen(q)
            await ctx.send(results)

    async def student_exists(self, ctx: commands.Context):
        """
        Verifica se um ID Discord existe no banco de dados ou não.\n
        Sintaxe: >>existe 263169934543028225
        """
        exists = self.stdao.find(split_args(ctx.message.content, prefixed=True), exists=True)

        if exists:
            await ctx.send("ID existente.")
        else:
            await ctx.send("ID não existente.")

    async def view_self(self, ctx: commands.Context):
        """
        Verifica se a pessoa que invocou o comando está cadastrada no banco de dados.\n
        Se sim, então os dados da pessoa são mostrados.
        """
        cur_student = self.stdao.find_by_discord_id(ctx.author.id)
        if cur_student is None:
            await ctx.send("Você não está cadastrado.")
        else:
            await ctx.send("Seus dados: " + smoothen(str(cur_student)))

    async def edit_student(self, ctx: commands.Context):
        """
        Edita o cadastro do usuário que invocou o comando.
        Sintaxe: >>editar campo novo valor
        O 'campo' pode ser 'nome' ou 'mtr' (matrícula).
        """

        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) < 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>st editar mtr 2019246852` ou `>>editar nome Carlos Eduardo`.")
            return

        res = None

        if str(arguments[0]).lower() == 'nome':
            res = self.stdao.update(ctx.author.id, name=' '.join(arguments[1::]))

        elif str(arguments[0]).lower() == 'mtr':
            res = self.stdao.update(ctx.author.id, registry=int(arguments[1]))

        else:
            await ctx.send("Campo inválido - o campo pode ser `nome` ou `mtr`.")
            return

        if res != 0:
            await ctx.send("Você não está cadastrado.")

        else:
            reply = "Dados alterados."
            cur_student = self.stdao.find_by_discord_id(ctx.author.id)
            reply += smoothen(str(cur_student))
            await ctx.send(reply)
