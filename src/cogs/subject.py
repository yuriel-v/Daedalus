# Módulo de controle de matérias.
# Nota: Somente o proprietário do bot pode invocar alguns desses comandos!
from core.utils import smoothen, print_exc
from db.dao import SubjectDao
from discord.message import Message
from discord.ext import commands


class SubjectController(commands.Cog, name='Subject Controller: mt'):
    def __init__(self, bot):
        self.bot = bot
        self.read_only_cmds = ('buscar', 'todas')
        self.sbdao = SubjectDao()

        self.cmds = {
            'add': self.add_subject,
            'buscar': self.find_subject,
            'editar': self.edit_subject
        }

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("Somente o proprietário do bot pode usar esse comando.")
        else:
            print_exc("(SubjectController) Exception raised:", error)

    @commands.group('mt')
    async def subject(self, ctx: commands.Context):
        """
        Comando mestre para o cog Subject Controller.
        - P.S. Usuários que não forem o proprietário do bot só podem visualizar matérias (read-only).
        """
        if ctx.subcommand_passed is None:
            await ctx.send("Sintaxe: `>>mt comando argumentos`")

        elif ctx.invoked_subcommand is None:
            await ctx.send("Comando inválido. Sintaxe: `>>mt comando argumentos`\nPara uma lista de comandos, use `>>help mt`.")

    @subject.command(name='add')
    @commands.is_owner()
    async def add_subject(self, ctx: commands.Context, *, arguments=''):
        """
        Adiciona uma matéria nova.
        - Sintaxe: `mt add CDE SM Nome da Matéria`, onde:
          - `CDE`: Código, uma sigla de precisamente 3 letras, única entre todas as matérias registradas.
          - `SM`: Semestre, um número inteiro de 0-8 indicando o semestre.
            - Semestre 0 significa que a matéria é eletiva (elo).
          - Exemplo: `mt add BD2 4 Banco de Dados II`
        """
        arguments = arguments.split()
        if len(arguments) <= 2:
            await ctx.send("Sintaxe inválida. Exemplo: `>>mt add BD2 4 Banco de Dados II`.")
        else:
            msg: Message = await ctx.send('Adicionando matéria...')
            try:
                statuses = (
                    "Algo deu errado. Consulte o log para detalhes.",
                    "Sintaxe inválida. Exemplo: `>>mt add BD2 4 Banco de Dados II`.",
                    "O código especificado para a matéria já existe."
                )
                result = self.sbdao.insert(code=arguments[0], fullname=' '.join(arguments[2::]), semester=abs(int(arguments[1])))

                if 'err' in result.keys():
                    await msg.edit(content=statuses[result.get('err') - 1])
                else:
                    await msg.edit(content=f"Matéria adicionada com sucesso.\n```{tuple(result.values())[0]}```")

            except Exception as e:
                print_exc("(SubjectController) Exception caught at adding subject:", e)
                await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")

    @subject.command(name='buscar')
    async def find_subject(self, ctx: commands.Context, *, arguments=''):
        """
        Procura uma matéria existente.
        - Sintaxe: `mt buscar <por> <filtro>`, onde:
          - `por` pode ser:
              - 'nome' (busca por nome completo ou parcial);
              - 'cod' (busca por código exato);
              - 'sem' (busca por semestre);
          - Em caso de busca por semestre, `filtro` deve ser um valor numérico inteiro de 0 a 8.
          - Matérias elo (eletivas) têm semestre 0, mas `mt buscar sem elo` também funciona.
        - Exemplos: `mt buscar nome banco`, `mt buscar cod est`, `mt buscar sem 4`.
        """
        arguments: list = arguments.split()
        if len(arguments) < 2 or arguments[0].lower() not in ('nome', 'cod', 'sem'):
            await ctx.send("Sintaxe inválida. Exemplos: `>>mt buscar nome banco` ou `>>mt buscar cod bd2`.\nUse `>>help mt buscar` para ajuda.")
        else:
            try:
                terms = ' '.join(arguments[1::])
                if arguments[0].lower() == 'nome':
                    by = 'name'
                elif arguments[0].lower() == 'cod':
                    by = 'code'
                else:
                    by = 'semester'
                    terms = 0 if terms.lower() == 'elo' else int(terms)
            except Exception:
                await ctx.send("Sintaxe inválida. Exemplos: `>>mt buscar nome banco` ou `>>mt buscar cod bd2`.")
                return

            msg: Message = await ctx.send('Buscando matéria...')
            try:
                matches = self.sbdao.find(terms=terms, by=by, single_result=False)

                if matches is None:
                    await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")
                elif len(matches) == 0:
                    await msg.edit(content="Nenhuma matéria foi encontrado para esse critério.")
                else:
                    await msg.edit(content=f"Encontrada(s): ```{smoothen(matches)}```")

            except Exception as e:
                print_exc(f"(SubjectController) Exception caught at finding one subject:", e)
                await msg.edit(content="Algo deu errado. Consulte o log para detalhes.")

    # find_all functionality implemented by find_subject.

    @subject.command(name='editar')
    @commands.is_owner()
    async def edit_subject(self, ctx: commands.Context, *, arguments=''):
        """
        Edita uma matéria em específico.
        - Sintaxe: `mt editar <campo> <código> <novo valor>`, onde:
          - `código`: Código da matéria;
          - `campo`: Campo a editar (`nome`, `cod`, `sem` ou `todos`);
          - `novo valor`: Novo valor;
          - No caso de `campo == 'todos'`, a ordem dos novos valores é `<código> <semestre> <nome completo>`.
        - Exemplos: `mt editar AL1 cod ALG`, `mt editar AL1 todos ALG 0 Algoritmos 1`.
        """
        arguments: list = arguments.split()
        syntax_error = "Sintaxe inválida. Exemplos: `mt editar AL1 cod ALG`, `mt editar AL1 todos ALG 0 Algoritmos 1`."
        if len(arguments) < 3 or any([arguments[0].lower() not in ('nome', 'cod', 'sem', 'todos'), len(arguments[1]) != 3]):
            await ctx.send(syntax_error)
        else:
            msg: Message = await ctx.send('Editando matéria...')
            err_msgs = (
                "Algo deu errado. Consulte o log para detalhes.",
                syntax_error,
                "A matéria informada não existe."
            )
            try:
                field = arguments[0].lower()
                code = arguments[1].upper()
                if field == 'todos':
                    new_value = arguments[2::]
                    if len(new_value) < 3:
                        raise SyntaxError('(SubjectController.update) Number of arguments passed is lower than minimum for option \'todos\'')
                elif field == 'cod':
                    new_value = arguments[2].upper()
                elif field == 'sem':
                    new_value = int(arguments[2])
                else:
                    new_value = ' '.join(arguments[2::])
            except Exception:
                await msg.edit(content=syntax_error + '\nPara mais detalhes, use `>>help mt editar`.')
                return

            try:
                update_kwargs = {'code': code}
                if field == 'todos':
                    update_kwargs['newcode'] = new_value[0]
                    update_kwargs['semester'] = new_value[1]
                    update_kwargs['fullname'] = ' '.join(new_value[2::])
                else:
                    update_kwargs['newcode'] = new_value if field == 'cod' else None
                    update_kwargs['semester'] = new_value if field == 'sem' else None
                    update_kwargs['fullname'] = new_value if field == 'nome' else None

                result = self.sbdao.update(**update_kwargs)
                if 'err' in result.keys():
                    await msg.edit(content=err_msgs[result.get('err') - 1])
                else:
                    await msg.edit(content=f'Matéria editada: ```{smoothen(str(result.get(0)))}```')

            except Exception as e:
                print_exc(f"(SubjectController) Exception caught at editing subject:", e)
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
