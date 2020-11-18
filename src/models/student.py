# Arquivo de mapeamento objeto-relacional para estudantes.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)               # nome, obviamente
    registry = Column(Integer)          # matrícula

    def __repr__(self):
        return f"Student(id={self.id}, name={self.name}, registry={self.registry}"

    def name_yourself(self, classes):
        reply = ['```\n']
        reply.extend([
            f"Nome: {self.name} | Matrícula: {self.registry}\n",
            f"Matérias: {', '.join(classes)}\n```"
        ])
        return ''.join(reply)
