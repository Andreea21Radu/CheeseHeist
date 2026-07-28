"""Tests for movement and gameplay rules."""

from core.game_logic import GameLogic
from core.game_state import GameState
from entities.entity_manager import EntityManager
from generation.level_manager import LevelManager
from generation.tile_type import TileType


def create_logic_level() -> LevelManager:
    """Create a small level for gameplay tests."""

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


def create_game_logic() -> GameLogic:
    """Create gameplay objects for one test level."""

    level = create_logic_level()

    entities = EntityManager.from_level(
        level
    )

    return GameLogic(
        level,
        entities,
    )


def test_mouse_can_move_on_floor() -> None:
    """The mouse should enter walkable floor cells."""

    game_logic = create_game_logic()

    moved = game_logic.move_mouse(
        0,
        1,
    )

    assert moved
    assert game_logic.mouse.position == (1, 2)
    assert game_logic.mouse.number_of_moves == 1


def test_mouse_cannot_move_through_wall() -> None:
    """Walls should block mouse movement."""

    game_logic = create_game_logic()

    moved = game_logic.move_mouse(
        -1,
        0,
    )

    assert not moved
    assert game_logic.mouse.position == (1, 1)
    assert game_logic.mouse.number_of_moves == 0


def test_mouse_collects_cheese() -> None:
    """Reaching cheese should collect and hide it."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        0,
        1,
    )

    game_logic.move_mouse(
        0,
        1,
    )

    assert game_logic.mouse.has_cheese
    assert game_logic.entity_manager.cheese.is_collected
    assert not game_logic.entity_manager.cheese.is_active


def test_player_wins_after_returning_home() -> None:
    """The player should win after bringing cheese home."""

    game_logic = create_game_logic()

    game_logic.move_mouse(0, 1)
    game_logic.move_mouse(0, 1)

    game_logic.move_mouse(0, -1)
    game_logic.move_mouse(0, -1)

    assert game_logic.state == GameState.WON
    assert game_logic.has_won()


def test_trap_causes_game_over() -> None:
    """Reaching a trap should end the game."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        1,
        0,
    )

    game_logic.move_mouse(
        0,
        1,
    )

    assert game_logic.state == GameState.LOST
    assert game_logic.has_lost()
    assert game_logic.entity_manager.traps[0].is_triggered


def test_mouse_cannot_move_after_winning() -> None:
    """Movement should stop after the level is completed."""

    game_logic = create_game_logic()

    game_logic.move_mouse(0, 1)
    game_logic.move_mouse(0, 1)
    game_logic.move_mouse(0, -1)
    game_logic.move_mouse(0, -1)

    previous_position = (
        game_logic.mouse.position
    )

    moved = game_logic.move_mouse(
        1,
        0,
    )

    assert not moved
    assert game_logic.mouse.position == previous_position


def test_mouse_cannot_move_after_losing() -> None:
    """Movement should stop after touching a trap."""

    game_logic = create_game_logic()

    game_logic.move_mouse(1, 0)
    game_logic.move_mouse(0, 1)

    previous_position = (
        game_logic.mouse.position
    )

    moved = game_logic.move_mouse(
        0,
        1,
    )

    assert not moved
    assert game_logic.mouse.position == previous_position


def test_invalid_move_is_not_counted() -> None:
    """Blocked movements should not increase the counter."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        -1,
        0,
    )

    assert game_logic.mouse.number_of_moves == 0