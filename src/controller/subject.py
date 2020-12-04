# Módulo de controle de matérias.
# Nota: Somente o proprietário do bot pode invocar esses comandos!
from os import getenv
from controller.misc import smoothen, split_args, dprint
from discord.ext import commands
from controller import sbdao


class SubjectController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
        nenhuma matéria pode ter a mesma sigla que outra matéria). Já o campo 'SM'
        é um inteiro de 0-8 indicando o semestre. Semestre 0 é para matérias eletivas.

        Sintaxe: `mt add CDE SM Nome da Matéria`

        Exemplo: `mt add BD2 4 Banco de Dados II`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) <= 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>mt add BD2 4 Banco de Dados II`.")
        else:
            try:
                ret = sbdao.insert(code=arguments[0], fullname=' '.join(arguments[2::]), semester=abs(int(arguments[1])))
                if ret == 1:
                    await ctx.send("Sintaxe inválida. Exemplo: `>>mt add BD2 4 Banco de Dados II`.")
                elif ret == 2:
                    await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
                else:
                    await ctx.send("Matéria registrada com sucesso.")
            except Exception as e:
                print(f"Exception caught: {e}")
                await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")

    async def find_subject(self, ctx: commands.Context):
        """
        Procura uma matéria existente. Se o nome dado for de comprimento 3 ou
        menor, uma busca por código é realizada. Senão, uma busca por nome
        completo é realizada. Caso o filtro especificado for numérico, retorna
        todas as matérias do semestre especificado.

        Sintaxe: `mt buscar filtro`

        Exemplos: `mt buscar banco`, `mt buscar bd` ou `mt buscar 4`
        """
        subject = split_args(ctx.message.content, prefixed=True)
        if len(subject) == 0 or not subject[1].isnumeric():
            await ctx.send("Sintaxe inválida. Exemplos: `>>mt buscar banco`, `mt buscar bd` ou `mt buscar 4`.")
        else:
            try:
                matches = sbdao.find(' '.join(subject))
                if matches is None:
                    await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
                elif len(matches) == 0:
                    await ctx.send("Nenhuma matéria foi encontrado para esse critério.")
                else:
                    await ctx.send(f"Encontrada(s): ```{smoothen(matches)}```")
            except Exception as e:
                print(f"Exception caught: {e}")
                await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")

    async def find_all(self, ctx: commands.Context):
        """
        Retorna uma lista com todas as matérias cadastradas.
        Para evitar spam, o semestre deve ser informado.

        Sintaxe: `mt todas sem`

        Exemplo: `mt todas primeiro`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        syntax_error = "Sintaxe inválida. Exemplo: `>>mt todas primeiro`."
        sem = None
        if len(arguments) == 0:
            await ctx.send(syntax_error)
            return
        elif arguments[0].isnumeric() and int(arguments[0]) in range(0, 9):
            sem = int(arguments[0])
        else:
            numbas = {
                0: ["elo", 'eletivas'], 1: ['primeiro'], 2: ['segundo'],
                3: ['terceiro'], 4: ['quarto'], 5: ['quinto'],
                6: ['sexto'], 7: ['setimo', 'sétimo'], 8: ['oitavo']
            }
            sem = next(iter([key for key, value in numbas.items() if arguments[0].lower() in value]), None)
            if sem is None:
                await ctx.send(syntax_error)
                return

        all_subjects = sbdao.find_by_semester(sem)
        if len(all_subjects) == 0:
            await ctx.send("Registro(s) não encontrado(s).")
        else:
            all_subjects = {x.semester: [str(y) for y in all_subjects if y.semester == x.semester] for x in all_subjects}
            for x in all_subjects.keys():
                await ctx.send(f"```{smoothen(all_subjects[x])}```")

    async def edit_subject(self, ctx: commands.Context):
        """
        Edita uma matéria em específico.

        Sintaxe: `mt editar mtr cmp newval`, onde `mtr = matéria (código)`,
        `cmp = campo` ('nome', 'cod', 'sem' ou 'todos') e `newval = novo valor`.

        Exemplos: `mt editar AL1 cod ALG`, `mt editar AL1 nome Algoritmos 1`,
        `mt editar AL1 sem 1` ou `mt editar AL1 todos ALG 0 Algoritmos 1`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        syntax_error = "Sintaxe inválida. Exemplos: `mt editar AL1 cod ALG`, `mt editar AL1 nome Algoritmos 1`, "
        syntax_error += "`mt editar AL1 sem 0` ou `mt editar AL1 todos ALG 0 Algoritmos 1`."
        if len(arguments) < 3:
            await ctx.send(syntax_error)
        else:
            res = None
            op = None
            arguments[0] = arguments[0].upper()
            arguments[1] = arguments[1].lower()
            if arguments[1] == 'cod':
                res = sbdao.update(arguments[0], newcode=arguments[2].upper())
                op = 2
            elif arguments[1] == 'nome':
                res = sbdao.update(arguments[0], fullname=' '.join(arguments[2::]))
                op = 0
            elif arguments[1] == 'todos' and len(arguments) >= 5:
                res = sbdao.update(code=arguments[0], newcode=arguments[2].upper(), semester=abs(int(arguments[3])), fullname=' '.join(arguments[4::]))
                op = 2
            elif arguments[1] == 'sem' and arguments[2].isnumeric():
                res = sbdao.update(code=arguments[0], semester=abs(int(arguments[2])))
                op = 0
            else:
                res = 1

            if res == 1:
                await ctx.send(syntax_error)
            elif res == 2:
                await ctx.send("A matéria informada não existe.")
            elif res == 3:
                await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
            else:
                edited_sbj = sbdao.find(arguments[op].upper())
                if len(edited_sbj) == 0:
                    await ctx.send("Alguma coisa deu errado. Consulte o log para detalhes.")
                else:
                    await ctx.send(f"Editada: ```{smoothen(str(edited_sbj[0]))}```")
