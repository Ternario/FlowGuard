from PyQt6.QtCore import (
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QEasingCurve,
)
from PyQt6.QtWidgets import QStackedWidget, QWidget

from src.utils.enum_choices.direction import Direction


class NavWidget(QStackedWidget):
    def __init__(self, parent=None, duration: int = 220) -> None:
        super(NavWidget, self).__init__(parent)
        self.duration = duration
        self.animation = QParallelAnimationGroup(self)
        self.is_animating = False

    def slide_to_index(self, widget: QWidget, direction: Direction = Direction.VERTICAL) -> None:
        next_index: int = self.indexOf(widget)

        if next_index == -1:
            return

        current_index: int = self.currentIndex()

        if current_index == next_index or self.is_animating:
            return
        if next_index < 0 or next_index >= self.count():
            return

        self.is_animating = True
        current_widget: QWidget | None = self.widget(current_index)
        next_widget: QWidget | None = self.widget(next_index)

        if current_widget is None or next_widget is None:
            return

        width: int = self.width()
        height: int = self.height()

        if direction == Direction.VERTICAL:
            if next_index > current_index:
                offset_current = QPoint(0, -height)
                offset_next = QPoint(0, height)
            else:
                offset_current = QPoint(0, height)
                offset_next = QPoint(0, -height)
        else:
            if next_index > current_index:
                offset_current = QPoint(-width, 0)
                offset_next = QPoint(width, 0)
            else:
                offset_current = QPoint(width, 0)
                offset_next = QPoint(-width, 0)

        next_widget.setGeometry(0, 0, width, height)
        next_widget.move(offset_next)
        next_widget.show()
        next_widget.raise_()

        animation_current: QPropertyAnimation = QPropertyAnimation(current_widget, b'pos', self)
        animation_current.setDuration(self.duration)
        animation_current.setStartValue(QPoint(0, 0))
        animation_current.setEndValue(offset_current)
        animation_current.setEasingCurve(QEasingCurve.Type.OutCubic)

        animation_next: QPropertyAnimation = QPropertyAnimation(next_widget, b'pos', self)
        animation_next.setDuration(self.duration)
        animation_next.setStartValue(offset_next)
        animation_next.setEndValue(QPoint(0, 0))
        animation_next.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.animation.clear()
        self.animation.addAnimation(animation_current)
        self.animation.addAnimation(animation_next)

        def on_finished() -> None:
            try:
                self.animation.finished.disconnect(on_finished)
            except RuntimeError:
                pass

            self.setCurrentIndex(next_index)
            current_widget.hide()
            current_widget.move(0, 0)
            self.is_animating = False

        self.animation.finished.connect(on_finished)
        self.animation.start()
