"""Ninja game main script."""

import sys

import pygame
from pygame import Surface

# aliases
Color = tuple[int, int, int]
Point2D = list[float]
# color constants
skycolor: Color = (14, 219, 248)
collision_color: Color = (0, 100, 225)
not_collision_color: Color = (0, 50, 155)
# game constants
speed: int = 5


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
        self.screen: Surface = pygame.display.set_mode(size=(640, 480))

        # clock to restric the framerate latter (we are going to use this instead of delta time, because of math)
        self.clock = pygame.time.Clock()
        # to load an image we use pygame.image.load, it works with png and other formats
        self.img: Surface = pygame.image.load("data/images/clouds/cloud_1.png")
        # to replace a color from the image with transparency we use set_colorkey, receive the color as a list
        # or a tuple
        self.img.set_colorkey((0, 0, 0))
        self.img_pos = [160, 260]
        self.movement = [False, False]
        # for collision detection (left, top, width, height)
        # for some reason name parameter doesn't work, so each time try if name parameters work or not
        self.collision_area = pygame.Rect(50, 50, 300, 50)

    def run(self) -> None:  # noqa: C901, PLR0912
        """Run game loop."""
        # a game loop: the game everyframe, there can be multiple game loop running simultaneusly
        # each frame is an iteration in the loop
        while True:
            self.screen.fill(color=skycolor)
            
            # creates a collision rectangle for the cloud, used for collision detection
            img_r = pygame.Rect(self.img_pos[0], self.img_pos[1], self.img.get_width(), self.img.get_height())
            # check if two rectangles overlap in this frame
            if img_r.colliderect(self.collision_area):
                pygame.draw.rect(self.screen, collision_color, self.collision_area, border_radius=10)
            else:
                pygame.draw.rect(self.screen, not_collision_color, self.collision_area, border_radius=10)

            # making our image move, we do this trick of movement 1- movement 0 to ensure that
            # if both are true, we do not move
            self.img_pos[1] += (self.movement[1] - self.movement[0]) * speed
            # blit function draws/merges an image (surface object in pygame) into another one
            # in gpu base rendering it is not this way.
            # see https://en.wikipedia.org/wiki/Bit_blit for more reference on blit as a computer graphics operation
            #  dest = (coordinates x, y) top left is 0, 0.
            self.screen.blit(source=self.img, dest=self.img_pos)
            # if we do like this, the images will keep merging into each other if we move them
            # so remember to clear the screen each time
            # pygame even is the event handler (button press, mouse, touch types, resize)

            # in pygame, layering is done  in the order we put things in the screen, so as we put the rectangles first 
            # and the cloud then, the cloud, when moved, will appear in front of the rectangle
            # when working with objects is great idea to separate update and rendering of an object
            for event in pygame.event.get():
                # events have types, so that's how we know what happen
                # print event)
                if event.type == pygame.QUIT:
                    # to quit the game we quit pygame and we close the app
                    pygame.quit()
                    sys.exit()
                # all buttons game pad events, see https://www.pygame.org/docs/ref/joystick.html for more reference
                # keydown doesn't mean something is being pressed continuosly, combining keydown and key up we can get
                # holding behavior
                if event.type == pygame.KEYDOWN:
                    print(event)
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                # when the key lifts
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False
                # using the dpad
                if event.type == pygame.JOYHATMOTION:
                    print(event)
                    if event.value == (0, 1):
                        self.movement[0] = True
                    if event.value == (0, -1):
                        self.movement[1] = True
                    if event.value == (0, 0):
                        self.movement = [False, False]
                """
                if event.type in [pygame.JOYBUTTONDOWN, pygame.KEYDOWN]:
                    print(f"key down: {event}")
                # the joysticks of the game pad and the triggers
                if event.type == pygame.JOYAXISMOTION:
                    print(f"Joystick motion: {event}")
                # the dpad
                if event.type == pygame.JOYHATMOTION:
                    print(f"Dpad action: {event}")
                """
            # updates the screen, if we do not call this, the changes we made to the screen won't be displayed
            pygame.display.update()
            # dynamic sleep, it sleeps as long as it need to mantain the 60fps
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
