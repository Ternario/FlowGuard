import uuid
from datetime import time, date, datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Time, Date, Boolean, Enum, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.connection import Base
from src.utils.enum_choices.recurrence_type import RecurrenceType


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    to_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    recurrence_type: Mapped[RecurrenceType] = mapped_column(
        Enum(RecurrenceType),
        default=RecurrenceType.NONE,
        index=True
    )

    recurrence_interval: Mapped[int] = mapped_column(Integer, default=1)

    recurrence_days: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recurrence_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    completions: Mapped[List['TaskCompletion']] = relationship(
        'TaskCompletion', back_populates='task', cascade='all, delete-orphan'
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class TaskCompletion(Base):
    __tablename__ = 'task_completions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(ForeignKey('tasks.id'), nullable=False, index=True)
    task: Mapped['Task'] = relationship('Task', back_populates='completions')

    date: Mapped[date] = mapped_column(Date, nullable=False)

    is_started: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
