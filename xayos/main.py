import argparse
import logging
import time
from pathlib import Path

import sdl2
import sdl2.ext
from sdl2.ext import raise_sdl_err
from OpenGL import GL as gl

from . import colors
from .fonts import FontLoader
from .gamepad import GamepadHandler, BUTTON_START
from .gamepad_viewer import GamepadViewer
from .input import MenuController, TextController
from .logger import setup_logging
from .menu import Menu
from .starfield import StarField
from .text import TextEditor, TextLine

log = logging.getLogger(__name__)

HERE = Path(__file__).parent
RESOURCES_PATH = HERE / "resources"
OUTDIR = HERE / "out"


class XayosLunarShell:
    window_title = "Xayos Lunar Shell [POC]"
    renderer_backend = -1  # Default backend
    renderer_flags = 0
    window_flags = sdl2.SDL_WINDOW_OPENGL
    logical_size = (960, 540)
    window_size = logical_size

    def __init__(
        self,
        renderer_backend=None,
        software_renderer=False,
        vsync=False,
        fps_target=None,
    ):
        # SDL2 objects
        self.window = None
        self.context = None
        # Application configuration
        self.fps_target = fps_target
        # Application state
        self.running = True
        self.fps_avg = 0
        self.renderer_backend = renderer_backend or self.renderer_backend
        self.renderer_flags |= sdl2.SDL_RENDERER_SOFTWARE if software_renderer else 0
        self.renderer_flags |= sdl2.SDL_RENDERER_PRESENTVSYNC if vsync else 0
        # Application objects
        width, height = self.logical_size
        self.font_loader = FontLoader()
        self.gamepad = GamepadHandler(on_input=self.handle_input)
        self.gamepad_watcher = GamepadViewer(self.gamepad)
        self.starfield = StarField(width, height)
        self.menu = Menu(self.font_loader, 200, 200, active=False)
        self.menu_controller = MenuController(self.menu)
        self.text_editor = TextEditor(
            self.font_loader,
            text="Hello, Galaxy!\n",
            font_name="10x20",
            x=18,
            y=18,
            fg=colors.LIGHT_GREY_2,
        )
        self.open_file()
        self.text_controller = TextController(self.gamepad, self.text_editor)
        self.status_line = TextLine(
            self.font_loader,
            x=10,
            y=height - 18 - 10,
            text=b"[Status Line]",
            font_name="9x18B",
            fg=colors.GREY,
        )
        self.date_time = TextLine(
            self.font_loader,
            x=width - len("YYYY-mm-dd HH:MM:SS") * 9 - 10,
            y=height - 18 - 10,
            text=b"YYYY-mm-dd HH:MM:SS",
            font_name="9x18B",
            fg=colors.GREY,
        )
        self.fps_counter = TextLine(
            self.font_loader,
            x=width - len("FPS") * 9 - 10,
            y=10,
            text=b"FPS",
            font_name="9x18B",
            fg=colors.DARK_GREY_2,
        )

    def init_sdl(self):
        sdl2.ext.init(joystick=True, controller=True)
        self.window = sdl2.ext.Window(
            self.window_title, size=self.window_size, flags=self.window_flags
        )
        self.context = sdl2.ext.Renderer(
            self.window, backend=self.renderer_backend, flags=self.renderer_flags
        )
        self.renderer_info(self.context.sdlrenderer)
        if self.fps_target:
            log.info(f"Frame rate limited to {self.fps_target} FPS")
        sdl2.SDL_RenderSetLogicalSize(self.context.sdlrenderer, *self.logical_size)
        self.window.show()

    def init_opengl(self):
        gl_attributes = {
            # Use OpenGL 3.3 (core context)
            sdl2.SDL_GL_CONTEXT_MAJOR_VERSION: 3,
            sdl2.SDL_GL_CONTEXT_MINOR_VERSION: 3,
            sdl2.SDL_GL_CONTEXT_PROFILE_MASK: sdl2.SDL_GL_CONTEXT_PROFILE_CORE,
            # Double buffering and depth buffer size
            sdl2.SDL_GL_DOUBLEBUFFER: 1,
            sdl2.SDL_GL_DEPTH_SIZE: 24,
        }
        for attr, value in gl_attributes.items():
            if sdl2.SDL_GL_SetAttribute(attr, value) != 0:
                raise_sdl_err("setting OpenGL attributes")
        gl_context = sdl2.SDL_GL_CreateContext(self.window.window)
        if not gl_context:
            raise_sdl_err("creating OpenGL context")
        log.info("OpenGL version: %s", gl.glGetString(gl.GL_VERSION).decode())
        log.info("OpenGL renderer: %s", gl.glGetString(gl.GL_RENDERER).decode())
        # Number of vertex attributes supported
        log.debug("GL_MAX_VERTEX_ATTRIBS: %s", gl.glGetInteger(gl.GL_MAX_VERTEX_ATTRIBS))
        return gl_context

    def main(self):
        self.init_sdl()
        # self.gl_context = self.init_opengl()

        self.setup_gamepads()

        # Wait until the user closes the window
        ticks = sdl2.SDL_GetTicks()

        #

        while self.running:
            # Calculate the elapsed time since the last frame
            last_ticks, ticks = ticks, sdl2.SDL_GetTicks()
            elapsed_ms = ticks - last_ticks
            self.calculate_fps(elapsed_ms)

            # Handle events
            events = sdl2.ext.get_events()
            self.handle_events(events)
            self.handle_menu()

            # Update the date and time
            self.date_time.set_text(time.strftime("%Y-%m-%d %H:%M:%S").encode())
            self.fps_counter.set_text(f"{self.fps_avg:3.0f}".encode())
            self.status_line.set_text(self.text_controller.get_status_line().encode())

            if self.text_controller:
                self.text_controller.update(elapsed_ms)

            # Render the starfield
            self.context.clear(color=colors.BLACK)
            self.starfield.draw(self.context.sdlrenderer)

            self.gamepad_watcher.render(self.context)

            self.text_editor.render_cursor(self.context.sdlrenderer)
            self.text_editor.render(self.context.sdlrenderer)

            if self.menu.active:
                self.menu.render(self.context)

            self.date_time.render(self.context.sdlrenderer)
            self.fps_counter.render(self.context.sdlrenderer)
            self.status_line.render(self.context.sdlrenderer)

            # Update the window
            self.context.present()
            # Limit the frame rate
            self.limit_frame_rate(ticks)

    def open_file(self):
        # Get the latest file from the out directory
        files = sorted(OUTDIR.glob("starpad-*.txt"))
        if files:
            filename = files[-1]
            with open(filename, "rt") as f:
                text = f.read()
                self.text_editor.set_text(text)
                log.info(f"Opened text file: {filename}")

    def save_file(self):
        template = "starpad-{timestamp}.txt"
        OUTDIR.mkdir(parents=True, exist_ok=True)
        filename = OUTDIR / template.format(timestamp=time.strftime("%Y%m%d-%H%M%S"))
        text = self.text_editor.get_text()
        with open(filename, "wt") as f:
            f.write(text)
        log.info(f"Saved text file: {filename}")

    def handle_events(self, events):
        if sdl2.ext.quit_requested(events):
            self.running = False

        for event in events:
            # Handle all gamepad events
            if event.type == sdl2.SDL_KEYDOWN:
                # Check for the ESC key to exit the program
                # if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                #     self.running = False
                # Check for the F11 key to toggle fullscreen mode
                if event.key.keysym.sym == sdl2.SDLK_F11:
                    self.toggle_fullscreen()
            # Handle all gamepad events
            self.gamepad.handle_event(event)

    def handle_input(self, button, state):
        if button == BUTTON_START and state:
            self.toggle_menu()
        if self.menu.active:
            self.menu_controller.handle_input(button, state)
        else:
            self.text_controller.handle_input(button, state)

    def handle_menu(self):
        if self.menu.selected:
            log.info(f"Selected menu item: {self.menu.selected}")
            if self.menu.selected == "New File":
                self.text_editor.clear()
            elif self.menu.selected == "Open...":
                self.open_file()
            elif self.menu.selected in ("Save", "Save As..."):
                self.save_file()
            elif self.menu.selected == "Quit":
                self.running = False
            else:
                log.warning(f"Unknown menu item: {self.menu.selected}")
            self.menu.selected = None

    def toggle_menu(self):
        self.menu.active = not self.menu.active
        # if self.menu.active:
        #    self.menu.reset_selection()

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


def parse_args():
    parser = argparse.ArgumentParser(description="Xayos Lunar Shell")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--backend",
        type=str,
        help="Use the specified renderer backend (e.g. 'opengl', 'software')",
    )
    parser.add_argument(
        "--software",
        action="store_true",
        help="Use a software renderer instead of a hardware renderer",
    )
    parser.add_argument(
        "--vsync", action="store_true", help="Enable vertical synchronization"
    )
    parser.add_argument(
        "--fps",
        type=int,
        help="Limit the frame rate to the specified frames per second",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(verbose=args.verbose)
    app = XayosLunarShell(
        renderer_backend=args.backend,
        software_renderer=args.software,
        vsync=args.vsync,
        fps_target=args.fps,
    )
    app.main()
