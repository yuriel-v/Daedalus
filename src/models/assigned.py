# Arquivo de mapeamento objeto-relacional para provas/trabalhos.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey

Base = declarative_base()


class Assigned(Base):
    __tablename__ = 'assigned'

    std_id = Column(Integer, ForeignKey("students.id"), primary_key=True)  # ID do estudante
    sbj_id = Column(Integer, ForeignKey("subjects.id"), primary_key=True)  # ID da matéria
    status = Column(Integer)                                               # Status
    exam_type = Column(Integer)                                            # Tipo de trabalho

    def __repr__(self):
        return f"Assigned(std_id={self.std_id}, sbj_id={self.sbj_id}, status={self.status}, exam_type={self.exam_type}"

# Status:
# - 0: Pendente
# - 1: Entrega pendente (tarefa concluída/parcialmente concluída)
# - 2: TBD (To Be Disclosed, detalhes ainda para serem esclarecidos)
# - 3: OK
#
# Tipo de trabalho:
# - 0: Trabalho AV1 (3pt)
# - 1: Trabalho AV2 (2pt)
# - 2: Prova AV1 (7pt)
# - 3: Prova AV2 (8pt)
# - 4: Prova AV3 (10pt)
