from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel('Menu')
        title.setStyleSheet('font-size: 20px; font-weight: bold;')
        layout.addWidget(title)

        self.menu_list = QListWidget()
        self.menu_list.addItem("Today's Tasks")
        self.menu_list.addItem('Tasks')
        self.menu_list.addItem('Analytics (Soon)')
        self.menu_list.addItem('Settings (Soon)')
        self.menu_list.setCurrentRow(0)
        self.menu_list.setStyleSheet("""
            QListWidget::item {
                border-bottom: 1px solid #555555;
                padding: 10px;
            }

            QListWidget::item:selected {
                background-color: transparent;
            }
        """)

        layout.addWidget(self.menu_list)
