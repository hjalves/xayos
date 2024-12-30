from pathlib import Path
import logging

import sdl2
import sdl2.ext
from sdl2.ext import Renderer

from . import colors

HERE = Path(__file__).parent
RESOURCES_PATH = HERE / "resources"

log = logging.getLogger(__name__)


class GamepadViewer:
    def __init__(self):
        # Load png image
        self.img_surface = sdl2.ext.load_img(str(RESOURCES_PATH / "ds4.png"))
        self.img_texture = None
        # Create a surface 45x30
        self.drawing_surface = sdl2.SDL_CreateRGBSurface(0, 45, 30, 32, 0, 0, 0, 0)
        self.a_position = (34, 12)
        self.b_position = (36, 10)
        self.x_position = (32, 10)
        self.y_position = (34, 8)
        self.dpad_r_position = (12, 10)
        self.dpad_d_position = (10, 12)
        self.dpad_l_position = (8, 10)
        self.dpad_u_position = (10, 8)

    def create_texture(self, renderer):
        self.img_texture = sdl2.ext.Texture(renderer, self.img_surface)

    def draw_pixel(self):
        dpad_color = colors.LIGHT_GREY_2
        Renderer(self.img_surface).draw_point(self.a_position, colors.DODGER_BLUE)
        Renderer(self.img_surface).draw_point(self.b_position, colors.RED)
        Renderer(self.img_surface).draw_point(self.x_position, colors.MAGENTA)
        Renderer(self.img_surface).draw_point(self.y_position, colors.GREEN)
        Renderer(self.img_surface).draw_point(self.dpad_r_position, dpad_color)
        Renderer(self.img_surface).draw_point(self.dpad_d_position, dpad_color)
        Renderer(self.img_surface).draw_point(self.dpad_l_position, dpad_color)
        Renderer(self.img_surface).draw_point(self.dpad_u_position, dpad_color)

    def render(self, renderer):
        sdl2.SDL_BlitSurface(self.img_surface, None, self.drawing_surface, None)

        self.draw_pixel()
        screen_width, screen_height = renderer.logical_size

        # Create a texture
        texture = sdl2.ext.Texture(renderer, self.drawing_surface)

        # Render the image
        rect = sdl2.SDL_Rect()
        rect.w, rect.h = texture.size
        rect.w *= 2
        rect.h *= 2
        rect.x = screen_width - rect.w - 10
        rect.y = screen_height - rect.h - 30

        sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture.tx, None, rect)
