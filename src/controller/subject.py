# Módulo de controle de matérias.
# Nota: Somente o proprietário do bot pode invocar esses comandos!
from os import getenv
from controller.misc import smoothen, split_args, dprint
from discord.ext import commands
from dao.subjectdao import SubjectDao


class SubjectController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sbdao = SubjectDao()
        self.read_only_cmds = {'buscar', 'todas'}

    @commands.command('mt')
    async def subject_controller(self, ctx: commands.Context):
        # Usuários comuns só têm acesso aos comandos read-only.
        command = next(iter(split_args(ctx.message.content)), "").lower()

        if str(ctx.author.id) != getenv("DAEDALUS_OWNERID") and command not in self.read_only_cmds:
            await ctx.send("Somente o proprietário do bot pode utilizar esse comando.")
            return

        if command == "add":
            await self.add_subject(ctx)
        elif command == "buscar":
            await self.find_subject(ctx)
        elif command == "todas":
            await self.find_all(ctx)
        elif command == "editar":
            await self.edit_subject(ctx)

    async def add_subject(self, ctx: commands.Context):
        """
        Adiciona uma matéria nova. O campo 'CDE' (código) deve ser uma sigla de,
        precisamente, 3 letras que unicamente representem a matéria (ou seja,
        nenhuma matéria pode ter a mesma sigla que outra matéria).

        Sintaxe: `mt add CDE Nome da Matéria`

        Exemplo: `mt add BD2 Banco de Dados II`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) < 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>mt add BD2 Banco de Dados II`.")
        else:
            ret = self.sbdao.insert(arguments[0], ' '.join(arguments[1::]))
            if ret == 1:
                await ctx.send("Sintaxe inválida. Exemplo: `>>mt add BD2 Banco de Dados II`.")
            elif ret == 2:
                await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
            else:
                await ctx.send("Matéria registrada com sucesso.")

    async def find_subject(self, ctx: commands.Context):
        """
        Procura uma matéria existente. Se o nome dado for de comprimento 3 ou
        menor, uma busca por código é realizada. Senão, uma busca por nome
        completo é realizada.

        Sintaxe: `mt buscar filtro`

        Exemplos: `mt buscar banco` ou `mt buscar bd`
        """
        subject = split_args(ctx.message.content, prefixed=True, islist=False)
        if len(subject) == 0:
            await ctx.send("Sintaxe inválida. Exemplos: `>>mt buscar banco` ou `>>mt buscar bd`.")
        else:
            matches = self.sbdao.find(subject)
            if len(matches) == 0:
                await ctx.send("Nenhuma matéria foi encontrado para esse critério.")
            else:
                await ctx.send(f"Encontrada(s): {smoothen(matches)}")

    async def find_all(self, ctx: commands.Context):
        """
        Retorna uma lista com todas as matérias cadastradas.

        Sintaxe: `mt todas`
        """
        all_subjects = self.sbdao.find_all()
        if len(all_subjects) == 0:
            await ctx.send("Nenhuma matéria foi registrada ainda.")
        else:
            await ctx.send(f"Matérias existentes: {smoothen([str(x) for x in all_subjects])}")

    async def edit_subject(self, ctx: commands.Context):
        """
        Edita uma matéria em específico.

        Sintaxe: `mt editar mtr cmp newval`, onde `mtr = matéria (código)`,
        `cmp = campo` ('nome', 'cod' ou 'ambos') e `newval = novo valor`.

        Exemplos: `mt editar AL1 cod ALG`, `mt editar AL1 nome Algoritmos 1`,
        ou `mt editar AL1 ambos ALG Algoritmos 1`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        syntax_error = "Sintaxe inválida. Exemplos: `mt editar AL1 cod ALG`, `mt editar AL1 nome Algoritmos 1`, ou `mt editar AL1 ambos ALG Algoritmos 1`."
        if len(arguments) < 3:
            await ctx.send(syntax_error)
        else:
            res = None
            op = None
            arguments[0] = arguments[0].upper()
            arguments[1] = arguments[1].lower()
            if arguments[1] == 'cod':
                res = self.sbdao.update(arguments[0], newcode=arguments[2].upper())
                op = 2
            elif arguments[1] == 'nome':
                res = self.sbdao.update(arguments[0], fullname=' '.join(arguments[2::]))
                op = 0
            elif arguments[1] == 'ambos' and len(arguments) >= 4:
                res = self.sbdao.update(arguments[0], newcode=arguments[2].upper(), fullname=' '.join(arguments[3::]))
                op = 2
            else:
                res = 1

            if res == 1:
                await ctx.send(syntax_error)
            elif res == 2:
                await ctx.send("A matéria informada não existe.")
            elif res == 3:
                await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
            else:
                edited_sbj = self.sbdao.find(arguments[op].upper())
                if len(edited_sbj) == 0:
                    await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
                else:
                    await ctx.send(f"Editada: {smoothen(str(edited_sbj[0]))}")
