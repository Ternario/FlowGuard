from datetime import date, time
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def base_task():
    task = MagicMock()
    task.id = 'task-id'
    task.title = 'a' * 25
    task.description = 'a' * 100
    task.to_date = date.today()
    task.start_time = time(hour=10, minute=0)
    task.end_time = time(hour=11, minute=0)
    return task


@pytest.fixture
def base_task_with_completion(base_task):
    task = base_task
    completion = MagicMock()

    completion.id = 'completion-id'
    completion.task_id = task.id

    task.completion = completion

    return task
