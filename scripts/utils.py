"""Utilities."""

import os

import pygame
from pygame import Surface

BASE_IMG_PATH = "data/images/"


def load_image(path: str, color_key: tuple[int, int, int] = (0, 0, 0)) -> Surface:
    """Load image in pygame from path."""
    # we use convert to because it creates a more efficient way to
    # have the image in memory for rendering
    img: Surface = pygame.image.load(BASE_IMG_PATH + path).convert()
    # the color to use a background and to put to transparency
    img.set_colorkey(color_key)  # pure black
    return img


def load_images(path: str) -> list[Surface]:
    """Load all images in a directory."""
    # images in folder depend on them being in alphabetical order. For number, we pad with zeros so that the smallest numbers
    # are always at the begining
    images: list[Surface] = [load_image(path + "/" + img_name) for img_name in sorted(os.listdir(BASE_IMG_PATH + path))]
    return images
