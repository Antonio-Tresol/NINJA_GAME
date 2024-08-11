"""Physics Entity."""

from typing import TYPE_CHECKING

import pygame
from pygame import Rect, Surface

from scripts.tilemap import Tilemap

if TYPE_CHECKING:
    from game import Game
    from scripts.utils import Animation

# aliases
Vector2D = tuple[float, float] | list[float] | list[int] | tuple[int, int]
TERMINAL_VELOCITY: float = 5
DELTA_VELOCITY_PER_FRAME: float = 0.1


class PhysicsEntity:
    """A Physics entity class."""

    def __init__(self, game: "Game", entity_type: str, position: tuple[float, float], size: tuple[int, int]) -> None:
        """Init class."""
        self.game = game
        self.type = entity_type
        # the position is the top (position[0], -left (position[1]) of our entity
        # also the position[0] is the x axis, the position[1] is the y axis
        self.position = list(position)  # to ensure that each entity has its own
        # the size of the entity
        # remember that size [1] is height, size [0] is width
        self.size = size
        # rate of change in the position, acceleration is the rate of change in velocity
        self.velocity: list[float] = [0, 0]
        # usually acceleration is a constant (gravity)
        # to keep track of which collisions we had, it is useful for wall jumping to.
        self.collisions: dict[str, bool] = {"up": False, "down": False, "left": False, "right": False}

        # our animation is a state machine essentially
        self.action: str = ""
        # h-acky: the object that you are animating might have different dimensions, so you add padding to the edges
        # of you images. The animation will overflow the hitbox of the entity
        self.animation_offset: tuple[int, int] = (-3, -3)
        # to make the player look right or left, as we only have our animation facing one way, we
        # flip them to have both sides
        self.flip: bool = False
        self.set_action("idle")

    def rect(self) -> Rect:
        """Get a pygame Rect object with the dimensions an position of the player for collision purposes.

        Returns
        -------
            Rect: a rectangle object with the position and size of the player.

        """
        # better to build the new all the time than updating it
        return Rect(self.position[0], self.position[1], self.size[0], self.size[1])

    def set_action(self, action: str) -> None:
        """Set the action of the physics entity."""
        if action != self.action:
            # we only want to create a new instance of the animation when
            # when we are actually changing state, so that the object keeps track
            # of the frame and all the that stuff
            self.action = action
            self.animation: Animation = self.game.assets[f"{self.type}/{self.action}"].copy()

    def update(self, tilemap: Tilemap, movement: Vector2D = (0, 0)) -> None:  # noqa: C901
        """Update physics entity position."""
        # reset collisions dictionary
        self.collisions = {"up": False, "down": False, "right": False, "left": False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        # we do the position update in two dimensions, separately. This is useful to know what was
        # collide with and to act accordingly.
        # move first, then make rectangle, then check collision in right and left, based on that update position.
        self.position[0] += frame_movement[0]
        entity_rect = self.rect()
        # handle if the collision was from moving left and right
        for rect in tilemap.physics_rects_around(self.position):
            if entity_rect.colliderect(rect):
                # we had a collision, so handle
                # first case I moved right and i collided with a tile, so:
                # snap the entity right "border" to the left "border" of the tile
                if frame_movement[0] > 0:  # remember positive x frame movement means right
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                # second case I moved left and I collided with a tile, so:
                # snap the entity left "border" to the right "border" of the tile
                if frame_movement[0] < 0:  # remember negative x frame movement means left
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                # here we only updated the rect position, we need to update the player position.
                # player position should be a tuple of float to allow to subpixel position, even when
                # with rendering it will default to int, saving the subpixel increments is useful. We can
                # get that functionality with FRect in pygame-ce. So to do not use the extra pos list.
                # Update the entity's position to match the resolved collision position
                self.position[0] = entity_rect.x
        # first move, then make a rect, then check collision up and down, then update position.
        self.position[1] += frame_movement[1]
        # we make a new rect because the old one might be outdated
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.position):
            if entity_rect.colliderect(rect):
                # if we collided while going down, entity bottom will be rect top
                if frame_movement[1] > 0:  # remember positive y frame movement means down
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                # if we collided while going up, entity top will be rect bottom
                if frame_movement[1] < 0:  # remember negative y frame movement means up
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                # Update the entity's position to match the resolved collision position
                self.position[1] = entity_rect.y
        # we apply acceleration by modifying velocity
        # here we use terminal velocity
        # update y velocity
        self.velocity[1] = min(TERMINAL_VELOCITY, self.velocity[1] + DELTA_VELOCITY_PER_FRAME)
        # reset velocity if we collided with the ground or the floor
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0
        # updating the animation
        if movement[0] > 0:  # we are moving right
            self.flip = False
        if movement[0] < 0:  # we are moving left
            self.flip = True
        self.animation.update()

    def render(self, surface: Surface, offset: Vector2D) -> None:
        """Render the physics entity into the surface."""
        # we apply offset negatively to move the things in the opposite direction to the where the camera is moving
        # then we apply the animation offset to pad
        surface.blit(
            pygame.transform.flip(self.animation.img(), flip_x=self.flip, flip_y=False),
            (
                self.position[0] - offset[0] + self.animation_offset[0],
                self.position[1] - offset[1] + self.animation_offset[1],
            ),
        )


JUMP_ANIMATION_THRESHOLD: int = 4
MAX_CONSECUTIVE_JUMPS: int = 2


class Player(PhysicsEntity):
    """A player object."""

    def __init__(self, game: "Game", position: tuple[float, float], size: tuple[int, int]) -> None:
        """Init a Player object."""
        super().__init__(game, "player", position, size)
        # to keep track of how long have we been in the air
        self.air_time: int = 0

    def update(self, tilemap: Tilemap, movement: Vector2D = (0, 0)) -> None:
        """Update player position and state."""
        super().update(tilemap=tilemap, movement=movement)
        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jump_count = 0

        if self.air_time > JUMP_ANIMATION_THRESHOLD:  # if you've been in the air for a while, jump animation
            self.set_action("jump")
        elif movement[0] != 0:  # we are running, cause our x movement is not 0
            # takes priority over jump
            self.set_action("run")
        else:  # idle probably
            self.set_action("idle")
