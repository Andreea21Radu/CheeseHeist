"""Test movement, interactions and game state changes."""

from core.game_logic import GameLogic
from core.game_state import GameState
from entities.entity_manager import EntityManager
from generation.level_manager import LevelManager
from generation.tile_type import TileType


def create_test_level() -> LevelManager:
    """Create a small level containing all gameplay elements."""

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
            TileType.TRAP,
            TileType.FLOOR,
            TileType.FLOOR,
            TileType.WALL,
        ],
        [
            TileType.WALL,
            TileType.FLOOR,
            TileType.FLOOR,
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
    """Create game logic using the test level."""

    level = create_test_level()

    entity_manager = EntityManager.from_level(
        level
    )

    return GameLogic(
        level,
        entity_manager,
    )


def test_mouse_can_move_on_floor() -> None:
    """The mouse should enter walkable floor cells."""

    game_logic = create_game_logic()

    moved = game_logic.move_mouse(
        0,
        1,
        current_time=0,
    )

    assert moved is True
    assert game_logic.mouse.position == (1, 2)
    assert game_logic.mouse.number_of_moves == 1


def test_mouse_cannot_move_through_wall() -> None:
    """Walls should block mouse movement."""

    game_logic = create_game_logic()

    moved = game_logic.move_mouse(
        -1,
        0,
        current_time=0,
    )

    assert moved is False
    assert game_logic.mouse.position == (1, 1)
    assert game_logic.mouse.number_of_moves == 0


def test_mouse_collects_cheese() -> None:
    """Reaching cheese should collect and hide it."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        0,
        1,
        current_time=0,
    )

    game_logic.move_mouse(
        0,
        1,
        current_time=100,
    )

    assert game_logic.mouse.has_cheese is True
    assert game_logic.entity_manager.cheese.is_active is False
    assert game_logic.mouse.position == (1, 3)


def test_player_wins_after_returning_home() -> None:
    """The player should win after bringing cheese home."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        0,
        1,
        current_time=0,
    )

    game_logic.move_mouse(
        0,
        1,
        current_time=100,
    )

    game_logic.move_mouse(
        0,
        -1,
        current_time=200,
    )

    game_logic.move_mouse(
        0,
        -1,
        current_time=300,
    )

    assert game_logic.state == GameState.WON
    assert game_logic.has_won() is True
    assert game_logic.mouse.position == (1, 1)


def test_trap_stuns_mouse() -> None:
    """Reaching a trap should temporarily stun the mouse."""

    game_logic = create_game_logic()

    trap_time = 1000

    moved = game_logic.move_mouse(
        1,
        0,
        current_time=trap_time,
    )

    trap = game_logic.entity_manager.traps[0]

    assert moved is True
    assert game_logic.mouse.position == (2, 1)
    assert game_logic.state == GameState.PLAYING
    assert game_logic.is_stunned(trap_time) is True
    assert (
        game_logic.get_stun_seconds_remaining(
            trap_time
        )
        == 5
    )
    assert trap.is_triggered is True
    assert trap.is_active is False


def test_mouse_cannot_move_while_stunned() -> None:
    """Movement should be blocked during the trap penalty."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        1,
        0,
        current_time=1000,
    )

    moved = game_logic.move_mouse(
        0,
        1,
        current_time=3000,
    )

    assert moved is False
    assert game_logic.mouse.position == (2, 1)
    assert game_logic.mouse.number_of_moves == 1


def test_stun_countdown_decreases() -> None:
    """The trap countdown should decrease over time."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        1,
        0,
        current_time=1000,
    )

    assert (
        game_logic.get_stun_seconds_remaining(
            1000
        )
        == 5
    )

    assert (
        game_logic.get_stun_seconds_remaining(
            2000
        )
        == 4
    )

    assert (
        game_logic.get_stun_seconds_remaining(
            3000
        )
        == 3
    )

    assert (
        game_logic.get_stun_seconds_remaining(
            4000
        )
        == 2
    )

    assert (
        game_logic.get_stun_seconds_remaining(
            5000
        )
        == 1
    )


def test_mouse_can_move_after_stun_expires() -> None:
    """The mouse should move again after five seconds."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        1,
        0,
        current_time=1000,
    )

    game_logic.update(
        current_time=6000
    )

    moved = game_logic.move_mouse(
        0,
        1,
        current_time=6000,
    )

    assert moved is True
    assert game_logic.mouse.position == (2, 2)
    assert game_logic.mouse.number_of_moves == 2
    assert game_logic.is_stunned(6000) is False


def test_release_message_appears_after_stun() -> None:
    """A release message should appear after the penalty."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        1,
        0,
        current_time=1000,
    )

    game_logic.update(
        current_time=6000
    )

    assert (
        game_logic.is_release_message_visible(
            6000
        )
        is True
    )

    game_logic.update(
        current_time=7500
    )

    assert (
        game_logic.is_release_message_visible(
            7500
        )
        is False
    )


def test_triggered_trap_cannot_stun_twice() -> None:
    """A triggered trap should remain inactive."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        1,
        0,
        current_time=1000,
    )

    game_logic.update(
        current_time=6000
    )

    game_logic.move_mouse(
        0,
        1,
        current_time=6000,
    )

    game_logic.move_mouse(
        0,
        -1,
        current_time=6100,
    )

    assert game_logic.mouse.position == (2, 1)
    assert game_logic.is_stunned(6100) is False


def test_mouse_cannot_move_after_winning() -> None:
    """Movement should stop after the level is completed."""

    game_logic = create_game_logic()

    game_logic.move_mouse(
        0,
        1,
        current_time=0,
    )

    game_logic.move_mouse(
        0,
        1,
        current_time=100,
    )

    game_logic.move_mouse(
        0,
        -1,
        current_time=200,
    )

    game_logic.move_mouse(
        0,
        -1,
        current_time=300,
    )

    moved = game_logic.move_mouse(
        1,
        0,
        current_time=400,
    )

    assert game_logic.state == GameState.WON
    assert moved is False
    assert game_logic.mouse.position == (1, 1)


def test_invalid_move_is_not_counted() -> None:
    """Blocked movements should not increase the counter."""

    game_logic = create_game_logic()

    moved = game_logic.move_mouse(
        -1,
        0,
        current_time=0,
    )

    assert moved is False
    assert game_logic.mouse.number_of_moves == 0