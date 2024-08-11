"""Utilities."""

import os

import pygame
from pygame import Surface

BASE_IMG_PATH = "data/images/"


def load_image(path: str, color_key: tuple[int, int, int] = (0, 0, 0)) -> Surface:
    """Load image in pygame from path.

    Returns
    -------
    a Surface with the Image

    """
    # we use convert to because it creates a more efficient way to
    # have the image in memory for rendering
    img: Surface = pygame.image.load(BASE_IMG_PATH + path).convert()
    # the color to use a background and to put to transparency
    img.set_colorkey(color_key)  # pure black
    return img


def load_images(path: str) -> list[Surface]:
    """Load all images in a directory.

    Returns
    -------
    a list of surfaces with the images

    """
    # images in folder depend on them being in alphabetical order. For number, we pad with zeros so that the smallest
    # numbers are always at the begining
    images: list[Surface] = [load_image(path + "/" + img_name) for img_name in sorted(os.listdir(BASE_IMG_PATH + path))]
    return images


# pygame doesn't have a animation object by default
class Animation:
    """An animation class."""

    def __init__(self, images: list[Surface], image_duration: int = 5, loop: bool = True) -> None:  # noqa: FBT001, FBT002
        """Init basic animation class."""
        # each image will be displayed the same amount of time, it can be done in other ways.
        self.images = images
        self.image_duration = image_duration
        self.loop = loop
        # specific to an individual animation
        self.done: bool = False  # to keep track if the animation has finished
        self.frame: int = 0  # frame of the game
        self.total_animation_frames: int = self.image_duration * len(self.images)

    def copy(self) -> "Animation":
        """Copy animation object.

        Returns
        -------
        a copy of itself. Images are a reference.

        """
        return Animation(self.images, self.image_duration, self.loop)

    def update(self) -> None:
        """Update the animation object."""
        if self.loop:
            # goes to the maximum frame per animation and loops around
            self.frame = (self.frame + 1) % self.total_animation_frames
        else:
            # we substract one so that we do not get pass the animation frames
            self.frame = min(self.frame + 1, self.total_animation_frames - 1)
            if self.frame >= self.total_animation_frames - 1:
                self.done = True

    def img(self) -> Surface:
        """Get animation image.

        Returns
        -------
        Surface with the current image of the animation.

        """
        return self.images[int(self.frame / self.image_duration)]
