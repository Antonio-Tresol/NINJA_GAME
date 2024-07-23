"""Tile map module."""

from pygame import Surface


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
        self.tilemap = {}
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

    def render(self, surface: Surface) -> None:
        """Render tilemap and offgrid tiles."""
        for tile in self.offgrid_tiles:
            surface.blit(
                source=self.game.assets[tile["type"]][tile["variant"]],
                dest=tile["pos"],
            )
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            # we multiply by the tile size to get the tiles in terms of pixels, because they are in terms of grids
            surface.blit(
                source=self.game.assets[tile["type"]][tile["variant"]],
                dest=(tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size),
            )
