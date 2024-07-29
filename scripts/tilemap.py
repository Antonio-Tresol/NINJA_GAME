"""Tilemap module."""

from pygame import Rect, Surface

# aliases
Vector2D = tuple[float, float] | list[float] | list[int] | tuple[int, int]
Tile = dict[str, str | int | tuple[float, float]]
# for physics and collisions with the player, one efficient way to do it is to know what are the
# neighboring tile to the player and only simulate collision with those. (take care if the sprite for the player
# is bigger)
NEIGHBOR_OFFSET: list[tuple[float, float]] = [
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
    (1, 0),
    (0, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]
# a set to store the tile type we want to have physics, sets use the
PHYSICS_TILES: set[str] = {"grass", "stone"}


class Tilemap:
    """Tile map class."""

    def __init__(self, game, tile_size: int = 16) -> None:  # noqa: ANN001
        """Init tilemap."""
        self.game = game
        self.tile_size = tile_size
        # The tilemap is implemented as a dictionary to efficiently store and access the tiles.
        # Unlike a matrix approach (where tiles might be represented by 1s and empty spaces by 0s),
        # a dictionary allows for sparse storage. This means we only store entries for tiles that exist,
        # which is more memory-efficient and simplifies saving/loading the map.
        #
        # This dictionary will be the primary structure for handling physics interactions within the game,
        # as it allows for quick lookups and updates of tile states based on their grid coordinates.
        #
        # The keys in this dictionary represent the grid coordinates (x, y) of each tile. Given that each
        # tile has a fixed size (16x16 pixels in this case), rendering the tiles requires converting these
        # grid coordinates into pixel coordinates. This conversion is straightforward: multiply the grid
        # coordinates by the tile size to determine the pixel coordinates of the tile's top-left corner.
        # This approach simplifies the rendering process and aligns with how we handle physics and other
        # game mechanics based on the tilemap.
        self.tilemap: dict = {}
        # things that are all over the place that might no line up with the grid
        # they will be the dictionary {type, variant, pos (already in pixels)}
        # we mostly use off grid tiles for decor
        self.offgrid_tiles = []
        # creating some tiles
        for i in range(10):
            # tile will be save as a map, we could make an object for this
            # horizontal line of grass variant 1 at y = 10, x from 3 to 13
            self.tilemap[str(3 + i) + ";10"] = {"type": "grass", "variant": 1, "pos": (3 + i, 10)}
            # vertical line of stone variant 1 at x = 10 and y from 5 to 15
            self.tilemap["10;" + str(5 + i)] = {"type": "stone", "variant": 1, "pos": (10, 5 + i)}

    def tiles_around(self, position: Vector2D) -> list:
        """Get the tiles around a tile."""
        tiles: list = []
        # be careful when rounding grid and position, we use interger division here to ensure a expected behavior
        tile_location = (int(position[0] // self.tile_size), int(position[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSET:
            check_loc = str(tile_location[0] + offset[0]) + ";" + str(tile_location[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def physics_rects_around(self, position: Vector2D) -> list[Rect]:
        """Return the tiles as pygame Rects for physics."""
        # remember that rect receives left, top, width and heigh, the position will be the pixel position, that's why
        # we are multiplying the grid position by the tile size to get the actual pixel position tha we need to render.
        return [
            Rect(tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size, self.tile_size, self.tile_size)
            for tile in self.tiles_around(position)
            if tile["type"] in PHYSICS_TILES
        ]

    def render(self, surface: Surface, offset: Vector2D = (0, 0)) -> None:
        """Render tilemap and offgrid tiles."""
        for tile in self.offgrid_tiles:
            surface.blit(
                source=self.game.assets[tile["type"]][tile["variant"]],
                dest=(
                    tile["pos"][0] - offset[0],
                    tile["pos"][1] - offset[1],
                ),  # here we apply the offset, negative because so that everythin in the screen moves to the left
            )
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            # we multiply by the tile size to get the tiles in terms of pixels, because they are in terms of grids
            surface.blit(
                source=self.game.assets[tile["type"]][tile["variant"]],
                dest=(tile["pos"][0] * self.tile_size - offset[0], tile["pos"][1] * self.tile_size - offset[1]),
            )
