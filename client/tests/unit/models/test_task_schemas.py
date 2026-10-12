import uuid
from datetime import date, time, timedelta
import pytest
from pydantic import ValidationError

from src.core.models import Task
from src.core.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from src.utils.enum_choices.recurrence_type import RecurrenceType


class TestTaskSchemas:
    def test_task_create(self):
        data = {
            'title': 'a' * 50,
            'description': 'a' * 100,
            'to_date': date.today(),
            'start_time': time(hour=10, minute=0),
            'end_time': time(hour=20, minute=0),
        }

        schema = TaskCreate(**data)

        assert schema.title == 'a' * 50
        assert schema.description == 'a' * 100
        assert schema.to_date == date.today()
        assert schema.start_time == time(hour=10, minute=0)
        assert schema.end_time == time(hour=20, minute=0)
        assert schema.is_all_day is False

    @pytest.mark.parametrize('invalid_title', ['a' * 5, 'a' * 256])
    def test_title_length_validation(self, invalid_title):
        with pytest.raises(ValidationError) as context:
            TaskCreate(title=invalid_title, to_date=date.today())

        errors = context.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('title',)

    @pytest.mark.parametrize('invalid_description', ['a' * 2001])
    def test_description_length_validation(self, invalid_description):
        with pytest.raises(ValidationError) as context:
            TaskCreate(title='a' * 50, description=invalid_description, to_date=date.today())

        errors = context.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('description',)

    def test_date_in_past(self):
        with pytest.raises(ValidationError) as context:
            TaskCreate(title='a' * 50, to_date=date.today() - timedelta(days=1))

        assert 'Start date cannot be in the past' in str(context.value)

    def test_time_overlap(self):
        with pytest.raises(ValidationError) as context:
            TaskCreate(
                title='a' * 50,
                to_date=date.today(),
                start_time=time(hour=10, minute=0),
                end_time=time(hour=9, minute=0),
            )

        assert 'End time cannot be less than start time' in str(context.value)

    def test_date_overlap(self):
        with pytest.raises(ValidationError) as context:
            TaskCreate(title='a' * 50, to_date=date.today(), recurrence_end_date=date.today() - timedelta(days=1))

        assert 'End date cannot be less than start date' in str(context.value)

    def test_is_all_day_and_time(self):
        data = {
            'title': 'a' * 50,
            'to_date': date.today(),
            'start_time': time(hour=10, minute=0),
            'end_time': time(hour=11, minute=0),
            'is_all_day': True,
        }

        with pytest.raises(ValidationError) as context:
            TaskCreate(**data)

        assert 'Start and end time cannot be set for all days tasks' in str(context.value)

    def test_recurrence_end_date(self):
        with pytest.raises(ValidationError) as context:
            TaskCreate(
                title='a' * 50,
                to_date=date.today(),
                recurrence_type=RecurrenceType.DAILY,
                recurrence_interval=1,
                recurrence_end_date=None,
            )

        assert 'End date must be set for recurrence tasks' in str(context.value)

    def test_recurrence_interval(self):
        with pytest.raises(ValidationError) as context:
            TaskCreate(
                title='a' * 50,
                to_date=date.today(),
                recurrence_type=RecurrenceType.DAILY,
                recurrence_interval=None,
                recurrence_end_date=date.today() + timedelta(days=10),
            )

        assert 'Recurrence interval cannot be empty' in str(context.value)

    def test_all_fields_optional(self):
        schema = TaskUpdate()

        assert schema.model_dump(exclude_unset=True) == {}

    def test_partial_update(self):
        schema = TaskUpdate(title='a' * 60)

        assert schema.title == 'a' * 60

    @pytest.mark.parametrize('invalid_title', ['a' * 5, 'a' * 256])
    def test_update_title_length_validation(self, invalid_title):
        with pytest.raises(ValidationError) as context:
            TaskUpdate(title=invalid_title)

        errors = context.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('title',)

    def test_task_response(self):
        task_id = str(uuid.uuid4())
        today = date.today()
        end_date = today + timedelta(days=10)

        task = Task(
            id=task_id,
            title='a' * 25,
            description='a' * 500,
            is_all_day=False,
            to_date=today,
            start_time=time(hour=10, minute=0),
            end_time=time(hour=12, minute=0),
            recurrence_type=RecurrenceType.DAILY,
            recurrence_interval=2,
            recurrence_days='1,2,3',
            recurrence_end_date=end_date,
            is_active=True,
            is_synced=True,
        )

        response = TaskResponse.model_validate(task)

        assert response.id == task_id
        assert response.title == task.title
        assert response.description == task.description
        assert response.is_all_day == task.is_all_day
        assert response.to_date == task.to_date
        assert response.start_time == task.start_time
        assert response.end_time == task.end_time
        assert response.recurrence_type == task.recurrence_type
        assert response.recurrence_interval == task.recurrence_interval
        assert response.recurrence_days == task.recurrence_days
        assert response.recurrence_end_date == task.recurrence_end_date
        assert response.is_active == task.is_active
