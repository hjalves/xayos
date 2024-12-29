import logging
import re
from pathlib import Path

from sdl2 import sdlgfx

HERE = Path(__file__).parent
FONT_PATH = HERE / "fonts"

log = logging.getLogger(__name__)

class FontLoader:
    def __init__(self):
        # {font_name: (width, height, font_data)}
        self.font_data = {
            "8x8": (8, 8, None),
        }

    def available_fonts(self):
        return self.font_data.keys()

    def load_all_fonts(self):
        log.info(f"Loading all fonts from {FONT_PATH}")
        for font_file in FONT_PATH.glob("*.fnt"):
            self.load_font(font_file.stem)
        fonts = sorted(self.font_data.items(), key=lambda x: (x[1][0], x[1][1]))
        self.font_data = dict(fonts)

    def load_font(self, font_name, width=None, height=None):
        log.debug(f"Loading font {font_name}")
        if width is None and height is None:
            m = re.match(r"(\d+)x(\d+)", font_name)
            if m:
                width, height = map(int, m.groups())

        if width is None or height is None:
            raise ValueError("Width and height must be provided")

        with open(FONT_PATH / f"{font_name}.fnt", "rb") as f:
            font_data = f.read()

        self.font_data[font_name] = (width, height, font_data)

    def set_font(self, font_name=None):
        if font_name is None:
            sdlgfx.gfxPrimitivesSetFont(None, 0, 0)
            return
        if font_name not in self.font_data:
            self.load_font(font_name)
        width, height, font_data = self.font_data[font_name]
        sdlgfx.gfxPrimitivesSetFont(font_data, width, height)
