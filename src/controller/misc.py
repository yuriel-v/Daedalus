# Módulo de sei lá o quê. Utilidades em geral. E memes.
from os import getenv
from typing import Iterable, Union
from discord.ext import commands
from sys import getsizeof

from discord.ext.commands.core import is_owner
from model import initialize_sql
from model.exam import Exam
from model.registered import Registered

from model.student import Student
from model.subject import Subject
from dao import smkr, devsmkr, engin

daedalus_environment = getenv("DAEDALUS_ENV").upper()
debug = bool(daedalus_environment == "DEV")


def nround(number: float, decimals=1):
    """Round, só que normalizado. nround(0.5) = 1"""
    number = str(number)
    # if decimal places <= decimals
    if len(number[number.index('.')::]) <= decimals + 1:
        return float(number)
    if number[-1] == '5':
        number = number[:-1:] + '6'
    return round(float(number), decimals)


# i don't trust statistics.median, it's not an average
def avg(items: Union[list, tuple, set]):
    """Média entre itens de um iterável."""
    return sum(items) / len(items)


def uni_avg(av1: float, aps1: float, av2: float, aps2: float, av3: float):
    """
    Médias de provas, de acordo com os padrões estabelecidos pelo Centro Universitário Carioca (UniCarioca).
    - A prova de menor nota é descartada, e a média é feita entre as duas que sobrarem.
    """
    items = [av1 + aps1, av2 + aps2, av3]
    items.remove(min(items))
    return nround(avg(items), 1)


def split_args(arguments: str, prefixed=False, islist=True) -> Union[list[str], str]:
    """
    Separa os argumentos passados num comando em uma lista de strings, ou em uma string só, caso `islist = False`.
    - Use `prefixed = True` quando um comando for separado por espaço, ex.: `st cadastrar mtr nome = ['mtr', 'nome']`.
    """
    arguments = arguments.split(' ')
    if arguments[0] == 'Roger':
        arguments.pop(0)

    # for commands like >>st ver, so 'ver' doesn't get treated as an argument
    if prefixed:
        arguments.pop(1)

    arguments.pop(0)
    if islist:
        return arguments
    else:
        return ' '.join(arguments)


def arg_types(arguments: Iterable, repr=False):
    """Separa argumentos passados num iterável em strings, floats ou ints."""
    arg_with_types = {0: [], 1: [], 2: []}
    for x in arguments:
        x = str(x)
        # if one dot and string without dots is numeric = float
        if x.count('.') == 1 and x.replace('.', '').isnumeric():
            arg_with_types[0].append(x)
        elif x.isnumeric():
            arg_with_types[1].append(x)
        else:
            arg_with_types[2].append(x)
    if not repr:
        return arg_with_types
    else:
        return f"{{\n  Strings: `{arg_with_types.get(2)}`\n  Integers: `{arg_with_types.get(1)}`\n  Floats: `{arg_with_types.get(0)}`\n}}"


def dprint(message: str):
    """Print para log, só quando `debug = True`."""
    if debug:
        print(message)


def smoothen(message: Iterable):
    """
    Recebe um iterável e o formata numa caixinha.
    - Feito para lidar especialmente com strings ou listas/tuplas/conjuntos/dicionários de strings.
    - Para dicionários, somente os valores, convertidos para string, são 'encaixados'.
    """
    if isinstance(message, Union[list, tuple, set].__args__):
        message = [str(x) for x in message]
        dashes = len(max(message, key=len))
    elif isinstance(message, dict):
        message = [str(x) for x in message.values()]
        dashes = len(max(message, key=len))
    else:
        message = str(message)
        dashes = len(message)
    dashes += 2

    formatted_message = f'\n+{"-" * dashes}+\n'
    if isinstance(message, str):
        formatted_message += f'| {message} |\n'
    else:
        for string in message:
            spaces = dashes - 1 - len(string)
            # if string is just a string of dashes, extend it until box boundary if it's not there already
            if string == len(string) * '-' and spaces > 1:
                string += '-' * (spaces - 1)
                spaces = 1
            formatted_message += f'| {string}{" " * spaces}|\n'

    formatted_message += f'+{"-" * dashes}+\n'
    return formatted_message


class Misc(commands.Cog, name='Misc'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def emphasize(self, ctx):
        """Texto com ÊNFASE!!"""
        await ctx.send(f"**{split_args(ctx.message.content, islist=False).upper()}!!**")

    @commands.command(name='code')
    async def text_code(self, ctx):
        """Texto em código"""
        reply = ''.join([
            "```\n",
            split_args(ctx.message.content, islist=False),
            "\n```"
        ])
        await ctx.send(reply)

    @commands.command('sizeof')
    async def sizeof_value(self, ctx):
        """Tamanho em bytes do valor digitado"""
        args = split_args(ctx.message.content)
        if not args:
            await ctx.send("Sintaxe: `>>sizeof numero`")
        elif not str(args[0]).isnumeric():
            await ctx.send("Sintaxe: `>>sizeof numero`")
        else:
            numba = None
            if '.' in str(args[0]):
                numba = float(args[0])
            else:
                numba = int(args[0])

            await ctx.send(f"Tamanho de `{numba}`: {getsizeof(numba)} bytes.")

    @commands.command('drop')
    async def drop_tables(ctx):
        if not is_owner(ctx.author):
            await ctx.send("Somente o proprietário pode rodar esse comando.")
            return
        Exam.__table__.drop()
        Registered.__table__.drop()
        initialize_sql(engin)
        await ctx.send("Feito. Verifique o log para confirmação.")

    @commands.command('backup')
    async def move_to_dev_db(ctx):
        """Copia estudantes e matérias no BD de produção (Heroku Postgres) para o SQLite de desenvolvimento."""
        if str(ctx.author.id) != getenv("DAEDALUS_OWNERID"):
            await ctx.send("Somente o proprietário pode rodar esse comando.")
        elif daedalus_environment != "DEV":
            return
        else:
            try:
                devsession = devsmkr()
                session = smkr()
                print("---------- Sessions initialized ----------")
            except Exception:
                print("Exception caught while initializing sessions and databases")
                return

            try:
                prd_students = session.query(Student).all()
                prd_subjects = session.query(Subject).all()
                print("---------- Subjects and students fetched ----------")
            except Exception as e:
                print(f"Exception caught while fetching current data from PRD DB: {e}")
                devsession.close()
                session.close()
                return

            try:
                dev_students = [Student(
                    id=int(student.id),
                    name=str(student.name),
                    registry=int(student.registry),
                    discord_id=int(student.discord_id)
                ) for student in prd_students]

                dev_subjects = [Subject(
                    id=int(subject.id),
                    code=str(subject.code),
                    fullname=str(subject.fullname),
                    semester=int(subject.semester)
                ) for subject in prd_subjects]
                print("---------- Subjects and students copied ----------")
            except Exception as e:
                print("Exception caught while sanitizing data")
                devsession.close()
                session.close()
                return

            try:
                session.expunge_all()
                devsession.add_all(dev_students)
                devsession.add_all(dev_subjects)
                print("---------- Data added to DEV session ----------")
            except Exception:
                print("Exception caught while adding current data to DEV session")
                devsession.close()
                session.close()
                return

            try:
                devsession.commit()
                session.rollback()
                print("---------- Changes committed ----------")
                await ctx.send("Feito. Verifique o log para confirmação.")
            except Exception:
                print("Exception caught while committing changes to DEV DB")
            finally:
                devsession.close()
                session.close()

    @commands.command('restore')
    async def move_to_prd_db(ctx):
        """Copia estudantes e matérias no SQLite de desenvolvimento para o BD de produção (Heroku Postgres)."""
        if str(ctx.author.id) != getenv("DAEDALUS_OWNERID"):
            await ctx.send("Somente o proprietário pode rodar esse comando.")
        elif daedalus_environment != "DEV":
            return
        else:
            try:
                devsession = devsmkr()
                session = smkr()
                print("---------- Sessions initialized ----------")
            except Exception:
                print("Exception caught while initializing sessions and databases")
                return

            try:
                dev_students = devsession.query(Student).all()
                dev_subjects = devsession.query(Subject).all()
                print("---------- Subjects and students fetched ----------")
            except Exception:
                print("Exception caught while fetching current data from DEV DB")
                devsession.close()
                session.close()
                return

            try:
                prd_students = [Student(
                    id=int(student.id),
                    name=str(student.name),
                    registry=int(student.registry),
                    discord_id=int(student.discord_id)
                ) for student in dev_students]

                prd_subjects = [Subject(
                    id=int(subject.id),
                    code=str(subject.code),
                    fullname=str(subject.fullname),
                    semester=int(subject.semester)
                ) for subject in dev_subjects]
                print("---------- Subjects and students copied ----------")
            except Exception as e:
                print("Exception caught while sanitizing data")
                devsession.close()
                session.close()
                return

            try:
                devsession.expunge_all()
                session.add_all(prd_students)
                session.add_all(prd_subjects)
                print("---------- Data added to PRD session ----------")
            except Exception:
                print("Exception caught while adding current data to PRD session")
                devsession.close()
                session.close()
                return

            try:
                session.commit()
                devsession.rollback()
                print("---------- Changes committed ----------")
                await ctx.send("Feito. Verifique o log para confirmação.")
            except Exception:
                print("Exception caught while committing changes to PRD DB")
            finally:
                devsession.close()
                session.close()
