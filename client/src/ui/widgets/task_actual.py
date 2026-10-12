from datetime import datetime, date
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)

from src.core.schemas.tasks import TaskCompletionResponse
from src.utils.constants.task_btn import btn_height, btn_width
from src.ui.utils.time_formatter import format_or_fact_dt


class TaskActual(QWidget):
    def __init__(self, task, on_start_cb, on_complete_cb):
        super().__init__()
        completion: Optional[TaskCompletionResponse] = task.completion or None
        self.tc_date = completion.date if completion else None
        self.is_started = completion.is_started if completion else False
        self.is_completed = completion.is_completed if completion else False

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        text_wrapper = QWidget()
        text_wrapper.setMinimumWidth(0)
        text_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

        text_layout = QVBoxLayout(text_wrapper)

        title = task.title
        label_title = QLabel(title)
        label_title.setStyleSheet('font-size: 20px; font-weight: bold;')
        label_title.setWordWrap(True)

        text_layout.addWidget(label_title)

        description = task.description or 'No description'
        label_description = QLabel(description)
        label_description.setStyleSheet('font-size: 18px;')
        label_description.setWordWrap(True)
        label_description.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        text_layout.addWidget(label_description)

        main_layout.addWidget(text_wrapper, 2)
        main_layout.addStretch()

        time_wrapper = QWidget()
        time_wrapper.setMinimumWidth(0)
        time_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        time_layout = QVBoxLayout(time_wrapper)

        self.scheduled_start_dt = format_or_fact_dt(task.start_time)
        self.scheduled_end_dt = format_or_fact_dt(task.end_time)

        self.actual_start_dt = format_or_fact_dt(completion.started_at if completion else None)
        self.actual_end_dt = format_or_fact_dt(completion.completed_at if completion else None)

        self.start_status_text = '<b>Start:</b> Scheduled at: {} || Actual started at: {}'
        self.end_status_text = '<b>Finish:</b> Scheduled at: {} || Actual finished at: {}'

        self.label_start_dt = QLabel(self.start_status_text.format(self.scheduled_start_dt, self.actual_start_dt))
        self.label_start_dt.setStyleSheet('font-size: 16px;')

        self.label_end_at = QLabel(self.end_status_text.format(self.scheduled_end_dt, self.actual_end_dt))
        self.label_end_at.setStyleSheet('font-size: 16px;')

        time_layout.addWidget(self.label_start_dt)
        time_layout.addWidget(self.label_end_at)
        time_layout.addStretch()

        main_layout.addWidget(time_wrapper, 2)

        btn_wrapper = QWidget()
        btn_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        btn_layout = QHBoxLayout(btn_wrapper)
        self.btn_start = QPushButton('Start')
        self.btn_start.setMaximumWidth(btn_width)
        self.btn_start.setFixedHeight(btn_height)
        self.btn_start.setStyleSheet(
            """
            QPushButton {
                background-color: #F7ED3B; color: #000000; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #1b5e20;}
            """
        )

        self.btn_end = QPushButton('Finish')
        self.btn_end.setMaximumWidth(btn_width)
        self.btn_end.setFixedHeight(btn_height)
        self.btn_end.setStyleSheet(
            """
            QPushButton {
                background-color: #1E3AB8; color: #FFFFFF; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #0d47a1;}
            """
        )

        self.done_label = QLabel('Done')
        self.done_label.setMaximumWidth(btn_width)
        self.done_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.done_label.setFixedHeight(btn_height)
        self.done_label.setStyleSheet(
            """
                background-color: #2e7d32; color: #FFFFFF; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            """
        )

        self.btn_start.clicked.connect(lambda: on_start_cb(self, task.id))
        self.btn_end.clicked.connect(lambda: on_complete_cb(self, task.id))

        self.handle_btn_status()

        main_layout.addStretch()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_end)
        btn_layout.addWidget(self.done_label)
        main_layout.addWidget(btn_wrapper, 1)

    def handle_start_status(self) -> None:
        self.is_started = True
        self.tc_date = date.today()

        actual_start: str = format_or_fact_dt(datetime.now().time())

        self.label_start_dt.setText(self.start_status_text.format(self.scheduled_start_dt, actual_start))
        self.btn_start.hide()
        self.btn_end.show()

    def handle_end_status(self) -> None:
        self.is_completed = True

        actual_end: str = format_or_fact_dt(datetime.now().time())

        self.label_end_at.setText(self.end_status_text.format(self.scheduled_end_dt, actual_end))
        self.btn_end.hide()
        self.done_label.show()

    def handle_btn_status(self) -> None:
        if not self.is_started:
            self.btn_end.hide()
            self.done_label.hide()

        if self.is_started and not self.is_completed:
            self.btn_start.hide()
            self.done_label.hide()

        if self.is_started and self.is_completed:
            self.btn_start.hide()
            self.btn_end.hide()
            self.done_label.show()
