import logging

import ignition
import sdl2.ext
from sdl2 import sdlgfx

from . import colors
from .gamepad import BUTTON_START
from .input import MenuController
from .menu import Menu

log = logging.getLogger(__name__)


class Voyager:
    MENU_ENTRIES = [
        "Open Location...",
        "Quit",
    ]
    MENU_HELP = {
        "Open Location...": "Open a capsule by providing its URL",
        "Quit": "Exit the program",
    }

    def __init__(self, font_loader, gamepad, width, height):
        self.running = True
        self.font_loader = font_loader
        self.gamepad = gamepad
        self.menu = Menu(
            self.font_loader,
            200,
            200,
            active=True,
            title="Voyager Menu",
            entries=self.MENU_ENTRIES,
        )
        self.menu_controller = MenuController(self.menu)
        self.text_viewer = TextViewer(
            self.font_loader,
            font_name="10x20",
            text="Gemini Voyager\n\nPress START to open the menu.",
        )

    def update(self, elapsed_ms):
        self.handle_menu()

    def render(self, renderer):
        self.text_viewer.render(renderer, 10, 10)
        if self.menu.active:
            self.menu.render(renderer)

    def handle_menu(self):
        if self.menu.chosen:
            log.info(f"Selected menu item: {self.menu.chosen}")
            if self.menu.chosen == "Open Location...":
                self.open_location()
            elif self.menu.chosen == "Quit":
                self.running = False
            else:
                log.warning(f"Unknown menu item: {self.menu.chosen}")
            self.menu.chosen = None

    def toggle_menu(self):
        self.menu.active = not self.menu.active

    def handle_input(self, button, state):
        if button == BUTTON_START and state:
            self.toggle_menu()
        if self.menu.active:
            self.menu_controller.handle_input(button, state)

    def open_location(self):
        log.info("Open Location...")
        # Fetch capsule content
        # response = ignition.request('//geminiprotocol.net/')
        # Get status from remote capsule
        # print(response.status)
        # Get response information from remote capsule
        # data = response.data()
        data = "# Project Gemini\n\n## Gemini in 100 words\n\nGemini is a new internet technology supporting an electronic library of interconnected text documents.  That's not a new idea, but it's not old fashioned either.  It's timeless, and deserves tools which treat it as a first class concept, not a vestigial corner case.  Gemini isn't about innovation or disruption, it's about providing some respite for those who feel the internet has been disrupted enough already.  We're not out to change the world or destroy other technologies.  We are out to build a lightweight online space where documents are just documents, in the interests of every reader's privacy, attention and bandwidth.\n\n=> docs/faq.gmi\tIf you'd like to know more, read our FAQ\n=> https://www.youtube.com/watch?v=DoEI6VzybDk\tOr, if you'd prefer, here's a video overview\n\n## Official resources\n\n=> news/\tProject Gemini news\n=> docs/\tProject Gemini documentation\n=> history/\tProject Gemini history\n=> software/\tKnown Gemini software\n\nAll content at geminiprotocol.net is CC BY-NC-ND 4.0 licensed unless stated otherwise:\n=> https://creativecommons.org/licenses/by-nc-nd/4.0/\tCC Attribution-NonCommercial-NoDerivs 4.0 International\n"
        self.text_viewer.set_text(data)


class TextViewer:
    def __init__(
        self,
        font_loader,
        width=940,
        height=520,
        font_name="10x20",
        text="<Insert text here>",
        fg=colors.LIGHT_GREY_2,
        line_spacing=0,
    ):
        self.surface = sdl2.SDL_CreateRGBSurface(
            0, width, height, 32, 0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF
        )
        self.renderer = sdl2.ext.Renderer(self.surface)
        self.font_loader = font_loader
        self.font = font_name
        self.text = text
        self.width = width
        self.height = height
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
        cursor_x = 0 + self.cursor_cx * font_size[0]
        cursor_y = 0 + self.cursor_cy * font_size[1]
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

    def draw_to_surface(self):
        # self.renderer.clear((0x30, 0x30, 0x40, 0x80))
        self.renderer.clear(colors.TRANSPARENT)

        self.font_loader.set_font(self.font)
        # Calculate width and height in characters
        font_size = self.font_loader.get_font_size(self.font)
        width_chars = self.width // font_size[0]
        height_chars = self.height // font_size[1]

        lines = self.split_text_into_lines(self.text, width_chars, height_chars)

        # Split text into lines
        for i, line in enumerate(lines):
            y = i * font_size[1] + i * self.line_spacing
            sdlgfx.stringRGBA(
                self.renderer.sdlrenderer,
                0,
                y,
                line,
                self.fg[0],
                self.fg[1],
                self.fg[2],
                self.fg[3],
            )

    def split_text_into_lines(self, text, width_chars, height_chars):
        lines = []

        for line in wrap_text(text, width_chars):
            line = line.encode()
            line = line.replace(b"\t", b" ")  # Replace tabs with 1 space for now
            if not line:
                lines.append(b"")
                continue
            while line:
                if len(line) <= width_chars:
                    lines.append(line)
                    break
                else:
                    lines.append(line[:width_chars])
                    line = line[width_chars:]

        return lines

    def render(self, renderer, x=0, y=0):
        self.draw_to_surface()
        texture = sdl2.ext.Texture(renderer, self.surface)
        dstrect = sdl2.SDL_Rect(x, y, *texture.size)
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture.tx, None, dstrect)


def tokenize(text):
    """Tokenize text into words."""
    # "Hello, World!" -> ["Hello,", " ", "World!"]
    # "Hello,  World!" -> ["Hello,", " ", " ", "World!"]
    tokens = []
    token = ""
    for char in text:
        if char.isspace():
            if token:
                tokens.append(token)
                token = ""
            tokens.append(char)
        else:
            token += char
    if token:
        tokens.append(token)
    return tokens


def wrap_text(text, width_chars):
    tokens = tokenize(text)
    wrapped = []
    current_line = ""
    for token in tokens:
        if token == "\n":
            wrapped.append(current_line)
            current_line = ""
        elif len(current_line) + len(token) <= width_chars:
            current_line += token
        else:
            wrapped.append(current_line)
            current_line = token
    wrapped.append(current_line)
    return wrapped
