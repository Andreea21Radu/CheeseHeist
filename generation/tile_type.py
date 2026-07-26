"""Tile types used inside a Cheese Heist level."""

from enum import IntEnum


class TileType(IntEnum):
    """Represent every type of cell that can appear in the grid."""

    WALL = 0
    FLOOR = 1
    HOME = 2
    CHEESE = 3
    TRAP = 4