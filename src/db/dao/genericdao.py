from abc import ABC
from db import DBSession
from sqlalchemy.orm import Session, scoped_session
from typing import Union


class GenericDao(ABC):
    def __init__(self, session=None, autoinit=True):
        if not autoinit:
            self.session = None
        elif session is None or not isinstance(session, Union[Session, scoped_session].__args__):
            self.session: scoped_session = DBSession()
        else:
            self.session = session
        self.session.expire_on_commit = False

    def destroy(self):
        self.session.remove()
        self.session = None

    def create(self, session=None):
        if session is None or not isinstance(session, Union[Session, scoped_session].__args__):
            self.session: scoped_session = DBSession()
        else:
            self.session = session
        self.session.expire_on_commit = False

    def active(self):
        return self.session is None
