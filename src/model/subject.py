# Arquivo de mapeamento objeto-relacional para matérias.

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from model import Base


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String)        # Código da matéria, por exemplo 'BD2' para banco de dados II
    fullname = Column(String)    # Nome completo da matéria, por exemplo 'Banco de Dados II'

    assigned_to = relationship('Assigned', back_populates='subject')
    registered_by = relationship('Registered', back_populates='subject')
