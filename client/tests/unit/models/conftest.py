import uuid
from datetime import date

import pytest

from src.core.models import Task


@pytest.fixture
def task_model():
    return Task(
        id=str(uuid.uuid4()),
        title='Test task from fixture',
        to_date=date.today(),
    )
