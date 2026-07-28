"""Tests for BFS and level playability validation."""

from generation.level_manager import LevelManager
from generation.level_validator import LevelValidator
from generation.maze_generator import MazeGenerator
from generation.tile_type import TileType


def create_playable_level() -> LevelManager:
    """Create a small level with a valid path."""

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
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
        ],
    ]

    return LevelManager(grid)


def create_blocked_level() -> LevelManager:
    """Create a level where the cheese cannot be reached."""

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
            TileType.WALL,
            TileType.CHEESE,
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


def test_bfs_finds_shortest_path() -> None:
    """BFS should return the shortest path to the cheese."""

    validator = LevelValidator(
        create_playable_level()
    )

    path = validator.get_home_to_cheese_path()

    assert path == [
        (1, 1),
        (1, 2),
        (1, 3),
    ]


def test_shortest_path_length_is_correct() -> None:
    """Path length should count movements, not positions."""

    validator = LevelValidator(
        create_playable_level()
    )

    assert validator.get_shortest_path_length() == 2


def test_playable_level_is_accepted() -> None:
    """A connected home and cheese should form a valid level."""

    validator = LevelValidator(
        create_playable_level()
    )

    assert validator.is_level_playable()


def test_blocked_level_is_rejected() -> None:
    """A blocked cheese should make the level invalid."""

    validator = LevelValidator(
        create_blocked_level()
    )

    assert not validator.is_level_playable()


def test_blocked_level_has_no_path() -> None:
    """BFS should return an empty list when no route exists."""

    validator = LevelValidator(
        create_blocked_level()
    )

    assert validator.get_home_to_cheese_path() == []


def test_missing_home_is_rejected() -> None:
    """A level without a mouse home cannot be played."""

    grid = [
        [
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.CHEESE,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
        ],
    ]

    validator = LevelValidator(
        LevelManager(grid)
    )

    assert not validator.is_level_playable()


def test_missing_cheese_is_rejected() -> None:
    """A level without cheese cannot be completed."""

    grid = [
        [
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.HOME,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.WALL,
            TileType.WALL,
        ],
    ]

    validator = LevelValidator(
        LevelManager(grid)
    )

    assert not validator.is_level_playable()


def test_generated_maze_is_playable() -> None:
    """A generated recursive-backtracking maze should pass validation."""

    generator = MazeGenerator(
        rows=15,
        columns=21,
        seed=25,
    )

    level = generator.generate_maze()
    validator = LevelValidator(level)

    assert validator.is_level_playable()


def test_return_path_exists() -> None:
    """The mouse should also be able to return home."""

    validator = LevelValidator(
        create_playable_level()
    )

    return_path = (
        validator.get_cheese_to_home_path()
    )

    assert return_path == [
        (1, 3),
        (1, 2),
        (1, 1),
    ]