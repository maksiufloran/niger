import sys
from PyQt6.QtWidgets import QApplication
from Screenshot import Screenshot
from AI import AI
from Screen import Screen
import ctypes
import logging

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)

if __name__ == '__main__':

    logging.info("--- START APLIKACJI ---")

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        logging.error("--- ctype ERROR ---")
        pass

    app = QApplication(sys.argv)

    sc = Screen()
    sc.show()

    def handle_ai_response(response):
        sc.ai_signal.emit(response.text)

    def on_screenshot_taken(file_path):
        sc.clear_signal.emit()
        gem.received_last_photo(file_path)

    def manual_clear():
        sc.clear_signal.emit()

    gem = AI("gemini-3.6-flash", "ss", handle_ai_response)
    ss = Screenshot("ss",
                    "shift",
                    "ctrl_l",
                    "test",
                    on_screenshot_taken=on_screenshot_taken,
                    on_clear_requested=manual_clear)

    ss.start(blocking=False)

    sys.exit(app.exec())