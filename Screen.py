import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QBrush, QColor
import json
import logging

logger = logging.getLogger(__name__)


class Screen(QWidget):
    ai_signal = pyqtSignal(str)
    clear_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dots = []
        self.screen_width = 0
        self.screen_height = 0

        self.dots_color = QColor("#00FF00")
        self.dots_color.setAlphaF(120)

        self.ai_signal.connect(self.response_analysis)
        self.clear_signal.connect(self.clear_dots)
        self.init_ui()

        logger.info('init')

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
        logger.info('update_dots')

    def clear_dots(self):
        self.dots = []
        self.update()
        logger.info('clear_dots')

    def response_analysis(self, response_text):
        temp_dots = []
        try:
            data = json.loads(response_text)

            bg_hex = data.get('bgcolor', "#00FF00")
            self.dots_color = QColor(bg_hex)
            self.dots_color.setAlpha(120)


            answers = data.get('answers', [])

            for item in answers:
                box = item.get('box_2d')
                if box and len(box) == 4:
                    ymin, xmin, ymax, xmax = box

                    # 1. Przeliczenie skali 0-1000 na piksele monitora
                    real_xmin = (xmin / 1000.0) * self.screen_width
                    real_xmax = (xmax / 1000.0) * self.screen_width
                    real_ymin = (ymin / 1000.0) * self.screen_height
                    real_ymax = (ymax / 1000.0) * self.screen_height

                    center_x = int((real_xmin + real_xmax) / 2)
                    center_y = int((real_ymin + real_ymax) / 2)

                    temp_dots.append((center_x, center_y))

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Błąd parsowania: {e}")
            print(f"Błąd parsowania: {e}")
            temp_dots.append((self.screen_width - 10, self.screen_height - 10))

        self.update_dots(temp_dots)
        logger.info('response_analysis')

    def paintEvent(self, event):
        if not self.dots:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(self.dots_color))
        painter.setPen(Qt.PenStyle.NoPen)

        dot_radius = 5

        for x, y in self.dots:
            painter.drawEllipse(x - dot_radius, y - dot_radius, dot_radius * 2, dot_radius * 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = Screen()
    screen.show()
    sys.exit(app.exec())