# Módulo de controle para a agenda de trabalhos/provas.
import sqlalchemy as sqla

from sqlalchemy.orm import sessionmaker
from discord.ext import commands
from secret import ownerid
from models.student import Student
from models.subject import Subject
from models.registered import Registered
from models.assigned import Assigned
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import initialize_sql
from misc import split_args

engin = create_engine('sqlite:///database\\data.db', echo=True)


class UniReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.smkr = sessionmaker(bind=engin)
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
        if len(arguments) < 2 or not str(arguments[0]).isnumeric():
            await ctx.send("Sintaxe inválida. Exemplo: `>>cadastrar 2020123456 Celso Souza`.")
            return

        session = self.smkr()
        new_student = None
        q = session.query(Student).filter(Student.discord_id == ctx.author.id).all()
        if len(q) != 0:
            await ctx.send("Você já está cadastrado.")
            return
        else:
            new_student = Student(registry=arguments[0], name=' '.join(arguments[1::]), discord_id=ctx.author.id)
            session.add(new_student)
            session.commit()

            if len(session.query(Student).filter(Student.discord_id == ctx.author.id).all()) != 0:
                await ctx.send("Cadastro realizado com sucesso.")
            else:
                await ctx.send("Algo deu errado - cadastro não realizado.")

        session.close()

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
        session = self.smkr()
        q = None
        if str(arguments[0]).isnumeric():
            q = session.query(Student).filter(Student.registry == int(arguments[0])).all()
        else:
            q = session.query(Student).filter(Student.name.like(f'%{" ".join(arguments)}%')).all()

        if len(q) == 0:
            await ctx.send("Estudante não encontrado.")
            return
        else:
            results = "Encontrado(s):```\n"
            for match in q:
                results += f"Matrícula: {match.registry} | Nome: {match.name}\n"
            results += "```"
            await ctx.send(results)

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

        session = self.smkr()
        cur_student = session.query(Student).filter(Student.discord_id == ctx.author.id).first()

        if cur_student is None:
            await ctx.send("Você não está cadastrado.")
            return

        session.add(cur_student)
        if str(arguments[0]).lower() == 'nome':
            print(f"Editar nome para: {' '.join(arguments[1::])}")
            print(session.dirty)
            cur_student.name = ' '.join(arguments[1::])

        elif str(arguments[0]).lower() == 'mtr':
            cur_student.registry = int(arguments[1])

        else:
            await ctx.send("Campo inválido - o campo pode ser `nome` ou `mtr`.")
            session.rollback()
            session.close()
            return

        session.commit()
        reply = "Dados alterados.```\n"
        cur_student = session.query(Student).filter(Student.discord_id == ctx.author.id).first()
        reply += f"Matrícula: {cur_student.registry} | Nome: {cur_student.name}```"
        await ctx.send(reply)
