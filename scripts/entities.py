"""Physics Entity."""

from pygame import Surface

from game import Game


class PhysicsEntity:
    """A Physics entity class."""

    def __init__(self, game: Game, e_type: str, pos: tuple[int, int], size: tuple[int, int]) -> None:
        """Init class."""
        self.game = game
        self.type = e_type
        self.pos = list(pos)  # to ensure that each entity has its own
        self.size = size
        # rate of change in the position, acceleration is the rate of change in velocity
        self.velocity = [0, 0]
        # usually acceleration is a constant (gravity)

    def update(self, movement: tuple[int, int] = (0, 0)) -> None:
        """Update physics entity position."""
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        # we do the position update in two dimensions
        self.pos[0] += frame_movement[0]
        self.pos[1] += frame_movement[1]

    def render(self, surface: Surface) -> None:
        """Render the physics entity into the surface."""
        surface.blit(self.game.assets["player"], dest=self.pos)
