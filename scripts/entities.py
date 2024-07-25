"""Physics Entity."""

from pygame import Rect, Surface

from scripts.tilemap import Tilemap

TERMINAL_VELOCITY = 5
DELTA_VELOCITY_PER_FRAME = 0.1


class PhysicsEntity:
    """A Physics entity class."""

    def __init__(self, game, entity_type: str, position: tuple[float, float], size: tuple[int, int]) -> None:  # noqa: ANN001
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
        self.velocity = [0, 0]
        # usually acceleration is a constant (gravity)
        # to keep track of which collisions we had, it is useful for wall jumping to.
        self.collisions: dict[str, bool] = {"up": False, "down": False, "left": False, "right": False}

    def rect(self) -> Rect:
        """Get a pygame Rect object with the dimensions an position of the player for collision purposes."""
        # better to build the new all the time than updating it
        return Rect(self.position[0], self.position[1], self.size[0], self.size[1])

    def update(self, tilemap: Tilemap, movement: tuple[float, float] = (0, 0)) -> None:
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
                # update player position
                self.position[1] = entity_rect.y
        # we apply acceleration by modifying velocity
        # here we use terminal velocity
        # update y velocity
        self.velocity[1] = min(TERMINAL_VELOCITY, self.velocity[1] + DELTA_VELOCITY_PER_FRAME)
        # reset velocity if we collided with the ground or the floor
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0

    def render(self, surface: Surface) -> None:
        """Render the physics entity into the surface."""
        surface.blit(self.game.assets["player"], dest=self.position)
