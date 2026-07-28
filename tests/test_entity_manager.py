"""Tests for creating entities from a level."""

import pytest

from entities.entity_manager import EntityManager
from generation.level_manager import LevelManager
from generation.tile_type import TileType


def create_entity_level() -> LevelManager:
    """Create a small level containing all entity types."""

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

    return LevelManager(
        grid
    )


def test_entity_manager_creates_mouse() -> None:
    """The mouse should be created at the home position."""

    manager = EntityManager.from_level(
        create_entity_level()
    )

    assert manager.mouse.position == (1, 1)
    assert manager.mouse.sprite_name == "mouse"


def test_entity_manager_creates_cheese() -> None:
    """The cheese entity should use the cheese tile position."""

    manager = EntityManager.from_level(
        create_entity_level()
    )

    assert manager.cheese.position == (1, 3)
    assert manager.cheese.sprite_name == "cheese"


def test_entity_manager_creates_traps() -> None:
    """Every trap tile should become a trap entity."""

    manager = EntityManager.from_level(
        create_entity_level()
    )

    assert len(manager.traps) == 1
    assert manager.traps[0].position == (2, 2)
    assert manager.traps[0].sprite_name == "trap"


def test_active_entities_include_all_entities() -> None:
    """All initially active entities should be returned."""

    manager = EntityManager.from_level(
        create_entity_level()
    )

    active_entities = (
        manager.get_active_entities()
    )

    assert manager.mouse in active_entities
    assert manager.cheese in active_entities
    assert manager.traps[0] in active_entities
    assert len(active_entities) == 3


def test_inactive_cheese_is_not_returned() -> None:
    """Collected cheese should not be returned as active."""

    manager = EntityManager.from_level(
        create_entity_level()
    )

    manager.cheese.collect()

    active_entities = (
        manager.get_active_entities()
    )

    assert manager.cheese not in active_entities
    assert manager.mouse in active_entities


def test_level_without_home_is_rejected() -> None:
    """Entities cannot be created without a home position."""

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

    with pytest.raises(
        ValueError,
        match="mouse home",
    ):
        EntityManager.from_level(
            LevelManager(grid)
        )


def test_level_without_cheese_is_rejected() -> None:
    """Entities cannot be created without cheese."""

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

    with pytest.raises(
        ValueError,
        match="cheese",
    ):
        EntityManager.from_level(
            LevelManager(grid)
        )