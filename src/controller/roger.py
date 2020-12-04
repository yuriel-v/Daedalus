# Memes do Roger.
from asyncio.tasks import sleep
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.file import File
from discord.embeds import Embed
from discord.colour import Colour
from os import listdir
from os.path import isfile, join
from random import randint


class Roger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roger_respostas = {
            1: "SE LASCAR",
            2: "sim, é justo",
            3: "escreva novamente, serumaninho",
            4: "Justo",
            5: "Pega no meu canudo",
            6: "NA tu",
            7: "NA você, NA eu, NA todo mundo",
            8: "Cacilda"
        }

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Calma, rapaz. Sem pressa, tem um pouco de Roger pra todo mundo.")
        else:
            print(f"Exception raised: {error}")

    @commands.command('?')
    @commands.cooldown(rate=1, per=10, type=BucketType.user)
    async def roger(self, ctx):
        """Você perguntou? O Roger aparece!"""
        if ctx.prefix != 'Roger ':
            return

        roger_pics = [f for f in listdir('./src/roger') if isfile(join('./src/roger', f))]
        fn = str(roger_pics[randint(0, len(roger_pics) - 1)])
        pic = File(f'./src/roger/{fn}', fn)
        embed = Embed(description=fn, colour=Colour(randint(0x000000, 0xFFFFFF)))
        embed.set_image(url=f"attachment://{fn}")

        await ctx.send(file=pic, embed=embed)
        if fn == 'julio_cobra.png':
            original_roles = [x for x in ctx.author.roles if x.name != '@everyone']

            try:
                for role in original_roles:
                    await ctx.author.remove_roles(role)
            except Exception as e:
                if 'missing permissions' in str(e).lower():
                    ctx.send(u"Deu sorte, malandro. Não tenho permissão pra te mandar pro xilindró.")
                return

            await ctx.send("Como você tirou o julio_cobra.png, você vai virar prisioneiro por dois minutos.")
            await ctx.author.add_roles(ctx.guild.get_role(778774271869583480))
            await sleep(120)
            try:
                await ctx.author.remove_roles(ctx.guild.get_role(778774271869583480))
                for role in original_roles:
                    await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention}: Você não é mais prisioneiro.")
            except Exception as e:
                if 'unknown member' in str(e).lower():
                    escaped = f"""Bem, parece que {ctx.author.name} fugiu da prisão...\n
                    Ele(a) tinha essas roles: `{[r.name for r in original_roles]}`\n
                    Se ele(a) for visto(a) novamente, entreguem essas roles de volta porque eu tô me lixando.
                    """
                    await ctx.send(escaped)

    @commands.command('responde:')
    async def roger_responde(self, ctx):
        """
        Roger responde: Eu sou bom programador?
        Roger diz: SE LASCAR
        """
        if ctx.prefix != 'Roger ':
            return

        await ctx.send(f"<@450731404532383765> diz: {self.roger_respostas[randint(1, len(self.roger_respostas.keys()))]}")
