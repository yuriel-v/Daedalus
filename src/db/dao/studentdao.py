from core.utils import print_exc
from db.dao.genericdao import GenericDao
from db.model import Student
from sqlalchemy.orm import Query
from typing import Union


class StudentDao(GenericDao):
    def __init__(self, session=None, autoinit=True):
        super().__init__(session=session, autoinit=autoinit)

    def insert(self, discord_id: int, name: str, registry: int) -> dict:
        """
        Cadastra um estudante novo.
        Caso o `discord_id` já exista no banco de dados, o estudante é tido como já cadastrado, e nada é feito.
        ### Params
        - `discord_id: int`: O ID Discord do estudante a ser cadastrado;
        - `name: str`: O nome completo do estudante a ser cadastrado;
        - `registry: int`: O número de matrícula do estudante a ser cadastrado.

        ### Retorno
        - Um dict no formato `{std.discord_id: std}` em caso de sucesso.
        - Casos excepcionais:
            - `{'err': 1}`: Erro desconhecido, usuário não foi cadastrado;
            - `{'err': 2}`: Erro de sintaxe nos argumentos passados;
            - `{'err': 3}`: Usuário já existente.

        ### Levanta
        - `SyntaxError` caso os argumentos não possam ser convertidos para seus respectivos tipos.
        """
        try:
            if not isinstance(discord_id, int):
                discord_id = int(discord_id)
            if not isinstance(name, str):
                name = str(name)
            if not isinstance(registry, int):
                registry = int(registry)
        except Exception:
            raise SyntaxError("Arguments could not be cast to their intended types")

        try:
            #    no name      or first name only or                   registry not in 20xxxxxxxx format
            if len(name) == 0 or ' ' not in name or (len(str(registry)) != 10 and not str(registry).startswith('20')):
                return {'err': 2}
        except Exception:
            print_exc()
            return {'err': 1}

        if self.find(discord_id, by='id') is not None:
            return {'err': 3}
        else:
            tr = None
            try:
                tr = self._session.begin_nested()
                new_student = Student(name=name, registry=registry, discord_id=discord_id)
                self._session.add(new_student)
                self._gcommit(tr)
                return {new_student.discord_id: new_student}
            except Exception:
                print_exc()
                if tr is not None:
                    tr.rollback()
                return {'err': 1}

    def find(self, terms: Union[int, str], by: str) -> Union[list[Student], Student, None]:
        """
        Busca um estudante que corresponda aos termos passados.
        ### Params
        - `terms: int | str`: Os termos da busca;
        - `by: str`: O critério de busca. Valores válidos:
          - `'id'`: Busca por ID Discord;
          - `'name'`: Busca por nome, parcial ou completo;
          - `'registry'`: Busca por matrícula.

        ### Retorno
        - Uma instância de `Student`, ou `None` caso nada seja encontrado, quando uma busca por matrícula ou ID for feita;
        - Uma lista de instâncias de `Student` correspondentes, ou uma lista vazia se nada for encontrado, caso a busca for por nome.

        ### Levanta
        - `SyntaxError` caso o critério de busca esteja incorreto;
        - `SyntaxError` caso o argumento passado para `terms` não seja um `int` nem uma `str`.
          - Isso também inclui o caso de `terms` ser `None`!
        """
        by = by.lower()
        if by not in ('id', 'registry', 'name'):
            raise SyntaxError("Invalid search criteria")
        if not isinstance(terms, Union[int, str].__args__):
            raise SyntaxError("Terms are not an int nor a string")

        if terms is None or terms == '':
            return None
        else:
            q: Query = self._session.query(Student)
            if by == 'id':
                q = q.filter(int(terms) == Student.discord_id)
            elif by == 'registry':
                q = q.filter(int(terms) == Student.registry)
            else:
                q = q.filter(Student.name.ilike(f'%{str(terms)}%'))

            if by == 'name':
                return q.all()
            else:
                return q.first()

    def find_all(self) -> list[Student]:
        """
        Busca todos os estudantes cadastrados no banco de dados.
        """
        return self._session.query(Student).all()

    def find_all_ids(self) -> tuple[int]:
        """
        Busca todos os IDs Discord dos estudantes cadastrados.
        Este método não depende de sessão.
        """
        return tuple([int(std.discord_id) for std in self.find_all()])

    def update(self, student: Union[int, Student], name=None, registry=None) -> dict:
        """
        Atualiza o cadastro de um estudante.
        ### Params
        - `student: int | Student`: O estudante (ou seu ID Discord) a ser cadastrado;
        - `name: str`: O novo nome do estudante. Se `None`, não vai ser alterado.
        - `registry: int`: O novo número de matrícula do estudante. Se `None`, não vai ser alterado.
        - Pelo menos um dentre `name` e `registry` precisa não ser `None`.

        ### Retorno
        - Um dict no formato `{std.discord_id: std}` em caso de sucesso.
        - Casos excepcionais:
            - `{'err', 1}`: Exceção levantada, transação sofreu rollback;
            - `{'err', 2}`: Estudante inexistente;
            - `{'err', 3}`: Nada a modificar (`name` e `registry` ambos são `None`).

        ### Levanta
        - `SyntaxError` caso `student` não seja uma instância de `int` nem `Student`, nem possa ser convertido para `int`.
        """
        try:
            if not isinstance(student, Union[Student, int].__args__):
                student = int(student)
        except Exception:
            raise SyntaxError("Argument 'student' is neither an instance of Student nor int, nor can it be casted to int")

        if all([name is None, registry is None]):
            return {'err', 3}

        tr = None
        try:
            tr = self._session.begin_nested()
            cur_student = self.find(student if isinstance(student, int) else student.id, by='id')
            if cur_student is None:
                return {'err', 2}

            if name is not None:
                cur_student.name = str(name)
            if registry is not None:
                cur_student.registry = int(registry)

            self._gcommit(tr)
            return {cur_student.discord_id: cur_student}
        except Exception:
            print_exc()
            if tr is not None:
                tr.rollback()
            return {'err': 1}

    def delete(self, discord_id: int) -> int:
        """
        Exclui um estudante do banco de dados.
        ### Params
        - `discord_id: int`: O ID Discord do estudante a ser excluído.

        ### Retorna
        - `0`: Operação bem-sucedida;
        - `1`: Exceção levantada, transação sofreu rollback.

        ### Levanta
        - `SyntaxError` caso `discord_id` não for um `int` nem poder ser convertido para `int`.
        """
        try:
            if not isinstance(discord_id, int):
                discord_id = int(discord_id)
        except Exception:
            raise SyntaxError("Discord ID is not an instance of 'int' and could not be cast to 'int' either")

        tr = None
        try:
            tr = self._session.begin_nested()
            deleted_student = self._session.query(Student).filter(Student.discord_id == discord_id).first()
            self._session.delete(deleted_student)

            self._gcommit(tr)
            return 0
        except Exception:
            print_exc()
            if tr is not None:
                tr.rollback()
            return 1
