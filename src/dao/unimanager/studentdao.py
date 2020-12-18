from typing import Union
from sqlalchemy.orm.session import Session
from model.unimanager.student import Student
from dao import smkr


class StudentDao:
    def __init__(self):
        self.session: Session = smkr()

    def sclear(self):
        """Limpa a sessão de transações."""
        self.session.rollback()
        self.session.close()

    def begin(self):
        """Estabelece uma nova conexão com o banco de dados."""
        self.session = smkr()

    def expunge_all(self):
        """Remove todos os objetos relacionados com a sessão do DAO atual."""
        self.session.expunge_all()

    def expunge(self, std: Student):
        """Remove o estudante especificado da sessão do DAO atual."""
        self.session.expunge(std)

    def insert(self, discord_id: str, name: str, registry: int) -> int:
        """
        Cadastra um estudante novo.
        - Caso o `discord_id` já exista no banco de dados, o estudante é tido como já cadastrado, e nada é feito.

        Retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Erro desconhecido, usuário não foi cadastrado;
        - `2`: Erro de sintaxe nos argumentos passados;
        - `3`: Usuário já existente.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        retval = None
        # integrity checks
        try:  # in case some funny asshat decides to put a string as registry
            if len(name) == 0 or ' ' not in name or (len(str(registry)) != 10 and not str(registry).startswith('20')):
                return 2
        except Exception as e:
            print(f"Exception caught on StudentDao: {e}")
            return 1

        if self.find_by_discord_id(discord_id) is not None:
            return 3
        else:
            try:
                self.session.add(Student(name=name, registry=registry, discord_id=int(discord_id)))
                self.session.commit()
                self.session.expunge_all()
            except Exception as e:
                print(f"Exception caught on StudentDao: {e}")
                self.session.rollback()
                return 1

            success = self.find_by_discord_id(discord_id) is not None
            if success:
                return 0
            else:
                return 1

    def find(self, filter: Union[int, str]) -> list[Student]:
        """
        Busca um estudante baseado num filtro.
        - Se o filtro for um inteiro, é feita uma busca por matrícula;
        - Se o filtro for uma string, é feita uma busca por nome completo.

        Retorna uma lista de instâncias de `Student` contendo os estudantes que correspondem ao filtro.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if len(filter) == 0:
            return []
        else:
            if isinstance(filter, int):
                q = self.session.query(Student).filter(Student.registry == filter)
            else:
                q = self.session.query(Student).filter(Student.name.ilike(f'%{filter}%'))
            q: list = q.all()

            return q

    def find_by_discord_id(self, discord_id: int) -> Union[Student, None]:
        """
        Busca um estudante por ID Discord.
        - Retorna a instância de `Student` encontrada, ou `None`.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        return self.session.query(Student).filter(Student.discord_id == discord_id).first()

    def find_all(self) -> list[Student]:
        """
        Busca todos os estudantes cadastrados no banco de dados.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        return self.session.query(Student).all()

    def find_all_ids(self) -> tuple[int]:
        """
        Busca todos os IDs Discord dos estudantes cadastrados.
        - Retorna uma tupla.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        return tuple([std.discord_id for std in self.session.query(Student).all()])

    def update(self, student: Union[int, Student], name=None, registry=None) -> int:
        """
        Atualiza o cadastro de um estudante identificado por ID Discord e retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Estudante inexistente;
        - `3`: Nada a modificar.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        try:
            if isinstance(student, int):
                cur_student = self.find_by_discord_id(student)
            elif isinstance(student, Student):
                cur_student = student
            else:
                raise TypeError("Student is neither an integer Discord ID nor an instance of Student")

            if cur_student is None:
                return 2
            else:
                self.session.add(cur_student)

            if name is not None:
                cur_student.name = name

            if registry is not None:
                cur_student.registry = registry

            if not self.session.is_modified():
                self.session.expunge_all()
                return 3
            else:
                self.session.commit()
                self.session.expunge_all()
                return 0
        except Exception as e:
            print(f'Exception caught at updating student: {e}')
            self.session.rollback()
            return 1

    def delete(self, discord_id: int) -> int:
        """
        Exclui um estudante do banco de dados e retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")

        try:
            d = self.session.query(Student).filter(Student.discord_id == discord_id)
            d.delete(synchronize_session=False)
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            print(f"Exception caught: {e}")
            return 1
