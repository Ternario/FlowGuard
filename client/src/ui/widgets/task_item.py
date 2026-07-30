from datetime import datetime, date, time

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy


class TaskItem(QWidget):
    def __init__(self, task, on_start_cb, on_complete_cb):
        super().__init__()
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        completion = task.completions or None
        is_started = completion.is_started if completion else False
        is_completed = completion.is_completed if completion else False

        text_wrapper = QWidget()
        text_wrapper.setMinimumWidth(0)
        text_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

        text_layout = QVBoxLayout(text_wrapper)

        title = task.title
        label_title = QLabel(title)
        label_title.setStyleSheet('font-size: 20px; font-weight: bold;')
        label_title.setWordWrap(True)

        text_layout.addWidget(label_title)

        main_layout.addWidget(text_wrapper, 2)
        main_layout.addStretch()

        time_wrapper = QWidget()
        time_wrapper.setMinimumWidth(0)
        time_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        timee_layout = QVBoxLayout(time_wrapper)

        scheduled_start_dt = self._format_or_fact_dt(task.start_time)
        scheduled_end_dt = self._format_or_fact_dt(task.end_time)

        actual_start_dt = self._format_or_fact_dt(completion.started_at) if completion else '-'
        actual_end_dt = self._format_or_fact_dt(completion.completed_at) if completion else '-'

        label_start_dt = QLabel(
            f'<b>Start:</b> Scheduled at: {scheduled_start_dt} || Actual started at: {actual_start_dt}'
        )
        label_start_dt.setStyleSheet('font-size: 16px;')

        label_end_at = QLabel(
            f'<b>Finish:</b> Scheduled at: {scheduled_end_dt} || Actual finished at: {actual_end_dt}'
        )
        label_end_at.setStyleSheet('font-size: 16px;')

        timee_layout.addWidget(label_start_dt)
        timee_layout.addWidget(label_end_at)
        timee_layout.addStretch()

        main_layout.addWidget(time_wrapper, 2)

        btn_wrapper = QWidget()
        btn_wrapper.setMinimumWidth(0)
        btn_wrapper.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        btn_layout = QHBoxLayout(btn_wrapper)
        btn_start = QPushButton('Start')
        btn_start.setFixedWidth(90)
        btn_start.setStyleSheet(
            """
            QPushButton {
                background-color: #2e7d32; color: white; font-weight: bold; padding: 4px 12px; border-radius: 4px;
                height: 40px;
            }
            QPushButton:hover {background-color: #1b5e20;}
            """
        )

        btn_end = QPushButton('Finish')
        btn_end.setFixedWidth(90)
        btn_end.setStyleSheet(
            """
            QPushButton {
                background-color: #1976d2; color: white; font-weight: bold; padding: 4px 12px; border-radius: 4px;
                height: 40px;
            }
            QPushButton:hover {background-color: #0d47a1;}
            """
        )

        btn_start.clicked.connect(lambda: on_start_cb(task.id))
        btn_end.clicked.connect(lambda: on_complete_cb(task.id))

        if is_started or is_completed:
            btn_start.hide()
        else:
            btn_start.show()

        if is_started and not is_completed:
            btn_end.show()
        else:
            btn_end.hide()
        main_layout.addStretch()
        btn_layout.addWidget(btn_start)
        btn_layout.addWidget(btn_end)

        main_layout.addWidget(btn_wrapper, 1)

        description = task.description or 'No description'
        label_description = QLabel(description)
        label_description.setStyleSheet('font-size: 18px;')
        label_description.setWordWrap(True)
        label_description.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum
        )

        text_layout.addWidget(label_description)

    @staticmethod
    def _format_or_fact_dt(value):
        if not value:
            return '-'
        if isinstance(value, time):
            value = datetime.combine(date.today(), value)
        return value.strftime('%d.%m.%Y %H:%M')
