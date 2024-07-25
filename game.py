"""Ninja game main script."""

import sys

import pygame
from pygame import Surface

from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images

# aliases
Color = tuple[int, int, int]
Point2D = list[float]
# color constants
skycolor: Color = (14, 219, 248)
collision_color: Color = (0, 100, 225)
not_collision_color: Color = (0, 50, 155)
# game constants
JUMP_SPEED = -3
SPEED: float = 5
LEFT_AXIS_THRESHOLD: float = -0.4
RIGHT_AXIS_THRESHOLD: float = 0.4
# screen constants
SCREEN_SIZE: tuple[int, int] = (640, 480)
# display size will be half the screen size to keep the proportions
DISPLAY_SIZE: tuple[int, int] = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)


class Game:
    """a game wrapper."""

    def __init__(self) -> None:
        """Init the game object."""
        # this init the pygame module
        pygame.init()
        # to init joystick (controller, gamepad)
        pygame.joystick.init()
        self.joystics = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        # here we give a name to the game
        pygame.display.set_caption("Ninja Game")
        # create window (surface is an object representing images in pygame)
        # coordinates system right is positive x and down is positive y
        self.screen: Surface = pygame.display.set_mode(size=SCREEN_SIZE)
        # set custom icons to game
        pygame.display.set_icon(pygame.image.load("data/images/icon.png").convert())
        # the actual render display, half resolutions of screen
        # we are going to draw here and the scale it up to the screen, pixel art effect
        self.display = pygame.Surface(size=DISPLAY_SIZE)  # empty, image of this dimension
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.assets: dict[str, Surface | list[Surface]] = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "stone": load_images("tiles/stone"),
            "large_decor": load_images("tiles/large_decor"),
            "player": load_image("entities/player.png"),
        }

        self.player = PhysicsEntity(game=self, entity_type="player", position=(50, 50), size=(8, 15))
        self.tilemap = Tilemap(game=self, tile_size=16)

    def run(self) -> None:  # noqa: C901, PLR0912
        """Run game loop."""
        # a game loop: the game everyframe, there can be multiple game loop running simultaneusly
        # each frame is an iteration in the loop
        while True:
            self.display.fill(color=skycolor)
            self.tilemap.render(surface=self.display)
            # we only want to update x, not y, because platformer
            self.player.update(
                tilemap=self.tilemap,
                movement=(self.movement[1] - self.movement[0], 0),
            )
            self.player.render(surface=self.display)
            for event in pygame.event.get():
                # events have types, so that's how we know what happen
                # print event
                if event.type == pygame.QUIT:
                    # to quit the game we quit pygame and we close the app
                    pygame.quit()
                    sys.exit()
                # all buttons game pad events, see https://www.pygame.org/docs/ref/joystick.html for more reference
                # keydown doesn't mean something is being pressed continuosly, combining keydown and key up we can get
                # holding behavior
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        # override vertical velocity to jump
                        self.player.velocity[1] = JUMP_SPEED
                # when the key lifts
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                # using the dpad
                if event.type == pygame.JOYHATMOTION:
                    if event.value == (-1, 0):  # left
                        self.movement[0] = True
                    if event.value == (1, 0):
                        self.movement[1] = True  # right
                    if event.value == (0, 0):
                        self.movement = [False, False]

                # using the joysticks (axis 0 is left right of Left Axis, axis 1 is right of left axis)
                if event.type == pygame.JOYAXISMOTION and event.axis == 0:
                    print(event)
                    if event.value < LEFT_AXIS_THRESHOLD:  # axis moved to the left
                        self.movement[0] = True
                        self.movement[1] = False
                    elif event.value > RIGHT_AXIS_THRESHOLD:  # axis moved to the right
                        self.movement[1] = True
                        self.movement[0] = False
                    else:
                        self.movement[0] = False
                        self.movement[1] = False

                if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    # jump by overriding the vertical velocity
                    self.player.velocity[1] = JUMP_SPEED
            # we render the display scale up into the screen, for that we use pygame.transform.scale
            self.screen.blit(
                source=pygame.transform.scale(surface=self.display, size=self.screen.get_size()),
                dest=(0, 0),
            )
            # updates the screen, if we do not call this, the changes we made to the screen won't be displayed
            pygame.display.update()
            # dynamic sleep, it sleeps as long as it need to mantain the 60fps
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
