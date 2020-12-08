# Módulo de sei lá o quê. Utilidades em geral. E memes.
from os import getenv
from typing import Iterable, Union
from discord.ext import commands
from sys import getsizeof

from model.student import Student
from model.subject import Subject
from dao import smkr, dsvsmkr

daedalus_environment = getenv("DAEDALUS_ENV").upper()
debug = bool(daedalus_environment == "DSV")


# i don't trust statistics.median, it's not an average
def avg(items: Union[list, tuple, set]):
    return sum(items) / len(items)


def uni_avg(av1: float, aps1: float, av2: float, aps2: float, av3: float):
    items = [av1 + aps1, av2 + aps2, av3]
    items.remove(min(items))
    return round(avg(items), 1)


def split_args(arguments: str, prefixed=False, islist=True):
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
    if debug:
        print(message)


def smoothen(message: Iterable, complement=False):
    """
    Recebe um iterável e o formata numa caixinha.
    Feito para lidar especialmente com strings ou listas/tuplas/conjuntos/dicionários de strings.

    Para dicionários, somente os valores, convertidos para string, são 'encaixados'.
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

    formatted_message = (lambda: f'\n+{"-" * dashes}+\n' if not complement else "")()
    if isinstance(message, str):
        formatted_message += f'| {message} |\n'
    else:
        for string in message:
            spaces = dashes - 1 - len(string)
            # if string is just a string of dashes, extend it until end of line if it's not there already
            if string == len(string) * '-' and spaces > 1:
                string += '-' * (spaces - 1)
                spaces = 1
            formatted_message += f'| {string}{" " * spaces}|\n'

    formatted_message += f'+{"-" * dashes}+\n'
    return formatted_message


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Texto com ÊNFASE!!
    @commands.command()
    async def emphasize(self, ctx):
        await ctx.send(f"**{split_args(ctx.message.content, islist=False).upper()}!!**")

    # Texto em código
    @commands.command(name='code')
    async def text_code(self, ctx):
        reply = ''.join([
            "```\n",
            split_args(ctx.message.content, islist=False),
            "\n```"
        ])
        await ctx.send(reply)

    # Tamanho em bytes do valor digitado
    @commands.command('sizeof')
    async def sizeof_value(self, ctx):
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

    @commands.command('backup')
    async def move_to_dsv_db(ctx):
        if str(ctx.author.id) != getenv("DAEDALUS_OWNERID"):
            await ctx.send("Somente o proprietário pode rodar esse comando.")
        elif daedalus_environment != "DSV":
            return
        else:
            try:
                dsvsession = dsvsmkr()
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
                dsvsession.close()
                session.close()
                return

            try:
                dsv_students = [Student(
                    id=int(student.id),
                    name=str(student.name),
                    registry=int(student.registry),
                    discord_id=int(student.discord_id)
                ) for student in prd_students]

                dsv_subjects = [Subject(
                    id=int(subject.id),
                    code=str(subject.code),
                    fullname=str(subject.fullname),
                    semester=int(subject.semester)
                ) for subject in prd_subjects]
                print("---------- Subjects and students copied ----------")
            except Exception as e:
                print("Exception caught while sanitizing data")
                dsvsession.close()
                session.close()
                return

            try:
                session.expunge_all()
                dsvsession.add_all(dsv_students)
                dsvsession.add_all(dsv_subjects)
                print("---------- Data added to DSV session ----------")
            except Exception:
                print("Exception caught while adding current data to DSV session")
                dsvsession.close()
                session.close()
                return

            try:
                dsvsession.commit()
                session.rollback()
                print("---------- Changes committed ----------")
                await ctx.send("Feito. Verifique o log para confirmação.")
            except Exception:
                print("Exception caught while committing changes to DSV DB")
            finally:
                dsvsession.close()
                session.close()

    @commands.command('restore')
    async def move_to_prd_db(ctx):
        if str(ctx.author.id) != getenv("DAEDALUS_OWNERID"):
            await ctx.send("Somente o proprietário pode rodar esse comando.")
        elif daedalus_environment != "DSV":
            return
        else:
            try:
                dsvsession = dsvsmkr()
                session = smkr()
                print("---------- Sessions initialized ----------")
            except Exception:
                print("Exception caught while initializing sessions and databases")
                return

            try:
                dsv_students = dsvsession.query(Student).all()
                dsv_subjects = dsvsession.query(Subject).all()
                print("---------- Subjects and students fetched ----------")
            except Exception:
                print("Exception caught while fetching current data from DSV DB")
                dsvsession.close()
                session.close()
                return

            try:
                prd_students = [Student(
                    id=int(student.id),
                    name=str(student.name),
                    registry=int(student.registry),
                    discord_id=int(student.discord_id)
                ) for student in dsv_students]

                prd_subjects = [Subject(
                    id=int(subject.id),
                    code=str(subject.code),
                    fullname=str(subject.fullname),
                    semester=int(subject.semester)
                ) for subject in dsv_subjects]
                print("---------- Subjects and students copied ----------")
            except Exception as e:
                print("Exception caught while sanitizing data")
                dsvsession.close()
                session.close()
                return

            try:
                dsvsession.expunge_all()
                session.add_all(prd_students)
                session.add_all(prd_subjects)
                print("---------- Data added to PRD session ----------")
            except Exception:
                print("Exception caught while adding current data to PRD session")
                dsvsession.close()
                session.close()
                return

            try:
                session.commit()
                dsvsession.rollback()
                print("---------- Changes committed ----------")
                await ctx.send("Feito. Verifique o log para confirmação.")
            except Exception:
                print("Exception caught while committing changes to PRD DB")
            finally:
                dsvsession.close()
                session.close()
