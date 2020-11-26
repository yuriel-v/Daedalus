# Arquivo de mapeamento objeto-relacional para matérias.

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from model import Base


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True)  # Código da matéria, por exemplo 'BD2' para banco de dados II
    fullname = Column(String)           # Nome completo da matéria, por exemplo 'Banco de Dados II'
    semester = Column(Integer, nullable=False)

    assigned_to = relationship('Assigned', back_populates='subject', cascade="all, delete-orphan")
    registered_by = relationship('Registered', back_populates='subject', cascade="all, delete-orphan")

    def __str__(self):
        sem = ""
        if int(self.semester) == 0:
            sem = "Elo"
        else:
            sem = str(self.semester)
        return f"Semestre: {sem} | Código: {self.code} | Matéria: {self.fullname}"
