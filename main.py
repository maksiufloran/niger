import sys
from PyQt6.QtWidgets import QApplication
from Screenshot import Screenshot
from AI import AI
from Screen import Screen

if __name__ == '__main__':
    app = QApplication(sys.argv)

    sc = Screen()
    sc.show()

    def handle_ai_response(response):
        sc.ai_signal.emit(response.text)


    gem = AI("ss", handle_ai_response)
    ss = Screenshot("ss", "f4", "test", on_screenshot_taken=gem.received_last_photo)

    ss.start(blocking=False)

    sys.exit(app.exec())