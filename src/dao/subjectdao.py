from model.subject import Subject
from dao import smkr


class SubjectDao:
    def insert(self, code: str, fullname: str):
        if len(code) != 3 or len(fullname) == 0:
            return 1
        else:
            session = smkr()
            try:
                session.add(Subject(code=code.upper(), fullname=fullname))
                session.commit()
            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")
            finally:
                session.close()

    def find(self, filter: str):
        if len(filter) == 0:
            return None
        else:
            session = smkr()
            try:
                q = session.query(Subject)
                if len(filter) <= 3:
                    q = q.filter(Subject.code.like(f'%{filter}%'))
                else:
                    q = q.filter(Subject.fullname.like(f'%{filter}%'))
                return q.all()
            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")
            finally:
                session.close()

    def update(self, code: str, newcode=None, fullname=None):
        if newcode is None and fullname is None:
            return 1
        else:
            session = smkr()
            try:
                cur_sbj = session.query(Subject).filter(Subject.code.like(f"%{code}%")).first()
                if cur_sbj is None:
                    return 2
                if newcode is not None and len(newcode) == 3 and len(self.find(newcode)) == 0:
                    cur_sbj.code = newcode
                if fullname is not None and len(fullname) > 3:
                    cur_sbj.fullname = fullname
                session.add(cur_sbj)
                session.commit()
            except Exception as e:
                print(f"Exception caught on SubjectDao: {e}")
            finally:
                session.close()
