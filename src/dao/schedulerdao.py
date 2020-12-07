from typing import Union
from sqlalchemy.orm import joinedload
from model.student import Student
from model.subject import Subject
from model.exam import Exam
from model.registered import Registered
from dao import smkr
from datetime import date


class SchedulerDao:
    def __init__(self):
        self.session = smkr()
        self.cur_semester = date(month=(lambda: 1 if date.today().month < 7 else 7)(), day=1, year=date.today().year)

    def register(self, student: Student, subjects: set[Subject]):
        self.session.rollback()
        try:
            self.session.add(student)

            for reg in student.registered_on:
                if reg.subject in subjects:
                    subjects.remove(reg.subject)
                    if not reg.active:  # reactivating a locked subject
                        reg.active = True
                    if reg.semester != self.cur_semester:  # retrying a failed subject
                        reg.semester = self.cur_semester
                        for exam in reg.exams:
                            exam.reset()

            for subj in subjects:  # registering new subjects
                self.session.add(subj)
                registry = Registered(semester=self.cur_semester, active=True)
                registry.subject = subj
                registry.student = student
                student.registered_on.append(registry)
                for x in range(1, 6):
                    exam = Exam(exam_type=x, status=3, grade=0.0)
                    exam.registry = registry
                    registry.exams.append(exam)

            self.session.commit()
            self.session.expunge_all()
            return 0
        except Exception as e:
            self.session.rollback()
            print(f"Exception caught at registering students: {e}")
            return 1

    def find(self, student: Student, exams=False, previous=False):
        self.session.rollback()
        if student is not None:
            q = self.session.query(Registered)
            if not previous:
                q = q.filter(Registered.semester == self.cur_semester, Registered.std_id == student.id)
            else:
                q = q.filter(Registered.semester < self.cur_semester, Registered.std_id == student.id)
            q = q.all()

            # attach subjects
            subjects = self.session.query(Subject).filter(Subject.id.in_([int(x.sbj_id) for x in q])).all()
            for subj in subjects:
                for reg in q:
                    if int(reg.sbj_id) == int(subj.id):
                        reg.subject = subj
            # attach exams
            if exams:
                exams = list(self.session.query(Exam).filter(Exam.id.in_([int(x.id) for x in q])).all())
                for reg in q:
                    reg.eager_exams = [exam for exam in exams if int(exam.id) == int(reg.id)]
                    reg.eager_exams.sort(key=lambda x: x.exam_type)
            return q
        else:
            return None

    def find_exam(self, student: Student, subject_id: int, exam_type: int, current=True, active=True):
        self.session.rollback()
        if not all((student, subject_id, exam_type in range(1, 6))):
            return None
        else:
            q = self.session.query(Exam).join(Registered, Registered.id == Exam.id)
            q = q.filter(Registered.std_id == student.id, Registered.sbj_id == subject_id, Exam.exam_type == exam_type)
            # SELECT * FROM exam AS e JOIN registered AS r ON e.id = r.id
            # WHERE r.std_id = student.id AND r.sbj_id = subject.id AND e.exam_type = exam_type
            if current:
                cur_semester = date(day=1, year=date.today().year, month=(lambda: 1 if date.today().month < 7 else 7)())
                q = q.filter(Registered.semester == cur_semester)
                # AND e.semester = cur_semester
            if active:
                q = q.filter(Registered.active == 'true')
            return q.first()

    def update(self, student: Student, subject: Union[int, Subject], exam_type: int, newval, grade: bool, current=True, active=True):
        """
        Atualiza um dado em um trabalho.
        O booleano 'grade' será verdadeiro para atualizar a nota, falso para atualizar o status.
        """
        self.session.rollback()
        if not all((student, subject, exam_type, newval)):
            return 2
        else:
            try:
                exam: Exam = self.find_exam(
                    student=student,
                    subject_id=(lambda: subject.id if isinstance(subject, Subject) else subject)(),
                    exam_type=exam_type, current=current,
                    active=active
                )
                if exam is None:
                    return 3
                else:
                    if grade:
                        exam.grade = round(newval, 1)
                    else:
                        if isinstance(newval, str):
                            exam.status = ['OK', 'EPN', 'PND'].index(newval) + 1
                        else:
                            exam.status = newval
                    self.session.add(exam)
                    self.session.commit()
                    return 0
            except Exception as e:
                print(f"Exception caught at update grade: {e}")
                self.session.rollback()
                return 1

    def lock(self, student: Student, subjects: list[Subject], lock_all=False):
        if not (subjects or lock_all):
            return 2
        self.session.rollback()

        try:
            self.session.add(student)
            for reg in student.registered_on:
                if lock_all or reg.subject in subjects:
                    reg.active = False
            self.session.commit()
            self.session.expunge_all()
            return 0
        except Exception as e:
            self.session.rollback()
            print(f"Exception caught at registering students: {e}")
            return 1
