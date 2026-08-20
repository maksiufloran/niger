import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QBrush, QColor
import json


class Screen(QWidget):
    ai_signal = pyqtSignal(str)
    clear_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dots = []
        self.screen_width = 0
        self.screen_height = 0

        self.ai_signal.connect(self.response_analysis)
        self.clear_signal.connect(self.clear_dots)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()
        self.screen_width = self.screen().size().width()
        self.screen_height = self.screen().size().height()

    def update_dots(self, new_dots: list):
        self.dots = new_dots
        self.update()

    def clear_dots(self):
        self.dots = []
        self.update()

    def response_analysis(self, response_text):
        temp_dots = []
        try:
            data = json.loads(response_text)
            json_dots = data.get('dots', [])
            for dot in json_dots:
                temp_dots.append((dot['x'], dot['y']))
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Błąd parsowania: {e}")
            temp_dots.append((self.screen_width - 10, self.screen_height - 10))

        self.update_dots(temp_dots)

    def paintEvent(self, event):
        if not self.dots:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.PenStyle.NoPen)
        dot_radius = 5

        for x, y in self.dots:
            painter.drawEllipse(x - dot_radius, y - dot_radius, dot_radius * 2, dot_radius * 2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = Screen()
    screen.show()
    sys.exit(app.exec())