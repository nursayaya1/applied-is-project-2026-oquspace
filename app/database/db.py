import os
from pathlib import Path

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
engine = create_engine(DATABASE_URL, echo=os.getenv('SQL_ECHO') == '1',
                       connect_args={'check_same_thread': False})


@event.listens_for(engine, 'connect')
def enable_foreign_keys(connection, _):
    connection.execute('PRAGMA foreign_keys=ON')


def init_db():
    from app.database import models  # Register all tables before creation.
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
