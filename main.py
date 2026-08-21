import sys
from PyQt6.QtWidgets import QApplication
from Screenshot import Screenshot
from AI import AI
from Screen import Screen
import ctypes
import logging
from time import sleep

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
        sleep(0.1)
        gem.received_last_photo(file_path)

    gem = AI("gemini-3.5-flash", "ss", handle_ai_response)
    ss = Screenshot("ss", "f4", "test", on_screenshot_taken=on_screenshot_taken)

    ss.start(blocking=False)

    sys.exit(app.exec())