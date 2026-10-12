from datetime import date
from typing import Type, List

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
)

from src.core.services.local_tasks import TaskService
from src.ui.widgets.header_date import HeaderDate
from src.ui.widgets.task_create import TaskCreate
from src.core.schemas.tasks import (
    TaskCreate as TaskCreateSchema,
    TaskWithCompletionResponse,
    TaskResponse,
)
from src.ui.widgets.task_actual import TaskActual
from src.ui.utils.decorators import db_errors
from src.ui.utils.widget_navigate import NavWidget
from src.ui.widgets.task import Task
from src.utils.enum_choices.direction import Direction
from src.utils.enum_choices.menu_title import MenuTitle
from src.utils.enum_choices.task_status import TaskStatus


class TaskList(QWidget):
    def __init__(self, session_factory, parent=None):
        super().__init__(parent)

        self.session_factory = session_factory
        self.selected_date = date.today()
        self.page = MenuTitle.TODAY.value
        self.task_status = TaskStatus.ACTIVE

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.date_header = HeaderDate(initial_date=self.selected_date)
        self.date_header.date_changed.connect(self.on_date_changed)

        self.task_create = TaskCreate()
        self.task_create.btn_add.clicked.connect(self._on_click_create_task)
        self.task_create.task_created.connect(self.create_task)

        self.header = QHBoxLayout()
        self.header_label = QLabel('Tasks for today:')
        self.header_label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self.header_refresh_button = QPushButton('Refresh')
        self.header_refresh_button.setMaximumWidth(100)
        self.header_refresh_button.setFixedHeight(40)
        self.header_refresh_button.setStyleSheet(
            """
            QPushButton {
                background-color: #1E3AB8; color: #FFFFFF; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #1b5e20;}
            """
        )

        self.header_refresh_button.clicked.connect(self.refresh_tasks)

        self.task_status_filter = QComboBox()
        self.task_status_filter.setMaximumWidth(100)
        self.task_status_filter.setMaximumHeight(40)

        for ts_type in TaskStatus:
            self.task_status_filter.addItem(ts_type.value, ts_type)

        self.task_status_filter.currentIndexChanged.connect(self.on_task_status_changed)

        self.header.addWidget(self.header_label, 8)
        self.header.addStretch()
        self.header.addWidget(self.task_status_filter, 1)
        self.header.addWidget(self.header_refresh_button, 1)

        if self.page == MenuTitle.TODAY.value:
            self.task_status_filter.hide()
            self.task_create.hide()

        self.container = NavWidget(duration=220)

        self.td_task_list = QListWidget()
        self.td_task_list.setStyleSheet("""
            QListWidget::item {
                border-bottom: 1px solid #555555;
                padding: 5px;
            }

            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
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

        self.container.addWidget(self.td_task_list)
        self.container.addWidget(self.task_list)

        layout.addWidget(self.date_header)
        layout.addWidget(self.task_create)

        layout.addLayout(self.header)
        layout.addWidget(self.container)

        self.refresh_tasks()

    def set_page(self, page: str) -> None:
        if self.page == page:
            return

        self.page = page

        if self.page == MenuTitle.TODAY.value:
            self.date_header.show()
            self.task_create.hide()
            self.task_status_filter.hide()
            self.header_label.setText('Tasks for today:')
            self.container.slide_to_index(self.td_task_list, direction=Direction.HORIZONTAL)

        elif self.page == MenuTitle.ALL.value:
            self.date_header.hide()
            self.task_create.show()
            self.task_status_filter.show()
            self.header_label.setText('All tasks:')
            self.container.slide_to_index(self.task_list, direction=Direction.HORIZONTAL)

        self.refresh_tasks()

    def on_date_changed(self, new_date: date) -> None:
        self.selected_date = new_date

        is_today = 'today' if self.selected_date == date.today() else f'{self.selected_date.strftime("%d.%m.%Y")}'

        self.header_label.setText(f'Tasks for {is_today}:')
        self.refresh_tasks()

    def on_task_status_changed(self) -> None:
        active_status: TaskStatus = self.task_status_filter.currentData()

        if active_status == TaskStatus.ACTIVE:
            self.task_status = TaskStatus.ACTIVE
            self.header_label.setText('Active tasks:')

        elif active_status == TaskStatus.INACTIVE:
            self.task_status = TaskStatus.INACTIVE
            self.header_label.setText('Inactive tasks:')

        else:
            self.task_status = TaskStatus.ALL
            self.header_label.setText('All tasks:')

        self.refresh_tasks()

    def _on_click_create_task(self) -> None:
        target_date = max(self.selected_date, date.today())

        self.task_create.open_create_dialog(target_date)

    def _handle_task_list(
        self,
        tasks: List[TaskWithCompletionResponse] | List[TaskResponse],
        task_widget: Type[TaskActual | Task],
        **kwargs,
    ) -> None:
        for task in tasks:
            selected_list = self.td_task_list if self.page == MenuTitle.TODAY.value else self.task_list

            item = QListWidgetItem(selected_list)

            widget: TaskActual | Task = task_widget(task=task, **kwargs)

            if isinstance(widget, Task):
                widget.item = item

            item.setSizeHint(widget.sizeHint())

            selected_list.addItem(item)
            selected_list.setItemWidget(item, widget)

    def refresh_tasks(self) -> None:
        selected_list = self.td_task_list if self.page == MenuTitle.TODAY.value else self.task_list
        selected_list.clear()

        with self.session_factory() as db:
            service = TaskService(db)

            if self.page == MenuTitle.TODAY.value:
                tasks_actual: List[TaskWithCompletionResponse] = service.get_task_actual_list(self.selected_date)
                self._handle_task_list(
                    tasks=tasks_actual,
                    task_widget=TaskActual,
                    on_start_cb=self.start_task,
                    on_complete_cb=self.complete_task,
                )

            else:
                tasks: List[TaskResponse] = service.get_task_list(self.task_status)
                self._handle_task_list(
                    tasks=tasks,
                    task_widget=Task,
                    on_active_task=self.activate_task,
                    on_deactivate_task=self.deactivate_task,
                    on_delete_task=self.delete_task,
                )

    @db_errors
    def create_task(self, task_dto: TaskCreateSchema) -> None:
        with self.session_factory() as db:
            service = TaskService(db)
            new_task = service.create_task(task_dto)

        task_widget: Task = Task(
            task=new_task,
            on_active_task=self.activate_task,
            on_deactivate_task=self.deactivate_task,
            on_delete_task=self.delete_task,
        )

        item = QListWidgetItem(self.task_list)
        task_widget.item = item

        item.setSizeHint(task_widget.sizeHint())

        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, task_widget)

        QMessageBox.information(self, 'Success', 'Task created successfully!')

    @db_errors
    def activate_task(self, task_widget: Task, task_id: str) -> None:
        with self.session_factory() as db:
            service = TaskService(db)
            service.activate_task_status(task_id=task_id)

        task_widget.is_active = True

        if self.task_status == TaskStatus.INACTIVE:
            selected_list = self.task_list
            selected_list.takeItem(selected_list.row(task_widget.item))
        else:
            task_widget.activate_status()

    @db_errors
    def deactivate_task(self, task_widget: Task, task_id: str) -> None:
        with self.session_factory() as db:
            service = TaskService(db)
            service.deactivate_task_status(task_id=task_id)

        task_widget.is_active = False

        if self.task_status == TaskStatus.ACTIVE:
            selected_list = self.task_list
            selected_list.takeItem(selected_list.row(task_widget.item))
        else:
            task_widget.deactivate_status()

    @db_errors
    def delete_task(self, task_widget: Task, task_id: str) -> None:
        with self.session_factory() as db:
            service = TaskService(db)
            service.delete_task(task_id=task_id)

        selected_list = self.task_list
        selected_list.takeItem(selected_list.row(task_widget.item))
        QMessageBox.information(self, 'Success', 'Task deleted successfully!')

    @db_errors
    def start_task(self, task_widget: TaskActual, task_id: str) -> None:
        if self.selected_date > date.today():
            raise ValueError('A future task cannot be started today')
        if self.selected_date < date.today():
            raise ValueError('A task with a past due date cannot be started today')

        with self.session_factory() as db:
            service = TaskService(db)
            service.start_task(task_id=task_id, target_date=self.selected_date)

        task_widget.handle_start_status()

    @db_errors
    def complete_task(self, task_widget: TaskActual, task_id: str) -> None:
        if task_widget.tc_date is None:
            raise ValueError('A task has not been started yet')

        if task_widget.tc_date < date.today():
            raise ValueError('A task with a past due date cannot be completed today')

        with self.session_factory() as db:
            service = TaskService(db)
            service.complete_task(task_id=task_id, target_date=self.selected_date)

        task_widget.handle_end_status()
