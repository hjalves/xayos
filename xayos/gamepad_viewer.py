from pathlib import Path
import logging

import sdl2
import sdl2.ext
from sdl2.ext import Renderer

from . import colors
from .gamepad import (
    BUTTON_A,
    BUTTON_B,
    BUTTON_X,
    BUTTON_Y,
    BUTTON_DPAD_RIGHT,
    BUTTON_DPAD_DOWN,
    BUTTON_DPAD_LEFT,
    BUTTON_DPAD_UP,
    BUTTON_START,
    BUTTON_BACK,
    BUTTON_GUIDE,
    BUTTON_LEFTSTICK,
    BUTTON_RIGHTSTICK,
    BUTTON_LEFTSHOULDER,
    BUTTON_RIGHTSHOULDER,
    BUTTON_TRIGGERLEFT,
    BUTTON_TRIGGERRIGHT,
)

HERE = Path(__file__).parent
RESOURCES_PATH = HERE / "resources"

log = logging.getLogger(__name__)


class GamepadViewer:
    def __init__(self, gamepad_state, scale=2):
        self.gamepad_state = gamepad_state
        self.scale = scale
        # Load png image
        self.img_surface = sdl2.ext.load_img(str(RESOURCES_PATH / "ds4.png"))
        self.img_texture = None
        # Create a surface 45x30
        self.drawing_surface = sdl2.SDL_CreateRGBSurface(
            0, 45, 30, 32, 0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF
        )
        self.a_pos = [(34, 12)]
        self.b_pos = [(36, 10)]
        self.x_pos = [(32, 10)]
        self.y_pos = [(34, 8)]
        self.dpad_r_pos = [(12, 10)]
        self.dpad_d_pos = [(10, 12)]
        self.dpad_l_pos = [(8, 10)]
        self.dpad_u_pos = [(10, 8)]
        self.dpad_u_pos = [(10, 8)]
        self.start_pos = [
            (30, 6),
            (30, 7),
        ]
        self.back_pos = [
            (14, 6),
            (14, 7),
        ]
        self.guide_pos = [(22, 15)]
        self.left_stick_pos = [(16, 15)]
        self.right_stick_pos = [(28, 15)]
        self.left_shoulder_pos = [(9, 3), (10, 3)]
        self.right_shoulder_pos = [(34, 3), (35, 3)]
        self.left_trigger_pos = [
            # (11, 3),
            (12, 3),
            (13, 3)
        ]
        self.right_trigger_pos = [
            (31, 3),
            (32, 3),
            # (33, 3)
        ]

    def create_texture(self, renderer):
        self.img_texture = sdl2.ext.Texture(renderer, self.img_surface)

    def draw_button_states(self, surface_renderer):
        buttons_pressed = self.gamepad_state.buttons_pressed()
        if BUTTON_A in buttons_pressed:
            surface_renderer.draw_point(self.a_pos, colors.DODGER_BLUE)
        if BUTTON_B in buttons_pressed:
            surface_renderer.draw_point(self.b_pos, colors.RED)
        if BUTTON_X in buttons_pressed:
            surface_renderer.draw_point(self.x_pos, colors.PURPLE_3)
        if BUTTON_Y in buttons_pressed:
            surface_renderer.draw_point(self.y_pos, colors.GREEN)
        if BUTTON_DPAD_RIGHT in buttons_pressed:
            surface_renderer.draw_point(self.dpad_r_pos, colors.YELLOW)
        if BUTTON_DPAD_DOWN in buttons_pressed:
            surface_renderer.draw_point(self.dpad_d_pos, colors.YELLOW)
        if BUTTON_DPAD_LEFT in buttons_pressed:
            surface_renderer.draw_point(self.dpad_l_pos, colors.YELLOW)
        if BUTTON_DPAD_UP in buttons_pressed:
            surface_renderer.draw_point(self.dpad_u_pos, colors.YELLOW)

        if BUTTON_START in buttons_pressed:
            surface_renderer.draw_point(self.start_pos, colors.LIGHT_GREY_2)
        if BUTTON_BACK in buttons_pressed:
            surface_renderer.draw_point(self.back_pos, colors.LIGHT_GREY_2)
        if BUTTON_GUIDE in buttons_pressed:
            surface_renderer.draw_point(self.guide_pos, colors.LIGHT_GREY_2)

        if BUTTON_LEFTSTICK in buttons_pressed:
            surface_renderer.draw_point(self.left_stick_pos, colors.LIGHT_GREY_2)
        if BUTTON_RIGHTSTICK in buttons_pressed:
            surface_renderer.draw_point(self.right_stick_pos, colors.LIGHT_GREY_2)
        if BUTTON_LEFTSHOULDER in buttons_pressed:
            surface_renderer.draw_point(self.left_shoulder_pos, colors.LIGHT_GREY_2)
        if BUTTON_RIGHTSHOULDER in buttons_pressed:
            surface_renderer.draw_point(self.right_shoulder_pos, colors.LIGHT_GREY_2)

        if BUTTON_TRIGGERLEFT in buttons_pressed:
            surface_renderer.draw_point(self.left_trigger_pos, colors.ORANGE)
        if BUTTON_TRIGGERRIGHT in buttons_pressed:
            surface_renderer.draw_point(self.right_trigger_pos, colors.ORANGE)

    def render(self, renderer):
        surface_renderer = Renderer(self.drawing_surface)
        surface_renderer.clear(colors.TRANSPARENT)
        sdl2.SDL_BlitSurface(self.img_surface, None, self.drawing_surface, None)

        self.draw_button_states(surface_renderer)
        screen_width, screen_height = renderer.logical_size

        # Create a texture
        texture = sdl2.ext.Texture(renderer, self.drawing_surface)

        # Render the image
        rect = sdl2.SDL_Rect()
        rect.w, rect.h = texture.size
        rect.w *= self.scale
        rect.h *= self.scale
        rect.x = screen_width - rect.w - 10
        rect.y = screen_height - rect.h - 30

        sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture.tx, None, rect)
