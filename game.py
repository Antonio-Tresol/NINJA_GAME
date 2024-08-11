"""Ninja game main script."""

import sys

import pygame
from pygame import Surface

from scripts.clouds import Clouds
from scripts.entities import Player
from scripts.tilemap import Tilemap
from scripts.utils import Animation, load_image, load_images

# aliases
Color = tuple[int, int, int]
Vector2D = tuple[float, float] | list[float] | tuple[int, int] | list[int]
# color constants
skycolor: Color = (14, 219, 248)
collision_color: Color = (0, 100, 225)
not_collision_color: Color = (0, 50, 155)
# game constants
JUMP_SPEED: float = -3
SPEED: float = 5
LEFT_AXIS_THRESHOLD: float = -0.4
RIGHT_AXIS_THRESHOLD: float = 0.4
# screen constants
SCREEN_SIZE: tuple[int, int] = (640, 480)
# display size will be half the screen size to keep the proportions
DISPLAY_SIZE: tuple[int, int] = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
SCROLL_STEP: float = 30


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
        self.movement: list[bool] = [False, False]
        # this dictionary has key str and value Surface or list[Surface], be mindfull of that
        self.assets: dict = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "stone": load_images("tiles/stone"),
            "large_decor": load_images("tiles/large_decor"),
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "player/idle": Animation(images=load_images("entities/player/idle"), image_duration=6),
            "player/run": Animation(images=load_images("entities/player/run"), image_duration=4),
            "player/jump": Animation(images=load_images("entities/player/jump")),
            "player/slide": Animation(images=load_images("entities/player/slide")),
            "player/wall_slide": Animation(images=load_images("entities/player/wall_slide")),
        }
        # cloud collection
        self.clouds = Clouds(cloud_images=self.assets["clouds"], count=16)

        self.player = Player(game=self, position=(50, 50), size=(8, 15))
        self.tilemap = Tilemap(game=self, tile_size=16)
        # illusion of a camera, moving things in the world moves this around
        # cameras location, we apply it as an offset to everything we are rendering in the screen
        # for us the scroll is the camera position
        self.scroll: list[float] = [0, 0]

    def run(self) -> None:  # noqa: C901, PLR0912
        """Run game loop."""
        # a game loop: the game everyframe, there can be multiple game loop running simultaneusly
        # each frame is an iteration in the loop
        while True:
            self.display.blit(source=self.assets["background"], dest=(0, 0))
            # we want our camera to center the player smothly. We divide between the display width to adjust to the fact
            # that the player centerx is the top left of the player, by dividing by the display width we ensure the
            # player is at the center of the camera.
            # this formula is the first part is where we want the camera to be  minus the position where the camera is
            # that gives us how far the camera is to the point where we are right now, so we add that to the scroll x.
            # divinding by a scroll step gives us a smoth "adapting" of the camera to the position where we want it to
            # be.
            # So in a nutshell our "camera" or "viewport" is just moving everything a bit in some direction to always
            # have in this case the player at the middle of the screen.
            self.scroll[0] += (
                (self.player.rect().centerx - self.display.get_width() / 2) - self.scroll[0]
            ) / SCROLL_STEP
            # the process is equivalent for the y position of the camera
            self.scroll[1] += (
                (self.player.rect().centery - self.display.get_height() / 2) - self.scroll[1]
            ) / SCROLL_STEP
            # the approach before might cause some jittering due to subpixel movement, so we will transform everything
            # so we will transform to int an pass that, so that it is smoth for pixel art, not an issue for the camera
            # to use int

            render_scroll: Vector2D = (int(self.scroll[0]), int(self.scroll[1]))
            # we want the clouds to be render before/behind the tiles
            self.clouds.update()
            # the offset parameter is how much we move the object we are about to render
            self.clouds.render(surface=self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)
            # we only want to update x, not y, because platformer
            self.player.update(
                tilemap=self.tilemap,
                movement=(self.movement[1] - self.movement[0], 0),
            )
            self.player.render(surface=self.display, offset=render_scroll)
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
