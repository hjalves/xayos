"""2D drawing examples utilising the SDL2_gfx functions."""
import logging
import sys
import ctypes
from random import randint

import sdl2
import sdl2.sdlgfx
import sdl2.ext

from xayos.logger import setup_logging


log = logging.getLogger(__name__)

# Draws random lines using the passed rendering context
def draw_lines(context, width, height):
    # Reset the visible area with a black color.
    context.clear(0)
    # Split the visible area
    whalf = width // 2 - 2
    hhalf = height // 2 - 2
    lw = 5
    x0, x1 = whalf, whalf
    y0, y1 = 0, height
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, x0, y0, x1, y1, lw,
                               0xFFFFFFFF)
    x0, x1 = 0, width
    y0, y1 = hhalf, hhalf
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, x0, y0, x1, y1, lw,
                               0xFFFFFFFF)
    for x in range(15):
        # In the first quadrant, draw normal lines
        color = randint(0, 0xFFFFFFFF)
        x0, x1 = randint(0, whalf), randint(0, whalf)
        y0, y1 = randint(0, hhalf), randint(0, hhalf)
        sdl2.sdlgfx.lineColor(context.sdlrenderer, x0, y0, x1, y1, color)
        # In the second quadrant, draw aa lines
        color = randint(0, 0xFFFFFFFF)
        x0, x1 = randint(whalf + lw, width), randint(whalf + lw, width)
        y0, y1 = randint(0, hhalf), randint(0, hhalf)
        sdl2.sdlgfx.aalineColor(context.sdlrenderer, x0, y0, x1, y1, color)
        # In the third quadrant, draw horizontal lines
        color = randint(0, 0xFFFFFFFF)
        x0, x1 = randint(0, whalf), randint(0, whalf)
        y0 = randint(hhalf + lw, height)
        sdl2.sdlgfx.hlineColor(context.sdlrenderer, x0, x1, y0, color)
        # In the fourth quadrant, draw vertical lines
        color = randint(0, 0xFFFFFFFF)
        x0 = randint(whalf + lw, width)
        y0, y1 = randint(hhalf + lw, height), randint(hhalf + lw, height)
        sdl2.sdlgfx.vlineColor(context.sdlrenderer, x0, y0, y1, color)


# Draws random circles using the passed rendering context
def draw_circles(context, width, height):
    # Reset the visible area with a black color.
    context.clear(0)
    # Split the visible area
    wthird = width // 3 - 1
    lw = 3
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, wthird, 0, wthird, height,
                               lw, 0xFFFFFFFF)
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, (2 * wthird + lw), 0,
                               (2 * wthird + lw), height, lw, 0xFFFFFFFF)
    for x in range(15):
        # In the first part, draw circles
        color = randint(0, 0xFFFFFFFF)
        x, y = randint(0, wthird), randint(0, height)
        r = randint(1, max(min(x, wthird - x), 2))
        sdl2.sdlgfx.circleColor(context.sdlrenderer, x, y, r, color)
        # In the second part, draw aa circles
        color = randint(0, 0xFFFFFFFF)
        x, y = randint(0, wthird), randint(0, height)
        r = randint(1, max(min(x, wthird - x), 2))
        sdl2.sdlgfx.aacircleColor(context.sdlrenderer, x + wthird + lw, y, r,
                                  color)
        # In the third part, draw filled circles
        color = randint(0, 0xFFFFFFFF)
        x, y = randint(0, wthird), randint(0, height)
        r = randint(1, max(min(x, wthird - x), 2))
        sdl2.sdlgfx.filledCircleColor(context.sdlrenderer, x + 2 * (wthird + lw),
                                      y, r, color)


# Draws random ellipsis using the passed rendering context
def draw_ellipsis(context, width, height):
    # Reset the visible area with a black color.
    context.clear(0)
    # Split the visible area
    wthird = width // 3 - 1
    eheight = height // 4
    lw = 3
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, wthird, 0, wthird, height,
                               lw, 0xFFFFFFFF)
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, (2 * wthird + lw), 0,
                               (2 * wthird + lw), height, lw, 0xFFFFFFFF)
    for x in range(15):
        # In the first part, draw ellipsis
        color = randint(0, 0xFFFFFFFF)
        x, y = randint(0, wthird), randint(0, height)
        rx, ry = randint(1, max(min(x, wthird - x), 2)), randint(0, eheight)
        sdl2.sdlgfx.ellipseColor(context.sdlrenderer, x, y, rx, ry, color)
        # In the second part, draw aa ellipsis
        color = randint(0, 0xFFFFFFFF)
        x, y = randint(0, wthird), randint(0, height)
        rx, ry = randint(1, max(min(x, wthird - x), 2)), randint(0, eheight)
        sdl2.sdlgfx.aaellipseColor(context.sdlrenderer, x + wthird + lw, y,
                                   rx, ry, color)
        # In the third part, draw filled ellipsis
        color = randint(0, 0xFFFFFFFF)
        x, y = randint(0, wthird), randint(0, height)
        rx, ry = randint(1, max(min(x, wthird - x), 2)), randint(0, eheight)
        sdl2.sdlgfx.filledEllipseColor(context.sdlrenderer,
                                       x + 2 * (wthird + lw), y, rx, ry,
                                       color)


# Draws random rectangles using the passed rendering context
def draw_rects(context, width, height):
    # Reset the visible area with a black color.
    context.clear(0)
    # Split the visible area
    whalf = width // 2 - 2
    hhalf = height // 2 - 2
    lw = 5
    x0, x1 = whalf, whalf
    y0, y1 = 0, height
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, x0, y0, x1, y1, lw,
                               0xFFFFFFFF)
    x0, x1 = 0, width
    y0, y1 = hhalf, hhalf
    sdl2.sdlgfx.thickLineColor(context.sdlrenderer, x0, y0, x1, y1, lw,
                               0xFFFFFFFF)
    for x in range(15):
        # In the first quadrant, draw normal rectangles
        color = randint(0, 0xFFFFFFFF)
        x0, x1 = randint(0, whalf), randint(0, whalf)
        y0, y1 = randint(0, hhalf), randint(0, hhalf)
        sdl2.sdlgfx.rectangleColor(context.sdlrenderer, x0, y0, x1, y1, color)
        # In the second quadrant, draw rounded rectangles
        color = randint(0, 0xFFFFFFFF)
        x0, x1 = randint(whalf + lw, width), randint(whalf + lw, width)
        y0, y1 = randint(0, hhalf), randint(0, hhalf)
        r = randint(0, max(x1 - x0, x0 - x1))
        sdl2.sdlgfx.roundedRectangleColor(context.sdlrenderer, x0, y0, x1, y1, r,
                                          color)
        # In the third quadrant, draw horizontal lines
        color = randint(0, 0xFFFFFFFF)
        x0, x1 = randint(0, whalf), randint(0, whalf)
        y0, y1 = randint(hhalf + lw, height), randint(hhalf + lw, height)
        sdl2.sdlgfx.boxColor(context.sdlrenderer, x0, y0, x1, y1, color)
        # In the fourth quadrant, draw vertical lines
        color = randint(0, 0xFFFFFFFF)
        x0, x1 = randint(whalf + lw, width), randint(whalf + lw, width)
        y0, y1 = randint(hhalf + lw, height), randint(hhalf + lw, height)
        r = randint(0, max(x1 - x0, x0 - x1))
        sdl2.sdlgfx.roundedBoxColor(context.sdlrenderer, x0, y0, x1, y1, r,
                                    color)


def run():
    setup_logging(verbose=True)
    # You know those from the helloworld.py example.
    # Initialize the video subsystem, create a window and make it visible.
    sdl2.ext.init(joystick=True, controller=True)
    window = sdl2.ext.Window("sdlgfx drawing examples", size=(640, 480))
    window.show()

    log.info("Adding gamecontroller mappings")

    sdl2.SDL_GameControllerAddMappingsFromFile(b"gamecontrollerdb.txt")

    num_joysticks = sdl2.SDL_NumJoysticks()
    for i in range(num_joysticks):
        if sdl2.SDL_IsGameController(i) == sdl2.SDL_TRUE:
            print("Joystick {0} is controller".format(i))
            pad = sdl2.SDL_GameControllerOpen(i)
            # Get controller info
            print("Controller: {0}".format(sdl2.SDL_GameControllerName(pad)))
            # mapping = sdl2.SDL_GameControllerMapping(pad)
            # print("Controller mapping: {0}".format(mapping))

    renderflags = sdl2.render.SDL_RENDERER_SOFTWARE
    context = sdl2.ext.Renderer(window, flags=renderflags)

    # Retrieve and display renderer + available renderer info
    info = sdl2.render.SDL_RendererInfo()
    sdl2.SDL_GetRendererInfo(context.sdlrenderer, info)

    print("\nUsing renderer: {0}".format(info.name.decode('utf-8')))

    # A storage variable for the function we are currently on, so that we know
    # which function to execute next.
    curindex = 0
    draw_lines(context, 640, 480)
    # sdl2.sdlgfx.gfxPrimitivesSetFont()
    sdl2.sdlgfx.stringColor(context.sdlrenderer, 10, 10, b"Hello World", 0xFFFFFFFF)
    context.present()

    controller_events = (
        sdl2.SDL_CONTROLLERAXISMOTION,
        sdl2.SDL_CONTROLLERBUTTONDOWN,
        sdl2.SDL_CONTROLLERBUTTONUP,
        sdl2.SDL_CONTROLLERDEVICEADDED,
        sdl2.SDL_CONTROLLERDEVICEREMOVED,
        sdl2.SDL_CONTROLLERDEVICEREMAPPED,
    )

    # The event loop is nearly the same as we used in colorpalettes.py. If you
    # do not know, what happens here, take a look at colorpalettes.py for a
    # detailed description.
    running = True
    while running:
        events = sdl2.ext.get_events()
        if sdl2.ext.quit_requested(events):
            break
        for event in events:
            if event.type in controller_events:
                match event.type:
                    # case sdl2.SDL_CONTROLLERAXISMOTION:
                    #     print("Axis {0} moved to {1}".format(event.caxis.axis, event.caxis.value))
                    case sdl2.SDL_CONTROLLERBUTTONDOWN:
                        log.debug("Button {0} pressed".format(event.cbutton.button))
                    case sdl2.SDL_CONTROLLERBUTTONUP:
                        log.debug("Button {0} released".format(event.cbutton.button))
                    case sdl2.SDL_CONTROLLERDEVICEADDED:
                        log.debug("Controller added")
                    case sdl2.SDL_CONTROLLERDEVICEREMOVED:
                        log.debug("Controller removed")
                    case sdl2.SDL_CONTROLLERDEVICEREMAPPED:
                        log.debug("Controller remapped")

    sdl2.ext.quit()
    return 0


if __name__ == "__main__":
    sys.exit(run())
