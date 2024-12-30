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
from .input import TextInputHandler
from .logger import setup_logging
from .starfield import StarField
from .text import TextEditor, TextLine

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


def setup_gamepads():
    log.info("Adding gamecontroller mappings")
    sdl2.SDL_GameControllerAddMappingsFromFile(b"gamecontrollerdb.txt")
    num_joysticks = sdl2.SDL_NumJoysticks()
    for i in range(num_joysticks):
        if sdl2.SDL_IsGameController(i) == sdl2.SDL_TRUE:
            log.info("Joystick {0} is controller".format(i))
            pad = sdl2.SDL_GameControllerOpen(i)
            log.info("Controller: {0}".format(sdl2.SDL_GameControllerName(pad)))




def main():
    setup_logging(verbose=True)
    sdl2.ext.init(joystick=True, controller=True)
    window = sdl2.ext.Window("XAYOS UI Prototype", size=(960, 540))
    window.show()

    setup_gamepads()

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
    text_editor = TextEditor(
        font_loader,
        text="Hello, World!",
        font_name="10x20",
        x=18,
        y=18,
        fg=colors.WHITE,
    )
    text_input = TextInputHandler()
    text_input.set_active_text_editor(text_editor)

    text_editor.set_text(
        "This is a test of the text canvas \n"
        "It should be able to render multiple lines\n"
        "This is a really long line that should wrap around to the next line if\n"
        " it gets too long\n"
        "Here be dragons\n"
        "\n"
        "def main():\n"
        "    print('Hello, World!')\n"
        "    return 0\n"
    )

    date_time = TextLine(
        font_loader,
        x=width - len("YYYY-mm-dd HH:MM:SS") * 9 - 10,
        y=height - 18 - 10,
        text=b"YYYY-mm-dd HH:MM:SS",
        font_name="9x18B",
        fg=colors.GREY,
    )

    # Wait until the user closes the window
    ticks = sdl2.SDL_GetTicks()
    elapsed = 0
    running = True
    while running:
        # Process events
        events = sdl2.ext.get_events()
        if sdl2.ext.quit_requested(events):
            break
        # Check for key presses
        for event in events:
            if event.type == sdl2.SDL_CONTROLLERAXISMOTION:
                text_input.on_controller_axis_motion(event.caxis.axis, event.caxis.value)
            elif event.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                text_input.on_controller_button_down(event.cbutton.button)
            elif event.type == sdl2.SDL_CONTROLLERBUTTONUP:
                text_input.on_controller_button_up(event.cbutton.button)
            elif event.type == sdl2.SDL_KEYDOWN:
                # Check if the user press alphanumeric keys
                if is_alpha_numeric(event.key.keysym.sym):
                    text_editor.set_text(text_editor.text + chr(event.key.keysym.sym))
                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                    text_editor.set_text(text_editor.text[:-1])
                elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                    text_editor.set_text(text_editor.text + "\n")
                elif event.key.keysym.sym == sdl2.SDLK_F11:
                    toggle_fullscreen(window)
                else:
                    text_input.on_key_down(event.key.keysym.sym)

        # Update the date and time
        date_time.set_text(time.strftime("%Y-%m-%d %H:%M:%S").encode())

        # Update the text editor
        text_input.update(elapsed)

        # Render the starfield
        context.clear(color=colors.BLACK)
        starfield.draw(context.sdlrenderer)

        text_editor.render_cursor(context.sdlrenderer)
        text_editor.render(context.sdlrenderer)

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
    # Hide the mouse cursor when in fullscreen mode
    sdl2.SDL_ShowCursor(0 if flags else 1)
    if result != 0:
        log.error("Failed to toggle fullscreen mode")
