# Memes do Roger.
import requests

from asyncio.tasks import sleep
from cogs.dbc import DaedalusBaseCog
from core.utils import yaml, print_exc
from discord import Message
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.embeds import Embed
from discord.colour import Colour
from os import getenv
from random import randint


class RogerDotNet(DaedalusBaseCog, name='Roger'):
    def __init__(self, bot):
        self.bot = bot
        with open('./src/resources/roger.yml', encoding='utf-8') as file:
            self.roger_respostas = yaml.load(file)['roger_respostas']
        self.cmds = {
            '?': self.roger_foto,
            'responde': self.roger_responde
        }

        nl = '\n'
        self._help_info = f"""
        Roger hotline: Fale com o Roger!
        A nossa emulação do Roger, auxiliada pela própria lenda em charme e osso, responde às suas perguntas
        com `Roger responde:` e, caso tenha saudades do mito, só pergunte pelo Roger com `Roger ?` (com espaço!)
        que ele aparece em uma de dezenas de fotos lendárias!
        Mas tenha cuidado com o Julio e a sua cobra de estimação.\n
        Comandos incluem:
        {nl.join([f'- {x}' for x in self.cmds.keys()])}
        """
        self._help_info = '\n'.join([x.strip() for x in self._help_info.split('\n')]).strip()

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Calma, rapaz. Sem pressa, tem um pouco de Roger pra todo mundo.")
        else:
            print(f"Exception raised: {error}")

    @commands.command(name='?')
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def roger_foto(self, ctx: commands.Context):
        """Você perguntou? O Roger aparece!"""
        msg: Message = await ctx.send("Invocando o Roger...")
        try:
            roger_img = self._fetch_roger_image()
            embed = Embed(description=roger_img[0], colour=Colour(randint(0x000000, 0xFFFFFF)))
            embed.set_image(url=roger_img[1])

            if roger_img[0].lower() == "julio_cobra":
                cobra = True
                ct = 'Cacilda, agora a cobra fumou. Você tirou o julio_cobra.'
            else:
                cobra = False
                ct = None
            await msg.edit(content=ct, embed=embed)

            if cobra and ctx.guild.id == 567817989806882818:
                await self._aprisionar(ctx)

        except Exception as e:
            await msg.edit("Ih, deu zica.")
            print_exc("Zica thrown:")

    def _fetch_roger_image(self):
        endpoint = "https://api.imgur.com/3/album/xv4Jn5D/images"
        response = requests.get(url=endpoint, headers={'Authorization': f"Client-ID {getenv('DAEDALUS_IMGUR_TOKEN')}"}).json()['data']
        image = response[randint(0, len(response) - 1)]

        return (image['description'], image['link'])

    async def _aprisionar(self, ctx: commands.Context):
        original_roles = [x for x in ctx.author.roles if x.name != '@everyone']
        try:
            for role in original_roles:
                await ctx.author.remove_roles(role)
        except Exception as e:
            if 'missing permissions' in str(e).lower():
                ctx.send(u"Deu sorte, malandro. Não tenho permissão pra te mandar pro xilindró.")
            return

        await ctx.send("Por causa disso, você vai virar prisioneiro por dois minutos.")
        await ctx.author.add_roles(ctx.guild.get_role(778774271869583480))
        await sleep(120)
        try:
            await ctx.author.remove_roles(ctx.guild.get_role(778774271869583480))
            for role in original_roles:
                await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention}: Você não é mais prisioneiro.")
        except Exception as e:
            if 'unknown member' in str(e).lower():
                # needed to avoid weird indentation shenanigans
                escaped = f"Bem, parece que {ctx.author.name} fugiu da prisão...\n"
                escaped += f"Ele(a) tinha essas roles: `{[r.name for r in original_roles]}`\n"
                escaped += "Se ele(a) for visto(a) novamente, entreguem essas roles de volta porque eu tô me lixando."
                await ctx.send(escaped)

    @commands.command('responde:')
    async def roger_responde(self, ctx: commands.Context, *, arguments=None):
        """
        https://i.gyazo.com/dc5e9bb1f93ebc622b9ae36e3c370fc8.png
        """
        if arguments:
            await ctx.send(f"<@450731404532383765> diz: {self.roger_respostas[randint(1, len(self.roger_respostas.keys()))]}")
        else:
            await ctx.send(f"<@450731404532383765> diz: Se lascar, pergunta alguma coisa!")
