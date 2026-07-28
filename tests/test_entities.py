"""Tests for game entities."""

from entities.cheese import Cheese
from entities.entity import Entity
from entities.mouse import Mouse
from entities.trap import Trap


def test_entity_stores_position() -> None:
    """An entity should store its grid position."""

    entity = Entity(
        position=(3, 5),
        sprite_name="example",
    )

    assert entity.position == (3, 5)
    assert entity.row == 3
    assert entity.column == 5


def test_entity_can_change_position() -> None:
    """An entity should be movable to another position."""

    entity = Entity(
        position=(1, 1),
        sprite_name="example",
    )

    entity.set_position(
        (2, 3)
    )

    assert entity.position == (2, 3)
    assert entity.row == 2
    assert entity.column == 3


def test_entity_can_be_deactivated() -> None:
    """A deactivated entity should no longer be active."""

    entity = Entity(
        position=(1, 1),
        sprite_name="example",
    )

    entity.deactivate()

    assert not entity.is_active


def test_entity_can_be_activated() -> None:
    """An inactive entity should be activatable again."""

    entity = Entity(
        position=(1, 1),
        sprite_name="example",
    )

    entity.deactivate()
    entity.activate()

    assert entity.is_active


def test_mouse_starts_without_cheese() -> None:
    """The mouse should not initially carry cheese."""

    mouse = Mouse(
        (1, 1)
    )

    assert not mouse.has_cheese
    assert mouse.number_of_moves == 0
    assert mouse.sprite_name == "mouse"


def test_mouse_can_collect_cheese() -> None:
    """The mouse should remember collecting cheese."""

    mouse = Mouse(
        (1, 1)
    )

    mouse.collect_cheese()

    assert mouse.has_cheese


def test_mouse_can_drop_cheese() -> None:
    """The mouse should be able to drop the cheese."""

    mouse = Mouse(
        (1, 1)
    )

    mouse.collect_cheese()
    mouse.drop_cheese()

    assert not mouse.has_cheese


def test_mouse_registers_movements() -> None:
    """The mouse should count completed movements."""

    mouse = Mouse(
        (1, 1)
    )

    mouse.register_move()
    mouse.register_move()

    assert mouse.number_of_moves == 2


def test_mouse_can_be_reset() -> None:
    """Resetting should restore the initial mouse state."""

    mouse = Mouse(
        (1, 1)
    )

    mouse.collect_cheese()
    mouse.register_move()
    mouse.deactivate()

    mouse.reset(
        (4, 5)
    )

    assert mouse.position == (4, 5)
    assert not mouse.has_cheese
    assert mouse.number_of_moves == 0
    assert mouse.is_active


def test_cheese_can_be_collected() -> None:
    """Collected cheese should become inactive."""

    cheese = Cheese(
        (2, 3)
    )

    cheese.collect()

    assert cheese.is_collected
    assert not cheese.is_active


def test_cheese_can_be_reset() -> None:
    """Resetting cheese should restore its active state."""

    cheese = Cheese(
        (2, 3)
    )

    cheese.collect()

    cheese.reset(
        (5, 6)
    )

    assert cheese.position == (5, 6)
    assert not cheese.is_collected
    assert cheese.is_active


def test_trap_can_be_triggered() -> None:
    """A trap should remember when it was triggered."""

    trap = Trap(
        (4, 5)
    )

    trap.trigger()

    assert trap.is_triggered


def test_trap_can_be_reset() -> None:
    """Resetting a trap should remove its triggered state."""

    trap = Trap(
        (4, 5)
    )

    trap.trigger()
    trap.deactivate()
    trap.reset()

    assert not trap.is_triggered
    assert trap.is_active