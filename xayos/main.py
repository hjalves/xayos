import logging
import time
from pathlib import Path

import sdl2
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


class XayosLunarShell:
    window_title = "Xayos Lunar Shell [POC]"
    renderer_backend = -1  # Default backend
    # renderer_flags = 0
    renderer_flags = sdl2.SDL_RENDERER_SOFTWARE
    # renderer_flags = sdl2.SDL_RENDERER_PRESENTVSYNC
    logical_size = (960, 540)
    window_size = logical_size

    def __init__(self):
        # SDL2 objects
        self.window = None
        self.context = None
        # Application configuration
        self.fps_target = 30
        # Application state
        self.running = True
        self.fps_avg = 0
        self.in_menu = False
        # Application objects
        self.starfield = None
        self.font_loader = None
        self.menu = None
        self.gamepad = None
        self.gamepad_viewer = None
        self.input_handler = None
        self.text_editor = None
        self.date_time = None
        self.fps_counter = None

    def init_sdl(self):
        sdl2.ext.init(joystick=True, controller=True)
        self.window = sdl2.ext.Window(self.window_title, size=self.window_size)
        self.context = sdl2.ext.Renderer(
            self.window, backend=self.renderer_backend, flags=self.renderer_flags
        )
        self.renderer_info(self.context.sdlrenderer)
        sdl2.SDL_RenderSetLogicalSize(self.context.sdlrenderer, *self.logical_size)
        self.window.show()

    def main(self):
        setup_logging(verbose=True)
        self.init_sdl()

        self.setup_gamepads()

        width, height = self.logical_size
        starfield = StarField(width, height)

        self.gamepad = GamepadHandler()
        self.gamepad_viewer = GamepadViewer(self.gamepad)
        self.gamepad_viewer.create_texture(self.context)

        self.font_loader = FontLoader()
        self.text_editor = TextEditor(
            self.font_loader,
            text="Hello, Galaxy!\n",
            font_name="10x20",
            x=18,
            y=18,
            fg=colors.WHITE,
        )
        self.input_handler = TextInputHandler()
        self.input_handler.set_active_widget(self.text_editor)
        self.input_handler.connect_gamepad(self.gamepad)
        # text_input.disconnect_gamepad()

        menu = Menu(self.font_loader, 200, 200)
        # menu.connect_gamepad(gamepad)
        menu.active = False

        date_time = TextLine(
            self.font_loader,
            x=width - len("YYYY-mm-dd HH:MM:SS") * 9 - 10,
            y=height - 18 - 10,
            text=b"YYYY-mm-dd HH:MM:SS",
            font_name="9x18B",
            fg=colors.GREY,
        )
        fps_counter = TextLine(
            self.font_loader,
            x=10,
            y=height - 18 - 10,
            text=b"FPS: 60.0",
            font_name="9x18B",
            fg=colors.DARK_GREY_3,
        )

        # Wait until the user closes the window
        ticks = sdl2.SDL_GetTicks()

        while self.running:
            # Calculate the elapsed time since the last frame
            last_ticks, ticks = ticks, sdl2.SDL_GetTicks()
            elapsed_ms = ticks - last_ticks
            self.calculate_fps(elapsed_ms)

            # Handle events
            events = sdl2.ext.get_events()
            self.handle_events(events)

            # Handle menu
            if menu.active and menu.selected:
                log.info(f"Selected menu item: {menu.selected}")
                if menu.selected == "Quit":
                    self.running = False
                menu.selected = None

            # Update the date and time
            date_time.set_text(time.strftime("%Y-%m-%d %H:%M:%S").encode())
            fps_counter.set_text(f"FPS: {self.fps_avg:.0f}".encode())

            # Update the text editor
            self.input_handler.update(elapsed_ms)

            # Render the starfield
            self.context.clear(color=colors.BLACK)
            starfield.draw(self.context.sdlrenderer)

            self.gamepad_viewer.render(self.context)

            self.text_editor.render_cursor(self.context.sdlrenderer)
            self.text_editor.render(self.context.sdlrenderer)

            if menu.active:
                menu.render(self.context)

            date_time.render(self.context.sdlrenderer)
            fps_counter.render(self.context.sdlrenderer)

            # Update the window
            self.context.present()
            # Limit the frame rate
            self.limit_frame_rate(ticks)

    def handle_events(self, events):
        if sdl2.ext.quit_requested(events):
            self.running = False

        for event in events:
            # Handle all gamepad events
            if event.type == sdl2.SDL_KEYDOWN:
                # Check for the ESC key to exit the program
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    self.running = False
                # Check for the F11 key to toggle fullscreen mode
                elif event.key.keysym.sym == sdl2.SDLK_F11:
                    self.toggle_fullscreen()
            if (
                sdl2.SDL_CONTROLLERAXISMOTION
                <= event.type
                <= sdl2.SDL_CONTROLLERSENSORUPDATE
                or event.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP)
            ):
                self.gamepad.handle_event(event)

    def renderer_info(self, sdlrenderer):
        info = sdl2.render.SDL_RendererInfo()
        sdl2.SDL_GetRendererInfo(sdlrenderer, info)
        log.info(f"Renderer: {info.name.decode()}")

    def setup_gamepads(self):
        log.info("Adding game controller mappings")
        sdl2.SDL_GameControllerAddMappingsFromFile(b"gamecontrollerdb.txt")
        num_joysticks = sdl2.SDL_NumJoysticks()
        for i in range(num_joysticks):
            if sdl2.SDL_IsGameController(i) == sdl2.SDL_TRUE:
                log.info("Joystick {0} is controller".format(i))
                pad = sdl2.SDL_GameControllerOpen(i)
                log.info("Controller: {0}".format(sdl2.SDL_GameControllerName(pad)))

    def toggle_fullscreen(self):
        flags = sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
        if sdl2.SDL_GetWindowFlags(self.window.window) & sdl2.SDL_WINDOW_FULLSCREEN:
            flags = 0
        result = sdl2.SDL_SetWindowFullscreen(self.window.window, flags)
        # Hide the mouse cursor when in fullscreen mode
        sdl2.SDL_ShowCursor(0 if flags else 1)
        if result != 0:
            log.error("Failed to toggle fullscreen mode")

    def limit_frame_rate(self, start_ticks):
        if self.fps_target:
            end_ticks = sdl2.SDL_GetTicks()
            frame_time = end_ticks - start_ticks
            wait_time = (1000 / self.fps_target) - frame_time
            if wait_time > 0:
                sdl2.SDL_Delay(int(wait_time))

    def calculate_fps(self, elapsed):
        # Calculate the frame rate
        if elapsed > 0:
            # weight the new frame rate by 10% and the average by 90%
            fps = 1000 / elapsed
            self.fps_avg = fps * 0.1 + self.fps_avg * 0.9 if self.fps_avg > 0 else fps


def is_alpha_numeric(key):
    return (
        sdl2.SDLK_a <= key <= sdl2.SDLK_z
        or sdl2.SDLK_0 <= key <= sdl2.SDLK_9
        or key == sdl2.SDLK_SPACE
        or key == sdl2.SDLK_UNDERSCORE
        or key == sdl2.SDLK_MINUS
    )


def main():
    app = XayosLunarShell()
    app.main()
