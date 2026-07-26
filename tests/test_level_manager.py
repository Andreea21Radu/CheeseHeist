"""Tests for the level grid representation."""

import pytest

from generation.level_manager import LevelManager
from generation.tile_type import TileType


def create_test_level() -> LevelManager:
    """Create a small level used by multiple tests."""

    grid = [
        [
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.HOME,
            TileType.FLOOR,
            TileType.CHEESE,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.FLOOR,
            TileType.TRAP,
            TileType.FLOOR,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
        ],
    ]

    return LevelManager(grid)


def test_level_dimensions_are_detected() -> None:
    """The manager should store the correct grid dimensions."""

    level = create_test_level()

    assert level.rows == 4
    assert level.columns == 5


def test_position_inside_grid_is_detected() -> None:
    """Valid coordinates should be recognized as inside the grid."""

    level = create_test_level()

    assert level.is_inside_grid((1, 1))
    assert level.is_inside_grid((3, 4))


def test_position_outside_grid_is_detected() -> None:
    """Invalid coordinates should be rejected."""

    level = create_test_level()

    assert not level.is_inside_grid((-1, 0))
    assert not level.is_inside_grid((0, -1))
    assert not level.is_inside_grid((4, 0))
    assert not level.is_inside_grid((0, 5))


def test_wall_is_not_walkable() -> None:
    """The mouse should not be able to enter a wall tile."""

    level = create_test_level()

    assert not level.is_walkable((0, 0))


def test_gameplay_tiles_are_walkable() -> None:
    """Floor, home, cheese and trap tiles should be traversable."""

    level = create_test_level()

    assert level.is_walkable((1, 1))
    assert level.is_walkable((1, 2))
    assert level.is_walkable((1, 3))
    assert level.is_walkable((2, 2))


def test_neighbors_only_include_walkable_tiles() -> None:
    """Neighbor retrieval should ignore walls and invalid positions."""

    level = create_test_level()

    neighbors = level.get_neighbors((1, 2))

    assert (1, 1) in neighbors
    assert (1, 3) in neighbors
    assert (2, 2) in neighbors
    assert (0, 2) not in neighbors


def test_find_tile_returns_correct_position() -> None:
    """The manager should find unique level elements."""

    level = create_test_level()

    assert level.find_tile(TileType.HOME) == (1, 1)
    assert level.find_tile(TileType.CHEESE) == (1, 3)


def test_get_tile_rejects_invalid_position() -> None:
    """Reading outside the grid should raise an error."""

    level = create_test_level()

    with pytest.raises(IndexError):
        level.get_tile((10, 10))


def test_invalid_grid_shape_is_rejected() -> None:
    """Rows with different lengths should not create a valid level."""

    invalid_grid = [
        [TileType.WALL, TileType.WALL],
        [TileType.WALL],
    ]

    with pytest.raises(ValueError):
        LevelManager(invalid_grid)


def test_text_representation_is_generated() -> None:
    """The level should produce a readable ASCII representation."""

    level = create_test_level()

    expected_text = (
        "#####\n"
        "#H.C#\n"
        "#.T.#\n"
        "#####"
    )

    assert level.to_text() == expected_text