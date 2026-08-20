from Screenshot import Screenshot
from AI import AI

gem = AI("ss", )

sc = Screenshot("ss", "f4", "test", on_screenshot_taken=gem.received_last_photo)
sc.start(blocking=True)
