from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import datetime

Base = declarative_base()

class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    extension = Column(String, nullable=True)
    creation_time = Column(DateTime, nullable=False)
    remark = Column(String, nullable=True)
    record_creation_time = Column(DateTime, default=datetime.datetime.now)

def create_tables(engine):
    Base.metadata.create_all(engine)

def clean_tables(engine):
    for table in reversed(Base.metadata.sorted_tables):
        engine.execute(table.delete())