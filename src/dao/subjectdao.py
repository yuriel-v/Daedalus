from sqlalchemy import literal
from sqlalchemy.orm.session import Session
from model.subject import Subject
from dao import smkr


class SubjectDao:
    def __init__(self):
        self.session: Session = smkr()

    def expunge_all(self):
        self.session.expunge_all()

    def expunge(self, sbj):
        self.session.expunge(sbj)

    def insert(self, code: str, fullname: str, semester: int):
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if len(code) != 3 or len(fullname) == 0:
            return 2  # invalid data
        else:
            try:
                self.session.add(Subject(code=code.upper(), fullname=fullname, semester=abs(semester)))
                self.session.commit()
                self.session.expunge_all()
                return 0  # success
            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")
                self.session.rollback()
                return 1  # ???

    def find(self, filter: str, exists=False, by_key=True):
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
                elif filter.isnumeric():
                    q = q.filter(Subject.semester == abs(int(filter)))
                else:
                    q = q.filter(Subject.fullname.ilike(f'%{filter}%'))

                if exists:
                    q = self.session.query(literal(True)).filter(q.exists()).scalar()
                elif by_key:
                    q = q.first()
                else:
                    q = q.order_by(Subject.semester).all()

            except Exception as e:
                q = []
                print(f"Exception caught on SubjectDao: {e}")
            return q

    def find_by_code(self, filter: list[str]):
        """
        Encontra TUTO baseado numa lista de strings, contendo códigos de matéria.

        Todos os códigos nessa lista necessariamente têm que ser de comprimento 3,
        logo códigos incompletos não vão ser reconhecidos, assim sendo descartados.
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

    def find_one_by_code(self, code: str):
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if len(code) != 3:
            return None
        else:
            code = code.upper()
            return self.session.query(Subject).filter(Subject.code == code).first()

    def find_by_semester(self, semester: int):
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if semester > 8 or semester < 0:
            return []
        else:
            return self.session.query(Subject).filter(Subject.semester == semester).all()

    def find_all(self):
        """
        Encontra TUTO CHESSUS.

        POR FAVOR, PERCEBA QUE ESSE COMANDO GERA MUITO SPAM QUANDO ENVIADO
        EM UMA OU VÁRIAS MENSAGENS DEVIDO AO FATO DE TERMOS MUITAS MATÉRIAS
        CADASTRADAS.

        Ao invés de se afundar em um mar de lama, utilize o método :py:meth:`~dao.subjectdao.SubjectDao.find_by_semester`.
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
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if newcode is None and fullname is None and (semester is None or int(semester) not in range(0, 9)):
            return 1  # invalid syntax
        else:
            retval = None
            try:
                cur_sbj = self.find(code.upper())
                if len(cur_sbj) == 0:
                    return 2  # subject doesn't exist
                else:
                    cur_sbj = cur_sbj[0]

                if newcode is not None and len(newcode) == 3 and len(self.find(newcode)) == 0:
                    cur_sbj.code = newcode
                if fullname is not None and len(fullname) > 3:
                    cur_sbj.fullname = fullname
                if semester is not None and str(semester).isnumeric():
                    cur_sbj.semester = abs(int(semester))

                self.session.add(cur_sbj)
                self.session.commit()
                retval = 0  # success

            except Exception as e:
                self.session.rollback()
                print(f"Exception caught on SubjectDao: {e}")
                retval = 3  # ???
            finally:
                self.session.expunge_all()
            return retval
