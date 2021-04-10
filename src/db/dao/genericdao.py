from abc import ABC

from sqlalchemy.engine.base import Transaction
from db import DBSession
from sqlalchemy.orm import Session, scoped_session
from typing import Union


class GenericDao(ABC):
    def __init__(self, session=None, autoinit=True):
        if not autoinit:
            self._session = None
        elif session is None or not isinstance(session, Union[Session, scoped_session].__args__):
            self._session: scoped_session = DBSession()
        else:
            self._session = session
        self._session.expire_on_commit = False

    def destroy(self):
        self._session.close()
        self._session = None

    def create(self, session=None):
        if session is None or not isinstance(session, Union[Session, scoped_session].__args__):
            self._session: scoped_session = DBSession()
        else:
            self._session = session
        self._session.expire_on_commit = False

    def active(self):
        return self._session is None

    def _gcommit(self, tr: Transaction):
        tr.commit()
        self._session.commit()
        # DBSession.commit()
