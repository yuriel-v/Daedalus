from typing import Union
from sqlalchemy.orm.session import Session
from db.model.student import Student
from db import DBSession as session
session: Session


class StudentDao:
    def __init__(self):
        pass

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
            session.rollback()
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
                session.add(Student(name=name, registry=registry, discord_id=int(discord_id)))
                session.commit()
                session.expunge_all()
            except Exception as e:
                print(f"Exception caught on StudentDao: {e}")
                session.rollback()
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
            session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if len(filter) == 0:
            return []
        else:
            if isinstance(filter, int):
                q = session.query(Student).filter(Student.registry == filter)
            else:
                q = session.query(Student).filter(Student.name.ilike(f'%{filter}%'))
            q: list = q.all()

            return q

    def find_by_discord_id(self, discord_id: int) -> Union[Student, None]:
        """
        Busca um estudante por ID Discord.
        - Retorna a instância de `Student` encontrada, ou `None`.
        """
        try:
            session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        return session.query(Student).filter(Student.discord_id == discord_id).first()

    def find_all(self) -> list[Student]:
        """
        Busca todos os estudantes cadastrados no banco de dados.
        """
        try:
            session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        return session.query(Student).all()

    def find_all_ids(self) -> tuple[int]:
        """
        Busca todos os IDs Discord dos estudantes cadastrados.
        - Retorna uma tupla.
        """
        try:
            session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        return tuple([std.discord_id for std in session.query(Student).all()])

    def update(self, student: Union[int, Student], name=None, registry=None) -> int:
        """
        Atualiza o cadastro de um estudante identificado por ID Discord e retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Estudante inexistente;
        - `3`: Nada a modificar.
        """
        try:
            session.rollback()
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
                session.add(cur_student)

            if name is not None:
                cur_student.name = name

            if registry is not None:
                cur_student.registry = registry

            if not session.is_modified():
                session.expunge_all()
                return 3
            else:
                session.commit()
                session.expunge_all()
                return 0
        except Exception as e:
            print(f'Exception caught at updating student: {e}')
            session.rollback()
            return 1

    def delete(self, discord_id: int) -> int:
        """
        Exclui um estudante do banco de dados e retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        """
        try:
            session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")

        try:
            d = session.query(Student).filter(Student.discord_id == discord_id)
            d.delete(synchronize_session=False)
            session.commit()
            return 0
        except Exception as e:
            session.rollback()
            print(f"Exception caught: {e}")
            return 1
