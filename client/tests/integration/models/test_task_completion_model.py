from datetime import date, time
import pytest
from sqlalchemy.exc import IntegrityError

from src.core.models.tasks import TaskCompletion


class TestTaskCompletionModel:
    def test_task_completion_create(self, db_session, task_model):
        today = date.today()

        completion = TaskCompletion(
            task_id=task_model.id, date=today, is_started=True, started_at=time(hour=10, minute=0)
        )

        db_session.add(completion)
        db_session.commit()
        db_session.refresh(completion)

        saved_completion = db_session.get(TaskCompletion, completion.id)

        assert saved_completion is not None
        assert saved_completion.task_id == task_model.id
        assert saved_completion.date == today
        assert saved_completion.is_started == True
        assert saved_completion.started_at == time(hour=10, minute=0)
        assert saved_completion.is_completed == False
        assert saved_completion.is_synced == False

    def test_task_completion_constraint(self, db_session, task_model):
        today = date.today()

        first_completion = TaskCompletion(
            task_id=task_model.id,
            date=today,
        )

        db_session.add(first_completion)
        db_session.commit()

        second_completion = TaskCompletion(
            task_id=task_model.id,
            date=today,
        )

        db_session.add(second_completion)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_task_completion_cascade_delete(self, db_session, task_model):
        completion = TaskCompletion(task_id=task_model.id, date=date.today())

        db_session.add(completion)
        db_session.commit()

        completion_id = completion.id

        db_session.delete(task_model)
        db_session.commit()

        deleted_completion = db_session.get(TaskCompletion, completion_id)

        assert deleted_completion is None
