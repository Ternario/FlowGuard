from datetime import date, datetime, timezone

from typing import List, Optional

from sqlalchemy import or_, select, and_
from sqlalchemy.orm import Session

from src.core.models.tasks import Task, RecurrenceType, TaskCompletion
from src.core.schemas.tasks import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TaskListResponse,
    TaskWithCompletionResponse,
    TaskCompletionResponse,
)


class TaskService:
    """
    Service layer managing the lifecycle, validation, and analytics-ready state of tasks.

    This class serves as the main entry point for all task-related business logic.
    It provides capabilities for CRUD operations, schedule validation for dynamic/recurring
    tasks (daily, weekly, or non-repeating), and two-pass fetching strategies to pair active
    tasks with their daily completion status without polluting the database
    with empty records for missed days.

    Attributes:
        db (Session): The active SQLAlchemy database session used for transaction management.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _check_recurrence_math(task: Task, target_date: date) -> bool:
        """
        Evaluates whether a task is scheduled to appear on a given target date.

        Calculates recurrence intervals for daily and weekly recurring tasks based
        on their initial start date and configuration parameters.

        Args:
            task (Task): The task entity containing recurrence rules.
            target_date (date): The specific calendar date being validated.

        Returns:
            bool: True if the task should be active on the target date, False otherwise.
        """
        if task.recurrence_type == RecurrenceType.NONE:
            return True

        if task.recurrence_type == RecurrenceType.DAILY:
            delta_days = (target_date - task.to_date).days
            return delta_days % task.recurrence_interval == 0

        if task.recurrence_type == RecurrenceType.WEEKLY:
            if not task.recurrence_days:
                return True

            return bool(str(target_date.weekday()) in task.recurrence_days)

        return False

    def _get_task_by_id(self, task_id: str) -> Optional[Task]:
        task: Optional[Task] = self.db.scalar(select(Task).where(Task.id == task_id))

        if not task:
            raise ValueError(f'Task with id {task_id} not found')

        return task

    def _get_task_completion_by_id_and_date(
        self, task_id: str, target_date: date
    ) -> Optional[TaskCompletion]:
        return self.db.scalar(
            select(TaskCompletion).where(
                TaskCompletion.task_id == task_id,
                TaskCompletion.date == target_date,
            )
        )

    def create_task(self, schema: TaskCreate) -> TaskResponse:
        """
        Persists a new task entity in the database.

        Args:
            schema (TaskCreate): Data transfer object containing task attributes.

        Returns:
            TaskResponse: Validated schema representation of the created task.
        """
        task: Task = Task(**schema.model_dump(), is_synced=False)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return TaskResponse.model_validate(task)

    def update_task(self, task_id: str, schema: TaskUpdate) -> TaskResponse:
        """
        Modifies attributes of an existing task by its identifier.

        Args:
            task_id (str): Unique identifier of the task to update.
            schema (TaskUpdate): DTO containing updated fields (partial updates allowed).

        Returns:
            TaskResponse: Updated task data.

        Raises:
            ValueError: If no task matches the provided task_id.
        """
        task: Optional[Task] = self._get_task_by_id(task_id)

        update_data = schema.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(task, k, v)

        task.is_synced = False

        self.db.commit()
        self.db.refresh(task)

        return TaskResponse.model_validate(task)

    def update_task_active_status(self, task_id: str) -> TaskResponse:
        """
        Deactivates a task, effectively hiding it from active task lists.

        Args:
            task_id (str): Unique identifier of the task to deactivate.

        Returns:
            TaskResponse: Updated task data reflecting deactivated status.

        Raises:
            ValueError: If no task matches the provided task_id.
        """
        task: Optional[Task] = self._get_task_by_id(task_id)

        task.is_active = False
        task.is_synced = False

        self.db.commit()
        self.db.refresh(task)

        return TaskResponse.model_validate(task)

    def delete_task(self, task_id: str) -> None:
        """
        Permanently removes a task entity from the database.

        Args:
            task_id (str): Unique identifier of the task to delete.

        Raises:
            ValueError: If no task matches the provided task_id.
        """
        task: Optional[Task] = self._get_task_by_id(task_id)

        if not task:
            raise ValueError(f'Task with id {task_id} not found')

        self.db.delete(task)
        self.db.commit()

    def get_task_list(self, status: Optional[bool] = None) -> List[TaskListResponse]:
        """
        Fetches all tasks, with optional filtering by active status.

        Args:
            status (Optional[bool]): Filter tasks by `is_active` flag.
                    If None, retrieves all tasks regardless of status.

        Returns:
            List[TaskListResponse]: Collection of matching task representations.
        """
        task_query = select(Task)

        if isinstance(status, bool):
            task_query = task_query.where(Task.is_active == status)

        task_list = self.db.scalars(task_query).all()

        if not task_list:
            return []

        return [TaskListResponse.model_validate(task) for task in task_list]

    def get_task_by_id(self, task_id: str) -> TaskResponse:
        """
        Fetches a single task entity by its unique identifier.

        Args:
            task_id (str): Unique identifier of the target task.

        Returns:
            TaskResponse: Schema representation of the requested task.

        Raises:
            ValueError: If no task matches the provided task_id.
        """
        task: Optional[Task] = self._get_task_by_id(task_id)

        return TaskResponse.model_validate(task)

    def get_task_actual_list(
        self, target_date: date
    ) -> List[TaskWithCompletionResponse]:
        """
        Retrieves all active tasks scheduled for a given date with completion states.

        Queries candidates matching global date constraints, filters them via
        recurrence logic, and attaches corresponding `TaskCompletion` records for
        the target date in a two-stage fetch for maximum performance.

        Args:
            target_date (date): Calendar date for which tasks are requested.

        Returns:
            List[TaskWithCompletionResponse]: List of tasks active on target_date,
                each paired with its daily completion record (or None if unstarted).
        """
        tasks_to_validate = select(Task).where(
            Task.is_active == True,
            Task.to_date <= target_date,
            or_(
                Task.recurrence_end_date == None,
                Task.recurrence_end_date >= target_date,
            ),
            or_(
                Task.recurrence_type != RecurrenceType.NONE,
                and_(
                    Task.recurrence_type == RecurrenceType.NONE,
                    Task.to_date == target_date,
                ),
            ),
        )

        validated_tasks = self.db.scalars(tasks_to_validate).all()

        if not validated_tasks:
            return []

        active_tasks = [
            task
            for task in validated_tasks
            if self._check_recurrence_math(task, target_date)
        ]

        if not active_tasks:
            return []

        active_ids = [task.id for task in active_tasks]

        task_completions = select(TaskCompletion).where(
            TaskCompletion.task_id.in_(active_ids),
            TaskCompletion.date == target_date,
        )

        task_completions_result = self.db.scalars(task_completions).all()

        task_completions_map = {c.task_id: c for c in task_completions_result}

        result = []

        for task in active_tasks:
            completion = task_completions_map.get(task.id)

            result.append(
                TaskWithCompletionResponse.model_validate(task).model_copy(
                    update={'completions': completion}
                )
            )

        return result

    def start_task(self, task_id: str, target_date: date) -> TaskCompletionResponse:
        """
        Marks a task as started for a specific target date.

        Creates a new `TaskCompletion` record if none exists for the given date,
        or updates the existing entry. Preserves the original `started_at` timestamp
        if the task was previously started.

        Args:
            task_id (str): Unique identifier of the task to start.
            target_date (date): Calendar date for which the task is being started.

        Returns:
            TaskCompletionResponse: Validated schema representation of the completion state.

        Raises:
            ValueError: If no task matches the provided task_id.
        """
        # is correct request and checking?
        self._get_task_by_id(task_id)

        completion: Optional[TaskCompletion] = self._get_task_completion_by_id_and_date(
            task_id, target_date
        )

        current_datetime: datetime = datetime.now(timezone.utc)

        if completion:
            completion.is_started = True
            if not completion.started_at:
                completion.started_at = current_datetime

            completion.is_synced = False
        else:
            completion: TaskCompletion = TaskCompletion(
                task_id=task_id,
                date=target_date,
                is_started=True,
                started_at=current_datetime,
                is_synced=False,
            )
            self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)

        return TaskCompletionResponse.model_validate(completion)

    def complete_task(self, task_id: str, target_date: date) -> TaskCompletionResponse:
        """
        Marks a previously started task as completed for a specific target date.

        Updates the matching `TaskCompletion` record with completion flags and
        records the current timestamp.

        Args:
            task_id (str): Unique identifier of the task to complete.
            target_date (date): Calendar date for which the task is being completed.

        Returns:
            TaskCompletionResponse: Validated schema representation of the completion state.

        Raises:
            ValueError: If the task does not exist, or if no completion record
                        exists for the target date, or if the task has not been started yet.
        """
        self._get_task_by_id(task_id)

        completion: Optional[TaskCompletion] = self._get_task_completion_by_id_and_date(
            task_id, target_date
        )

        if not completion or not completion.is_started:
            raise ValueError('You cannot complete a task that has not been started')

        completion.is_completed = True
        completion.completed_at = datetime.now(timezone.utc)
        completion.is_synced = False

        self.db.commit()
        self.db.refresh(completion)

        return TaskCompletionResponse.model_validate(completion)
