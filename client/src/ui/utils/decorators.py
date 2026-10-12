from functools import wraps
from PyQt6.QtWidgets import QMessageBox


def db_errors(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    return wrapper
