from core.utils import print_exc, nround
from datetime import date
from db.dao.genericdao import GenericDao
from db.model import Student, Subject, Exam, Registered
from sqlalchemy.orm import Query
from typing import Union


class SchedulerDao(GenericDao):
    def __init__(self, session=None, autoinit=True):
        super().__init__(session=session, autoinit=autoinit)
        self.cur_semester = date(month=(1 if date.today().month < 7 else 7), day=1, year=date.today().year)

    def register(self, student: Union[Student, int], subjects: Union[list[str], tuple[str], set[str]]) -> dict:
        """
        Matricula um estudante em uma ou várias matérias.\n
        Se a matéria for trancada, ela é reativada.
        Se a matéria for de um semestre anterior, todos os seus trabalhos são redefinidos.
        ### Params
        - `student: Student | int`: O estudante (ou seu ID Discord) ingressando nas matérias especificadas;
        - `subjects: list | tuple | set`: Um iterável contendo os códigos (todos `str`) das matérias a serem registradas.

        ### Retorno
        - Um dict com o formato `sbj.code: sbj.fullname` para cada item.
        - Casos excepcionais:
          - `{'err': 1}`: Exceção lançada, transação sofreu rollback;
          - `{'err': 2}`: Erro de sintaxe nos argumentos passados:
              - Estudante nulo ou inexistente;
              - Lista de matérias vazia
          - `{'err': 3}`: Lista de matérias válidas vazia, nada a matricular.
              - Isso é diferente do erro 2, onde o argumento `subjects` é vazio ou nulo. No erro 3, nenhuma matéria com os códigos informados foi encontrada.

        ### Levanta
        - `SyntaxError` nos seguintes casos:
            - Caso `student` não seja uma instância de `Student` ou `int`, nem possa ser convertido para `int`;
            - Caso os valores de `subject` não sejam todos `str`s nem possam ser convertidas para tal.
        """
        if not all([bool(student), bool(subjects)]):
            return {'err': 2}

        try:
            if not isinstance(student, Union[Student, int].__args__):
                student = int(student)
        except Exception:
            raise SyntaxError("Argument 'student' not an instance of Student nor int, cannot be cast to int")

        try:
            subjects = [str(x).upper() for x in subjects if bool(x)]
        except Exception:
            raise SyntaxError("At least one object in argument 'subjects' is not a string and cannot be cast to string")

        tr = None
        try:
            student = self._session.query(Student).filter(Student.discord_id == (student if isinstance(student, int) else student.id)).first()
            if student is None or len(subjects) == 0:
                return {'err': 2}

            tr = self._session.begin_nested()
            modified_subjects = dict({})
            enrollments = self.find_enrollments(student.id, previous=True, active=False)
            for reg in enrollments:
                if reg.subject.code in subjects:
                    modified_subjects[reg.subject.code] = reg.subject.fullname

                    while reg.subject.code in subjects:
                        subjects.remove(reg.subject.code)

                    if not reg.active:  # reactivating a locked subject
                        reg.active = True

                    if reg.semester != self.cur_semester:  # retrying a failed subject
                        reg.semester = self.cur_semester
                        for exam in reg.exams:
                            exam.reset()
                    # no need to add reg to session here, it already is in the session

            loaded_subjects = self._session.query(Subject).filter(Subject.code.in_(subjects)).all()
            if not loaded_subjects and not modified_subjects:
                return {'err': 3}

            for subj in loaded_subjects:
                registry = Registered(semester=self.cur_semester, active=True)
                registry.subject = subj
                registry.student = student
                for x in range(1, 6):
                    exam = Exam(exam_type=x, status=3, grade=0.0)
                    exam.registry = registry
                    registry.exams.append(exam)
                student.registered_on.append(registry)
                modified_subjects[subj.code] = subj.fullname

            self._gcommit(tr)
            self._session.expire_all()
            return modified_subjects
        except Exception:
            print_exc()
            if tr is not None:
                tr.rollback()
            return {'err': 1}

    def find_enrollments(self, std_id: int, previous=False, active=True) -> list[Registered]:
        """
        Busca todas as matrículas correspondentes a um ID de estudante.
        ### Params
        - `std_id: int`: O ID Discord do estudante cujas matrículas vão ser retornadas;
        - `previous: bool`: Quando `True`, retorna matérias de semestres anteriores, senão, somente matérias do semestre atual;
        - `active: bool`: Quando `False`, retorna também matérias trancadas, senão, somente matérias ativas.

        ### Retorno
        - Uma `list`a com instâncias de `Registered` para todos os resultados encontrados.
          - Se nenhum for encontrado, ou se alguma exceção for lançada durante a execução, retorna uma lista vazia.

        ### Levanta
        - `SyntaxError` caso `std_id` não for uma instância de `int`, nem puder ser convertido para `int`.
          - Isso inclui o caso de `std_id` ser `None`.
        """
        if not isinstance(std_id, int):
            try:
                std_id = int(std_id)
            except Exception:
                raise SyntaxError("Student ID is not an instance of 'int' and cannot be cast to 'int'")
        try:
            q = self._session.query(Registered).filter(Registered.std_id == std_id)
            if active:
                q = q.filter(Registered.active == 'true')
            if previous:
                q = q.filter(Registered.semester <= self.cur_semester)
            else:
                q = q.filter(Registered.semester == self.cur_semester)
            return q.all()
        except Exception as e:
            print_exc()
            return []

    def find_exam(self, student: Union[Student, int], subject: Union[Subject, str], exam_type: int, current=True, active=True) -> Union[Exam, None]:
        """
        Busca uma prova em específico, para um estudante e matéria em específico.
        ### Params
        - `student: int | Student`: O estudante (ou o ID Discord dele) cuja prova deve ser pesquisada;
        - `subject: str | Subject`: A matéria (ou o código dela) cuja prova deve ser pesquisada;
        - `current: bool`: Caso `True`, busca provas do semestre atual somente;
        - `active: bool`: Caso `True`, busca provas somente em matérias não trancadas;
        - `exam_type: int`: O tipo da prova ou trabalho a ser pesquisado(a):
          - `1`: Prova AV1
          - `2`: Trabalho APS1
          - `3`: Prova AV2
          - `4`: Trabalho APS2
          - `5`: Prova AV3
        - Por padrão, `current == True` e `active == True`. Isso realiza uma pesquisa entre as matérias ativas do semestre atual.

        ### Retorno
        - A primeira instância de `Exam` encontrada, ou `None` caso uma exceção for lançada, ou nada for encontrado.

        ### Levanta
        - `SyntaxError` nos seguintes casos:
          - `student` não é uma instância de `Student` nem `int` e não pode ser convertido para `int`;
          - `subject` não é uma instância de `Subject` nem `str` e não pode ser convertido para `str`;
          - `exam_type` não é um `int` entre 1 e 5.
        """
        if not isinstance(student, Union[Student, int].__args__):
            try:
                student = int(student)
            except Exception:
                raise SyntaxError("Argument 'student' not an instance of Student nor int, cannot be cast to int")

        if not isinstance(subject, Union[Subject, str].__args__):
            try:
                subject = str(subject)
            except Exception:
                raise SyntaxError("Argument 'subject' not an instance of Subject nor str, cannot be cast to str")

        if not isinstance(exam_type, int):
            try:
                exam_type = int(exam_type)
            except Exception:
                raise SyntaxError("Argument 'exam_type' is not an instance of int, nor can it be cast to int")

        if exam_type not in range(1, 6):
            raise SyntaxError("Argument 'exam_type' is not an integer between 1 and 5")

        try:
            if isinstance(student, int):
                student = self._session.query(Student).filter(Student.discord_id == student).first()
            if isinstance(subject, str):
                subject = self._session.query(Subject).filter(Subject.code == subject.upper()).first()

            q: Query = self._session.query(Exam).join(Registered, Registered.id == Exam.id)
            q = q.filter(Registered.std_id == student.id, Registered.sbj_id == subject.id, Exam.exam_type == exam_type)
            if current:
                q = q.filter(Registered.semester == self.cur_semester)
            if active:
                q = q.filter(Registered.active == 'true')
            return q.first()
        except Exception:
            print_exc()
            return None

    def update(self, student: Union[Student, int], subject: Union[Subject, str], exam_type: int, newval, grade: bool, current=True, active=True) -> dict:
        """
        Atualiza um dado em um trabalho.
        ### Params
        - `student: Student | int`: O estudante (ou o ID Discord dele) cujo trabalho deverá ser atualizado;
        - `subject: Subject | str`: A matéria (ou o código dela) cujo trabalho deverá ser atualizado;
        - `newval`: O novo valor do status ou da nota do trabalho/prova;
        - `grade: bool`: Caso `True`, atualiza a nota do trabalho/prova com `newval`, senão, atualiza o status.
        - `current: bool`: Caso `True`, busca entre provas do semestre atual somente;
        - `active: bool`: Caso `True`, busca entre provas somente em matérias não trancadas;
        - `exam_type: int`: O tipo da prova ou trabalho a ser pesquisado(a):
          - `1`: Prova AV1
          - `2`: Trabalho APS1
          - `3`: Prova AV2
          - `4`: Trabalho APS2
          - `5`: Prova AV3

        ### Retorno
        - Um dict no formato `{sbj.fullname: 0}` no caso de sucesso.
        - Casos excepcionais:
            - `{'err': 1}`: Exceção lançada, transação sofreu rollback;
            - `{'err': 2}`: Erro de sintaxe nos argumentos passados.
            - `{'err': 3}`: Trabalho não encontrado.
            - `{'err': 4}`: (Atualização de nota) Trabalho ainda não entregue. Não se atualiza notas de trabalhos não entregues.

        ### Levanta
        - `SyntaxError` nos casos a seguir:
          - `student` não é uma instância de `Student` nem `int` e não pode ser convertido para `int`;
          - `subject` não é uma instância de `Subject` nem `str` e não pode ser convertido para `str`;
          - `exam_type` não é um `int` entre 1 e 5.
        """
        if not isinstance(student, Union[Student, int].__args__):
            try:
                student = int(student)
            except Exception:
                raise SyntaxError("Argument 'student' not an instance of Student nor int, cannot be cast to int")

        if not isinstance(subject, Union[Subject, str].__args__):
            try:
                subject = str(subject)
            except Exception:
                raise SyntaxError("Argument 'subject' not an instance of Subject nor str, cannot be cast to str")

        if not isinstance(exam_type, int):
            try:
                exam_type = int(exam_type)
            except Exception:
                raise SyntaxError("Argument 'exam_type' is not an instance of int, nor can it be cast to int")

        if exam_type not in range(1, 6):
            raise SyntaxError("Argument 'exam_type' is not an integer between 1 and 5")

        tr = None
        try:
            tr = self._session.begin_nested()
            if isinstance(student, int):
                student = self._session.query(Student).filter(Student.discord_id == student).first()
            if isinstance(subject, str):
                subject = self._session.query(Subject).filter(Subject.code == subject.upper()).first()

            exam = self.find_exam(
                student=student,
                subject=subject,
                exam_type=exam_type, current=current,
                active=active
            )

            if exam is None:
                return {'err': 3}
            else:
                if grade:
                    if int(exam.status) != 1:
                        tr.rollback()
                        return {'err': 4}
                    else:
                        exam.grade = nround(newval, 1)
                else:
                    if isinstance(newval, str):
                        exam.status = ('OK', 'EPN', 'PND').index(newval - 1)
                    elif isinstance(newval, int):
                        exam.status = newval
                    else:
                        tr.rollback()
                        return {'err': 2}
                self._gcommit(tr)
                return {subject.fullname: 0}
        except Exception:
            print_exc()
            if tr is not None:
                tr.rollback()
            return {'err': 1}

    def lock(self, student: Union[Student, int], subjects: Union[list[str], tuple[str], set[str]], lock_all: bool = False) -> dict:
        """
        Tranca uma, várias ou todas as matrículas de um estudante.
        ### Params
        - `student: Student | int`: O estudante (ou o ID Discord dele) cuja(s) matéria(s) deverá(ão) ser trancada(s);
        - `subjects: list[str]`: Um iterável contendo o(s) código(s) da(s) matéria(s) a ser(em) trancada(s);
        - `lock_all: bool`: Caso `True`, tranca todas as matérias do estudante.

        ### Retorno
        - Um dict no formato `{0: [sbj1.fullname, sbj2.fullname, ...]}` em caso de sucesso.
        - Casos excepcionais:
            - `{'err': 1}`: Exceção lançada, transação sofreu rollback;
            - `{'err': 2}`: Nada a trancar.

        ### Levanta
        - `SyntaxError` nos casos a seguir:
          - `student` não é uma instância de `Student` nem `int` e não pode ser convertido para `int`;
          - `subjects` não é uma instância de uma lista, tupla ou conjunto;
          - Pelo menos um elemento de `subject` não é uma `str` nem pode ser convertido para `str`.
        """
        if not isinstance(student, Union[Student, int].__args__):
            try:
                student = int(student)
            except Exception:
                raise SyntaxError("Argument 'student' not an instance of Student nor int, cannot be cast to int")

        if not isinstance(subjects, Union[list, tuple, set].__args__):
            raise SyntaxError("Argument 'subjects' not an instance of list, tuple or set")

        try:
            subjects = tuple([str(x).upper() for x in subjects])
        except Exception:
            raise SyntaxError("At least one object in argument 'subjects' is not a string and cannot be cast to string")

        if not (subjects or lock_all):
            return {'err': 2}

        tr = None
        try:
            print(f'Calling scdao.lock with student {student} | subjects {subjects}')
            tr = self._session.begin_nested()
            changed = False
            if isinstance(student, int):
                student = self._session.query(Student).filter(Student.discord_id == student).first()

            eager_enrollments = self.find_enrollments(student.id)
            modified_enrollments = []

            for reg in eager_enrollments:
                print(f"Current registry's subject code: {reg.subject.code}")
                if lock_all or reg.subject.code in subjects:
                    changed = True
                    reg.active = False
                    modified_enrollments.append(reg.subject.fullname)

            self._gcommit(tr)
            return {0: modified_enrollments} if changed else {'err': 2}
        except Exception:
            print_exc()
            if tr is not None:
                tr.rollback()
            return {'err': 1}
