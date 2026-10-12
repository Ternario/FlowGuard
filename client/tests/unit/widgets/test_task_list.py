from unittest.mock import MagicMock, patch

import pytest
from datetime import date, timedelta

from src.ui.widgets.task_list import TaskList
from src.utils.enum_choices.menu_title import MenuTitle


class TestTaskList:
    @pytest.fixture
    def mock_session_factory(self):
        return MagicMock()

    def test_task_list_initialization_today_page(self, qtbot, mock_session_factory):
        with patch('src.ui.widgets.task_list.TaskService') as mock_task_service:
            widget = TaskList(session_factory=mock_session_factory)
            qtbot.addWidget(widget)
            mock_service = mock_task_service.return_value
            mock_service.get_task_actual_list.return_value = []

            mock_service.get_task_actual_list.assert_called_once_with(date.today())
            assert widget.td_task_list.count() == 0
            assert widget.header_label.text() == 'Tasks for today:'
            assert widget.page == MenuTitle.TODAY.value

    def test_task_list_navigate(self, qtbot, mock_session_factory):
        with patch('src.ui.widgets.task_list.TaskService') as mock_task_service:
            widget = TaskList(session_factory=mock_session_factory)
            qtbot.addWidget(widget)
            mock_service = mock_task_service.return_value
            mock_service.get_task_list.return_value = []

            widget.set_page(MenuTitle.ALL.value)

            mock_service.get_task_list.assert_called_once()

            assert widget.header_label.text() == 'All tasks:'
            assert widget.page == MenuTitle.ALL.value

    def test_task_list_date_handler(self, qtbot, mock_session_factory):
        with patch('src.ui.widgets.task_list.TaskService') as mock_task_service:
            widget = TaskList(session_factory=mock_session_factory)
            qtbot.addWidget(widget)
            mock_service = mock_task_service.return_value
            mock_service.get_task_actual_list.return_value = []

            future_date = date.today() + timedelta(days=1)
            widget.on_date_changed(future_date)

            mock_service.get_task_actual_list.assert_called_with(future_date)

            assert widget.header_label.text() == f'Tasks for {future_date.strftime("%d.%m.%Y")}:'
            assert widget.selected_date == future_date

    def test_task_list_create_task(self, qtbot, base_task, mock_session_factory):
        with (
            patch('src.ui.widgets.task_list.TaskService') as mock_task_service,
            patch('src.ui.widgets.task_list.QMessageBox') as mock_msg_service,
        ):
            widget = TaskList(session_factory=mock_session_factory)
            qtbot.addWidget(widget)
            mock_service = mock_task_service.return_value

            task = base_task
            task.recurrence_end_date = None
            mock_service.create_task.return_value = task

            fake_dto = MagicMock()
            fake_dto.model_dump.return_value = {
                'title': task.title,
                'description': task.description,
                'to_date': task.to_date,
            }

            widget.create_task(fake_dto)

            mock_service.create_task.assert_called_once_with(fake_dto)
            mock_msg_service.information.assert_called_once_with(widget, 'Success', 'Task created successfully!')

    def test_task_list_activate_task(self, qtbot, mock_session_factory):
        with patch('src.ui.widgets.task_list.TaskService') as mock_task_service:
            widget = TaskList(session_factory=mock_session_factory)
            widget.task_list.row = MagicMock(return_value=0)
            qtbot.addWidget(widget)

            mock_service = mock_task_service.return_value

            fake_task = MagicMock()
            fake_task.item = MagicMock()

            fake_task.is_active = False

            widget.activate_task(fake_task, 'task-id')
            mock_service.activate_task_status.assert_called_once_with(task_id='task-id')

            assert fake_task.is_active == True

    def test_task_list_deactivate_task(self, qtbot, mock_session_factory):
        with patch('src.ui.widgets.task_list.TaskService') as mock_task_service:
            widget = TaskList(session_factory=mock_session_factory)
            widget.task_list.row = MagicMock(return_value=0)
            qtbot.addWidget(widget)

            mock_service = mock_task_service.return_value

            fake_task = MagicMock()
            fake_task.item = MagicMock()

            fake_task.is_active = True

            widget.deactivate_task(fake_task, 'task-id')
            mock_service.deactivate_task_status.assert_called_once_with(task_id='task-id')

            assert fake_task.is_active == False

    def test_task_list_delete_task(self, qtbot, mock_session_factory):
        with (
            patch('src.ui.widgets.task_list.TaskService') as mock_task_service,
            patch('src.ui.widgets.task_list.QMessageBox') as mock_msg_service,
        ):
            widget = TaskList(session_factory=mock_session_factory)
            widget.task_list.row = MagicMock(return_value=0)
            qtbot.addWidget(widget)

            mock_service = mock_task_service.return_value

            fake_task = MagicMock()

            widget.delete_task(fake_task, 'task-id')
            mock_service.delete_task.assert_called_once_with(task_id='task-id')
            mock_msg_service.information.assert_called_once_with(widget, 'Success', 'Task deleted successfully!')

    def test_task_start_rules(self, qtbot, mock_session_factory):
        with (
            patch('src.ui.widgets.task_list.TaskService'),
            patch('src.ui.utils.decorators.QMessageBox') as mock_msg_service,
        ):
            widget = TaskList(session_factory=mock_session_factory)
            qtbot.addWidget(widget)

            fake_task = MagicMock()

            widget.selected_date = date.today() + timedelta(days=1)
            widget.start_task(fake_task, 'task-id')

            mock_msg_service.critical.assert_called_with(widget, 'Error', 'A future task cannot be started today')

            widget.selected_date = date.today() - timedelta(days=1)
            widget.start_task(fake_task, 'task-id')

            mock_msg_service.critical.assert_called_with(
                widget, 'Error', 'A task with a past due date cannot be started today'
            )

    def test_task_complete_rules(self, qtbot, mock_session_factory):
        with (
            patch('src.ui.widgets.task_list.TaskService'),
            patch('src.ui.utils.decorators.QMessageBox') as mock_msg_service,
        ):
            widget = TaskList(session_factory=mock_session_factory)
            qtbot.addWidget(widget)

            fake_task = MagicMock()

            fake_task.tc_date = None
            widget.complete_task(fake_task, 'task-id')
            mock_msg_service.critical.assert_called_with(widget, 'Error', 'A task has not been started yet')

            fake_task.tc_date = date.today() - timedelta(days=1)
            widget.complete_task(fake_task, 'task-id')
            mock_msg_service.critical.assert_called_with(
                widget, 'Error', 'A task with a past due date cannot be completed today'
            )
