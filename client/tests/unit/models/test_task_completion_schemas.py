import uuid
from datetime import date, time

from src.core.schemas.tasks import TaskCompletionResponse, TaskWithCompletionResponse
from src.core.models import TaskCompletion


class TestTaskCompletionSchemas:
    def test_task_completion_response(self, task_model):
        completion_id = str(uuid.uuid4())
        today = date.today()

        completion = TaskCompletion(
            id=completion_id,
            task_id=task_model.id,
            date=today,
            is_started=True,
            started_at=time(hour=10, minute=0),
            is_completed=True,
            completed_at=time(hour=12, minute=0),
        )

        response = TaskCompletionResponse.model_validate(completion)

        assert response.id == completion_id
        assert response.date == today
        assert response.is_started == True
        assert response.started_at == time(hour=10, minute=0)
        assert response.is_completed == True
        assert response.completed_at == time(hour=12, minute=0)

    def test_task_with_completion_response(self, task_model):
        completion_id = str(uuid.uuid4())
        today = date.today()

        completion = TaskCompletion(
            id=completion_id,
            task_id=task_model.id,
            date=today,
            is_started=True,
            started_at=time(hour=10, minute=0),
            is_completed=True,
            completed_at=time(hour=12, minute=0),
        )

        response = TaskWithCompletionResponse.model_validate(task_model)
        response.completion = TaskCompletionResponse.model_validate(completion)

        assert response.id == task_model.id
        assert response.completion is not None
        assert response.completion.id == completion_id
        assert response.completion.date == today
        assert response.completion.is_started == True
        assert response.completion.started_at == time(hour=10, minute=0)
        assert response.completion.is_completed == True
        assert response.completion.completed_at == time(hour=12, minute=0)
