from core.utils import print_exc
from db import DBSession
from db.model import Subject
from sqlalchemy.orm import Session, scoped_session, Query
from typing import Union


class SubjectDao:
    def __init__(self, session=None):
        if session is None or not isinstance(session, Union[Session, scoped_session].__args__):
            self.session: scoped_session = DBSession()
        else:
            self.session = session
        self.session.expire_on_commit = False

    def insert(self, code: str, fullname: str, semester: int) -> int:
        """
        Cadastra uma matéria nova no banco de dados.
        ### Params
        - `code: str`: O código da matéria. Deverá ser uma string full uppercase de 3 chars;
        - `fullname: str`: O nome completo da matéria;
        - `semester: int`: O semestre a qual a matéria pertence.
          - Matérias eletivas são de semestre 0.

        ### Retorno
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Erro de sintaxe nos argumentos passados;
        - `3`: O código especificado já existe.

        ### Levanta
        - `SyntaxError` nos seguintes casos:
          - `code` ou `fullname` não são `str`, nem podem ser convertidas para `str`;
          - `semester` não é um `int` e nem pode ser convertido para `int`.
        """
        if not isinstance(code, str):
            try:
                code = str(code)
            except Exception:
                raise SyntaxError("Argument 'code' is not a string nor can it be converted to string")

        if not isinstance(fullname, str):
            try:
                fullname = str(fullname)
            except Exception:
                raise SyntaxError("Argument 'fullname' is not a string nor can it be converted to string")

        if not isinstance(semester, int):
            try:
                semester = int(semester)
            except Exception:
                raise SyntaxError("Argument 'semester' is not an int nor can it be converted to int")

        if any([len(code) != 3, len(fullname) == 0, semester not in range(0, 11)]):
            return 2
        else:
            try:
                if self.find(terms=code.upper(), by='code') is not None:
                    return 3
                else:
                    self.session.add(Subject(code=code.upper(), fullname=fullname, semester=abs(semester)))
                    self.session.commit()
                    return 0
            except Exception as e:
                print_exc("Exception caught on SubjectDao.insert:", e)
                self.session.rollback()
                return 1

    def find(self, terms: Union[int, str], by: str, single_result=True) -> Union[list[Subject], Subject, None]:
        """
        Busca uma matéria baseado num filtro.
        ### Params
        - `terms: str | int`: Os termos de pesquisa;
        - `single_result: bool`: Caso `True`, retorna o primeiro resultado ou None. Senão, retorna uma lista com todos os resultados. Opcional.
        - `by: str`: O critério de pesquisa. Deve ser um dos valores:
          - `'code'`: Busca por código de matéria;
          - `'name'`: Busca por nome, parcial ou completo;
          - `'semester'`: Busca por semestre. `terms` deverá ser um `int` ou poder ser convertido para `int`.

        ### Retorno
        - Caso `single_result == True`, retorna uma instância de `Subject`, ou `None` se nada for encontrado;
        - Senão, retorna uma lista de instâncias de `Subject`, ou uma lista vazia.
        - Em ambos os casos, retorna `None` se uma exceção for lançada.

        ### Levanta
        - `SyntaxError` nos seguintes casos:
          - `by` não é uma string com um dos valores válidos acima;
          - Caso `by` seja `'code'` ou `'name'`:
              - `terms` não é uma `str` nem pode ser convertido para `str`.
          - Caso `by` seja `'semester'`:
              - `terms` não é um `int` nem pode ser convertido para `int`.
        """
        if not isinstance(by, str) or by.lower() not in ('code', 'name', 'semester'):
            raise SyntaxError("Argument 'by' is not a string with a valid value")

        if by in ('code', 'name') and not isinstance(terms, str):
            try:
                terms = str(terms)
            except Exception:
                raise SyntaxError("Argument 'terms' is not a str and cannot be cast to str")

        if by == 'semester' and not isinstance(terms, int):
            try:
                terms = int(terms)
            except Exception:
                raise SyntaxError("Argument 'terms' is not an int and cannot be cast to int")

        try:
            q: Query = self.session.query(Subject)
            if by == 'code':
                q = q.filter(Subject.code == terms.upper())
            elif by == 'name':
                q = q.filter(Subject.fullname.ilike(terms))
            else:
                q = q.filter(Subject.semester == terms)

            if single_result:
                return q.first()
            else:
                return q.all()
        except Exception as e:
            print_exc("Exception caught on SubjectDao.find:", e)
            return None

    def find_all(self) -> list[Subject]:
        """
        Retorna uma lista enorme contendo todas as matérias cadastradas no banco de dados.
        - AVISO: NÃO tente imprimir essa lista completa em um chat - não só a lista pode exceder o limite de 2000 chars
          imposto pelo Discord, mas também pode causar muito spam!
        - Em vez de poluir o seu chat, considere usar o método `find()`.
        """
        # -> this text is left here as a lesson learned kind of thing. how to bypass the orm somewhat and connect to the
        #    DB API on a lower level

        # This is preferred over the usual session.query(Subject).all()
        # because the former issues multiple SELECT statements for each id.

        # Actually nevermind, it was the rollback at the end of every function causing this.
        # Leaving this here for reference on how to use DBAPI-like querying.
        # Also note: put a rollback BEFORE every command call that uses the DB.
        # Not only it avoids the problem mentioned above, it has 2 outcomes:
        # 1. if there is a current bad transaction in progress, it will be rolled back.
        # 2. if there are no active transactions, the method is a pass-through.

        # cnx = engin.connect()
        # res = []
        # for row in cnx.execute(Subject.__table__.select()):
        #     res.append(Subject(id=row['id'], code=row['code'], fullname=row['fullname'], semester=row['semester']))
        # return res
        try:
            return self.session.query(Subject).all()
        except Exception as e:
            print_exc("Exception caught on SubjectDao.find_all:", e)
            return []

    def update(self, code: Union[str, Subject], newcode=None, fullname=None, semester=None):
        """
        Atualiza as informações de uma matéria.
        ### Params
        - `code: Subject | str`: A matéria (ou o código dela) a ser atualizada;
        - `newcode: str`: O novo código;
        - `fullname: str`: O novo nome completo;
        - `semester: int`: O novo semestre.
        - Pelo menos um dos 3 acima não deve ser `None`. A matéria permanecerá inalterada nos atributos que forem `None`.

        ### Retorno
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Erro de sintaxe nos argumentos passados:
          - `newcode` ou `fullname` é uma string vazia;
          - `semester` não é um `int` dentro do intervalo [0, 11[
        - `3`: Matéria inexistente.

        ### Levanta
        - `SyntaxError` caso `code` não seja uma instância de `str` nem `Subject`, nem possa ser convertido para `str`.
        """
        if not isinstance(code, Union[str, Subject].__args__):
            try:
                code = str(code)
            except Exception:
                raise SyntaxError("Argument 'code' is not an instance of 'str' nor 'Subject', nor can it be cast to 'str'")

        try:
            if any([
                all([newcode is None, fullname is None, semester is None]),
                any([len(str(newcode)) != 3, fullname == '', semester is not None and int(semester) not in range(0, 11)])
            ]):
                return 2
        except Exception:
            return 2

        try:
            cur_sbj = self.find(code.upper() if isinstance(code, str) else code.id, by='code')
            if cur_sbj is None:
                return 3
            else:
                if newcode is not None:
                    cur_sbj.code = str(newcode).upper()

                if fullname is not None:
                    cur_sbj.fullname = str(fullname)

                if semester is not None:
                    cur_sbj.semester = int(semester)

                self.session.commit()
                return 0
        except Exception as e:
            print_exc("Exception caught on SubjectDao.update:", e)
            self.session.rollback()
            return 1
