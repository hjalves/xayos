import array
import logging
import sys
import ctypes
import time
from random import randint

import sdl2
from sdl2 import sdlgfx
import sdl2.ext

from . import colors
from .fonts import FontLoader
from .logger import setup_logging
from .starfield import StarField
from .text import TextCanvas

log = logging.getLogger(__name__)

FPS_TARGET = 60


def is_alpha_numeric(key):
    return (
        sdl2.SDLK_a <= key <= sdl2.SDLK_z
        or sdl2.SDLK_0 <= key <= sdl2.SDLK_9
        or key == sdl2.SDLK_SPACE
        or key == sdl2.SDLK_UNDERSCORE
        or key == sdl2.SDLK_MINUS
    )


def main():
    setup_logging(verbose=True)
    sdl2.ext.init(joystick=True, controller=True)
    window = sdl2.ext.Window("XAYOS UI Prototype", size=(960, 540))
    window.show()

    flags = sdl2.SDL_RENDERER_PRESENTVSYNC
    context = sdl2.ext.Renderer(window, flags=flags)
    sdl2.SDL_RenderSetLogicalSize(context.sdlrenderer, 960, 540)

    # Retrieve and display renderer + available renderer info
    info = sdl2.render.SDL_RendererInfo()
    sdl2.SDL_GetRendererInfo(context.sdlrenderer, info)
    log.info("Using renderer: {0}".format(info.name.decode()))

    width, height = context.logical_size
    log.info(f"Logical size: {width}x{height}")
    starfield = StarField(width, height)

    font_loader = FontLoader()
    text_canvas = TextCanvas(
        font_loader,
        text="Hello, World!",
        font_name="10x20",
        x=40,
        y=40,
        fg=colors.WHITE,
    )

    text_canvas.set_text(
        "This is a test of the text canvas \n"
        "It should be able to render multiple lines\n"
        "This is a really long line that should wrap around to the next line if it gets too long\n"
        "Here be dragons\n"
        "\n"
        "def main():\n"
        "    print('Hello, World!')\n"
        "    return 0\n"
    )

    date_time_placeholder = "YYYY-mm-dd HH:MM:SS"
    date_time = TextCanvas(
        font_loader,
        x=width - len(date_time_placeholder) * 9 - 10,
        y=height - 18 - 10,
        text="YYYY-mm-dd HH:MM:SS",
        font_name="9x18B",
        fg=colors.GREY,
    )

    # Wait until the user closes the window
    ticks = sdl2.SDL_GetTicks()
    running = True
    while running:
        # Process events
        events = sdl2.ext.get_events()
        if sdl2.ext.quit_requested(events):
            break
        # Check for key presses
        for event in events:
            if event.type == sdl2.SDL_KEYDOWN:
                # Check if the user press alpha-numeric keys
                if is_alpha_numeric(event.key.keysym.sym):
                    text_canvas.text += chr(event.key.keysym.sym)
                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                    text_canvas.text = text_canvas.text[:-1]
                elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                    text_canvas.text += "\n"
                elif event.key.keysym.sym == sdl2.SDLK_F11:
                    toggle_fullscreen(window)

        # Update the date and time
        date_time.set_text(time.strftime("%Y-%m-%d %H:%M:%S"))

        # Render the starfield
        context.clear(color=colors.BLACK)
        starfield.draw(context.sdlrenderer)

        lines = text_canvas.text.split("\n")
        last_pos = len(lines[-1])

        text_canvas.render_cursor(context.sdlrenderer, last_pos, len(lines) - 1)
        text_canvas.render(context.sdlrenderer)

        date_time.render(context.sdlrenderer)
        context.present()

        # Cap the frame rate
        last_ticks, ticks = ticks, sdl2.SDL_GetTicks()
        elapsed = ticks - last_ticks
        # wait_time = (1000 // FPS_TARGET) - elapsed
        # if wait_time > 0:
        #     sdl2.SDL_Delay(wait_time)


def toggle_fullscreen(window):
    flags = sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
    if sdl2.SDL_GetWindowFlags(window.window) & sdl2.SDL_WINDOW_FULLSCREEN:
        flags = 0
    result = sdl2.SDL_SetWindowFullscreen(window.window, flags)
    if result != 0:
        log.error("Failed to toggle fullscreen mode")
