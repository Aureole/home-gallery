import logging
from typing import Dict, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from database import get_session, db
from exceptions import DAOConfigError, DAOCreateFailedError, \
    DAOUpdateFailedError, DAODeleteFailedError

Base = declarative_base()

class BaseDAO:
    model_cls : Base

    def find_by_id(cls, model_id: int):
        """
        Find a model by id
        """
        id_col = getattr(cls.model_cls, "id", None)
        if id_col is None:
            return None
        with get_session() as session:
            return session.query(cls.model_cls).filter(id_col==model_id).one_or_none()

    @classmethod
    def find_by_ids(cls, model_ids: List[int]):
        """
        Find a List of models by a list of ids
        """
        id_col = getattr(cls.model_cls, "id", None)
        if id_col is None:
            return []
        with get_session() as session:
            return session.query(cls.model_cls).filter(id_col.in_(model_ids)).all()

    @classmethod
    def create(cls, properties: Dict, commit: bool = True):
        """
        Generic for creating models
        :raises: DAOCreateFailedError
        """
        if cls.model_cls is None:
            raise DAOConfigError()
        model = cls.model_cls()
        for key, value in properties.items():
            setattr(model, key, value)
        try:
            db.session().add(model)
            db.session().flush()
            if commit:
                db.session().commit()
        except SQLAlchemyError as ex:
            db.session().rollback()
            raise DAOCreateFailedError(exception=ex)
        return model

    @classmethod
    def create_if_not_exists(cls, properties: Dict):
        """
        Generic for creating models if not exists
        :raises: DAOCreateFailedError
        """
        if cls.model_cls is None:
            raise DAOConfigError()
        model = cls.model_cls()
        for key, value in properties.items():
            setattr(model, key, value)
        try:
            with get_session() as session:
                session.add(model)
            return model
        except IntegrityError as ex:
            error = str(ex)
            if 'UNIQUE constraint failed' in error or 'psycopg2.errors.UniqueViolation' in error:
                logging.warning("already exists %s ", str(properties))
            else:
                raise DAOCreateFailedError(exception=ex)
        except SQLAlchemyError as ex:
            raise DAOCreateFailedError(exception=ex)

    @classmethod
    def find_by(cls, *criterion):
        with get_session() as session:
            return session.query(cls.model_cls).filter(*criterion).one_or_none()

    @classmethod
    def find_or_create(cls, properties: Dict, commit: bool, *criterion):
        """
        Generic for get or creating models
        :raises: DAOCreateFailedError
        """
        model = cls.find_by(*criterion)
        if model:
            return model

        model = cls.model_cls()
        for key, value in properties.items():
            setattr(model, key, value)
        try:
            db.session().add(model)
            if commit:
                db.session().commit()
            return model
        except IntegrityError as ex:
            db.session().rollback()
            if 'UNIQUE constraint failed' in str(ex):
                logging.warning("already exists %s ", str(properties))
                model = cls.find_by(*criterion)
                if model:
                    return model
                else:
                    raise DAOCreateFailedError(message='model not found')
            else:
                raise DAOCreateFailedError(exception=ex)
        except SQLAlchemyError as ex:
            db.session().rollback()
            raise DAOCreateFailedError(exception=ex)

    @classmethod
    def update(cls, model: Base, properties: Dict, commit: bool = True):
        """
        Generic update a model
        :raises: DAOUpdateFailedError
        """
        for key, value in properties.items():
            setattr(model, key, value)
        try:
            db.session().merge(model)
            if commit:
                db.session().commit()
        except SQLAlchemyError as ex:
            db.session().rollback()
            raise DAOUpdateFailedError(exception=ex)
        return model

    @classmethod
    def delete(cls, model: Base, commit: bool = True):
        """
        Generic delete a model
        :raises: DAODeleteFailedError
        """
        try:
            db.session().delete(model)
            if commit:
                db.session().commit()
        except SQLAlchemyError as ex:
            db.session().rollback()
            raise DAODeleteFailedError(exception=ex)

    @classmethod
    def add(cls, model: Base):
        with get_session() as session:
            return session.add(model)

    @classmethod
    def count(cls):
        with get_session() as session:
            return session.query(cls.model_cls).count()

    @classmethod
    def find_last_one(cls):
        id_col = getattr(cls.model_cls, "id", None)
        if id_col is None:
            return None
        with get_session() as session:
            return session.query(cls.model_cls).order_by(id_col.desc()).limit(1).one_or_none()

    @classmethod
    def get(cls, model: Base):
        id_col = getattr(cls.model_cls, "id", None)
        if id_col is None:
            return None
        with get_session() as session:
            return session.query(cls.model_cls).filter(id_col==model.id).one_or_none()
