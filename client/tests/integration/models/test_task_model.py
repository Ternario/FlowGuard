from datetime import date
import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError


from src.core.models.tasks import Task
from src.utils.enum_choices.recurrence_type import RecurrenceType


class TestTaskModel:
    def test_task_create(self, db_session):
        today = date.today()

        current_task_count = db_session.scalar(select(func.count()).select_from(Task))

        task = Task(title='a' * 25, to_date=today)

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        db_session.expunge_all()

        task_count_after_create = db_session.scalar(select(func.count()).select_from(Task))

        assert task_count_after_create == current_task_count + 1

        saved_task = db_session.get(Task, task.id)

        assert saved_task is not None
        assert saved_task.id == task.id
        assert saved_task.title == 'a' * 25
        assert saved_task.to_date == today

    def test_task_nullable_constraints(self, db_session):
        task = Task(title=None, to_date=None)

        db_session.add(task)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_task_defaults(self, db_session):
        today = date.today()

        task = Task(title='a' * 25, to_date=today)

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        db_session.expunge_all()

        saved_task = db_session.get(Task, task.id)

        assert isinstance(saved_task.id, str)
        assert saved_task.created_at is not None
        assert saved_task.is_all_day is False
        assert saved_task.is_active is True
        assert saved_task.is_synced is False
        assert saved_task.recurrence_type == RecurrenceType.NONE

    def test_task_delete(self, db_session, task_model):
        db_session.delete(task_model)
        db_session.commit()

        db_session.expunge_all()

        deleted_task = db_session.get(Task, task_model.id)

        assert deleted_task is None
