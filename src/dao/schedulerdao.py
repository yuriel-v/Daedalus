from dao import smkr
from datetime import date
from model.student import Student
from model.subject import Subject
from model.exam import Exam
from model.registered import Registered
from sqlalchemy.orm.session import Session
from typing import Union


class SchedulerDao:
    def __init__(self):
        self.session: Session = smkr()
        self.cur_semester = date(month=(lambda: 1 if date.today().month < 7 else 7)(), day=1, year=date.today().year)

    def register(self, student: Student, subjects: dict) -> int:
        if student is None or not subjects:
            return 2
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        try:
            self.session.add(student)

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
                            self.session.add(reg)
            except Exception as e:
                print('Caught at checking old subjects')
                raise e

            try:
                for subj in subjects.values():  # registering new subjects
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
                print('Caught at adding new subjects')
                raise e
        except Exception as e:
            self.session.rollback()
            print(f"Exception caught at registering students: {e}")
            return 1

    def find_enrollments(self, std_id: int, previous=False, active=True) -> list[Registered]:
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if std_id is not None:
            q = self.session.query(Registered).filter(Registered.std_id == std_id)
            if active:
                q = q.filter(Registered.active == 'true')
            if previous:
                q = q.filter(Registered.semester <= self.cur_semester)
            else:
                q = q.filter(Registered.semester == self.cur_semester)
            q: list = q.all()
            return q
        else:
            return []

    def find_exam(self, student: Student, subject_id: int, exam_type: int, current=True, active=True) -> Union[Registered, None]:
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if not all((student, subject_id, exam_type in range(1, 6))):
            return None
        else:
            q = self.session.query(Exam)
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

    def update(self, student: Student, subject: Subject, exam_type: int, newval, grade: bool, current=True, active=True) -> int:
        """
        Atualiza um dado em um trabalho.
        O booleano 'grade' será verdadeiro para atualizar a nota, falso para atualizar o status.
        """
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")
        if not all((student, subject, exam_type, newval is not None)):
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
                        if int(exam.status) != 1:
                            self.session.rollback()
                            return 4
                        else:
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

    def lock(self, student: Student, subjects: list[str], lock_all=False) -> int:
        if not (subjects or lock_all):
            return 2
        try:
            self.session.rollback()
        except Exception as e:
            print(f"Caught during rollback: {e}")

        try:
            eager_enrollments = self.find_enrollments(student.id)
            for reg in eager_enrollments:
                if lock_all or reg.subject.code in subjects:
                    reg.active = False
                    self.session.add(reg)
            self.session.commit()
            self.session.expunge_all()
            return 0
        except Exception as e:
            self.session.rollback()
            print(f"Exception caught at locking enrollments: {e}")
            return 1
