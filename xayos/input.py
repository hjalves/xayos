import logging

import sdl2

from xayos import colors
from xayos.gamepad import (
    BUTTON_TRIGGERLEFT,
    BUTTON_TRIGGERRIGHT,
    BUTTON_LEFTSHOULDER,
    BUTTON_A,
    BUTTON_X,
    BUTTON_Y,
    BUTTON_B,
    BUTTON_DPAD_DOWN,
    BUTTON_DPAD_LEFT,
    BUTTON_DPAD_UP,
    BUTTON_DPAD_RIGHT,
)

log = logging.getLogger(__name__)


class InputHandler:
    def __init__(self, gamepad):
        pass


class MenuController:
    def __init__(self, widget):
        self.widget = widget

    def handle_input(self, button, state):
        if state:
            self.on_button_press(button)

    def on_button_press(self, button):
        log.debug(f"SimpleInputHandler: Button pressed: {button}")
        if button == BUTTON_A:
            self.widget.select()
        elif button == BUTTON_B:
            self.widget.cancel()
        elif button == BUTTON_DPAD_UP:
            self.widget.move_up()
        elif button == BUTTON_DPAD_DOWN:
            self.widget.move_down()


class TextController:
    TRIGGER_THRESHOLD = 20000

    S1_KEYS = ("a", "b", "c")
    S2_KEYS = ("d", "e", "f")
    S3_KEYS = ("g", "h", "i")
    S4_KEYS = ("j", "k", "l")
    S5_KEYS = ("m", "n", "o")
    S6_KEYS = ("p", "q", "r", "s")
    S7_KEYS = ("t", "u", "v")
    S8_KEYS = ("w", "x", "y", "z")

    L1_KEYS = ("1", "2", "3")
    L2_KEYS = ("4", "5", "6")
    L3_KEYS = ("7", "8", "9")
    L4_KEYS = ("0", ".")
    L5_KEYS = ("(", "[", "{", "<", '"', "'")
    L6_KEYS = (".", ",", "?", "!", "_", ":", ";", "|")
    L7_KEYS = (")", "]", "}", ">", '"', "'")
    L8_KEYS = ("-", "=", "+", "*", "/", "^", "~", "#", "%", "@")

    def __init__(self, gamepad, widget):
        self.gamepad = gamepad
        # self.gamepad.set_callbacks(
        #     on_button_press=self.on_button_press,
        #     on_button_release=self.on_button_release,
        # )
        self.active_widget = widget
        self.current_char = None
        self.cycled_elapsed = 0
        self.uppercase = False
        self.caps_lock = False

    def handle_input(self, button, state):
        if state:
            self.on_button_press(button)
        else:
            self.on_button_release(button)

    def on_button_press(self, button):
        if button in (BUTTON_TRIGGERRIGHT, BUTTON_TRIGGERLEFT):
            self.on_trigger(button, pressed_state=True)
            return
        self.on_controller_button_down(button)

    def on_button_release(self, button):
        if button in (BUTTON_TRIGGERRIGHT, BUTTON_TRIGGERLEFT):
            self.on_trigger(button, pressed_state=False)
            return
        self.on_controller_button_up(button)

    def on_key_down(self, key):
        if key == sdl2.SDLK_F1:
            self.cycle(chars=self.S1_KEYS)
        elif key == sdl2.SDLK_F2:
            self.cycle(chars=self.S2_KEYS)
        elif key == sdl2.SDLK_F3:
            self.cycle(chars=self.S3_KEYS)
        elif key == sdl2.SDLK_F4:
            self.cycle(chars=self.S4_KEYS)
        elif key == sdl2.SDLK_F5:
            self.cycle(chars=self.S5_KEYS)
        elif key == sdl2.SDLK_F6:
            self.cycle(chars=self.S6_KEYS)
        elif key == sdl2.SDLK_F7:
            self.cycle(chars=self.S7_KEYS)
        elif key == sdl2.SDLK_F8:
            self.cycle(chars=self.S8_KEYS)
        else:
            log.debug(f"Key pressed: {key}")

    def on_controller_button_down(self, button):
        if button == BUTTON_LEFTSHOULDER:
            self.toggle_uppercase()
            log.debug(f"Uppercase: {self.uppercase}")
            return

        if self.gamepad.is_pressed(BUTTON_TRIGGERRIGHT):
            self.on_controller_button_down_r_modifier(button)
            return
        if self.gamepad.is_pressed(BUTTON_TRIGGERLEFT):
            self.on_controller_button_down_l_modifier(button)
            return
        mapping = {
            BUTTON_A: self.S1_KEYS,
            BUTTON_X: self.S2_KEYS,
            BUTTON_Y: self.S3_KEYS,
            BUTTON_B: self.S4_KEYS,
            BUTTON_DPAD_DOWN: self.S5_KEYS,
            BUTTON_DPAD_LEFT: self.S6_KEYS,
            BUTTON_DPAD_UP: self.S7_KEYS,
            BUTTON_DPAD_RIGHT: self.S8_KEYS,
        }
        if button in mapping:
            self.cycle(chars=mapping[button])
        else:
            log.debug(f"Unhandled button: {button}")

    def on_controller_button_down_r_modifier(self, button):
        if button == BUTTON_A:
            self.flush_char()
            self.active_widget.put_char("\n")
        elif button == BUTTON_X:
            self.flush_char()
            self.active_widget.put_char(" ")
        elif button == BUTTON_B:
            self.flush_char()
            self.active_widget.backspace()
        elif button == BUTTON_Y:
            self.flush_char()
            self.active_widget.delete()
        else:
            log.debug(f"Unhandled button: {button}")

    def on_controller_button_down_l_modifier(self, button):
        mapping = {
            BUTTON_A: self.L1_KEYS,
            BUTTON_X: self.L2_KEYS,
            BUTTON_Y: self.L3_KEYS,
            BUTTON_B: self.L4_KEYS,
            BUTTON_DPAD_LEFT: self.L5_KEYS,
            BUTTON_DPAD_DOWN: self.L6_KEYS,
            BUTTON_DPAD_RIGHT: self.L7_KEYS,
            BUTTON_DPAD_UP: self.L8_KEYS,
        }
        if button in mapping:
            self.cycle(chars=mapping[button])
        else:
            log.debug(f"Unhandled button: {button}")

    def on_controller_button_up(self, button):
        if button == sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER:
            if self.caps_lock:
                self.caps_lock = False

    def on_trigger(self, button, pressed_state):
        if button == BUTTON_TRIGGERLEFT:
            if not pressed_state:
                self.flush_char()
        elif button == BUTTON_TRIGGERRIGHT:
            if pressed_state:
                self.flush_char()
        # Update cursor color
        if self.gamepad.is_pressed(BUTTON_TRIGGERRIGHT):
            self.active_widget.set_cursor_color(colors.RED)
        elif self.gamepad.is_pressed(BUTTON_TRIGGERLEFT):
            self.active_widget.set_cursor_color(colors.GREEN)
        else:
            self.active_widget.set_cursor_color(colors.PINK)

    def update(self, elapsed):
        if self.current_char:
            self.cycled_elapsed += elapsed
            if self.cycled_elapsed >= 1000:
                self.flush_char()

    def flush_char(self):
        if self.current_char:
            current_char = self.current_char
            if self.uppercase:
                current_char = current_char.upper()
            self.active_widget.put_char(current_char)
            self.active_widget.set_cursor_char(None)
            self.current_char = None
            # if left shoulder is pressed while a char is flushed, enable caps lock
            if self.gamepad.is_pressed(BUTTON_LEFTSHOULDER):
                self.caps_lock = True
            elif not self.caps_lock:
                self.disable_uppercase()

    def update_cursor_char(self):
        if self.current_char:
            current_char = self.current_char
            if self.uppercase:
                current_char = current_char.upper()
            self.active_widget.set_cursor_char(current_char.encode())

    def toggle_uppercase(self):
        self.uppercase = not self.uppercase
        self.update_cursor_char()
        self.cycled_elapsed = 0

    def disable_uppercase(self):
        self.uppercase = False
        self.update_cursor_char()
        self.cycled_elapsed = 0

    def cycle(self, chars):
        if self.current_char is None:
            pos = 0
        elif self.current_char in chars:
            pos = chars.index(self.current_char) + 1
            pos %= len(chars)
        else:
            self.flush_char()
            pos = 0
        self.current_char = chars[pos]
        self.cycled_elapsed = 0
        log.debug(f"Cycling char: {self.current_char}")
        if self.active_widget:
            self.update_cursor_char()
