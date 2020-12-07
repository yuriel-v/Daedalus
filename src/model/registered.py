# Arquivo de mapeamento objeto-relacional para matrículas (estudantes matriculados em tal matéria).

from datetime import date
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey, UniqueConstraint, Sequence
from model.student import Student
from model.subject import Subject
from model import Base


class Registered(Base):
    __tablename__ = 'registered'
    __table_args__ = (
        UniqueConstraint('std_id', 'sbj_id', name='composite_enrollment_pk'),
        UniqueConstraint('id', name='unique_enrollment_id')
    )

    id = Column(Integer, Sequence('enrollment_id_seq', start=1, increment=1))
    std_id = Column(Integer, ForeignKey(Student.id), primary_key=True)
    sbj_id = Column(Integer, ForeignKey(Subject.id), primary_key=True)
    semester = Column(Date)
    active = Column(Boolean)

    student = relationship('Student', back_populates='registered_on')
    subject = relationship('Subject', back_populates='registered_by')
    exams = relationship('Exam', back_populates='registry')
    eager_exams = []

    def is_current(self):
        cur_semester = date(day=1, year=date().today().year, month=(lambda: 1 if date.today().month < 7 else 2)())
        return bool(self.semester == cur_semester)
