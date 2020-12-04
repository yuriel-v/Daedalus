from model.student import Student
from model.subject import Subject
from model.assigned import Assigned
from model.registered import Registered
from dao import smkr
from datetime import date


class SchedulerDao:
    def __init__(self):
        self.session = smkr()

    def register(self, student: Student, subjects: set[Subject]):
        if not subjects:
            return 2
        self.session.rollback()

        try:
            cur_semester = date(month=(lambda: 1 if date.today().month < 7 else 7)(), day=1, year=date.today().year)
            self.session.add(student)

            for reg in student.registered_on:
                if reg.subject in subjects:
                    subjects.remove(reg.subject)
                    if not reg.subject.active:  # reactivating a locked subject
                        reg.subject.active = True
                        if reg.semester != cur_semester:  # retrying a failed subject
                            reg.semester = cur_semester
                            for exam in student.is_assigned:
                                if exam.subject == reg.subject:
                                    exam.reset()

            for subj in subjects:  # registering for new subjects
                registry = Registered(semester=cur_semester, active=True)
                registry.subject = subj
                student.registered_on.append(registry)
                for x in range(0, 5):
                    exam = Assigned(status=2, exam_type=x, grade=0.0)
                    exam.subject = subj
                    student.is_assigned.append(exam)

            self.session.commit()
            self.session.expunge_all()
            return 0
        except Exception as e:
            self.session.rollback()
            print(f"Exception caught at registering students: {e}")
            return 1

    def lock_subject(self, student: Student, subjects: list[Subject], lock_all=False):
        if not (subjects or lock_all):
            return 2
        self.session.rollback()

        try:
            self.session.add(student)
            for reg in student.registered_on:
                if lock_all or reg.subject in subjects:
                    reg.active = False
