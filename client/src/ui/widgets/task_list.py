from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout, QLabel, QPushButton
)

from src.core.services.local_tasks import TaskService
from src.ui.widgets.header_date import HeaderDate
from src.ui.widgets.task_create import TaskCreate
from src.core.schemas.tasks import TaskCreate as TaskCreateSchema
from src.ui.widgets.task_item import TaskItem


class TaskList(QWidget):
    def __init__(self, session_factory, parent=None):
        super().__init__(parent)

        self.session_factory = session_factory
        self.selected_date = date.today()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.date_header = HeaderDate(initial_date=self.selected_date)
        self.date_header.date_changed.connect(self.on_date_changed)

        self.task_create = TaskCreate()
        self.task_create.btn_add.clicked.connect(self._on_click_create_task)
        self.task_create.task_created.connect(self.handle_create_task)

        self.header = QHBoxLayout()

        self.header_label = QLabel(f'Tasks for today:')
        self.header_label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self.header_refresh_button = QPushButton('Refresh')
        self.header_refresh_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2e7d32; color: white; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #1b5e20;}
            """
        )

        self.header_refresh_button.clicked.connect(lambda: self.refresh_tasks())

        self.header.addWidget(self.header_label)
        self.header.addStretch()
        self.header.addWidget(self.header_refresh_button)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget::item {
                border-bottom: 1px solid #555555;
                padding: 5px;
            }

            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
        layout.addWidget(self.date_header)
        layout.addWidget(self.task_create)
        layout.addLayout(self.header)
        layout.addWidget(self.task_list)

        self.refresh_tasks()

    def on_date_changed(self, new_date: date) -> None:
        self.selected_date = new_date

        is_today = 'today' if self.selected_date == date.today() else f' {self.selected_date.strftime('%d.%m.%Y')}'

        self.header_label.setText(f'Tasks for {is_today}:')
        self.refresh_tasks()

    def _on_click_create_task(self):
        target_date = max(self.selected_date, date.today())

        self.task_create.open_create_dialog(target_date)

    def handle_create_task(self, task_dto: TaskCreateSchema):
        try:
            with self.session_factory() as db:
                service = TaskService(db)
                service.create_task(
                    task_dto
                )

            self.refresh_tasks()
            QMessageBox.information(
                self, 'Success', 'Task created successfully!'
            )

        except Exception as e:
            QMessageBox.critical(
                self, 'Database Error', f'Failed to save task: {str(e)}'
            )

    def refresh_tasks(self):
        self.task_list.clear()

        with self.session_factory() as db:
            service = TaskService(db)
            tasks = service.get_task_actual_list(self.selected_date)

            for task in tasks:
                item = QListWidgetItem(self.task_list)
                widget = TaskItem(
                    task=task,
                    on_start_cb=self.handle_start_task,
                    on_complete_cb=self.handle_complete_task
                )

                item.setSizeHint(widget.sizeHint())
                self.task_list.addItem(item)
                self.task_list.setItemWidget(item, widget)

    def handle_start_task(self, task_id: str):
        try:
            with self.session_factory() as db:
                service = TaskService(db)
                service.start_task(task_id=task_id, target_date=date.today())
            self.refresh_tasks()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def handle_complete_task(self, task_id: str):
        try:
            with self.session_factory() as db:
                service = TaskService(db)
                service.complete_task(task_id=task_id, target_date=date.today())
            self.refresh_tasks()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
