# Arquivo de mapeamento objeto-relacional para matrículas (estudantes matriculados em tal matéria).

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Date, ForeignKey
from model.student import Student
from model.subject import Subject
from model import Base


class Registered(Base):
    __tablename__ = 'registered'

    std_id = Column(Integer, ForeignKey(Student.id), primary_key=True)
    sbj_id = Column(Integer, ForeignKey(Subject.id), primary_key=True)
    semester = Column(Date)

    student = relationship('Student', back_populates='registered_on')
    subject = relationship('Subject', back_populates='registered_by')
