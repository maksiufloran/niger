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

    def on_screenshot_taken(file_path):
        sc.clear_signal.emit()
        gem.received_last_photo(file_path)

    gem = AI("gemini-3.1-flash-lite", "ss", handle_ai_response)
    ss = Screenshot("ss", "f4", "test", on_screenshot_taken=on_screenshot_taken)

    ss.start(blocking=False)

    sys.exit(app.exec())