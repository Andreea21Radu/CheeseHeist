"""Tests for the global game settings."""

from config import settings


def test_grid_dimensions_are_odd() -> None:
    """The recursive backtracking maze requires odd dimensions."""

    assert settings.GRID_ROWS % 2 == 1
    assert settings.GRID_COLUMNS % 2 == 1


def test_grid_is_large_enough() -> None:
    """The maze needs enough room to create paths and walls."""

    assert settings.GRID_ROWS >= settings.MINIMUM_GRID_SIZE
    assert settings.GRID_COLUMNS >= settings.MINIMUM_GRID_SIZE


def test_window_has_valid_dimensions() -> None:
    """The Pygame window must have positive dimensions."""

    assert settings.WINDOW_WIDTH > 0
    assert settings.WINDOW_HEIGHT > 0