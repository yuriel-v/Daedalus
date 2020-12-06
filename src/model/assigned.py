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
    exam_type = Column(Integer, primary_key=True)                       # Tipo de trabalho
    status = Column(Integer)                                            # Status
    grade = Column(Float)                                               # Nota

    student = relationship('Student', back_populates='is_assigned')
    subject = relationship('Subject', back_populates='assigned_to')

    def reset(self):
        self.status = 3
        self.grade = 0.0

    def show_status(self):
        statuses = ['OK', 'EPN', 'PND']
        if self.status in statuses:
            return statuses[self.status]
        else:
            return "ERR"

    def show_type(self):
        exam_types = ['AV1', 'APS1', 'AV2', 'APS2', 'AV3']
        if self.exam_type in exam_types:
            return exam_types[self.exam_type]
        else:
            return "ERR"

# Status:
# - 1: OK
# - 2: Entrega pendente (tarefa concluída/parcialmente concluída)
# - 3: Pendente
#
# Tipo de trabalho:
# - 1: Prova AV1 (7pt)
# - 2: Trabalho AV1 (3pt)
# - 3: Prova AV2 (8pt)
# - 4: Trabalho AV2 (2pt)
# - 5: Prova AV3 (10pt)
