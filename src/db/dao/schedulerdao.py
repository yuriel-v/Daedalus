from sqlalchemy.orm.query import Query
from db import DBSession as session
from datetime import date
from db.model.student import Student
from db.model.subject import Subject
from db.model.exam import Exam
from db.model.registered import Registered
from sqlalchemy.orm.session import Session
from typing import Union
session: Session


class SchedulerDao:
    def __init__(self):
        self.cur_semester = date(month=(lambda: 1 if date.today().month < 7 else 7)(), day=1, year=date.today().year)

    def register(self, student: Student, subjects: dict) -> int:
        """
        Matricula um estudante qualquer em uma matéria qualquer.
        - Se a matéria for trancada, ela é reativada.
        - Se a matéria for de um semestre anterior, todos os seus trabalhos são redefinidos.

        Retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Erro de sintaxe nos argumentos passados.
        """
        if student is None or not subjects:
            return 2
        try:
            session.begin()
            session.add(student)

            try:
                enrollments = self.find_enrollments(student.id, previous=True, active=False)
                for reg in enrollments:
                    if reg.subject.code in subjects.keys():
                        del subjects[reg.subject.code]
                        changed = False
                        if not reg.active:  # reactivating a locked subject
                            changed = True
                            reg.active = True
                        if reg.semester != self.cur_semester:  # retrying a failed subject
                            changed = True
                            reg.semester = self.cur_semester
                            for exam in reg.exams:
                                exam.reset()
                        if changed:
                            session.add(reg)
            except Exception as e:
                print('Caught at checking old subjects')
                raise e

            try:
                for subj in subjects.values():  # registering new subjects
                    session.add(subj)
                    registry = Registered(semester=self.cur_semester, active=True)
                    registry.subject = subj
                    registry.student = student
                    student.registered_on.append(registry)
                    for x in range(1, 6):
                        exam = Exam(exam_type=x, status=3, grade=0.0)
                        exam.registry = registry
                        registry.exams.append(exam)

                session.commit()
                return 0
            except Exception as e:
                print('Caught at adding new subjects')
                raise e
        except Exception as e:
            session.rollback()
            print(f"Exception caught at registering students: {e}")
            return 1

    def find_enrollments(self, std_id: int, previous=False, active=True) -> list[Registered]:
        """
        Busca todas as matrículas correspondentes a um ID de estudante.
        - Se `previous = True`, retorna também matrículas de semestres anteriores.
        - Se `active = False`, retorna também matrículas trancadas.

        Retorna uma lista de instâncias `Registered` para todos os resultados encontrados, ou uma lista vazia.
        """
        if std_id is not None:
            try:
                q = session.query(Registered).filter(Registered.std_id == std_id)
                if active:
                    q = q.filter(Registered.active == 'true')
                if previous:
                    q = q.filter(Registered.semester <= self.cur_semester)
                else:
                    q = q.filter(Registered.semester == self.cur_semester)
                q: list = q.all()
                return q
            except Exception as e:
                print(f"Exception caught at finding enrollments: {e}")
                session.rollback()
                return []
        else:
            return []

    def find_exam(self, student: Student, subject_id: int, exam_type: int, current=True, active=True) -> Union[Exam, None]:
        """
        Busca uma prova em específico, para um estudante e matéria em específico.
        - Se `current = False`, busca também entre matrículas de semestres anteriores.
        - Se `active = False`, busca também entre matrículas trancadas.

        Retorna a instância correspondente de `Exam`, ou `None` em erro de sintaxe ou trabalho não encontrado.
        """
        if not all((student, subject_id, exam_type in range(1, 6))):
            return None
        else:
            try:
                q: Query = session.query(Exam).join(Registered, Registered.id == Exam.id)
                q = q.filter(Registered.std_id == student.id, Registered.sbj_id == subject_id, Exam.exam_type == exam_type)
                # SELECT * FROM exam AS e JOIN registered AS r ON e.id = r.id (implicit join, defined by joined eager load)
                # WHERE r.std_id = student.id AND r.sbj_id = subject.id AND e.exam_type = exam_type
                if current:
                    cur_semester = date(day=1, year=date.today().year, month=(lambda: 1 if date.today().month < 7 else 7)())
                    q = q.filter(Registered.semester == cur_semester)
                    # AND e.semester = cur_semester
                if active:
                    q = q.filter(Registered.active == 'true')
                    # AND e.active = true
                return q.first()
            except Exception as e:
                print(f'Rolling back, exception caught at finding exams: {e}')
                session.rollback()
                return None

    def update(self, student: Student, subject: Union[Subject, int], exam_type: int, newval, grade: bool, current=True, active=True) -> int:
        """
        Atualiza um dado em um trabalho.
        - Se `grade = True`, atualiza notas; senão, atualiza status.
        - Se `current = True`, busca também por matrículas de semestres anteriores.
        - Se `active = True`, busca também por matrículas trancadas.

        Retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Erro de sintaxe nos argumentos passados.
        - `3`: Trabalho não encontrado.
        - `4`: (Atualização de nota) Trabalho ainda não entregue. Não se atualiza notas de trabalhos não entregues.
        """
        if not all((student, subject, exam_type, newval is not None)):
            return 2
        else:
            session.begin()
            try:
                exam = self.find_exam(
                    student=student,
                    subject_id=(subject.id if isinstance(subject, Subject) else subject),
                    exam_type=exam_type, current=current,
                    active=active
                )
                if exam is None:
                    return 3
                else:
                    session.add(exam)
                    if grade:
                        if int(exam.status) != 1:
                            session.rollback()
                            return 4
                        else:
                            exam.grade = round(newval, 1)
                    else:
                        if isinstance(newval, str):
                            exam.status = ('OK', 'EPN', 'PND').index(newval) + 1
                        elif isinstance(newval, int):
                            exam.status = ('OK', 'EPN', 'PND')[newval + 1]
                        else:
                            session.rollback()
                            return 2
                    session.commit()
                    return 0
            except Exception as e:
                print(f"Exception caught at update grade: {e}")
                session.rollback()
                return 1

    def lock(self, student: Student, subjects: list[str], lock_all=False) -> int:
        """
        Tranca uma, várias ou todas as matrículas do estudante passado.
        - Se `lock_all = True`, tranca todas as matrículas; senão, tranca somente aquelas especificadas na lista `subjects`.
        - A lista `subjects` é uma lista de strings, contendo os códigos uppercase e 3-char das matérias a serem trancadas.
          - Essa lista pode ser passada vazia quando `lock_all = True`.

        Retorna um inteiro indicando o que aconteceu:
        - `0`: Operação bem-sucedida;
        - `1`: Exceção lançada, transação sofreu rollback;
        - `2`: Nada a trancar.
        """
        if not (subjects or lock_all):
            return 2

        try:
            eager_enrollments = self.find_enrollments(student.id)
            for reg in eager_enrollments:
                if lock_all or reg.subject.code in subjects:
                    reg.active = False
                    session.add(reg)
            return 0
        except Exception as e:
            session.rollback()
            print(f"Exception caught at locking enrollments: {e}")
            return 1
