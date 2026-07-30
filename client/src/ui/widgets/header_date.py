from datetime import date, timedelta

from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QDateEdit


class HeaderDate(QWidget):
    date_changed = pyqtSignal(date)

    def __init__(self, initial_date=None, parent=None):
        super().__init__(parent)
        self.current_date = initial_date or date.today()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)

        self.label = QLabel()
        self.label.setStyleSheet('font-size: 18px; font-weight: bold;')

        btn_prev = QPushButton('←')
        btn_prev.setFixedWidth(35)
        btn_prev.clicked.connect(self._prev_day)

        btn_today = QPushButton('Today')
        btn_today.clicked.connect(self._today)

        btn_next = QPushButton('→')
        btn_next.setFixedWidth(35)
        btn_next.clicked.connect(self._next_day)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat('dd.MM.yyyy')
        self.date_picker.dateChanged.connect(self._on_picker_changed)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(btn_prev)
        layout.addWidget(btn_today)
        layout.addWidget(btn_next)
        layout.addWidget(self.date_picker)

        self._update_ui()

    def _update_ui(self):
        day_str = self.current_date.strftime('%A, %d.%m.%Y')
        self.label.setText(day_str)
        self.date_picker.blockSignals(True)

        q_date = QDate(
            self.current_date.year,
            self.current_date.month,
            self.current_date.day,
        )

        self.date_picker.setDate(q_date)
        self.date_picker.blockSignals(False)

        self.date_changed.emit(self.current_date)

    def _prev_day(self):
        self.current_date -= timedelta(days=1)
        self._update_ui()

    def _today(self):
        self.current_date = date.today()
        self._update_ui()

    def _next_day(self):
        self.current_date += timedelta(days=1)
        self._update_ui()

    def _on_picker_changed(self, qdate: QDate):
        self.current_date = qdate.toPyDate()
        self._update_ui()
