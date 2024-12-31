import array
import logging
import sys
import ctypes
import time
from pathlib import Path
from random import randint

import sdl2
from sdl2 import sdlgfx
import sdl2.ext

from . import colors
from .fonts import FontLoader
from .gamepad import GamepadHandler
from .gamepad_viewer import GamepadViewer
from .input import TextInputHandler
from .logger import setup_logging
from .menu import Menu
from .starfield import StarField
from .text import TextEditor, TextLine

log = logging.getLogger(__name__)

HERE = Path(__file__).parent
RESOURCES_PATH = HERE / "resources"


FPS_TARGET = 30


def main():
    setup_logging(verbose=True)
    sdl2.ext.init(joystick=True, controller=True)
    window = sdl2.ext.Window("Xayos Lunar Shell [POC]", size=(960, 540))
    window.show()

    setup_gamepads()

    # flags = sdl2.SDL_RENDERER_PRESENTVSYNC
    flags = sdl2.SDL_RENDERER_SOFTWARE
    context = sdl2.ext.Renderer(window, flags=flags)
    sdl2.SDL_RenderSetLogicalSize(context.sdlrenderer, 960, 540)

    # Retrieve and display renderer + available renderer info
    info = sdl2.render.SDL_RendererInfo()
    sdl2.SDL_GetRendererInfo(context.sdlrenderer, info)
    log.info("Using renderer: {0}".format(info.name.decode()))

    width, height = context.logical_size
    log.info(f"Logical size: {width}x{height}")
    starfield = StarField(width, height)

    gamepad = GamepadHandler()
    gamepad_viewer = GamepadViewer(gamepad)
    gamepad_viewer.create_texture(context)

    font_loader = FontLoader()
    text_editor = TextEditor(
        font_loader,
        text="Hello, Galaxy!\n",
        font_name="10x20",
        x=18,
        y=18,
        fg=colors.WHITE,
    )
    text_input = TextInputHandler()
    text_input.set_active_text_editor(text_editor)
    text_input.connect_gamepad(gamepad)
    # text_input.disconnect_gamepad()

    menu = Menu(font_loader, 200, 200)
    # menu.connect_gamepad(gamepad)
    menu.active = False

    date_time = TextLine(
        font_loader,
        x=width - len("YYYY-mm-dd HH:MM:SS") * 9 - 10,
        y=height - 18 - 10,
        text=b"YYYY-mm-dd HH:MM:SS",
        font_name="9x18B",
        fg=colors.GREY,
    )
    fps_counter = TextLine(
        font_loader,
        x=10,
        y=height - 18 - 10,
        text=b"FPS: 60.0",
        font_name="9x18B",
        fg=colors.DARK_GREY_3,
    )

    fps_avg = 0  # Moving average of the frame rate

    # Wait until the user closes the window
    ticks = sdl2.SDL_GetTicks()

    running = True
    while running:
        # Get the current time
        last_ticks, ticks = ticks, sdl2.SDL_GetTicks()
        elapsed = ticks - last_ticks

        # Calculate the frame rate
        if elapsed > 0:
            fps = 1000 / elapsed
            fps_avg = fps * 0.1 + fps_avg * 0.9 if fps_avg > 0 else fps

        # Process events
        events = sdl2.ext.get_events()
        if sdl2.ext.quit_requested(events):
            break
        # Check for key presses
        for event in events:
            # Handle all gamepad events
            if event.type == sdl2.SDL_KEYDOWN:
                # Check for the ESC key to exit the program
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    running = False
                # Check for the F11 key to toggle fullscreen mode
                elif event.key.keysym.sym == sdl2.SDLK_F11:
                    toggle_fullscreen(window)
            if (
                sdl2.SDL_CONTROLLERAXISMOTION
                <= event.type
                <= sdl2.SDL_CONTROLLERSENSORUPDATE
                or event.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP)
            ):
                gamepad.handle_event(event)
            #
            # elif event.type == sdl2.SDL_KEYDOWN:
            #     # Check if the user press alphanumeric keys
            #     if is_alpha_numeric(event.key.keysym.sym):
            #         text_editor.set_text(text_editor.text + chr(event.key.keysym.sym))
            #     elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
            #         text_editor.set_text(text_editor.text[:-1])
            #     elif event.key.keysym.sym == sdl2.SDLK_RETURN:
            #         text_editor.set_text(text_editor.text + "\n")
            #     elif event.key.keysym.sym == sdl2.SDLK_F11:
            #         toggle_fullscreen(window)
            #     elif event.key.keysym.sym == sdl2.SDLK_UP:
            #         menu.select_previous()
            #     elif event.key.keysym.sym == sdl2.SDLK_DOWN:
            #         menu.select_next()
            #     elif event.key.keysym.sym == sdl2.SDLK_RETURN:
            #         text_input.on_key_down(event.key.keysym.sym)


        # Handle menu
        if menu.active and menu.selected:
            log.info(f"Selected menu item: {menu.selected}")
            if menu.selected == "Quit":
                running = False
            menu.selected = None

        # Update the date and time
        date_time.set_text(time.strftime("%Y-%m-%d %H:%M:%S").encode())
        fps_counter.set_text(f"FPS: {fps_avg:.0f}".encode())

        # Update the text editor
        text_input.update(elapsed)

        # Render the starfield
        context.clear(color=colors.BLACK)
        starfield.draw(context.sdlrenderer)

        gamepad_viewer.render(context)

        text_editor.render_cursor(context.sdlrenderer)
        text_editor.render(context.sdlrenderer)

        if menu.active:
            menu.render(context)

        date_time.render(context.sdlrenderer)
        fps_counter.render(context.sdlrenderer)

        # Update the window
        context.present()

        # Limit the frame rate
        if FPS_TARGET:
            end_ticks = sdl2.SDL_GetTicks()
            frame_time = end_ticks - ticks
            wait_time = (1000 / FPS_TARGET) - frame_time
            if wait_time > 0:
                sdl2.SDL_Delay(int(wait_time))


def toggle_fullscreen(window):
    flags = sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
    if sdl2.SDL_GetWindowFlags(window.window) & sdl2.SDL_WINDOW_FULLSCREEN:
        flags = 0
    result = sdl2.SDL_SetWindowFullscreen(window.window, flags)
    # Hide the mouse cursor when in fullscreen mode
    sdl2.SDL_ShowCursor(0 if flags else 1)
    if result != 0:
        log.error("Failed to toggle fullscreen mode")


def is_alpha_numeric(key):
    return (
        sdl2.SDLK_a <= key <= sdl2.SDLK_z
        or sdl2.SDLK_0 <= key <= sdl2.SDLK_9
        or key == sdl2.SDLK_SPACE
        or key == sdl2.SDLK_UNDERSCORE
        or key == sdl2.SDLK_MINUS
    )


def setup_gamepads():
    log.info("Adding game controller mappings")
    sdl2.SDL_GameControllerAddMappingsFromFile(b"gamecontrollerdb.txt")
    num_joysticks = sdl2.SDL_NumJoysticks()
    for i in range(num_joysticks):
        if sdl2.SDL_IsGameController(i) == sdl2.SDL_TRUE:
            log.info("Joystick {0} is controller".format(i))
            pad = sdl2.SDL_GameControllerOpen(i)
            log.info("Controller: {0}".format(sdl2.SDL_GameControllerName(pad)))
