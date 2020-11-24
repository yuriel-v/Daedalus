from sqlalchemy import literal
from model.student import Student
from dao import smkr


class StudentDao:
    def insert(self, discord_id: str, name: str, registry: int):
        session = smkr()
        retval = None
        # integrity checks
        try:  # in case some funny asshat decides to put a string as registry
            if len(name) == 0 or ' ' not in name or int(registry) < 2000000000:
                session.close()
                retval = 1  # invalid syntax
        except Exception as e:
            print(f"Exception caught on StudentDao: {e}")
            session.close()
            return 1

        if self.find_by_discord_id(discord_id, session) is not None:
            session.close()
            retval = 2  # user exists
        else:
            try:
                session.add(Student(name=name, registry=registry, discord_id=discord_id))
                session.commit()
                session.expunge_all()
            except Exception as e:
                print(f"Exception caught on StudentDao: {e}")

            success = self.find_by_discord_id(discord_id, session) is not None
            session.close()
            if success:
                retval = 0
            else:
                retval = 3  # ???
        return retval

    def find(self, filter: list, exists=False):
        if len(filter) == 0:
            return None
        else:
            session = smkr()
            q = None

            if exists:
                q = session.query(Student).filter(Student.discord_id == int(filter[0]))
                return session.query(literal(True)).filter(q.exists()).scalar()

            elif str(filter[0]).isnumeric():
                q = session.query(Student).filter(Student.registry == int(filter[0]))
            else:
                q = session.query(Student).filter(Student.name.like(f'%{" ".join(filter)}%'))

            q = q.all()
            session.close()
            return q

    def find_by_discord_id(self, discord_id: int, session=None):
        inherited_session = True
        if session is None:
            session = smkr()
            inherited_session = False

        q = session.query(Student).filter(Student.discord_id == discord_id).first()

        if not inherited_session:
            session.close()
        return q

    def update(self, discord_id: int, name=None, registry=None):
        session = smkr()
        cur_student = session.query(Student).filter(Student.discord_id == discord_id).first()

        if cur_student is None:
            return 1
        else:
            session.add(cur_student)

        if name is not None:
            cur_student.name = name

        if registry is not None:
            cur_student.registry = registry

        if len(session.dirty) > 0:
            session.commit()

        session.close()
        return 0
