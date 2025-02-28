import logging

import ignition
import sdl2.ext
from sdl2 import sdlgfx

from . import colors
from .gamepad import BUTTON_START, BUTTON_DPAD_DOWN, BUTTON_DPAD_UP
from .gemtext import GemtextParser
from .input import MenuController
from .menu import Menu
from .utils import wrap_text

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
        else:
            if button == BUTTON_DPAD_DOWN and state:
                self.text_viewer.scroll_down()
            elif button == BUTTON_DPAD_UP and state:
                self.text_viewer.scroll_up()

    def open_location(self):
        log.info("Open Location...")
        with open("faq.gmi") as f:
            data = f.read()
        # Fetch capsule content
        # response = ignition.request("//geminiprotocol.net/docs/faq.gmi")
        # Get status from remote capsule
        # print(response.status)
        # Get response information from remote capsule
        # data = response.data()
        gemtext_tokens = GemtextParser().parse(data)

        text = ""
        for token in gemtext_tokens:
            if token.type == "pre":
                text += token.text
            elif token.type == "link":
                text += f"=> {token.text}\t{token.meta}\n"
            elif token.type == "head1":
                text += f"# {token.text}\n"
            elif token.type == "head2":
                text += f"## {token.text}\n"
            elif token.type == "head3":
                text += f"### {token.text}\n"
            elif token.type == "list":
                text += f"* {token.text}\n"
            elif token.type == "quote":
                text += f"> {token.text}\n"
            else:
                assert token.type == "text"
                text += token.text + "\n"

        self.text_viewer.set_text(text)


class TextViewer:
    def __init__(
        self,
        font_loader,
        width=940,
        height=500,
        font_name="10x20",
        text="",
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
        self.line_offset = 0
        self.lines = []
        self.width_chars = 0
        self.height_chars = 0
        self.update_lines()

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.line_offset = 0
        self.update_lines()

    def scroll_up(self):
        self.line_offset -= 1
        if self.line_offset < 0:
            self.line_offset = 0
        log.debug(f"Scrolling up to {self.line_offset}")

    def scroll_down(self):
        self.line_offset += 1
        max_offset = max(len(self.lines) - self.height_chars, 0)
        if self.line_offset > max_offset:
            self.line_offset = max_offset
        log.debug(f"Scrolling down to {self.line_offset}")

    def update_lines(self):
        # Calculate width and height in characters
        font_size = self.font_loader.get_font_size(self.font)
        self.width_chars = self.width // font_size[0]
        self.height_chars = self.height // font_size[1]
        self.lines = self.split_text_into_lines(self.text, self.width_chars)

    def draw_to_surface(self):
        self.renderer.clear(colors.TRANSPARENT)

        self.font_loader.set_font(self.font)
        font_size = self.font_loader.get_font_size(self.font)

        lines = self.get_screen_lines()
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

    def get_screen_lines(self):
        return self.lines[self.line_offset : self.line_offset + self.height_chars]

    def split_text_into_lines(self, text, width_chars):
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
