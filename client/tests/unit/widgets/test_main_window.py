from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtGui import QCloseEvent
from pytestqt.plugin import qtbot

from src.ui.main_window import MainWindow
from src.utils.enum_choices.menu_title import MenuTitle


class TestMainWindow:
    @pytest.fixture
    def mock_session_factory(self):
        return MagicMock()

    def test_main_window_setup(self, qtbot, mock_session_factory):
        window = MainWindow(mock_session_factory)
        qtbot.addWidget(window)

        assert window.windowTitle() == 'Flow Guard Desktop'
        assert window.centralWidget() is not None
        assert window.task_list.page == MenuTitle.TODAY.value

    def test_main_window_minimize_on_close(self, qtbot, mock_session_factory):
        window = MainWindow(mock_session_factory)
        qtbot.addWidget(window)
        window.tray_icon = MagicMock()

        window.hide_notification_showing = False
        window.show()

        assert window.isVisible() is True

        close_event = QCloseEvent()

        with patch('src.ui.main_window.show_minimize_notification') as mock_notif:
            window.closeEvent(close_event)

        assert window.isVisible() is False
        assert close_event.isAccepted() is False
        mock_notif.assert_called_once_with('FlouGuard', 'Flow Guard is still running in the background.')

    def test_main_window_exit(self, qtbot, mock_session_factory):
        window = MainWindow(mock_session_factory)
        qtbot.addWidget(window)
        window.tray_icon = MagicMock()

        with patch('src.ui.main_window.QApplication') as mock_exit:
            window.force_exit()

        assert window.is_exiting is True
        window.tray_icon.hide.assert_called_once()
        mock_exit.quit.assert_called_once()
