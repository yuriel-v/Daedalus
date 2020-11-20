# Memes do Roger.
from asyncio.tasks import sleep
from discord.ext import commands
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
            7: "NA você, NA eu, NA todo mundo"
        }

    @commands.command('?')
    async def roger(self, ctx):
        """Você perguntou? O Roger aparece!"""
        if ctx.prefix != 'Roger ':
            return

        roger_pics = [f for f in listdir('./roger') if isfile(join('./roger', f))]
        fn = str(roger_pics[randint(0, len(roger_pics) - 1)])
        pic = File(f'./roger/{fn}', fn)
        embed = Embed(description=fn, colour=Colour(randint(0x000000, 0xFFFFFF)))
        embed.set_image(url=f"attachment://{fn}")

        await ctx.send(file=pic, embed=embed)
        if fn == 'julio_cobra.png':
            original_roles = [x for x in ctx.author.roles if x.name != '@everyone']

            try:
                for role in original_roles:
                    await ctx.author.remove_roles(role)
            except Exception as e:
                ctx.send("Deu sorte, malandro. Não tenho permissão pra te mandar pro xilindró. \N{GUN}")
                return

            await ctx.author.add_roles(ctx.guild.get_role(778774271869583480))
            await ctx.send("Como você tirou o julio_cobra.png, você vai virar prisioneiro por dois minutos.")
            await sleep(120)
            await ctx.author.remove_roles(ctx.guild.get_role(778774271869583480))
            for role in original_roles:
                await ctx.author.add_roles(role)

    @commands.command('responde:')
    async def roger_responde(self, ctx):
        """
        Roger responde: Eu sou bom programador?
        Roger diz: SE LASCAR
        """
        if ctx.prefix != 'Roger ':
            return

        await ctx.send(f"<@450731404532383765>: {self.roger_respostas[randint(1, len(self.roger_respostas.keys()))]}")
