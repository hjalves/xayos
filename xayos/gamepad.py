import logging

import sdl2

from xayos import colors

# Buttons and Axis constants

BUTTON_A = sdl2.SDL_CONTROLLER_BUTTON_A
BUTTON_B = sdl2.SDL_CONTROLLER_BUTTON_B
BUTTON_X = sdl2.SDL_CONTROLLER_BUTTON_X
BUTTON_Y = sdl2.SDL_CONTROLLER_BUTTON_Y
BUTTON_BACK = sdl2.SDL_CONTROLLER_BUTTON_BACK
BUTTON_GUIDE = sdl2.SDL_CONTROLLER_BUTTON_GUIDE
BUTTON_START = sdl2.SDL_CONTROLLER_BUTTON_START
BUTTON_LEFTSTICK = sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK
BUTTON_RIGHTSTICK = sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK
BUTTON_LEFTSHOULDER = sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER
BUTTON_RIGHTSHOULDER = sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER
BUTTON_DPAD_UP = sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP
BUTTON_DPAD_DOWN = sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN
BUTTON_DPAD_LEFT = sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT
BUTTON_DPAD_RIGHT = sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT

AXIS_LEFTX = sdl2.SDL_CONTROLLER_AXIS_LEFTX
AXIS_LEFTY = sdl2.SDL_CONTROLLER_AXIS_LEFTY
AXIS_RIGHTX = sdl2.SDL_CONTROLLER_AXIS_RIGHTX
AXIS_RIGHTY = sdl2.SDL_CONTROLLER_AXIS_RIGHTY
AXIS_TRIGGERLEFT = sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT
AXIS_TRIGGERRIGHT = sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT

BUTTON_TRIGGERLEFT = 100
BUTTON_TRIGGERRIGHT = 101


log = logging.getLogger(__name__)


class GamepadHandler:

    def __init__(self, on_input=None):
        # self.controller = None
        # self.controller_id = None
        self.trigger_threshold = 32767 // 2
        self.axis_states = {
            AXIS_LEFTX: 0,
            AXIS_LEFTY: 0,
            AXIS_RIGHTX: 0,
            AXIS_RIGHTY: 0,
            AXIS_TRIGGERLEFT: 0,
            AXIS_TRIGGERRIGHT: 0,
        }
        self.button_states = {
            BUTTON_A: False,
            BUTTON_B: False,
            BUTTON_X: False,
            BUTTON_Y: False,
            BUTTON_BACK: False,
            BUTTON_GUIDE: False,
            BUTTON_START: False,
            BUTTON_LEFTSTICK: False,
            BUTTON_RIGHTSTICK: False,
            BUTTON_LEFTSHOULDER: False,
            BUTTON_RIGHTSHOULDER: False,
            BUTTON_DPAD_UP: False,
            BUTTON_DPAD_DOWN: False,
            BUTTON_DPAD_LEFT: False,
            BUTTON_DPAD_RIGHT: False,
            BUTTON_TRIGGERLEFT: False,
            BUTTON_TRIGGERRIGHT: False,
        }
        self.key_button_mapping = {
            sdl2.SDLK_F1: BUTTON_A,
            sdl2.SDLK_F2: BUTTON_X,
            sdl2.SDLK_F3: BUTTON_Y,
            sdl2.SDLK_F4: BUTTON_B,
            sdl2.SDLK_F5: BUTTON_DPAD_DOWN,
            sdl2.SDLK_F6: BUTTON_DPAD_LEFT,
            sdl2.SDLK_F7: BUTTON_DPAD_UP,
            sdl2.SDLK_F8: BUTTON_DPAD_RIGHT,
            sdl2.SDLK_LSHIFT: BUTTON_TRIGGERLEFT,
            sdl2.SDLK_RSHIFT: BUTTON_TRIGGERRIGHT,
            sdl2.SDLK_LCTRL: BUTTON_LEFTSHOULDER,
            sdl2.SDLK_RCTRL: BUTTON_RIGHTSHOULDER,
            sdl2.SDLK_LALT: BUTTON_LEFTSTICK,
            sdl2.SDLK_RALT: BUTTON_RIGHTSTICK,
            sdl2.SDLK_F9: BUTTON_START,
            sdl2.SDLK_F10: BUTTON_BACK,
            sdl2.SDLK_F12: BUTTON_GUIDE,
            sdl2.SDLK_UP: BUTTON_DPAD_UP,
            sdl2.SDLK_DOWN: BUTTON_DPAD_DOWN,
            sdl2.SDLK_LEFT: BUTTON_DPAD_LEFT,
            sdl2.SDLK_RIGHT: BUTTON_DPAD_RIGHT,
            sdl2.SDLK_RETURN: BUTTON_START,
            sdl2.SDLK_ESCAPE: BUTTON_BACK,
            sdl2.SDLK_SPACE: BUTTON_A,
            sdl2.SDLK_BACKSPACE: BUTTON_B,
        }
        self.on_input = on_input

    def set_callbacks(self, on_input=None):
        if on_input:
            assert self.on_input is None, "Callback already set"
            self.on_input = on_input

    def clear_callbacks(self):
        self.on_input = None

    def is_pressed(self, button):
        return self.button_states[button]

    def buttons_pressed(self):
        return [button for button, state in self.button_states.items() if state]

    def handle_event(self, event):
        match event.type:
            case sdl2.SDL_CONTROLLERAXISMOTION:
                self.handle_axis_motion(event.caxis)
            case sdl2.SDL_CONTROLLERBUTTONDOWN:
                self.handle_button_down(event.cbutton)
            case sdl2.SDL_CONTROLLERBUTTONUP:
                self.handle_button_up(event.cbutton)
            case sdl2.SDL_CONTROLLERDEVICEADDED:
                self.handle_device_added(event.cdevice)
            case sdl2.SDL_CONTROLLERDEVICEREMOVED:
                self.handle_device_removed(event.cdevice)
            case sdl2.SDL_CONTROLLERDEVICEREMAPPED:
                self.handle_device_remapped(event.cdevice)
            case sdl2.SDL_CONTROLLERTOUCHPADDOWN:
                self.handle_touchpad_down(event.ctouchpad)
            case sdl2.SDL_CONTROLLERTOUCHPADMOTION:
                self.handle_touchpad_motion(event.ctouchpad)
            case sdl2.SDL_CONTROLLERTOUCHPADUP:
                self.handle_touchpad_up(event.ctouchpad)
            case sdl2.SDL_CONTROLLERSENSORUPDATE:
                self.handle_sensor_update(event.csensor)
            case sdl2.SDL_KEYDOWN:
                self.handle_key_down(event.key)
            case sdl2.SDL_KEYUP:
                self.handle_key_up(event.key)
            case _:
                pass

    def handle_axis_motion(self, caxis):
        if caxis.axis not in self.axis_states:
            log.debug(f"Unknown axis motion: {caxis.axis} (value: {caxis.value})")
            return
        # log.debug(f"Axis motion: {caxis.axis} (value: {caxis.value})")
        self.axis_states[caxis.axis] = caxis.value
        if caxis.axis in (AXIS_TRIGGERLEFT, AXIS_TRIGGERRIGHT):
            self.handle_trigger(caxis.axis, caxis.value)

    def handle_trigger(self, axis, value):
        if axis == AXIS_TRIGGERLEFT:
            button = BUTTON_TRIGGERLEFT
        elif axis == AXIS_TRIGGERRIGHT:
            button = BUTTON_TRIGGERRIGHT
        else:
            log.debug(f"Unknown trigger axis: {axis}")
            return
        if value >= self.trigger_threshold:
            log.debug(f"Trigger pressed: {button}")
            self.button_states[button] = True
            if self.on_input:
                self.on_input(button, True)
        else:
            log.debug(f"Trigger released: {button}")
            self.button_states[button] = False
            if self.on_input:
                self.on_input(button, False)

    def handle_button_down(self, cbutton):
        assert cbutton.state == sdl2.SDL_PRESSED
        if cbutton.button not in self.button_states:
            log.debug(
                f"Unknown button pressed: {cbutton.button} (which: {cbutton.which})"
            )
            return
        # log.debug(f"Button pressed: {cbutton.button} (which: {cbutton.which})")
        self.button_states[cbutton.button] = True
        if self.on_input:
            self.on_input(cbutton.button, True)

    def handle_button_up(self, cbutton):
        assert cbutton.state == sdl2.SDL_RELEASED
        if cbutton.button not in self.button_states:
            log.debug(
                f"Unknown button released: {cbutton.button} (which: {cbutton.which})"
            )
            return
        # log.debug(f"Button released: {cbutton.button} (which: {cbutton.which})")
        self.button_states[cbutton.button] = False
        if self.on_input:
            self.on_input(cbutton.button, False)

    def handle_device_added(self, cdevice):
        pass

    def handle_device_removed(self, cdevice):
        pass

    def handle_device_remapped(self, cdevice):
        pass

    def handle_touchpad_down(self, ctouchpad):
        pass

    def handle_touchpad_motion(self, ctouchpad):
        pass

    def handle_touchpad_up(self, ctouchpad):
        pass

    def handle_sensor_update(self, csensor):
        pass

    # This is to simulate the gamepad with the keyboard

    def generate_button_event(self, button, state, which=0):
        event = sdl2.SDL_Event()
        event.type = (
            sdl2.SDL_CONTROLLERBUTTONDOWN if state else sdl2.SDL_CONTROLLERBUTTONUP
        )
        event.cbutton.which = which
        event.cbutton.button = button
        event.cbutton.state = state
        return event

    def handle_key_down(self, key):
        if key.repeat:
            return
        log.debug(f"Key down: {key.keysym.sym}")
        if key.keysym.sym in self.key_button_mapping:
            button = self.key_button_mapping[key.keysym.sym]
            event = self.generate_button_event(button, True)
            self.handle_event(event)

    def handle_key_up(self, key):
        log.debug(f"Key up: {key.keysym.sym}")
        if key.keysym.sym in self.key_button_mapping:
            button = self.key_button_mapping[key.keysym.sym]
            event = self.generate_button_event(button, False)
            self.handle_event(event)
