import sys
from PyQt6.QtWidgets import QApplication
from Screenshot import Screenshot
from AI import AI
from Screen import Screen
import ctypes

if __name__ == '__main__':
    # --- DODANE: Wymuszenie fizycznych pikseli (DPI Awareness) ---
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    app = QApplication(sys.argv)

    sc = Screen()
    sc.show()

    def handle_ai_response(response):
        sc.ai_signal.emit(response.text)

    def on_screenshot_taken(file_path):
        sc.clear_signal.emit()
        gem.received_last_photo(file_path)

    gem = AI("gemini-3.6-flash", "ss", handle_ai_response)
    ss = Screenshot("ss", "f4", "test", on_screenshot_taken=on_screenshot_taken)

    ss.start(blocking=False)

    sys.exit(app.exec())