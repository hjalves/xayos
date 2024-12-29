import math
from random import randrange

from sdl2 import sdlgfx


class Star:
    __slots__ = ["x", "y", "z", "id", "radius", "fill"]

    def __init__(self, x, y, z) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.radius = 1
        self.fill = 0


class StarField:
    def __init__(self, width, height, depth=32, num_stars=400, speed=0.05):
        self.fov = 180 * math.pi / 180
        self.view_distance = 0
        self.stars = []
        self.width = width
        self.height = height
        self.max_depth = depth
        self.z_speed = speed

        for x in range(num_stars):
            star = Star(
                x=randrange(-self.width, self.width),
                y=randrange(-self.height, self.height),
                z=randrange(0, self.max_depth),
            )
            self.stars.append(star)

    def set_speed(self, speed):
        self.z_speed = speed

    def draw(self, renderer):
        for star in self.stars:
            # Move the star closer to the screen.
            star.z -= self.z_speed
            star.radius = (1 - float(star.z) / self.max_depth) * 1.2
            star.fill = int((1 - float(star.z) / self.max_depth) * 255)

            # If the star has moved out of the screen, we reposition it far away.
            if star.z <= 0:
                star.x = randrange(-self.width, self.width)
                star.y = randrange(-self.height, self.height)
                star.z = self.max_depth
                star.radius = 0
                star.fill = 0

            # Transforms this 3D point to 2D using a perspective projection.
            factor = self.fov / (self.view_distance + star.z)
            x = int(star.x * factor + self.width / 2)
            y = int(-star.y * factor + self.height / 2)
            sdlgfx.pixelRGBA(renderer, x, y, star.fill, star.fill, star.fill, 255)
            # if star.radius > 1:
            #     sdlgfx.filledCircleRGBA(
            #         renderer, x, y, int(star.radius), star.fill, star.fill, star.fill, 255
            #     )
