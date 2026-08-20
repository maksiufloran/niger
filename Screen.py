import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QColor
import json

class Screen(QWidget):
    def __init__(self):
        super().__init__()
        self.dots = []
        self.init_ui()
        self.screen_width = 0
        self.screen_height = 0

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

    def response_analysis(self, response):
        try:
            data = json.loads(response)
            json_dots = data['dots']
            for dot in json_dots:
                self.dots.append((dot['x'], dot['y']))

        except json.JSONDecodeError as e:
            print("Json sie wyjebal")
        except KeyError as e:
            print("Lipa z kluczami")



    # def paintEvent(self, event):


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = Screen()
    screen.show()
    sys.exit(app.exec())
