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
            return q
        else:
            return None

    def update_assignment(self, student: Student, subject: Subject, grade=None, state=None):
        if not (grade or state):
            return 2
        self.session.rollback()

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
