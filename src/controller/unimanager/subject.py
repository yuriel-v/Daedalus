# Módulo de controle de matérias.
# Nota: Somente o proprietário do bot pode invocar alguns desses comandos!
from controller.ferozes import ferozes
from controller.misc import smoothen, split_args
from discord.ext.commands.core import is_owner
from discord.message import Message
from discord.ext import commands
from dao.unimanager.subjectdao import SubjectDao


class SubjectController(commands.Cog, name='Subject Controller: mt'):
    def __init__(self, bot):
        self.bot = bot
        self.read_only_cmds = ('buscar', 'todas')
        self.sbdao = SubjectDao()

        self.cmds = {
            'add': self.add_subject,
            'buscar': self.find_subject,
            'todas': self.find_all,
            'editar': self.edit_subject
        }

    def ferozes():
        async def predicate(ctx):
            return ctx.guild.id == ferozes
        return commands.check(predicate)

    async def cog_after_invoke(self, ctx):
        self.sbdao.sclear()

    @commands.command('mt')
    @ferozes()
    async def select_command(self, ctx: commands.Context):
        """
        Comando mestre para o cog Subject Controller.
        - P.S. Usuários que não forem o proprietário do bot só podem visualizar matérias (read-only).
        """
        command = next(iter(split_args(ctx.message.content)), "").lower()

        if not is_owner() and command not in self.read_only_cmds:
            await ctx.send("Somente o proprietário do bot pode utilizar esse comando.")
        elif command in self.cmds.keys():
            await self.cmds[command](ctx)
        else:
            await ctx.send("Comando inválido. Sintaxe: `>>mt comando argumentos`")

    async def add_subject(self, ctx: commands.Context):
        """
        Adiciona uma matéria nova.
        - Sintaxe: `mt add CDE SM Nome da Matéria`, onde:
          - `CDE`: Código, uma sigla de precisamente 3 letras, única entre todas as matérias registradas.
          - `SM`: Semestre, um número inteiro de 0-8 indicando o semestre.
            - Semestre 0 significa que a matéria é eletiva (elo).
          - Exemplo: `mt add BD2 4 Banco de Dados II`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        if len(arguments) <= 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>mt add BD2 4 Banco de Dados II`.")
        else:
            msg: Message = await ctx.send('Adicionando matéria...')
            try:
                statuses = (
                    "Matéria registrada com sucesso.",
                    "Algo deu errado. Consulte o log para detalhes.",
                    "Sintaxe inválida. Exemplo: `>>mt add BD2 4 Banco de Dados II`."
                )
                ret = self.sbdao.insert(code=arguments[0], fullname=' '.join(arguments[2::]), semester=abs(int(arguments[1])))
                await msg.edit(content=statuses[ret])
            except Exception as e:
                print(f"Exception caught at adding subject: {e}\n Stack trace: {e.__traceback__}")
                await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")

    async def find_subject(self, ctx: commands.Context):
        """
        Procura uma matéria existente.
        - Sintaxe: `mt buscar filtro`, onde `filtro` pode ser:
          - Uma string de 3 ou menos caracteres, caracterizando uma busca por código;
          - Uma string de 4 ou mais caracteres, caracterizando uma busca por nome.
          - Exemplos: `mt buscar banco` ou `mt buscar bd`
        """
        subject = split_args(ctx.message.content, prefixed=True)
        if len(subject) == 0 or not subject[1].isnumeric():
            await ctx.send("Sintaxe inválida. Exemplos: `>>mt buscar banco` ou `mt buscar bd`.")
        else:
            msg: Message = await ctx.send('Buscando matéria...')
            try:
                matches = self.sbdao.find(' '.join(subject))
                if matches is None:
                    await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")
                elif len(matches) == 0:
                    await msg.edit(content="Nenhuma matéria foi encontrado para esse critério.")
                else:
                    await msg.edit(content=f"Encontrada(s): ```{smoothen(matches)}```")
            except Exception as e:
                print(f"Exception caught at finding one subject: {e}\n Stack trace: {e.__traceback__}")
                await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")

    async def find_all(self, ctx: commands.Context):
        """
        Retorna uma lista com todas as matérias cadastradas.
        - Para evitar spam, o semestre deve ser informado.
        - Sintaxe: `mt todas sem`
          - Exemplo: `mt todas primeiro`
        """
        arguments = split_args(ctx.message.content, prefixed=True)
        syntax_error = "Sintaxe inválida. Exemplo: `>>mt todas primeiro`."
        sem = None
        msg: Message = await ctx.send('Buscando matérias...')
        if len(arguments) == 0:
            await msg.edit(content=syntax_error)
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
                await msg.edit(content=syntax_error)
                return

        try:
            all_subjects = self.sbdao.find_by_semester(sem)
            if len(all_subjects) == 0:
                await msg.edit(content="Registro(s) não encontrado(s).")
            else:
                # remnants of the days when this wasn't limited by semester
                # all_subjects = {x.semester: [str(y) for y in all_subjects if y.semester == x.semester] for x in all_subjects}
                # for x in all_subjects.keys():
                #     await ctx.send(f"```{smoothen(all_subjects[x])}```")
                await msg.edit(content=f'Matérias encontradas: ```{smoothen(list(all_subjects))}```')
        except Exception as e:
            print(f"Exception caught at finding all subjects by semester: {e}\n Stack trace: {e.__traceback__}")
            await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")

    async def edit_subject(self, ctx: commands.Context):
        """
        Edita uma matéria em específico.
        - Sintaxe: `mt editar mtr cmp newval`, onde:
          - `mtr`: Código da matéria;
          - `cmp`: Campo a editar (`nome`, `cod`, `sem` ou `todos`);
          - `newval`: Novo valor.
          - Exemplos: `mt editar AL1 cod ALG`, `mt editar AL1 nome Algoritmos 1`,
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
            msg: Message = await ctx.send('Editando matéria...')
            statuses = (
                "Editada:",
                "Algo deu errado. Consulte o log para detalhes.",
                syntax_error,
                "A matéria informada não existe."
            )
            try:
                arguments[0] = arguments[0].upper()
                arguments[1] = arguments[1].lower()
                if arguments[1] == 'cod':
                    res = self.sbdao.update(arguments[0], newcode=arguments[2].upper())
                    op = 2
                elif arguments[1] == 'nome':
                    res = self.sbdao.update(arguments[0], fullname=' '.join(arguments[2::]))
                    op = 0
                elif arguments[1] == 'todos' and len(arguments) >= 5:
                    res = self.sbdao.update(code=arguments[0], newcode=arguments[2].upper(), semester=abs(int(arguments[3])), fullname=' '.join(arguments[4::]))
                    op = 2
                elif arguments[1] == 'sem' and arguments[2].isnumeric():
                    res = self.sbdao.update(code=arguments[0], semester=abs(int(arguments[2])))
                    op = 0
                else:
                    res = 1

                if res == 0:
                    edited_sbj = self.sbdao.find(arguments[op].upper())
                    await msg.edit(content=statuses[0] + f"```{smoothen(str(edited_sbj))}```")
                else:
                    await msg.edit(content=statuses[res])
            except Exception as e:
                print(f"Exception caught at editing subject: {e}\n Stack trace: {e.__traceback__}")
                await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")

    def cog_info(self, command=None) -> str:
        if command is not None and str(command).lower() in self.cmds.keys():
            reply = f'-- mt {str(command).lower()} --\n' + self.cmds[str(command)].__doc__
        else:
            nl = '\n'
            reply = f"""
            mt: Subject Controller
            Este módulo gerencia cadastros de matérias.
            Usuários comuns (não-proprietários) só podem usar comandos de busca (leitura em geral).\n
            Comandos incluem:
            {nl.join([f'- {x}' for x in self.cmds.keys()])}
            """

        return '\n'.join([x.strip() for x in reply.split('\n')]).strip()
