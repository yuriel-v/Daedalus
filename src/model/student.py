# Arquivo de mapeamento objeto-relacional para estudantes.

from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, BigInteger
from model import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    registry = Column(Integer)          # matrícula
    discord_id = Column(BigInteger, nullable=False, unique=True)

    registered_on = relationship('Registered', back_populates='student', cascade="all, delete-orphan")

    def __str__(self):
        return f"Matrícula: {self.registry} | Nome: {self.name}"
