"""Define the possible tile types used by a level."""

from enum import IntEnum


class TileType(IntEnum):
    """Represent the possible tiles inside a level."""

    FLOOR = 0
    WALL = 1
    HOME = 2
    CHEESE = 3
    TRAP = 4