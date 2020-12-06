"""
Core para o bot Daedalus.

Comandos aqui são somente para fins de teste. Comandos mais sofisticados
deverão ser adicionados a um "cog", um conjunto de comandos separado e adicionado
ali embaixo com o comando "bot.add_cog(Cogname(bot))".
--
Autor: Leonardo Valim

Licenciado sob a MIT License.
Ou seja, faça o que bem entender, eu estou pouco me lixando.
Contanto que me dê o crédito, claro.
"""

# Essenciais
from os import getenv
from discord.ext import commands
from sqlalchemy.orm import close_all_sessions
from dao import engin, dsvengin, smkr, dsvsmkr
from model import initialize_sql

# Imports de módulos customizados
from controller.misc import Misc, split_args, arg_types, smoothen
from controller.games import Games
from controller.roger import Roger
from controller.student import StudentController
from controller.scheduler import ScheduleController
from controller.subject import SubjectController

# Por alguma causa, motivo, razão ou circunstância, se esses imports não
# forem feitos, o sistema não mapeia os objetos.
from model.student import Student
from model.subject import Subject
# from model.assigned import Assigned
from model.exam import Exam
from model.registered import Registered

# Inicialização
daedalus_token = getenv("DAEDALUS_TOKEN")
bot = commands.Bot(command_prefix=['>>', 'Roger '])
daedalus_version = '0.4.3'
daedalus_environment = getenv("DAEDALUS_ENV").upper()
initialize_sql(engin)
if daedalus_environment == "DSV":
    initialize_sql(dsvengin)


# Cogs
bot.add_cog(Misc(bot))
bot.add_cog(Games(bot))
bot.add_cog(Roger(bot))
bot.add_cog(StudentController(bot))
bot.add_cog(SubjectController(bot))
bot.add_cog(ScheduleController(bot))


@bot.command('version')
async def show_version(ctx):
    await ctx.send(f"Project Daedalus v{daedalus_version} ({daedalus_environment})")


@bot.command()
async def hello(ctx):
    """Hello, WARUDO!!"""
    await ctx.send(f"Hello, {ctx.author.name} - or should I call you {ctx.author.nick}? Either way, hello.")


@bot.command()
async def argcount(ctx):
    arguments = split_args(ctx.message.content)
    await ctx.send(f"Arguments passed: {len(arguments)}\nArguments themselves: `{arguments}`\nArgument classes: {arg_types(arguments, repr=True)}")


@bot.command()
async def listroles(ctx):
    await ctx.send(f"Suas roles: `{[r.name for r in ctx.author.roles if r.name != '@everyone']}`")


@bot.command('log')
async def tolog(ctx):
    print(split_args(ctx.message.content, islist=False))


@bot.command('fmt')
async def fmt(ctx):
    await ctx.send(f"```{smoothen(split_args(ctx.message.content, islist=False))}```")


@bot.command('drop')
async def drop_tables(ctx):
    if str(ctx.author.id) != getenv("DAEDALUS_OWNERID"):
        await ctx.send("Somente o proprietário pode rodar esse comando.")
        return
    Exam.__table__.drop()
    Registered.__table__.drop()
    initialize_sql(engin)
    await ctx.send("Feito. Verifique o log para confirmação.")


@bot.command('backup')
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
            cur_students = session.query(Student).all()
            cur_subjects = session.query(Subject).all()
            bk_students = []
            bk_subjects = []
            print("---------- Subjects and students fetched ----------")
        except Exception as e:
            print(f"Exception caught while fetching current data from PRD DB: {e}")
            dsvsession.close()
            session.close()
            return

        try:
            # clean of any relationships
            for student in cur_students:
                bk_students.append(Student(
                    id=int(student.id),
                    name=str(student.name),
                    registry=int(student.registry),
                    discord_id=int(student.discord_id)
                ))

            for subject in cur_subjects:
                bk_subjects.append(Subject(
                    id=int(subject.id),
                    code=str(subject.code),
                    fullname=str(subject.fullname),
                    semester=int(subject.semester)
                ))
            print("---------- Subjects and students sanitized ----------")
        except Exception as e:
            print("Exception caught while sanitizing data")
            dsvsession.close()
            session.close()
            return

        try:
            session.expunge_all()
            dsvsession.add_all(bk_students)
            dsvsession.add_all(bk_subjects)
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


@bot.command('restore')
async def move_to_prd_db(ctx):
    if str(ctx.author.id) != getenv("DAEDALUS_OWNERID"):
        await ctx.send("Somente o proprietário pode rodar esse comando.")
    elif daedalus_environment != "DSV":
        return
    else:
        try:
            dsvsession = dsvsmkr()
            session = smkr()
        except Exception:
            print("Exception caught while initializing sessions and databases")
            return

        try:
            cur_students = dsvsession.query(Student).all()
            cur_subjects = dsvsession.query(Subject).all()
        except Exception:
            print("Exception caught while fetching current data from DSV DB")
            dsvsession.close()
            session.close()
            return

        try:
            dsvsession.expunge_all()
            session.add_all(cur_students)
            session.add_all(cur_subjects)
        except Exception:
            print("Exception caught while adding current data to PRD session")
            dsvsession.close()
            session.close()
            return

        try:
            session.commit()
            dsvsession.rollback()
            await ctx.send("Feito. Verifique o log para confirmação.")
        except Exception:
            print("Exception caught while committing changes to PRD DB")
        finally:
            dsvsession.close()
            session.close()

# Aqui é só a parte de rodar e terminar o bot.
bot.run(daedalus_token)
close_all_sessions()
print('Bye')
