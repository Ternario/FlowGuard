from datetime import date

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QDialog,
)

from src.ui.widgets.task_create_dialog import TaskCreateDialog


class TaskCreate(QWidget):
    task_created = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        self.btn_add = QPushButton('Create New Task')
        self.btn_add.setStyleSheet(
            """
            QPushButton { 
                background-color: #1976d2; 
                color: white; 
                font-size: 14px;
                font-weight: bold; 
                padding: 8px 16px; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #0d47a1; }
            """
        )

        layout.addWidget(self.btn_add)
        layout.addStretch()

    def open_create_dialog(self, target_date: date):
        dialog = TaskCreateDialog(initial_date=target_date, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.task_created.emit(dialog.created_task_data)
