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
from .gamepad import GamepadHandler, BUTTON_START, BUTTON_LEFTSTICK, BUTTON_RIGHTSTICK
from .gamepad_viewer import GamepadViewer
from .input import MenuController, TextController
from .logger import setup_logging
from .menu import Menu
from .psudo3d import (
    generate_sphere,
    render_wireframe,
    rotate_model,
    render_point_cloud,
    load_obj,
)
from .starfield import StarField
from .starpad import StarpadApp
from .text import TextEditor, TextLine
from .voyager import Voyager

log = logging.getLogger(__name__)

HERE = Path(__file__).parent
RESOURCES_PATH = HERE / "resources"


class XayosRootApplication:
    MENU_ENTRIES = [
        "Starpad",
        "Voyager",
        # "Spacewalk",
        "Settings",
        "About",
        "Quit",
    ]
    MENU_HELP = {
        "Spacewalk": "File manager",
        "Starpad": "Text editor",
        "Voyager": "Gemini client",
        "Settings": "System settings",
        "About": "About this shell",
        "Quit": "Exit the shell",
    }

    def __init__(self, font_loader, gamepad, width, height, load_application=None):
        self.running = True
        self.font_loader = font_loader
        self.gamepad = gamepad
        self.width = width
        self.height = height
        self.menu = Menu(
            font_loader,
            width // 3,
            height // 3,
            entries=self.MENU_ENTRIES,
            active=True,
            title="Lunar Shell",
            background=(0, 0, 0, 128),
        )
        self.status_line = TextLine(
            self.font_loader,
            x=10,
            y=height - 18 - 10,
            text=b"[Status Line]",
            font_name="9x18B",
            fg=colors.GREY,
        )
        # self.model_v, self.model_e = load_obj("teapot.obj")
        self.model_v, self.model_e = generate_sphere(1.0, 24, 24)
        self.menu_controller = MenuController(self.menu)
        self.load_application = load_application
        self.rotate_speed = [0.01, 0.04, 0.03]

    def update(self, elapsed_ms):
        help_text = self.MENU_HELP.get(self.menu.selected)
        self.status_line.set_text(help_text.encode() if help_text else b"")
        if self.menu.chosen:
            if self.menu.chosen == "Quit":
                self.running = False
            else:
                self.load_application(self.menu.chosen)
                self.menu.chosen = None
        x_rot, y_rot, z_rot = self.rotate_speed
        x_angle_delta = x_rot * elapsed_ms
        y_angle_delta = y_rot * elapsed_ms
        z_angle_delta = z_rot * elapsed_ms
        self.model_v = rotate_model(
            self.model_v, x_angle_delta, y_angle_delta, z_angle_delta
        )

    def render(self, renderer):
        # render_wireframe(
        #     renderer,
        #     self.sphere_v,
        #     self.sphere_e,
        #     self.width // 3,
        #     self.height,
        #     scale=80,
        #     color=colors.WHITE,
        # )
        render_point_cloud(
            renderer,
            self.model_v,
            self.width,
            self.height // 3,
            scale=50,
            color=colors.LIGHT_GREY_1,
        )
        self.menu.render(renderer)
        self.status_line.render(renderer.sdlrenderer)

    def handle_input(self, button, state):
        self.menu_controller.handle_input(button, state)


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
        self.width, self.height = self.logical_size
        self.font_loader = FontLoader()
        self.gamepad = GamepadHandler(on_input=self.handle_input)
        self.gamepad_watcher = GamepadViewer(self.gamepad)
        self.starfield = StarField(self.width, self.height)
        self.date_time = TextLine(
            self.font_loader,
            x=self.width - len("YYYY-mm-dd HH:MM:SS") * 9 - 10,
            y=self.height - 18 - 10,
            text=b"YYYY-mm-dd HH:MM:SS",
            font_name="9x18B",
            fg=colors.GREY,
        )
        self.fps_counter = TextLine(
            self.font_loader,
            x=self.width - len("FPS") * 9 - 10,
            y=10,
            text=b"FPS",
            font_name="9x18B",
            fg=colors.DARK_GREY_2,
        )
        self.application = None
        self.load_application("Voyager")
        if not self.application:
            self.load_root_application()

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

        ticks = sdl2.SDL_GetTicks()
        while self.running:
            # Calculate the elapsed time since the last frame
            last_ticks, ticks = ticks, sdl2.SDL_GetTicks()
            elapsed_ms = ticks - last_ticks
            self.calculate_fps(elapsed_ms)

            # Handle events
            events = sdl2.ext.get_events()
            self.handle_events(events)

            # Update the date/time and FPS counter
            self.date_time.set_text(time.strftime("%Y-%m-%d %H:%M:%S").encode())
            self.fps_counter.set_text(f"{self.fps_avg:3.0f}".encode())
            # Update the application
            if self.application:
                if self.application.running:
                    self.application.update(elapsed_ms)
                else:
                    self.unload_application()

            # Render the scene
            self.context.clear(color=colors.BLACK)
            self.starfield.draw(self.context)
            if self.application:
                self.application.render(self.context)
            self.gamepad_watcher.render(self.context)
            self.date_time.render(self.context.sdlrenderer)
            self.fps_counter.render(self.context.sdlrenderer)
            # Update the window
            self.context.present()
            self.limit_frame_rate(ticks)

    def load_root_application(self):
        assert self.application is None, "Application already loaded"
        self.application = XayosRootApplication(
            self.font_loader,
            self.gamepad,
            self.width,
            self.height,
            load_application=self.load_application,
        )

    def load_application(self, app_name):
        if app_name == "Starpad":
            self.application = StarpadApp(self.font_loader, self.gamepad, 960, 540)
        elif app_name == "Voyager":
            self.application = Voyager(self.font_loader, self.gamepad, 960, 540)
        else:
            log.error(f"Unknown application: {app_name}")

    def unload_application(self):
        # If the menu application is unloaded, then quit the shell
        if isinstance(self.application, XayosRootApplication):
            self.running = False
            return
        self.application = None
        self.load_root_application()

    def handle_events(self, events):
        if sdl2.ext.quit_requested(events):
            self.running = False

        for event in events:
            # Handle all gamepad events
            if event.type == sdl2.SDL_KEYDOWN:
                # Check for the F11 key to toggle fullscreen mode
                if event.key.keysym.sym == sdl2.SDLK_F11:
                    self.toggle_fullscreen()
            # Handle all gamepad events and some keyboard events
            self.gamepad.handle_event(event)

    def handle_input(self, button, state):
        if (
            button == BUTTON_LEFTSTICK
            and self.gamepad.is_pressed(BUTTON_RIGHTSTICK)
            and state
            or button == BUTTON_RIGHTSTICK
            and self.gamepad.is_pressed(BUTTON_LEFTSTICK)
            and state
        ):
            self.toggle_fullscreen()
        if self.application:
            self.application.handle_input(button, state)

    def renderer_info(self, sdlrenderer):
        info = sdl2.render.SDL_RendererInfo()
        sdl2.SDL_GetRendererInfo(sdlrenderer, info)
        log.info(f"Renderer: {info.name.decode()}")

    def setup_gamepads(self, mapping_file="gamecontrollerdb.txt"):
        path = str(RESOURCES_PATH / mapping_file)
        log.info("Loading game controller mappings from %s", path)
        if sdl2.SDL_GameControllerAddMappingsFromFile(path.encode()) != 0:
            log.error("Failed to load game controller mappings")
        num_joysticks = sdl2.SDL_NumJoysticks()
        for i in range(num_joysticks):
            if sdl2.SDL_IsGameController(i) == sdl2.SDL_TRUE:
                pad = sdl2.SDL_GameControllerOpen(i)
                name = sdl2.SDL_GameControllerName(pad)
                log.info("Controller #%d: %s", i, name.decode())

    def toggle_fullscreen(self):
        flags = sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
        if sdl2.SDL_GetWindowFlags(self.window.window) & sdl2.SDL_WINDOW_FULLSCREEN:
            flags = 0
        if sdl2.SDL_SetWindowFullscreen(self.window.window, flags) != 0:
            log.error("Failed to toggle fullscreen mode")
        else:
            # Hide the mouse cursor when in fullscreen mode
            sdl2.SDL_ShowCursor(0 if flags else 1)

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
