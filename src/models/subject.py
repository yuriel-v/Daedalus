# Arquivo de mapeamento objeto-relacional para matérias.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String)        # Código da matéria, por exemplo "BD2" para banco de dados II
    fullname = Column(String)    # Nome completo da matéria, por exemplo "Banco de Dados II"
