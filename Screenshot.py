from pathlib import Path
import mss
from pynput import keyboard
import logging

logger = logging.getLogger(__name__)

class Screenshot:
    def __init__(self, path, hot_key, clear_key, file_name_prefix, on_screenshot_taken=None, on_clear_requested=None):
        self.folder_name = path
        self.hot_key = hot_key
        self.clear_key = clear_key  # NOWOŚĆ: Klawisz do czyszczenia (np. F3)
        self.file_name_prefix = file_name_prefix
        self.last_screenshot = None
        self.on_screenshot_taken = on_screenshot_taken
        self.on_clear_requested = on_clear_requested  # NOWOŚĆ: Funkcja przekazywana z main.py
        self.listener = None
        logger.info('init')

    def take_screenshot(self):
        folder_path = Path(__file__).resolve().parent / self.folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        png_count = len(list(folder_path.glob("*.png")))
        prefix = f"{self.file_name_prefix}-" if self.file_name_prefix else ""
        output_path = folder_path / f"{prefix}monitor1-ss-{png_count + 1}.png"

        with mss.MSS() as sct:
            file = sct.shot(mon=1, output=str(output_path)) # temp only monitor 1
            self.last_screenshot = file
            logger.info('screenshot taken')

            if self.on_screenshot_taken:
                self.on_screenshot_taken(file)

    def on_press(self, key):
        try:
            key_name = key.name if hasattr(key, 'name') else key.char

            if key_name == self.hot_key:
                self.take_screenshot()
                logger.info('Screenshot hotkey pressed')

            elif key_name == self.clear_key:
                if self.on_clear_requested:
                    self.on_clear_requested()
                logger.info('Clear hotkey pressed')

        except Exception as e:
            logger.error(e)

    def start(self, blocking=True):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        if blocking:
            self.listener.join()  # Blokuje, żeby skrypt nie umarł

    def get_last_screenshot(self):
        return self.last_screenshot


if __name__ == "__main__":
    from AI import AI

    gem = AI("ss", "Gemini")

    sc = Screenshot("ss", "f4", "test", on_screenshot_taken=gem.received_last_photo)
    sc.start(blocking=True)

