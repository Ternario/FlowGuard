import sys

from PyQt6.QtWidgets import QApplication

from src.db.connection import session, init_db
from src.ui.main_window import MainWindow


def main():
    init_db()

    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(session_factory=session)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
