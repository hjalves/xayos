import logging
import sdl2.ext
from sdl2 import sdlgfx

from xayos import colors
from xayos.gamepad import BUTTON_DPAD_DOWN, BUTTON_DPAD_UP, BUTTON_A, BUTTON_B

log = logging.getLogger(__name__)


class Menu:
    def __init__(self, font_loader, width, height, active=False):
        self.gamepad = None
        self.font_loader = font_loader
        self.title_font = "9x18B"
        self.font = "10x20"
        self.background = colors.DARK_GREY_1[0:3] + (0xDD,)
        self.width = width
        self.height = height
        self.surface = sdl2.SDL_CreateRGBSurface(
            0, width, height, 32, 0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF
        )
        self.entries = [
            "New File",
            "Open...",
            "Save",
            "Save As...",
            "About",
            "Quit",
        ]
        self._current_selection = 0
        self.active = active
        self.selected = None

    def reset_selection(self):
        self._current_selection = 0
        self.selected = None

    def connect_gamepad(self, gamepad):
        self.gamepad = gamepad
        self.gamepad.set_callbacks(
            on_button_press=self.on_button_press,
            on_button_release=self.on_button_release,
        )

    def render(self, renderer):
        surface_renderer = sdl2.ext.Renderer(self.surface)
        surface_renderer.clear(self.background)
        # draw a line in the edges of the surface
        border = (0, 0, self.width, self.height)
        title_border = (0, 32, self.width, 32)
        footer_border = (0, self.height - 32, self.width, 32)
        surface_renderer.draw_rect(border, colors.LIGHT_GREY_3)
        surface_renderer.draw_line(title_border, colors.LIGHT_GREY_3)
        # surface_renderer.draw_line(footer_border, colors.LIGHT_GREY_2)

        self.font_loader.set_font(self.title_font)
        # font_size = self.font_loader.get_font_size(self.font)
        font_pos = (8, 8)
        menu_string = b"Starpad Main Menu"
        sdlgfx.stringRGBA(
            surface_renderer.sdlrenderer,
            font_pos[0],
            font_pos[1],
            menu_string,
            *colors.LIGHT_GREY_3,
        )
        self.draw_entries(surface_renderer.sdlrenderer)
        texture = sdl2.ext.Texture(renderer.sdlrenderer, self.surface)
        screen_center = (renderer.logical_size[0] // 2, renderer.logical_size[1] // 2)
        renderer.rcopy(texture, loc=screen_center, align=(0.5, 0.5))

    def draw_entries(self, sdlrenderer):
        y = 32 + 12
        spacing = 24
        for i, entry in enumerate(self.entries):
            self.font_loader.set_font(self.font)
            color = colors.LIGHT_GREY_3 if i == self._current_selection else colors.GREY
            sdlgfx.stringRGBA(
                sdlrenderer,
                16,
                y,
                entry.encode(),
                *color,
            )
            y += spacing

    def select_next(self):
        self._current_selection = (self._current_selection + 1) % len(self.entries)

    def select_previous(self):
        self._current_selection = (self._current_selection - 1) % len(self.entries)

    def move_up(self):
        self.select_previous()

    def move_down(self):
        self.select_next()

    def select(self):
        self.selected = self.entries[self._current_selection]
        self.active = False
        log.debug(f"Selected: {self.selected}")

    def cancel(self):
        self.active = False

    def on_button_release(self, button):
        pass
