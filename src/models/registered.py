# Arquivo de mapeamento objeto-relacional para matrículas (estudantes matriculados em tal matéria).

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Date, ForeignKey
from models.student import Student
from models.subject import Subject
from models import Base


class Registered(Base):
    __tablename__ = 'registered'

    std_id = Column(Integer, ForeignKey(Student.id), primary_key=True)
    sbj_id = Column(Integer, ForeignKey(Subject.id), primary_key=True)
    semester = Column(Date)

    student = relationship('Student', back_populates='registered_on')
    subject = relationship('Subject', back_populates='registered_by')

    def __repr__(self):
        return f'Registered(std_id={self.std_id}, sbj_id={self.sbj_id}, semester={self.semester}'
