import sdl2
import sdl2.ext
from sdl2 import sdlgfx

from . import colors


class TextCanvas:
    def __init__(
        self,
        font_loader,
        x=0,
        y=0,
        font_name="10x20",
        text="<Insert text here>",
        fg=colors.WHITE,
        line_spacing=0
    ):
        self.font_loader = font_loader
        self.font = font_name
        self.text = text
        self.x = x
        self.y = y
        self.fg = fg
        self.line_spacing = line_spacing
        self.font_loader.set_font(self.font)

    def set_text(self, text):
        self.text = text

    def render_cursor(self, renderer, cursor_x, cursor_y):
        font_size = self.font_loader.get_font_size(self.font)
        x = self.x + cursor_x * font_size[0]
        y = self.y + cursor_y * font_size[1]
        sdlgfx.boxRGBA(
            renderer,
            x,
            y + font_size[1] - 2,
            x + font_size[0],
            y + font_size[1],
            *colors.RED
        )

    def render(self, renderer):
        text = self.text
        if isinstance(text, str):
            text = text.encode("utf-8")

        self.font_loader.set_font(self.font)
        font_size = self.font_loader.get_font_size(self.font)

        # Split text into lines
        lines = text.split(b"\n")
        for i, line in enumerate(lines):
            y = self.y + i * font_size[1] + i * self.line_spacing
            sdlgfx.stringRGBA(
                renderer,
                self.x,
                y,
                line,
                self.fg[0],
                self.fg[1],
                self.fg[2],
                self.fg[3],
            )

