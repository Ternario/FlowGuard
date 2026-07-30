from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSystemTrayIcon,
    QMenu,
    QApplication,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QSplitter,
)

from src.ui.notifications.minimize_app import show_minimize_notification

from src.ui.widgets.sidebar import Sidebar
from src.ui.widgets.task_list import TaskList


class MainWindow(QMainWindow):
    def __init__(self, session_factory):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
        self.session_factory = session_factory
        self.hide_notification_showing = False
        self.is_exiting = False

        self.setWindowTitle('Flow Guard Desktop')
        self.resize(QApplication.primaryScreen().availableGeometry().size())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        splitter = QSplitter()

        sidebar = Sidebar()
        task_list = TaskList(session_factory=self.session_factory)

        splitter.addWidget(sidebar)
        splitter.addWidget(task_list)
        main_layout.addWidget(splitter)

        bottom_layout = QHBoxLayout()

        exit_button = QPushButton('Exit')
        exit_button.setFixedWidth(90)
        exit_button.setFixedHeight(30)
        exit_button.setStyleSheet(
            """
            QPushButton {
                background-color: red; color: white; font-weight: bold; padding: 4px 12px; border-radius: 4px;
            }
            QPushButton:hover {background-color: #1b5e20;}
            """
        )

        exit_button.clicked.connect(self.force_exit)

        bottom_layout.addStretch()
        bottom_layout.addWidget(exit_button)

        main_layout.addLayout(bottom_layout)

        self._setup_try()

    def _setup_try(self):
        self.tray_icon = QSystemTrayIcon(self)
        base_path = Path(__file__).resolve().parent.parent.parent
        icon_path = base_path / 'main_icon.png'
        self.tray_icon.setIcon(QIcon(str(icon_path)))

        tray_menu = QMenu()
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.show_normal)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.force_exit)

        tray_menu.addAction(open_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_click)
        self.tray_icon.show()

    def _on_tray_click(self, reason):
        if (
            reason == QSystemTrayIcon.ActivationReason.Trigger
            or reason == QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            self.show_normal()

    def show_normal(self):
        self.showNormal()
        self.activateWindow()

    def closeEvent(self, event):
        if self.is_exiting:
            event.accept()
            return

        if hasattr(self, 'tray_icon') and self.tray_icon:
            if not self.hide_notification_showing:
                self.hide_notification_showing = True
                timeout: int = 5000

                show_minimize_notification(
                    'FlouGuard', 'Flow Guard is still running in the background.'
                )

                QTimer.singleShot(
                    timeout, lambda: setattr(self, 'hide_notification_showing', False)
                )
            self.hide()

            event.ignore()
        else:
            event.accept()

    def force_exit(self):
        self.is_exiting = True
        # self.monitor_worker.stop()
        # self.sync_worker.stop()
        self.tray_icon.hide()
        QApplication.quit()
