import logging

import sdl2

from xayos import colors

log = logging.getLogger(__name__)


class TextInputHandler:
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
    L4_KEYS = ("0", )
    L5_KEYS = ("(", "[", "{", "<", "\"", "'")
    L6_KEYS = (".", ",", "?", "!", "_", ":", ";", "|" )
    L7_KEYS = (")", "]", "}", ">", "\"", "'")
    L8_KEYS = ("-", "=", "+", "*", "/", "^", "~", "#", "%", "@")


    def __init__(self):
        self.text_editor = None
        self.current_char = None
        self.cycled_elapsed = 0
        self.r_modifier = False
        self.l_modifier = False
        self.l_shoulder = False
        self.uppercase = False
        self.caps_lock = False

    def set_active_text_editor(self, text_editor):
        self.text_editor = text_editor

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
        log.debug(f"Controller button pressed: {button}")
        if button == sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER:
            self.toggle_uppercase()
            log.debug(f"Uppercase: {self.uppercase}")
            self.l_shoulder = True
            return

        if self.r_modifier:
            self.on_controller_button_down_r_modifier(button)
            return
        if self.l_modifier:
            self.on_controller_button_down_l_modifier(button)
            return
        mapping = {
            sdl2.SDL_CONTROLLER_BUTTON_A: self.S1_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_X: self.S2_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_Y: self.S3_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_B: self.S4_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN: self.S5_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT: self.S6_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP: self.S7_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT: self.S8_KEYS,
        }
        if button in mapping:
            self.cycle(chars=mapping[button])
        else:
            log.debug(f"Unhandled button: {button}")

    def on_controller_button_down_r_modifier(self, button):
        if button == sdl2.SDL_CONTROLLER_BUTTON_A:
            self.flush_char()
            self.text_editor.put_char("\n")
        elif button == sdl2.SDL_CONTROLLER_BUTTON_X:
            self.flush_char()
            self.text_editor.put_char(" ")
        elif button == sdl2.SDL_CONTROLLER_BUTTON_B:
            self.flush_char()
            self.text_editor.backspace()
        else:
            log.debug(f"Unhandled button: {button}")

    def on_controller_button_down_l_modifier(self, button):
        mapping = {
            sdl2.SDL_CONTROLLER_BUTTON_A: self.L1_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_X: self.L2_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_Y: self.L3_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_B: self.L4_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT: self.L5_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN: self.L6_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT: self.L7_KEYS,
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP: self.L8_KEYS,
        }
        if button in mapping:
            self.cycle(chars=mapping[button])
        else:
            log.debug(f"Unhandled button: {button}")

    def on_controller_button_up(self, button):
        log.debug(f"Controller button released: {button}")
        if button == sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER:
            self.l_shoulder = False
            if self.caps_lock:
                self.caps_lock = False


    def on_controller_axis_motion(self, axis, value):
        if axis == sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT:
            threshold = self.TRIGGER_THRESHOLD
            if value >= threshold:
                #log.debug(f"Right trigger pressed")
                self.flush_char()
                self.r_modifier = True
                self.text_editor.set_cursor_color(colors.RED)
            else:
                #log.debug(f"Right trigger released")
                self.r_modifier = False
                self.text_editor.set_cursor_color(colors.PINK)

        elif axis == sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT:
            threshold = self.TRIGGER_THRESHOLD
            if value >= threshold:
                #log.debug(f"Left trigger pressed")
                self.l_modifier = True
                self.text_editor.set_cursor_color(colors.GREEN)
            else:
                #log.debug(f"Left trigger released")
                self.flush_char()
                self.l_modifier = False
                self.text_editor.set_cursor_color(colors.PINK)

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
            self.text_editor.put_char(current_char)
            self.text_editor.set_cursor_char(None)
            self.current_char = None
            if self.l_shoulder:
                self.caps_lock = True
            elif not self.caps_lock:
                self.disable_uppercase()

    def update_cursor_char(self):
        if self.current_char:
            current_char = self.current_char
            if self.uppercase:
                current_char = current_char.upper()
            self.text_editor.set_cursor_char(current_char.encode())

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
        if self.text_editor:
            self.update_cursor_char()
