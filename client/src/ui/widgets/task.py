from datetime import date
from typing import List

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QListWidgetItem,
    QMessageBox,
)

from src.utils.enum_choices.recurrence_type import RecurrenceType
from src.utils.enum_choices.week_days import WeekDays
from src.utils.constants.task_btn import btn_height, btn_width


class Task(QWidget):
    def __init__(self, task, on_active_task, on_deactivate_task, on_delete_task) -> None:
        super().__init__()
        self.item: QListWidgetItem | None = None

        self.task = task
        self.is_active = task.is_active

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        text_wrapper = QWidget()
        text_wrapper.setMinimumWidth(0)
        text_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

        text_layout = QVBoxLayout(text_wrapper)
        title = self.task.title
        label_title = QLabel(title)
        label_title.setStyleSheet('font-size: 20px; font-weight: bold;')
        label_title.setWordWrap(True)

        text_layout.addWidget(label_title)

        description = self.task.description or 'No description'
        label_description = QLabel(description)
        label_description.setStyleSheet('font-size: 18px;')
        label_description.setWordWrap(True)
        label_description.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        text_layout.addWidget(label_description)

        main_layout.addWidget(text_wrapper, 3)

        time_wrapper = QWidget()
        text_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

        time_layout = QVBoxLayout(time_wrapper)

        self.start_date = QLabel(f'Start date: {self.task.to_date}')
        self.end_date = QLabel(
            f'End date: {self.task.recurrence_end_date if self.task.recurrence_end_date else self.task.to_date}'
        )
        self.task_duration = QLabel()
        self.recurrence_interval = QLabel()

        time_layout.addWidget(self.start_date)
        time_layout.addWidget(self.end_date)
        time_layout.addWidget(self.task_duration)
        time_layout.addWidget(self.recurrence_interval)
        time_layout.addStretch()

        main_layout.addWidget(time_wrapper, 2)

        self._show_actual_data()

        btn_wrapper = QWidget()
        btn_wrapper.setMinimumWidth(0)
        btn_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        btn_layout = QHBoxLayout(btn_wrapper)
        self.btn_activate = QPushButton('Activate')
        self.btn_activate.setMaximumWidth(btn_width)
        self.btn_activate.setFixedHeight(btn_height)
        self.btn_activate.setStyleSheet(
            """
            QPushButton {
                background-color: #2e7d32; color: #FFFFFF; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #1b5e20;}
            """
        )

        self.btn_deactivate = QPushButton('Deactivate')
        self.btn_deactivate.setMaximumWidth(btn_width)
        self.btn_deactivate.setFixedHeight(btn_height)
        self.btn_deactivate.setStyleSheet(
            """
            QPushButton {
                background-color: #1E3AB8; color: #FFFFFF; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #0d47a1;}
            """
        )

        self.btn_delete = QPushButton('Delete')
        self.btn_delete.setMaximumWidth(btn_width)
        self.btn_delete.setFixedHeight(btn_height)
        self.btn_delete.setStyleSheet(
            """
            QPushButton {
                background-color: #F41515; color: #FFFFFF; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #0d47a1;}
            """
        )

        self.btn_activate.clicked.connect(lambda: on_active_task(self, self.task.id))
        self.btn_deactivate.clicked.connect(lambda: on_deactivate_task(self, self.task.id))
        self.btn_delete.clicked.connect(lambda: on_delete_task(self, self.task.id))

        main_layout.addStretch()
        btn_layout.addWidget(self.btn_activate, 1)
        btn_layout.addWidget(self.btn_deactivate, 1)
        btn_layout.addWidget(self.btn_delete, 1)

        main_layout.addWidget(btn_wrapper, 1)

        self.handle_btn_status()

    def _show_actual_data(self) -> None:
        if not self.task.is_all_day:
            self.task_duration.setText(
                f'Start time: {self.task.start_time.strftime("%H:%M")} - End time: {self.task.end_time.strftime("%H:%M")}'
            )
        else:
            self.task_duration.setText('All day')

        if self.task.recurrence_type == RecurrenceType.NONE.value:
            self.recurrence_interval.hide()

        elif self.task.recurrence_type == RecurrenceType.DAILY.value:
            days: str = f'{self.task.recurrence_interval} days' if int(self.task.recurrence_interval) > 1 else 'day'
            self.recurrence_interval.setText(f'Recurrence interval: every {days}')
        else:
            week_days: List[str] = []
            task_rec_days: List[int] = [int(day) for day in self.task.recurrence_days.replace(',', '')]

            for day in WeekDays:
                if day.value in task_rec_days:
                    week_days.append(day.name.capitalize())

            week_days_to_show: str = ', '.join(week_days)

            self.recurrence_interval.setText(f'Recurrence interval: every {week_days_to_show}')

    def activate_status(self) -> None:
        if self.task.recurrence_end_date and self.task.recurrence_end_date > date.today():
            self.is_active = True
            self.btn_activate.hide()
            self.btn_deactivate.show()
        else:
            QMessageBox.information(
                self, 'Error', 'You cannot activate a task whose last recurrence date is in the past'
            )

    def deactivate_status(self) -> None:
        if self.task.recurrence_end_date and self.task.recurrence_end_date > date.today():
            self.is_active = False
            self.btn_deactivate.hide()
            self.btn_activate.show()
        else:
            QMessageBox.information(
                self, 'Error', 'You cannot deactivate a task whose last recurrence date is in the past'
            )

    def handle_btn_status(self) -> None:
        if (
            self.task.recurrence_end_date
            and self.task.recurrence_end_date < date.today()
            or not self.task.recurrence_end_date
            and self.task.to_date < date.today()
        ):
            self.btn_activate.hide()
            self.btn_deactivate.hide()
        elif self.is_active:
            self.btn_activate.hide()
            self.btn_deactivate.show()
        else:
            self.btn_activate.show()
            self.btn_deactivate.hide()
