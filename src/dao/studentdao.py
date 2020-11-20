from sqlalchemy import literal
from model.student import Student
from dao import smkr


class StudentDao:
    def insert(self, discord_id: int, name: str, registry: int):
        session = smkr()
        session.add(Student(name=name, registry=registry, discord_id=discord_id))
        session.commit()
        session.close()

    def find(self, filter: list, exists=False):
        session = smkr()
        q = None

        if exists:
            q = session.query(Student).filter(Student.discord_id == int(filter[0]))
            return session.query(literal(True)).filter(q.exists()).scalar()

        elif str(filter[0]).isnumeric():
            q = session.query(Student).filter(Student.registry == int(filter[0]))
        else:
            q = session.query(Student).filter(Student.name.like(f'%{" ".join(filter)}%'))

        return q.all()

    def find_by_discord_id(self, discord_id):
        session = smkr()
        return session.query(Student).filter(Student.discord_id == discord_id).first()

    def update(self, discord_id, name=None, registry=None):
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
