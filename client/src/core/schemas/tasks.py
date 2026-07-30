from datetime import date, time, datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from src.core.schemas.utils import title_to_validate
from src.core.models.tasks import RecurrenceType


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=10, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)

    is_all_day: bool = False
    to_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_interval: int = Field(1, ge=1)
    recurrence_days: Optional[str] = None
    recurrence_end_date: Optional[date] = None

    @field_validator('title')
    @classmethod
    def title_validator(cls, title_str: str) -> str:
        return title_to_validate(title_str)

    @model_validator(mode='after')
    def validate_data(self) -> TaskCreate:
        if not self.is_all_day and self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError('End time cannot be less than start time')

        if self.recurrence_type != RecurrenceType.NONE:
            if not self.to_date:
                raise ValueError('A start date is required for a recurring task')

        if self.recurrence_end_date and self.recurrence_end_date < self.to_date:
            raise ValueError('End date cannot be less than start date')

        return self


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)

    is_all_day: Optional[bool] = None
    to_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    recurrence_type: Optional[RecurrenceType] = None
    recurrence_interval: Optional[int] = Field(None, ge=1)
    recurrence_days: Optional[str] = None
    recurrence_end_date: Optional[date] = None

    @field_validator('title')
    @classmethod
    def title_validator(cls, title_str: Optional[str]) -> Optional[str]:
        if title_str is not None:
            return title_to_validate(title_str)
        return title_str


class TaskListResponse(BaseModel):
    id: str
    model_config = ConfigDict(from_attributes=True)
    title: str
    description: Optional[str] = None
    recurrence_type: RecurrenceType


class TaskResponse(BaseModel):
    id: str
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: Optional[str] = None

    is_all_day: bool
    to_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    recurrence_type: RecurrenceType
    recurrence_interval: int
    recurrence_days: Optional[str] = None
    recurrence_end_date: Optional[date] = None
    is_active: bool

    created_at: datetime
    updated_at: datetime


class TaskWithCompletionResponse(TaskResponse):
    completions: List[TaskCompletionResponse] = []


class TaskCompletionResponse(BaseModel):
    id: str
    model_config = ConfigDict(from_attributes=True)

    date: date

    is_started: bool
    started_at: Optional[datetime] = None

    is_completed: bool
    completed_at: Optional[datetime] = None


class TaskDateFilterSchema(BaseModel):
    target_date: date
