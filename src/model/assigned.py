# Arquivo de mapeamento objeto-relacional para provas/trabalhos.

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey
from model.student import Student
from model.subject import Subject
from model import Base


class Assigned(Base):
    __tablename__ = 'assigned'

    std_id = Column(Integer, ForeignKey(Student.id), primary_key=True)  # ID do estudante
    sbj_id = Column(Integer, ForeignKey(Subject.id), primary_key=True)  # ID da matéria
    status = Column(Integer)                                            # Status
    exam_type = Column(Integer)                                         # Tipo de trabalho
    grade = Column(Float)                                               # Nota

    student = relationship('Student', back_populates='is_assigned')
    subject = relationship('Subject', back_populates='assigned_to')

    def reset(self):
        self.status = 2
        self.grade = 0.0

# Status:
# - 0: OK
# - 1: Entrega pendente (tarefa concluída/parcialmente concluída)
# - 2: Pendente
#
# Tipo de trabalho:
# - 0: Trabalho AV1 (3pt)
# - 1: Trabalho AV2 (2pt)
# - 2: Prova AV1 (7pt)
# - 3: Prova AV2 (8pt)
# - 4: Prova AV3 (10pt)
