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

    is_assigned = relationship('Assigned', back_populates='student')
    registered_on = relationship('Registered', back_populates='student')
