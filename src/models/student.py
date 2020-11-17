# Arquivo de mapeamento objeto-relacional para estudantes.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)               # nome, obviamente
    registry = Column(Integer)          # matrícula
