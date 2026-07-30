from datetime import date
from typing import Optional

from PyQt6.QtCore import QDate, QTime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QDateEdit, QCheckBox, QHBoxLayout, QTimeEdit, QLabel,
    QComboBox, QSpinBox, QWidget, QPushButton, QMessageBox, QStackedWidget
)
from pydantic import ValidationError

from src.core.schemas.tasks import TaskCreate as TaskCreateSchema
from src.utils.enum_choices.recurrence_type import RecurrenceType


class TaskCreateDialog(QDialog):
    def __init__(self, initial_date: Optional[date] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Create New Task')
        self.resize(450, 500)

        self.created_task_data: Optional[TaskCreateSchema] = None
        self._initial_date = initial_date or date.today()

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText('Enter title (min 10 chars)...')
        form_layout.addRow('Title *:', self.input_title)

        self.input_description = QTextEdit()
        self.input_description.setMaximumHeight(80)
        self.input_description.setPlaceholderText('Optional description...')
        form_layout.addRow('Description:', self.input_description)

        self.input_to_date = QDateEdit()
        self.input_to_date.setCalendarPopup(True)
        self.input_to_date.setDisplayFormat('dd.MM.yyyy')
        self.input_to_date.setDate(
            QDate(
                self._initial_date.year,
                self._initial_date.month,
                self._initial_date.day,
            )
        )

        self.chk_is_all_day = QCheckBox('All Day Task')
        self.chk_is_all_day.toggled.connect(self._on_all_day_toggled)

        date_row = QHBoxLayout()
        date_row.addWidget(self.input_to_date)
        date_row.addWidget(self.chk_is_all_day)
        form_layout.addRow('Target Date:', date_row)

        self.input_start_time = QTimeEdit(QTime(9, 0))
        self.input_start_time.setDisplayFormat('HH:mm')

        self.input_end_time = QTimeEdit(QTime(10, 0))
        self.input_end_time.setDisplayFormat('HH:mm')

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel('From:'))
        time_row.addWidget(self.input_start_time)
        time_row.addWidget(QLabel('To:'))
        time_row.addWidget(self.input_end_time)
        form_layout.addRow('Time:', time_row)

        self.combo_recurrence_type = QComboBox()
        for r_type in RecurrenceType:
            self.combo_recurrence_type.addItem(r_type.value, r_type)

        form_layout.addRow('Recurrence Type:', self.combo_recurrence_type)

        self.recurrence_details_widget = QWidget()
        rec_details_layout = QVBoxLayout(self.recurrence_details_widget)
        rec_details_layout.setContentsMargins(0, 5, 0, 5)
        rec_details_layout.setSpacing(8)

        self.recurrence_stack = QStackedWidget()

        self.page_daily = QWidget()
        daily_layout = QHBoxLayout(self.page_daily)
        daily_layout.setContentsMargins(0, 0, 0, 0)
        daily_layout.addWidget(QLabel('Every'))
        self.input_interval = QSpinBox()
        self.input_interval.setRange(1, 30)
        self.input_interval.setValue(1)
        daily_layout.addWidget(self.input_interval)
        daily_layout.addWidget(QLabel('day(s)'))
        daily_layout.addStretch()

        self.page_weekly = QWidget()
        weekly_layout = QHBoxLayout(self.page_weekly)
        weekly_layout.setContentsMargins(0, 0, 0, 0)

        self.week_days_checkbox = {}
        days_names = [('Mon', 0), ('Tue', 1), ('Wed', 2), ('Thu', 3), ('Fri', 4), ('Sat', 5), ('Sun', 6)]

        for name, day_num in days_names:
            chk = QCheckBox(name)
            self.week_days_checkbox[day_num] = chk
            weekly_layout.addWidget(chk)

        weekly_layout.addStretch()

        self.recurrence_stack.addWidget(self.page_daily)
        self.recurrence_stack.addWidget(self.page_weekly)

        until_layout = QHBoxLayout()
        until_layout.addWidget(QLabel('Repeat Until:'))

        self.input_rec_end_date = QDateEdit()
        self.input_rec_end_date.setCalendarPopup(True)
        self.input_rec_end_date.setDisplayFormat('dd.MM.yyyy')
        self.input_rec_end_date.setDate(QDate.currentDate().addMonths(1))
        until_layout.addWidget(self.input_rec_end_date)
        until_layout.addStretch()

        rec_details_layout.addWidget(self.recurrence_stack)
        rec_details_layout.addLayout(until_layout)

        form_layout.addRow('', self.recurrence_details_widget)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        self.combo_recurrence_type.currentIndexChanged.connect(self._on_recurrence_changed)

        self._on_recurrence_changed()

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton('Cancel')
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton('Create Task')
        btn_save.setStyleSheet(
            """
            QPushButton { background-color: #2e7d32; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px; }
            QPushButton:hover { background-color: #1b5e20; }
            """
        )
        btn_save.clicked.connect(self._on_save)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        main_layout.addLayout(btn_layout)

    def _on_all_day_toggled(self, is_checked: bool):
        self.input_start_time.setEnabled(not is_checked)
        self.input_end_time.setEnabled(not is_checked)

    def _on_recurrence_changed(self):
        selected_type = self.combo_recurrence_type.currentData()

        if selected_type == RecurrenceType.NONE:
            self.recurrence_details_widget.setVisible(False)

        elif selected_type == RecurrenceType.DAILY:
            self.recurrence_details_widget.setVisible(True)
            self.recurrence_stack.setCurrentWidget(self.page_daily)

        elif selected_type == RecurrenceType.WEEKLY:
            self.recurrence_details_widget.setVisible(True)
            self.recurrence_stack.setCurrentWidget(self.page_weekly)

            target_day = self.input_to_date.date().toPyDate()
            current_weekday = target_day.weekday()

            has_chacked = any(chk.isChecked() for chk in self.week_days_checkbox.values())

            if not has_chacked:
                self.week_days_checkbox[current_weekday].setChecked(True)

    def _on_save(self):
        try:
            title = self.input_title.text().strip()
            desc = self.input_description.toPlainText().strip() or None

            is_all_day = self.chk_is_all_day.isChecked()
            to_date_val = self.input_to_date.date().toPyDate()

            start_time_val = (
                None
                if is_all_day
                else self.input_start_time.time().toPyTime()
            )
            end_time_val = (
                None if is_all_day else self.input_end_time.time().toPyTime()
            )

            rec_type = self.combo_recurrence_type.currentData()
            rec_interval = self.input_interval.value()

            rec_end_date_val = None
            if rec_type != RecurrenceType.NONE:
                rec_end_date_val = self.input_rec_end_date.date().toPyDate()

            task_dto = TaskCreateSchema(
                title=title,
                description=desc,
                is_all_day=is_all_day,
                to_date=to_date_val,
                start_time=start_time_val,
                end_time=end_time_val,
                recurrence_type=rec_type,
                recurrence_interval=rec_interval,
                recurrence_end_date=rec_end_date_val,
            )

            self.created_task_data = task_dto
            self.accept()

        except ValidationError as e:
            error_messages = []
            for err in e.errors():
                msg = err.get('msg', 'Invalid data')
                msg = msg.replace('Value error, ', '')
                error_messages.append(f'• {msg}')

            QMessageBox.warning(
                self,
                'Validation Error',
                'Please fix the following issues:\n\n'
                + '\n'.join(error_messages),
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
