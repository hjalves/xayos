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
from .starfield import StarField
from .text import TextEditor, TextLine

log = logging.getLogger(__name__)

HERE = Path(__file__).parent
OUTDIR = HERE / "out"


class StarpadApp:
    MENU_ENTRIES = [
        "New File",
        "Open...",
        "Save",
        "Save As...",
        "About",
        "Quit",
    ]
    MENU_HELP = {
        "New File": "Create a new file",
        "Open...": "Open a file",
        "Save": "Save the current file",
        "Save As...": "Save the current file with a new name",
        "About": "Show information about this program",
        "Quit": "Exit the program",
    }

    def __init__(self, font_loader, gamepad, width, height):
        self.running = True
        self.font_loader = font_loader
        self.gamepad = gamepad
        self.menu = Menu(
            self.font_loader,
            200,
            200,
            active=False,
            title="Starpad Menu",
            entries=self.MENU_ENTRIES,
        )
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

    def update(self, elapsed_ms):
        self.handle_menu()
        if not self.menu.active:
            self.status_line.set_text(self.text_controller.get_status_line().encode())
        else:
            help_text = self.MENU_HELP.get(self.menu.selected)
            self.status_line.set_text(help_text.encode() if help_text else b"")

        if self.text_controller:
            self.text_controller.update(elapsed_ms)

    def render(self, renderer):
        self.text_editor.render_cursor(renderer.sdlrenderer)
        self.text_editor.render(renderer.sdlrenderer)

        if self.menu.active:
            self.menu.render(renderer)

        self.status_line.render(renderer.sdlrenderer)

    def handle_input(self, button, state):
        if button == BUTTON_START and state:
            self.toggle_menu()
        if self.menu.active:
            self.menu_controller.handle_input(button, state)
        else:
            self.text_controller.handle_input(button, state)

    def handle_menu(self):
        if self.menu.chosen:
            log.info(f"Selected menu item: {self.menu.chosen}")
            if self.menu.chosen == "New File":
                self.text_editor.clear()
            elif self.menu.chosen == "Open...":
                self.open_file()
            elif self.menu.chosen in ("Save", "Save As..."):
                self.save_file()
            elif self.menu.chosen == "Quit":
                self.running = False
            else:
                log.warning(f"Unknown menu item: {self.menu.chosen}")
            self.menu.chosen = None

    def toggle_menu(self):
        self.menu.active = not self.menu.active
        # if self.menu.active:
        #    self.menu.reset_selection()

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
