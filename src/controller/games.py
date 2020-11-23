# Módulo de joguinhos (espero que) inofensivos.
from discord.ext import commands
from random import randint

from discord.ext.commands.cooldowns import BucketType
from controller.misc import split_args, dprint
from asyncio.tasks import sleep


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eightball_replies = {
            1: "As I see it, yes.",
            2: "Ask again later.",
            3: "Better not tell you now.",
            4: "Cannot predict now.",
            5: "Concentrate and ask again.",
            6: "Don't count on it.",
            7: "It is certain.",
            8: "It is decidedly so.",
            9: "Most likely.",
            10: "My reply is no.",
            11: "My sources say no.",
            12: "Outlook not so good.",
            13: "Outlook good.",
            14: "Reply hazy, try again.",
            15: "Signs point to yes.",
            16: "Very doubtful.",
            17: "Without a doubt.",
            18: "Yes.",
            19: "Yes - definitely.",
            20: "You may rely on it."
        }

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Calma, rapaz. Sem spam.")
        else:
            print(f"Exception raised: {error}")

    # Bola 8 mágica
    @commands.command(name='8ball')
    async def eight_ball(self, ctx):
        """Consulta a omnisciente bola 8 para responder uma pergunta."""
        await ctx.send(f"{ctx.message.author.mention}: {self.eightball_replies[randint(1, 20)]}")

    # Roleta Russa
    @commands.command(name='rr')
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def russian_roulette(self, ctx):
        """
        Roleta russa com N opções. Se o trigger cair no meio delas, você vai morrer por (opções / 2) minutos. 6 opções por padrão.\n
        Sintaxe: >>rr opções\n
        Exemplo: >>rr 10\n
        P.S. Não chame o bot de diabo e mande ele morrer ao mesmo tempo, ele fica nervoso.
        """
        arguments = split_args(ctx.message.content)
        options = 6
        if len(arguments) > 0 and str(arguments[0]).isnumeric() and int(arguments[0]) > 1:
            options = abs(int(arguments[0]))

        trigger = randint(1, options)

        morre_diabo = False
        if len(arguments) >= 2:
            morre_diabo = 'morre' in arguments[0].lower() and 'diabo' in arguments[1].lower()
        dprint(f"Roleta para {' '.join(arguments)}: {options} opções.")

        if trigger == options // 2 or morre_diabo:
            original_roles = [x for x in ctx.author.roles if x.name != '@everyone']
            if not morre_diabo:
                await ctx.send(u'<:ikillu:700684891251277904> \U0001F4A5')
            else:
                await ctx.send(u"<:morrediabo:779864127249055795><:ikillu:700684891251277904> \U0001F4A5")
            try:
                respawn = (options // 2) * 60
                response = None
                if morre_diabo:
                    response = "ENTÃO MORRE, DIABO!"
                    dprint(f"O DIABO {str(ctx.author.name).upper()} MORREU!!")
                else:
                    response = f"{ctx.author.mention} morreu! Respawn em {respawn} segundos..."

                for role in original_roles:
                    await ctx.author.remove_roles(role)
                await ctx.send(response)
                await ctx.author.add_roles(ctx.guild.get_role(778774271869583480))
                await sleep(respawn)
                try:
                    await ctx.author.remove_roles(ctx.guild.get_role(778774271869583480))
                    for role in original_roles:
                        await ctx.author.add_roles(role)
                    if not morre_diabo:
                        await ctx.send(f"{ctx.author.mention}: Levante e ande!")
                    else:
                        await ctx.send(f"{ctx.author.mention}: EU QUERO QUE VOCÊ SE FODA, SEU FILHO DE UMA PUTA! <:morrediabo:779864127249055795>")
                except Exception as e:
                    if 'unknown member' in str(e).lower():
                        await ctx.send(f"Parece que {ctx.author.name} morreu de vez...")
                    else:
                        print(f"Exception raised: {e}")
            except Exception as e:
                if 'missing permisisons' in str(e).lower():
                    await ctx.send(f"A arma atirou, mas parece que {ctx.author.name} é imortal...")
                else:
                    print(f"Exception raised: {e}")

        else:
            await ctx.send(u'<:ikillu:700684891251277904> \U0001F389')
            await ctx.send(f"{ctx.author.mention} deu sorte! A bala era de mentira!")
