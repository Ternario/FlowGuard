from datetime import date, time, timedelta
from unittest.mock import MagicMock

import pytest

from src.ui.widgets.task import Task
from src.utils.enum_choices.recurrence_type import RecurrenceType


class TestTask:
    @pytest.fixture
    def task(self, base_task):
        task = base_task
        task.start_date = time(hour=10, minute=0)
        task.end_date = time(hour=11, minute=0)
        task.recurrence_type = RecurrenceType.DAILY.value
        task.recurrence_interval = 3
        task.recurrence_end_date = date.today() + timedelta(days=30)
        task.is_active = True
        return task

    def test_task_widget_is_visible(self, qtbot, task):
        on_activate, on_deactivate, on_delete = MagicMock(), MagicMock(), MagicMock()

        widget = Task(task, on_activate, on_deactivate, on_delete)
        qtbot.addWidget(widget)
        widget.show()

        assert widget.isVisible() == True
        assert widget.task is not None
        assert widget.is_active == True
        assert widget.btn_activate.isVisible() == False
        assert widget.btn_deactivate.isVisible() == True
        assert widget.btn_delete.isVisible() == True

    def test_task_activate_btn_status(self, qtbot, task):
        on_deactivate, on_delete = MagicMock(), MagicMock()
        task_instance = task
        task_instance.is_active = False

        def mock_activate(task_widget, task_id):
            task_widget.activate_status()

        on_activate = MagicMock(side_effect=mock_activate)

        widget = Task(task_instance, on_activate, on_deactivate, on_delete)
        qtbot.addWidget(widget)
        widget.show()

        assert widget.is_active == False
        assert widget.btn_activate.isVisible() == True
        assert widget.btn_deactivate.isVisible() == False

        widget.btn_activate.click()
        on_activate.assert_called_once_with(widget, task.id)

        assert widget.is_active == True
        assert widget.btn_activate.isVisible() == False
        assert widget.btn_deactivate.isVisible() == True

    def test_task_deactivate_btn_status(self, qtbot, task):
        on_activate, on_delete = MagicMock(), MagicMock()

        def mock_deactivate(task_widget, task_id):
            task_widget.deactivate_status()

        on_deactivate = MagicMock(side_effect=mock_deactivate)

        widget = Task(task, on_activate, on_deactivate, on_delete)
        qtbot.addWidget(widget)
        widget.show()

        widget.btn_deactivate.click()
        on_deactivate.assert_called_once_with(widget, task.id)

        assert widget.is_active == False
        assert widget.btn_activate.isVisible() == True
        assert widget.btn_deactivate.isVisible() == False
