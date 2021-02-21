from core.utils import print_exc
from db.dao.genericdao import GenericDao
from db.model.student import Student
from sqlalchemy.orm import Query
from typing import Union


class StudentDao(GenericDao):
    def __init__(self, session=None, autoinit=True):
        super().__init__(session=session, autoinit=autoinit)

    def insert(self, discord_id: int, name: str, registry: int) -> int:
        """
        Cadastra um estudante novo.
        Caso o `discord_id` já exista no banco de dados, o estudante é tido como já cadastrado, e nada é feito.
        ### Params
        - `discord_id: int`: O ID Discord do estudante a ser cadastrado;
        - `name: str`: O nome completo do estudante a ser cadastrado;
        - `registry: int`: O número de matrícula do estudante a ser cadastrado.

        ### Retorno
        - `0`: Operação bem-sucedida;
        - `1`: Erro desconhecido, usuário não foi cadastrado;
        - `2`: Erro de sintaxe nos argumentos passados;
        - `3`: Usuário já existente.

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
                return 2
        except Exception as e:
            print_exc(f"Exception caught on StudentDao.insert:", e)
            return 1

        if self.find(discord_id, by='id') is not None:
            return 3
        else:
            try:
                self.session.add(Student(name=name, registry=registry, discord_id=discord_id))
                self.session.commit()
                return 0
            except Exception as e:
                print_exc(f"Exception caught on StudentDao.insert:", e)
                self.session.rollback()
                return 1

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
            q: Query = self.session.query(Student)
            if by == 'id':
                q = q.filter(int(terms) == Student.discord_id)
            elif by == 'registry':
                q = q.filter(int(terms) == Student.registry)
            else:
                q = q.filter(Student.name.ilike(str(terms)))

            if by == 'name':
                return q.all()
            else:
                return q.first()

    def find_all(self) -> list[Student]:
        """
        Busca todos os estudantes cadastrados no banco de dados.
        """
        return self.session.query(Student).all()

    def find_all_ids(self) -> tuple[int]:
        """
        Busca todos os IDs Discord dos estudantes cadastrados.
        Este método não depende de sessão.
        """
        return tuple([int(std.discord_id) for std in self.find_all()])

    def update(self, student: Union[int, Student], name=None, registry=None) -> int:
        """
        Atualiza o cadastro de um estudante.
        ### Params
        - `student: int | Student`: O estudante (ou seu ID Discord) a ser cadastrado;
        - `name: str`: O novo nome do estudante. Se `None`, não vai ser alterado.
        - `registry: int`: O novo número de matrícula do estudante. Se `None`, não vai ser alterado.
        - Pelo menos um dentre `name` e `registry` precisa não ser `None`.

        ### Retorno
        - `0`: Operação bem-sucedida;
        - `1`: Exceção levantada, transação sofreu rollback;
        - `2`: Estudante inexistente;
        - `3`: Nada a modificar (`name` e `registry` ambos são `None`).

        ### Levanta
        - `SyntaxError` caso `student` não seja uma instância de `int` nem `Student`, nem possa ser convertido para `int`.
        """
        try:
            if not isinstance(student, Union[Student, int].__args__):
                student = int(student)
        except Exception:
            raise SyntaxError("Argument 'student' is neither an instance of Student nor int, nor can it be casted to int")

        if all([name is None, registry is None]):
            return 3

        try:
            cur_student = self.find(student if isinstance(student, int) else student.id, by='id')
            if cur_student is None:
                return 2

            if name is not None:
                cur_student.name = str(name)
            if registry is not None:
                cur_student.registry = int(registry)

            self.session.commit()
            return 0
        except Exception as e:
            print_exc("Exception caught on StudentDao.update:", e)
            self.session.rollback()
            return 1

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

        try:
            d = self.session.query(Student).filter(Student.discord_id == discord_id)
            d.delete(synchronize_session=False)
            self.session.commit()
            return 0
        except Exception as e:
            print_exc("Exception caught on StudentDao.delete:", e)
            self.session.rollback()
            return 1
