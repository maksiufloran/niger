from pathlib import Path
import mss
from pynput import keyboard


class Screenshot:
    def __init__(self, path, hot_key, file_name_prefix, on_screenshot_taken=None):
        self.folder_name = path
        self.hot_key = hot_key
        self.file_name_prefix = file_name_prefix
        self.last_screenshot = None
        self.on_screenshot_taken = on_screenshot_taken # z klasie AI
        self.listener = None

    def take_screenshot(self):
        folder_path = Path(__file__).resolve().parent / self.folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        png_count = len(list(folder_path.glob("*.png")))
        prefix = f"{self.file_name_prefix}-" if self.file_name_prefix else ""
        output_path = folder_path / f"{prefix}monitor1-ss-{png_count + 1}.png"

        with mss.MSS() as sct:
            file = sct.shot(mon=1, output=str(output_path)) # temp only monitor 1
            self.last_screenshot = file

            if self.on_screenshot_taken:
                self.on_screenshot_taken(file)

    def on_press(self, key):
        try:
            if key.char == self.hot_key:
                self.take_screenshot()
        except AttributeError:
            if key.name == self.hot_key:
                self.take_screenshot()

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


