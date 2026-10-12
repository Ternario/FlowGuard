from datetime import date
from unittest.mock import MagicMock

from src.ui.widgets.task_actual import TaskActual
from src.ui.utils.time_formatter import format_or_fact_dt


class TestTaskActual:
    def test_task_actual_widget_is_visible(self, qtbot, base_task):
        task_instance = base_task
        task_instance.completion = None

        on_start, on_complete = MagicMock(), MagicMock()

        widget = TaskActual(task_instance, on_start, on_complete)
        qtbot.addWidget(widget)
        widget.show()

        assert widget.isVisible() == True
        assert widget.tc_date is None
        assert widget.is_started == False
        assert widget.is_completed == False
        assert widget.btn_start.isVisible() == True
        assert widget.btn_end.isVisible() == False
        assert widget.done_label.isVisible() == False
        assert widget.scheduled_start_dt == format_or_fact_dt(base_task.start_time)
        assert widget.scheduled_end_dt == format_or_fact_dt(base_task.end_time)
        assert widget.actual_start_dt == format_or_fact_dt(None)
        assert widget.actual_end_dt == format_or_fact_dt(None)

    def test_task_actual_start_btn_status(self, qtbot, base_task_with_completion):
        on_complete = MagicMock()

        def mock_start(task_widget, task_id):
            task_widget.handle_start_status()

        on_start = MagicMock(side_effect=mock_start)

        widget = TaskActual(base_task_with_completion, on_start, on_complete)
        qtbot.addWidget(widget)
        widget.show()

        widget.btn_start.click()
        on_start.assert_called_once()

        assert widget.is_started == True
        assert widget.tc_date == date.today()
        assert widget.btn_start.isVisible() == False
        assert widget.btn_end.isVisible() == True

    def test_task_actual_end_btn_status(self, qtbot, base_task_with_completion):
        on_start = MagicMock()

        def mock_complete(task_widget, task_id):
            task_widget.handle_end_status()

        on_complete = MagicMock(side_effect=mock_complete)

        widget = TaskActual(base_task_with_completion, on_start, on_complete)
        qtbot.addWidget(widget)
        widget.show()

        widget.btn_end.click()
        on_complete.assert_called_once()

        assert widget.is_completed == True
        assert widget.btn_start.isVisible() == False
        assert widget.btn_end.isVisible() == False
        assert widget.done_label.isVisible() == True
