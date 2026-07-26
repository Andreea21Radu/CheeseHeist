"""Temporary static level used while building the game foundation."""

from generation.tile_type import TileType


W = TileType.WALL
F = TileType.FLOOR
H = TileType.HOME
C = TileType.CHEESE
T = TileType.TRAP


SAMPLE_LEVEL = [
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, H, F, F, F, F, W, F, F, F, F, F, F, F, W, F, F, F, F, C, W],
    [W, W, W, W, W, F, W, F, W, W, W, W, W, F, W, F, W, W, W, F, W],
    [W, F, F, F, F, F, W, F, F, F, F, F, W, F, F, F, W, F, F, F, W],
    [W, F, W, W, W, W, W, W, W, W, W, F, W, W, W, W, W, F, W, W, W],
    [W, F, F, F, F, F, F, F, F, F, W, F, F, F, F, F, F, F, F, F, W],
    [W, W, W, W, W, F, W, W, W, F, W, W, W, W, W, F, W, W, W, F, W],
    [W, F, F, F, F, F, W, F, F, F, F, F, F, F, W, F, F, F, F, F, W],
    [W, F, W, W, W, W, W, F, W, W, W, W, W, F, W, W, W, W, W, F, W],
    [W, F, F, F, T, F, F, F, W, F, F, F, F, F, F, F, F, T, W, F, W],
    [W, W, W, F, W, W, W, W, W, F, W, W, W, W, W, W, W, F, W, F, W],
    [W, F, F, F, F, F, F, F, F, F, W, F, F, F, F, F, F, F, W, F, W],
    [W, F, W, W, W, W, W, W, W, W, W, F, W, W, W, W, W, W, W, F, W],
    [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
]