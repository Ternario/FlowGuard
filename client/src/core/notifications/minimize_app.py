from pathlib import Path

from notifypy import Notify

base_dir = Path(__file__).resolve().parent.parent.parent.parent

icon_path = base_dir / 'main_icon.png'


def show_minimize_notification(title: str, message: str):
    try:
        notification = Notify()
        notification.application_name = 'FlouGuard'
        notification.title = title
        notification.message = message
        notification.icon = icon_path
        notification.send(block=False)

    except Exception as e:
        print(f'Notification error: {e}')
