from model.student import Student
from model.subject import Subject
from model.assigned import Assigned
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
                    if not reg.subject.active:  # reactivating a locked subject
                        reg.subject.active = True
                        if reg.semester != self.cur_semester:  # retrying a failed subject
                            reg.semester = self.cur_semester
                            for exam in student.is_assigned:
                                if exam.subject == reg.subject:
                                    exam.reset()

            for subj in subjects:  # registering for new subjects
                self.session.add(subj)
                registry = Registered(semester=self.cur_semester, active=True)
                registry.subject = subj
                registry.student = student
                student.registered_on.append(registry)
                for x in range(1, 6):
                    exam = Assigned(status=3, exam_type=x, grade=0.0)
                    exam.subject = subj
                    exam.student = student
                    student.is_assigned.append(exam)

            self.session.commit()
            self.session.expunge_all()
            return 0
        except Exception as e:
            self.session.rollback()
            print(f"Exception caught at registering students: {e}")
            return 1

    def find(self, student, exams=True, previous=False):
        self.session.rollback()
        if isinstance(student, Student):
            if exams:
                if previous:
                    a = {
                        x.subject.code: [y for y in student.is_assigned if y.sbj_id == x.sbj_id]
                        for x in student.registered_on
                        if x.semester < self.cur_semester
                    }
                else:
                    a = {
                        x.subject.code: [y for y in student.is_assigned if y.sbj_id == x.sbj_id]
                        for x in student.registered_on
                        if x.semester == self.cur_semester
                    }
            else:
                if previous:
                    a = {x.subject.code: x.subject for x in student.registered_on if x.semester < self.cur_semester}
                else:
                    a = {x.subject.code: x.subject for x in student.registered_on if x.semester == self.cur_semester}
            return a

        elif isinstance(student, int):  # by discord ID only!
            # unable to use stdao.find_by_discord_id() here because of circular imports
            st = self.session.query(Student).filter(Student.discord_id == student).first()
            return self.find(student=st, exams=exams, previous=previous)

        else:
            return dict({})

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
