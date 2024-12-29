import array
import logging
import sys
import ctypes
import time
from random import randint

import sdl2
from sdl2 import sdlgfx
import sdl2.ext

from .colors import BLACK
from .fonts import FontLoader
from .logger import setup_logging
from .starfield import StarField

log = logging.getLogger(__name__)

FPS_TARGET = 60


def main():
    setup_logging(verbose=True)
    sdl2.ext.init(joystick=True, controller=True)
    window = sdl2.ext.Window("XAYOS UI Prototype", size=(960, 540))
    window.show()

    context = sdl2.ext.Renderer(window, flags=sdl2.render.SDL_RENDERER_SOFTWARE)
    sdl2.SDL_RenderSetLogicalSize(context.sdlrenderer, 960, 540)

    # Retrieve and display renderer + available renderer info
    info = sdl2.render.SDL_RendererInfo()
    sdl2.SDL_GetRendererInfo(context.sdlrenderer, info)
    log.info("Using renderer: {0}".format(info.name.decode()))

    width, height = context.logical_size
    log.info(f"Logical size: {width}x{height}")
    starfield = StarField(width, height)

    font_loader = FontLoader()
    font_loader.load_all_fonts()

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
                if event.key.keysym.sym == sdl2.SDLK_F11:
                    toggle_fullscreen(window)

        # Render the starfield
        context.clear(color=BLACK)
        starfield.draw(context.sdlrenderer)
        for i, font in enumerate(font_loader.available_fonts()):
            font_loader.set_font(font)
            text = b"The quick brown fox jumps over the lazy dog "
            text += b"1234567890!@#$%^&*()_+-=[]{}|;':\",.<>/?\\"
            text += ": {0}".format(font).encode()
            write_text(context.sdlrenderer, 10, 10 + (i * 20), text)
        context.present()

        # Cap the frame rate
        last_ticks, ticks = ticks, sdl2.SDL_GetTicks()
        elapsed = ticks - last_ticks
        wait_time = (1000 // FPS_TARGET) - elapsed
        if wait_time > 0:
            sdl2.SDL_Delay(wait_time)


def toggle_fullscreen(window, mode="desktop"):
    flags = (
        sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
        if mode == "desktop"
        else sdl2.SDL_WINDOW_FULLSCREEN
    )
    if sdl2.SDL_GetWindowFlags(window.window) & sdl2.SDL_WINDOW_FULLSCREEN:
        flags = 0
    result = sdl2.SDL_SetWindowFullscreen(window.window, flags)
    if result != 0:
        log.error("Failed to toggle fullscreen mode")


def write_text(renderer, x, y, text: bytes):
    sdlgfx.stringColor(renderer, x, y, text, 0xFFFFFFFF)
