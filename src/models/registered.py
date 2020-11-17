# Arquivo de mapeamento objeto-relacional para matrículas (estudantes matriculados em tal matéria).

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, ForeignKey

Base = declarative_base()


class Registered(Base):
    __tablename__ = 'registered'

    std_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    sbj_id = Column(Integer, ForeignKey("subjects.id"), primary_key=True)
    semester = Column(Date)
