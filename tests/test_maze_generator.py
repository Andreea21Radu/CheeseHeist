"""Tests for procedural maze generation."""

import pytest

from generation.maze_generator import MazeGenerator
from generation.tile_type import TileType


def test_generated_maze_has_correct_size() -> None:
    """The generated grid should preserve the requested dimensions."""

    generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=10,
    )

    level = generator.generate_maze()

    assert level.rows == 15
    assert level.columns == 21


def test_generated_maze_contains_one_home() -> None:
    """Every generated maze should contain one mouse home."""

    generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=10,
    )

    level = generator.generate_maze()

    homes = level.find_all_tiles(
        TileType.HOME
    )

    assert len(homes) == 1


def test_generated_maze_contains_one_cheese() -> None:
    """Every generated maze should contain one cheese tile."""

    generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=10,
    )

    level = generator.generate_maze()

    cheese_tiles = level.find_all_tiles(
        TileType.CHEESE
    )

    assert len(cheese_tiles) == 1


def test_home_and_cheese_are_different() -> None:
    """The cheese must not be placed on the mouse home."""

    generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=10,
    )

    level = generator.generate_maze()

    home_position = level.find_tile(
        TileType.HOME
    )

    cheese_position = level.find_tile(
        TileType.CHEESE
    )

    assert home_position != cheese_position


def test_maze_border_contains_only_walls() -> None:
    """The outer maze border should remain completely closed."""

    generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=10,
    )

    level = generator.generate_maze()

    for column in range(level.columns):
        assert (
            level.get_tile((0, column))
            == TileType.WALL
        )

        assert (
            level.get_tile(
                (level.rows - 1, column)
            )
            == TileType.WALL
        )

    for row in range(level.rows):
        assert (
            level.get_tile((row, 0))
            == TileType.WALL
        )

        assert (
            level.get_tile(
                (row, level.columns - 1)
            )
            == TileType.WALL
        )


def test_same_seed_generates_same_maze() -> None:
    """Using the same seed should reproduce the same level."""

    first_generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=42,
    )

    second_generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=42,
    )

    first_level = (
        first_generator.generate_maze()
    )

    second_level = (
        second_generator.generate_maze()
    )

    assert (
        first_level.to_text()
        == second_level.to_text()
    )


def test_even_row_count_is_rejected() -> None:
    """Recursive backtracking requires odd maze dimensions."""

    with pytest.raises(ValueError):
        MazeGenerator(
            rows=14,
            columns=21,
        )


def test_even_column_count_is_rejected() -> None:
    """Recursive backtracking requires odd maze dimensions."""

    with pytest.raises(ValueError):
        MazeGenerator(
            rows=15,
            columns=20,
        )


def test_small_maze_is_rejected() -> None:
    """Very small grids cannot form a useful maze."""

    with pytest.raises(ValueError):
        MazeGenerator(
            rows=3,
            columns=3,
        )


def test_generated_maze_contains_floor_tiles() -> None:
    """The generator must carve walkable corridors."""

    generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=10,
    )

    level = generator.generate_maze()

    floor_tiles = level.find_all_tiles(
        TileType.FLOOR
    )

    assert len(floor_tiles) > 0