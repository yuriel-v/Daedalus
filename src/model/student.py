# Arquivo de mapeamento objeto-relacional para estudantes.

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from model import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    registry = Column(Integer)          # matrícula
    discord_id = Column(Integer, nullable=False, unique=True)

    is_assigned = relationship('Assigned', back_populates='student')
    registered_on = relationship('Registered', back_populates='student')

    def __repr__(self):
        return f'Student(id={self.id}, name={self.name}, registry={self.registry}'

    def name_yourself(self, classes):
        reply = ['```\n']
        reply.extend([
            f'Nome: {self.name} | Matrícula: {self.registry}\n',
            f'Matérias: {", ".join(classes)}\n```'
        ])
        return ''.join(reply)
