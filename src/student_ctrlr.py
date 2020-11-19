# Módulo de controle para a agenda de trabalhos/provas.
from discord.ext import commands
from misc import split_args

from dao import engin
from dao.studentdao import StudentDao
from dao.subjectdao import SubjectDao
from model import initialize_sql


class StudentController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stdao = StudentDao()
        self.sbdao = SubjectDao()
        initialize_sql(engin)

    @commands.command('cadastrar')
    async def add_student(self, ctx):
        """
        Cadastra o usuário que invocou o comando.\n
        Sintaxe: >>cadastrar matricula nome completo\n
        Ex.: >>cadastrar 2020123456 Celso Souza

        O sistema não permite o cadastro de um usuário já cadastrado.
        """

        arguments = split_args(ctx.message.content)
        if self.stdao.find([ctx.author.id], exists=True):
            await ctx.send("Você já está cadastrado.")

        elif len(arguments) < 2 or not str(arguments[0]).isnumeric():
            await ctx.send("Sintaxe inválida. Exemplo: `>>cadastrar 2020123456 Celso Souza`.")

        else:
            self.stdao.insert(name=' '.join(arguments[1::]), registry=arguments[0], discord_id=ctx.author.id)
            if self.stdao.find([ctx.author.id], exists=True):
                await ctx.send("Cadastro realizado com sucesso.")
            else:
                await ctx.send("Algo deu errado - cadastro não realizado.")

    @commands.command('buscar')
    async def check_student(self, ctx):
        """
        Busca os dados de um estudante.
        Sintaxe: >>buscar filtro
        O 'filtro' pode ser uma matrícula (numérica) ou um nome (string).
        Ex.: >>buscar 2019123456
        """

        arguments = split_args(ctx.message.content)
        if len(arguments) == 0:
            await ctx.send("Sintaxe inválida. Exemplo: `>>student 2019123456` (matrícula) ou `>>student João Carlos`.")
            return

        q = self.stdao.find(arguments)

        if len(q) == 0:
            await ctx.send("Estudante não encontrado.")
            return
        else:
            results = "Encontrado(s):```\n"
            for match in q:
                results += f"Matrícula: {match.registry} | Nome: {match.name}\n"
            results += "```"
            await ctx.send(results)

    @commands.command('existe')
    async def student_exists(self, ctx):
        exists = self.stdao.find(split_args(ctx.message.content), exists=True)

        if exists:
            await ctx.send("ID existente.")
        else:
            await ctx.send("ID não existente.")

    @commands.command('visualizar')
    async def view_self(self, ctx):
        cur_student = self.stdao.find_by_discord_id(ctx.author.id)
        if cur_student is None:
            await ctx.send("Você não está cadastrado.")
        else:
            await ctx.send(f"Seus dados:```\nMatrícula: {cur_student.registry} | Nome: {cur_student.name}\n```")

    @commands.command('editar')
    async def edit_student(self, ctx):
        """
        Edita o cadastro do usuário que invocou o comando.
        Sintaxe: >>editar campo novo valor
        O 'campo' pode ser 'nome' ou 'mtr' (matrícula).
        """

        arguments = split_args(ctx.message.content)
        if len(arguments) < 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>editar mtr 2019246852` ou `>>editar nome Carlos Eduardo`.")
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
            reply = "Dados alterados.```\n"
            cur_student = self.stdao.find_by_discord_id(ctx.author.id)
            reply += f"Matrícula: {cur_student.registry} | Nome: {cur_student.name}```"
            await ctx.send(reply)
