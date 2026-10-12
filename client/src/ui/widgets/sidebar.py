from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from src.utils.enum_choices.menu_title import MenuTitle


class Sidebar(QWidget):
    page = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel('Menu')
        title.setStyleSheet('font-size: 20px; font-weight: bold;')
        layout.addWidget(title)

        self.btn_td_tasks = QPushButton("Today's tasks")
        self.btn_tasks = QPushButton('Tasks')
        self.btn_analytics = QPushButton('Analytics (Soon)')
        self.btn_settings = QPushButton('Settings (Soon)')

        self.btn_td_tasks.clicked.connect(lambda: self.page.emit(MenuTitle.TODAY.value))
        self.btn_tasks.clicked.connect(lambda: self.page.emit(MenuTitle.ALL.value))
        self.btn_analytics.clicked.connect(lambda: self.page.emit(MenuTitle.ANALYTICS.value))
        self.btn_settings.clicked.connect(lambda: self.page.emit(MenuTitle.SETTINGS.value))

        layout.addWidget(self.btn_td_tasks)
        layout.addWidget(self.btn_tasks)
        layout.addWidget(self.btn_analytics)

        layout.addStretch()

        layout.addWidget(self.btn_settings)
