from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.connection import Base
from src.core.models.tasks import Task


@pytest.fixture(scope='function')
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    test_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = test_session()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def task_model(db_session):
    task = Task(
        title='Test task from fixture',
        to_date=date.today(),
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task
