"""Clouds module."""

import random

from pygame import Surface

Vector2D = tuple[float, float] | list[float] | list[int] | tuple[int, int]


class Cloud:
    """Cloud object."""

    def __init__(self, position: Vector2D, img: Surface, speed: float, depth: float) -> None:
        """Init cloud object."""
        self.position: list[float] = list(position)
        self.img: Surface = img
        self.depth: float = depth
        self.speed: float = speed

    def update(self) -> None:
        """Update position of cloud."""
        self.position[0] += self.speed

    def render(self, surface: Surface, offset: Vector2D) -> None:
        """Render."""
        # here we use the depth to creat a parallax effect see: https://en.wikipedia.org/wiki/Parallax_scrolling
        # to know more about parallax effect, essentially we are making the cloud move slower to give a sense of
        # depth and layers.
        # we apply offset negatively to move the things in the opposite direction to the where the camera is moving
        render_position: tuple[float, float] = (
            self.position[0] - offset[0] * self.depth,
            self.position[1] - offset[1] * self.depth,
        )
        # Here we use the modulo operator for looping.
        # We use modulo so that when the image goes out of the screen in width, it reappears on the other end.
        # We add the img.get_width() to ensure the image is fully out of the screen before teleporting to the other end.
        surface.blit(
            source=self.img,
            dest=(
                render_position[0] % (surface.get_width() + self.img.get_width()) - self.img.get_width(),
                render_position[1] % (surface.get_height() + self.img.get_height()) - self.img.get_height(),
            ),
        )


class Clouds:
    """Cloud collection object."""

    def __init__(self, cloud_images: list[Surface], count: int = 16) -> None:
        """Init the cloud collection."""
        self.clouds: list[Cloud] = [
            Cloud(
                position=(random.random() * 99999, random.random() * 9999),
                img=random.choice(cloud_images),
                speed=random.random() * 0.05 + 0.05,  # max speed would be 0.1 and min is 0.05
                depth=random.random() * 0.6 + 0.2,  # max depth would be 0.8 and min depth will be 0.2
            )
            for _ in range(count)
        ]
        # to push the clouds closest to the camera are push to the front.
        self.clouds.sort(key=lambda cloud: cloud.depth)

    def update(self) -> None:
        """Update clouds position."""
        for cloud in self.clouds:
            cloud.update()

    def render(self, surface: Surface, offset: Vector2D = (0, 0)) -> None:
        """Render the cloud collection."""
        for cloud in self.clouds:
            cloud.render(surface=surface, offset=offset)
