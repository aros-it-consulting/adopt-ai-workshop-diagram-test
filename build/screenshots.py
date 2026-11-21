"""Draws an HTML page with the headless Chrome installed by mise and hands over its screenshot.

The screenshot has the size of the window, one pixel per CSS pixel: what a
screen capture gives. It is saved as a JPEG, the format a wiki, a chat tool
or a scanner turns a picture into.
"""

import io
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from tools import run_tool

BROWSER = "chrome-headless-shell"
SCREENSHOT_FLAGS = ["--headless", "--disable-gpu", "--hide-scrollbars"]
PAGE_NAME = "page.html"
PAGE_ENCODING = "utf-8"
SCREENSHOT_NAME = "page.png"
COLOR_MODE = "RGB"
JPEG = "JPEG"


def capture(page, width, height):
    """Returns the picture of an HTML page shown in a window of `width` by `height` CSS pixels."""
    with TemporaryDirectory() as folder:
        page_path = Path(folder) / PAGE_NAME
        screenshot_path = Path(folder) / SCREENSHOT_NAME
        page_path.write_text(page, encoding=PAGE_ENCODING)
        window_size = f"--window-size={width},{height}"
        run_tool(BROWSER, *SCREENSHOT_FLAGS, window_size, f"--screenshot={screenshot_path}", page_path.as_uri())
        screenshot = Image.open(screenshot_path)
        # Converting reads the whole file, which is gone once the folder is removed.
        return screenshot.convert(COLOR_MODE)


def as_jpeg(picture, quality):
    jpeg = io.BytesIO()
    picture.save(jpeg, JPEG, quality=quality)
    return jpeg
