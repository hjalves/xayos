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


class GamepadState:

    def __init__(self, on_button_press=None, on_button_release=None):
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
        self.on_button_press = on_button_press
        self.on_button_release = on_button_release

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
            case _:
                log.debug(f"Unhandled event: {event}")

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
            if self.on_button_press:
                self.on_button_press(button)
        else:
            log.debug(f"Trigger released: {button}")
            self.button_states[button] = False
            if self.on_button_release:
                self.on_button_release(button)

    def handle_button_down(self, cbutton):
        assert cbutton.state == sdl2.SDL_PRESSED
        if cbutton.button not in self.button_states:
            log.debug(
                f"Unknown button pressed: {cbutton.button} (which: {cbutton.which})"
            )
            return
        log.debug(f"Button pressed: {cbutton.button} (which: {cbutton.which})")
        self.button_states[cbutton.button] = True
        if self.on_button_press:
            self.on_button_press(cbutton.button)

    def handle_button_up(self, cbutton):
        assert cbutton.state == sdl2.SDL_RELEASED
        if cbutton.button not in self.button_states:
            log.debug(
                f"Unknown button released: {cbutton.button} (which: {cbutton.which})"
            )
            return
        log.debug(f"Button released: {cbutton.button} (which: {cbutton.which})")
        self.button_states[cbutton.button] = False
        if self.on_button_release:
            self.on_button_release(cbutton.button)

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
