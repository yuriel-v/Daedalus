from typing import Union
from sqlalchemy.orm.session import Session
from model.unimanager.subject import Subject
from dao import smkr


class SubjectDao:
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

    def expunge(self, sbj):
        """Remove a matéria especificada da sessão do DAO atual."""
        self.session.expunge(sbj)

    def insert(self, code: str, fullname: str, semester: int) -> int:
        """
        Cadastra uma matéria nova no banco de dados e retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Erro de sintaxe nos argumentos passados.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if len(code) != 3 or len(fullname) == 0:
            return 2
        else:
            try:
                self.session.add(Subject(code=code.upper(), fullname=fullname, semester=abs(semester)))
                self.session.commit()
                self.session.expunge_all()
                return 0
            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")
                self.session.rollback()
                return 1

    def find(self, filter: str, by_key=True) -> Union[list[Subject], Subject, None]:
        """
        Busca uma matéria baseada num filtro.
        - Se o filtro for uma string de 3 ou menos chars, ou se `by_key = True`, é feita uma busca por código;
        - Se o filtro for uma string de 4 ou mais chars, é feita uma busca por nome completo.

        Retorna uma lista de instâncias de `Subject`, ou uma única instância, caso `by_key = True`.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if len(filter) == 0:
            return []
        else:
            q = None
            try:
                q = self.session.query(Subject)

                if by_key or len(filter) <= 3:
                    q = q.filter(Subject.code.ilike(f'%{filter}%'))
                else:
                    q = q.filter(Subject.fullname.ilike(f'%{filter}%'))

                if by_key:
                    q = q.first()
                else:
                    q = q.order_by(Subject.semester).all()
            except Exception as e:
                q = None
                self.session.rollback()
                print(f"Exception caught on SubjectDao: {e}")
            return q

    def find_by_code(self, filter: list[str]) -> list[Subject]:
        """
        Busca matérias especificadas por um filtro de strings.
        - Tal filtro deve conter somente strings de 3 letras, ou seja, os códigos da matérias a serem buscadas.
          - As strings nesse filtro não precisam estar em full uppercase.

        Retorna uma lista de instâncias de `Subject`, contendo as matérias especificadas no filtro, ou uma lista vazia se uma exceção for lançada.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if not filter:
            return []
        else:
            try:
                filter = [str(x).upper() for x in filter if len(x) == 3]
                q = self.session.query(Subject).filter(Subject.code.in_(filter)).all()
            except Exception as e:
                self.session.rollback()
                q = []
                print(f"Exception caught on SubjectDao: {e}")
            return q

    def find_one_by_code(self, code: str) -> Union[Subject, None]:
        """Busca uma única matéria por código, ou `None`. Case insensitive."""
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if len(code) != 3:
            return None
        else:
            code = code.upper()
            q = self.session.query(Subject).filter(Subject.code == code).first()
            return q

    def find_by_semester(self, semester: int) -> list[Subject]:
        """
        Busca matérias por semestre.
        - Somente um número entre [0, 8] é aceito.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if semester > 8 or semester < 0:
            return []
        else:
            q = self.session.query(Subject).filter(Subject.semester == semester).all()
            return q

    def find_all(self) -> list[Subject]:
        """
        Retorna uma lista enorme contendo todas as matérias cadastradas no banco de dados.
        - AVISO: NÃO tente imprimir essa lista completa em um chat - não só a lista pode exceder o limite de 2000 chars
          imposto pelo Discord, mas também pode causar muito spam!
        - Em vez de poluir o seu chat, considere usar o método `find_by_semester()`.
        """
        """
        This is preferred over the usual self.session.query(Subject).all()
        because the former issues multiple SELECT statements for each id.

        Actually nevermind, it was the rollback at the end of every function causing this.
        Leaving this here for reference on how to use DBAPI-like querying.
        Also note: put a rollback BEFORE every command call that uses the DB.
        Not only it avoids the problem mentioned above, it has 2 outcomes:
        1. if there is a current bad transaction in progress, it will be rolled back.
        2. if there are no active transactions, the method is a pass-through.

        cnx = engin.connect()
        res = []
        for row in cnx.execute(Subject.__table__.select()):
            res.append(Subject(id=row['id'], code=row['code'], fullname=row['fullname'], semester=row['semester']))
        return res
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        return self.session.query(Subject).all()

    def update(self, code: str, newcode=None, fullname=None, semester=None):
        """
        Atualiza uma matéria e retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Erro de sintaxe nos argumentos passados;
        - `3`: Matéria inexistente.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if newcode is None and fullname is None and (semester is None or int(semester) not in range(0, 9)):
            return 2
        else:
            try:
                cur_sbj = self.find(code.upper(), by_key=True)
                if cur_sbj is None:
                    return 3
                else:
                    self.session.add(cur_sbj)

                if newcode is not None and isinstance(newcode, str) and len(newcode) == 3:
                    cur_sbj.code = newcode.upper()
                if fullname is not None and isinstance(fullname, str) and len(fullname) > 3:
                    cur_sbj.fullname = fullname
                if semester is not None and str(semester).isnumeric():
                    cur_sbj.semester = abs(int(semester))

                self.session.commit()
                self.session.expunge_all()
                return 0

            except Exception as e:
                self.session.rollback()
                print(f"Exception caught on SubjectDao: {e}")
                return 1
