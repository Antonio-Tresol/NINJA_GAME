"""A level editor for the ninja game."""

import sys

import pygame
from pygame import Surface

from scripts.tilemap import Tilemap
from scripts.utils import load_images

Vector2D = tuple[float, float] | list[float] | list[int] | tuple[int, int]
# screen constants
SCREEN_SIZE: tuple[int, int] = (640, 480)
# display size will be half the screen size to keep the proportions
DISPLAY_SIZE: tuple[int, int] = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
SCROLL_STEP: float = 30

RENDER_SCALE: float = 2.0
# button constans
LEFT_CLICK: int = 1
MOUSE_WHEEL_CLICK: int = 2
RIGHT_CLICK: int = 3
MOUSE_WHEEL_SCROLL_UP: int = 4
MOUSE_WHEEL_SCROLL_DOWN: int = 5


class Editor:
    """a game tile editor."""

    def __init__(self) -> None:
        """Init the level editor object."""
        # this init the pygame module
        pygame.init()
        # to init joystick (controller, gamepad)
        # here we give a name to the game
        pygame.display.set_caption("Ninja Game Level Editor")
        # create window (surface is an object representing images in pygame)
        # coordinates system right is positive x and down is positive y
        self.screen: Surface = pygame.display.set_mode(size=SCREEN_SIZE)
        # set custom icons to game
        pygame.display.set_icon(pygame.image.load("data/images/icon.png").convert())
        # the actual render display, half resolutions of screen
        # we are going to draw here and the scale it up to the screen, pixel art effect
        self.display = pygame.Surface(size=DISPLAY_SIZE)  # empty, image of this dimension
        self.clock = pygame.time.Clock()
        # to allow the camera to move in every direction
        self.movement: list[bool] = [False, False, False, False]
        # this dictionary has key str and value Surface or list[Surface], be mindfull of that
        self.assets: dict = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "stone": load_images("tiles/stone"),
            "large_decor": load_images("tiles/large_decor"),
        }
        self.tilemap = Tilemap(game=self, tile_size=16)
        # illusion of a camera, moving things in the world moves this around
        # cameras location, we apply it as an offset to everything we are rendering in the screen
        # for us the scroll is the camera position
        self.scroll: list[float] = [0, 0]

        # for the tile editor
        self.tile_list: list[str] = list(self.assets)
        self.tile_list_size = len(self.tile_list)
        self.tile_group: int = 0  # which ground are we using
        self.tile_variant: int = 0  # which tile in the group are we using
        # to handle mouse input
        self.clicking: bool = False
        self.right_clicking: bool = False
        self.shift: bool = False
        self.variants_count = {tile_group_name: len(self.assets[tile_group_name]) for tile_group_name in self.tile_list}

    def run(self) -> None:  # noqa: C901, PLR0912, PLR0915
        """Run the editor loop."""
        while True:
            # Fill the display with black color
            self.display.fill((0, 0, 0))

            # Get the current tile image based on the selected tile group and variant
            current_tile_img: Surface = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()

            # Calculate the scroll offset
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Render the tilemap with the current scroll offset
            self.tilemap.render(surface=self.display, offset=render_scroll)

            # Get the current mouse position and scale it down by the render scale factor
            mouse_position: Vector2D = pygame.mouse.get_pos()
            mouse_position: Vector2D = (mouse_position[0] / RENDER_SCALE, mouse_position[1] / RENDER_SCALE)

            # Calculate the tile grid position based on the mouse position and scroll offset
            tile_position: Vector2D = (
                int((mouse_position[0] + self.scroll[0]) // self.tilemap.tile_size),
                int((mouse_position[1] + self.scroll[1]) // self.tilemap.tile_size),
            )

            # Set some transparency to the current tile image
            current_tile_img.set_alpha(100)

            # Show a preview of where the tile would be placed
            self.display.blit(
                source=current_tile_img,
                # the following math is to render the image from the top left corner of the tile position
                # taking into accoun the position of the camera (scroll
                dest=(
                    tile_position[0] * self.tilemap.tile_size - self.scroll[0],
                    tile_position[1] * self.tilemap.tile_size - self.scroll[1],
                ),
            )

            # Add tile if the left mouse button is clicked
            if self.clicking:
                self.tilemap.tilemap[f"{tile_position[0]};{tile_position[1]}"] = {
                    "type": self.tile_list[self.tile_group],
                    "variant": self.tile_variant,
                    "pos": tile_position,
                }

            # Delete tile if the right mouse button is clicked
            if self.right_clicking:
                tile_location: str = f"{tile_position[0]};{tile_position[1]}"
                if tile_location in self.tilemap.tilemap:
                    del self.tilemap.tilemap[f"{tile_position[0]};{tile_position[1]}"]

            self.display.blit(source=current_tile_img, dest=(5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # to quit the game we quit pygame and we close the app
                    sys.exit()
                # activation of a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == LEFT_CLICK:  # left button click
                        self.clicking = True
                    if event.button == RIGHT_CLICK:  # right button click
                        self.right_clicking = True

                    if self.shift:  # we are holding shift so within the group go around tile variants
                        if event.button == MOUSE_WHEEL_SCROLL_UP:  # mouse wheel up
                            self.tile_variant = (self.tile_variant - 1) % self.variants_count[
                                self.tile_list[self.tile_group]
                            ]
                        if event.button == MOUSE_WHEEL_SCROLL_DOWN:  # mouse wheel down
                            self.tile_variant = (self.tile_variant + 1) % self.variants_count[
                                self.tile_list[self.tile_group]
                            ]
                    else:  # we are changing group because we are not holding shift
                        # reset the tile variant, to do not have index errors:w
                        if event.button == MOUSE_WHEEL_SCROLL_UP:  # mouse wheel up
                            self.tile_group = (self.tile_group - 1) % self.tile_list_size
                            self.tile_variant = 0
                        if event.button == MOUSE_WHEEL_SCROLL_DOWN:  # mouse wheel down
                            self.tile_group = (self.tile_group + 1) % self.tile_list_size
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == LEFT_CLICK:
                        self.clicking = False
                    if event.button == RIGHT_CLICK:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    if event.key in {pygame.K_LSHIFT, pygame.K_RSHIFT}:
                        self.shift = True

                # when the key lifts
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False
                    if event.key in {pygame.K_LSHIFT, pygame.K_RSHIFT}:
                        self.shift = False

            self.screen.blit(
                source=pygame.transform.scale(surface=self.display, size=self.screen.get_size()),
                dest=(0, 0),
            )
            # updates the screen, if we do not call this, the changes we made to the screen won't be displayed
            pygame.display.update()
            # dynamic sleep, it sleeps as long as it need to mantain the 60fps
            self.clock.tick(60)


if __name__ == "__main__":
    Editor().run()
