# Arquivo de mapeamento objeto-relacional para provas/trabalhos.

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey
from db.model.registered import Registered
from db import Base


class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, ForeignKey(Registered.id), primary_key=True)          # ID da matrícula
    exam_type = Column(Integer, primary_key=True)                              # Tipo de trabalho
    status = Column(Integer)                                                   # Status
    grade = Column(Float)                                                      # Nota

    registry = relationship("Registered", back_populates="exams", lazy="joined")

    def reset(self):
        self.status = 3
        self.grade = 0.0

    def show_status(self):
        statuses = ('OK ', 'EPN', 'PND')
        if self.status in range(1, 4):
            return statuses[self.status - 1]
        else:
            return "ERR"

    def show_type(self):
        exam_types = ('AV1', 'APS1', 'AV2', 'APS2', 'AV3')
        if self.exam_type in range(1, 6):
            return exam_types[self.exam_type - 1]
        else:
            return "ERR"

    def show_grade(self):
        if self.status != 1:
            return '?.?'
        else:
            return round(self.grade, 1)


"""
Status:
- 1: OK
- 2: Entrega pendente (tarefa concluída/parcialmente concluída)
- 3: Pendente

Tipo de trabalho:
- 1: Prova AV1 (8pt)
- 2: Trabalho AV1 (2pt)
- 3: Prova AV2 (8pt)
- 4: Trabalho AV2 (2pt)
- 5: Prova AV3 (10pt)
"""
