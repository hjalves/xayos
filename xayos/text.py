from sdl2 import sdlgfx

from . import colors


class TextLine:
    def __init__(
        self,
        font_loader,
        x=0,
        y=0,
        font_name="10x20",
        text=b"<Placeholder text>",
        fg=colors.WHITE,
    ):
        self.font_loader = font_loader
        self.font = font_name
        self.text = text
        assert isinstance(text, bytes), "Text must be a bytes object"
        self.x = x
        self.y = y
        self.fg = fg
        self.font_loader.set_font(self.font)

    def set_text(self, text):
        assert isinstance(text, bytes), "Text must be a bytes object"
        self.text = text

    def render(self, sdlrenderer):
        self.font_loader.set_font(self.font)
        # font_size = self.font_loader.get_font_size(self.font)
        sdlgfx.stringRGBA(
            sdlrenderer,
            self.x,
            self.y,
            self.text,
            self.fg[0],
            self.fg[1],
            self.fg[2],
            self.fg[3],
        )


class TextEditor:
    def __init__(
        self,
        font_loader,
        x=0,
        y=0,
        font_name="10x20",
        text="<Insert text here>",
        fg=colors.WHITE,
        line_spacing=0,
    ):
        self.font_loader = font_loader
        self.font = font_name
        self.text = text
        self.x = x
        self.y = y
        self.fg = fg
        self.line_spacing = line_spacing
        self.font_loader.set_font(self.font)
        self.cursor_cx = 0
        self.cursor_cy = 0
        self.cursor_char = None
        self.cursor_color = colors.PINK
        self.cursor_char_color = colors.PINK
        self.update_cursor_position()

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.update_cursor_position()

    def put_char(self, char):
        # TODO: put under cursor
        self.text += char
        self.update_cursor_position()

    def backspace(self):
        # TODO: remove char before cursor
        self.text = self.text[:-1]
        self.update_cursor_position()

    def delete(self):
        # TODO: for now delete the line
        lines = self.text.split("\n")
        self.text = "\n".join(lines[:-1])
        self.update_cursor_position()

    def clear(self):
        self.text = ""
        self.update_cursor_position()

    def update_cursor_position(self):
        lines = self.text.split("\n")
        self.cursor_cx = len(lines[-1])
        self.cursor_cy = len(lines) - 1

    def set_cursor_char(self, char):
        assert char is None or isinstance(char, bytes) and len(char) == 1
        self.cursor_char = char

    def set_cursor_color(self, color):
        self.cursor_color = color

    def render_cursor(self, sdlrenderer):
        font_size = self.font_loader.get_font_size(self.font)
        cursor_x = self.x + self.cursor_cx * font_size[0]
        cursor_y = self.y + self.cursor_cy * font_size[1]
        sdlgfx.boxRGBA(
            sdlrenderer,
            cursor_x,
            cursor_y + font_size[1] - 2,
            cursor_x + font_size[0],
            cursor_y + font_size[1],
            *self.cursor_color,
        )
        if self.cursor_char:
            self.font_loader.set_font(self.font)
            sdlgfx.stringRGBA(
                sdlrenderer, cursor_x, cursor_y, self.cursor_char, *self.cursor_char_color
            )

    def render(self, sdlrenderer):
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
                sdlrenderer,
                self.x,
                y,
                line,
                self.fg[0],
                self.fg[1],
                self.fg[2],
                self.fg[3],
            )
