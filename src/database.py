import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from exceptions import DatabaseException

class Database:
    def __init__(self):
        self._session = sessionmaker()
        self._session_factory = scoped_session(self._session)
        self._engine = None

    def init(self, uri, expire_on_commit=True):
        self.do_init(uri, expire_on_commit)

    def do_init(self, uri: str, expire_on_commit: bool = True):
        self._engine = create_engine(uri)
        self._session.configure(bind=self._engine, expire_on_commit=expire_on_commit)
        logging.info('database initialized')

    def engine(self):
        return self._engine

    def session(self):
        if not self._engine:
            raise DatabaseException("dabatase not initialized")
        return self._session_factory()

db = Database()

def get_db():
    if not db:
        raise DatabaseException("dabatase not initialized")
    return db

@contextmanager
def get_session():
    s = get_db().session()
    
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()
