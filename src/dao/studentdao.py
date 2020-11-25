from sqlalchemy import literal
from model.student import Student
from dao import smkr


class StudentDao:
    def __init__(self):
        self.session = smkr()

    def insert(self, discord_id: str, name: str, registry: int):
        retval = None
        # integrity checks
        try:  # in case some funny asshat decides to put a string as registry
            if len(name) == 0 or ' ' not in name or (len(str(registry)) != 10 and not str(registry).startswith('20')):
                retval = 1  # invalid syntax
        except Exception as e:
            print(f"Exception caught on StudentDao: {e}")
            return 1

        if self.find_by_discord_id(discord_id) is not None:
            retval = 2  # user exists
        else:
            try:
                self.session.add(Student(name=name, registry=registry, discord_id=discord_id))
                self.session.commit()
                self.session.expunge_all()
            except Exception as e:
                print(f"Exception caught on StudentDao: {e}")
                self.session.rollback()

            success = self.find_by_discord_id(discord_id) is not None
            if success:
                retval = 0
            else:
                retval = 3  # ???
        return retval

    def find(self, filter: list, exists=False):
        if len(filter) == 0:
            return None
        else:
            q = None

            if exists:
                q = self.session.query(Student).filter(Student.discord_id == int(filter[0]))
                return self.session.query(literal(True)).filter(q.exists()).scalar()

            elif str(filter[0]).isnumeric():
                q = self.session.query(Student).filter(Student.registry == int(filter[0]))
            else:
                q = self.session.query(Student).filter(Student.name.ilike(f'%{" ".join(filter)}%'))

            q = q.all()
            self.session.rollback()
            return q

    def find_by_discord_id(self, discord_id: int):
        q = self.session.query(Student).filter(Student.discord_id == discord_id).first()
        self.session.rollback()
        return q

    def update(self, discord_id: int, name=None, registry=None):
        cur_student = self.session.query(Student).filter(Student.discord_id == discord_id).first()

        if cur_student is None:
            return 1
        else:
            self.session.add(cur_student)

        if name is not None:
            cur_student.name = name

        if registry is not None:
            cur_student.registry = registry

        if len(self.session.dirty) > 0:
            self.session.commit()

        self.session.expunge_all()
        return 0
