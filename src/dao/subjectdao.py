from sqlalchemy import literal
from model.subject import Subject
from dao import smkr


class SubjectDao:
    def __init__(self):
        self.session = smkr()

    def insert(self, code: str, fullname: str):
        if len(code) != 3 or len(fullname) == 0:
            return 1
        else:
            try:
                self.session.add(Subject(code=code.upper(), fullname=fullname))
                self.session.commit()
            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")
            finally:
                self.session.expunge_all()

    def find(self, filter: str, exists=False):
        if len(filter) == 0:
            return None
        else:
            try:
                q = self.session.query(Subject)
                if len(filter) <= 3:
                    q = q.filter(Subject.code.ilike(f'%{filter}%'))
                else:
                    q = q.filter(Subject.fullname.ilike(f'%{filter}%'))

                if exists:
                    return self.session.query(literal(True)).filter(q.exists()).scalar()
                else:
                    return q.all()

            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")

    def update(self, code: str, newcode=None, fullname=None):
        if newcode is None and fullname is None:
            return 1  # invalid syntax
        else:
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

                self.session.add(cur_sbj)
                self.session.commit()

            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")
            finally:
                self.session.expunge_all()
