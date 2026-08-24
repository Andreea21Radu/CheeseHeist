"""Calculeaza metricile de dificultate pentru un nivel."""

from typing import Optional

from generation.level_manager import LevelManager
from generation.level_validator import LevelValidator
from generation.tile_type import TileType


def calculate_path_length(level: LevelManager) -> Optional[int]:
    """Returneaza lungimea traseului minim."""

    validator = LevelValidator(level)
    return validator.get_shortest_path_length()


def count_dead_ends(level: LevelManager) -> int:
    """Numara fundaturile nivelului."""

    dead_ends = 0

    for row in range(level.rows):
        for col in range(level.columns):
            pos = (row, col)

            if level.get_tile(pos) == TileType.WALL:
                continue

            if len(level.get_neighbors(pos)) == 1:
                dead_ends += 1

    return dead_ends


def count_intersections(level: LevelManager) -> int:
    """Numara intersectiile nivelului."""

    intersections = 0

    for row in range(level.rows):
        for col in range(level.columns):
            pos = (row, col)

            if level.get_tile(pos) == TileType.WALL:
                continue

            if len(level.get_neighbors(pos)) >= 3:
                intersections += 1

    return intersections


def calculate_wall_density(level: LevelManager) -> float:
    """Calculeaza densitatea peretilor."""

    total = level.rows * level.columns

    if total == 0:
        return 0.0

    walls = len(
        level.find_all_tiles(TileType.WALL)
    )

    return walls / total


def calculate_trap_risk(level: LevelManager) -> float:
    """Calculeaza riscul produs de capcane."""

    validator = LevelValidator(level)
    path = validator.get_home_to_cheese_path()
    traps = level.find_all_tiles(TileType.TRAP)

    if not path or not traps:
        return 0.0

    safe_chance = 1.0

    for trap_row, trap_col in traps:
        distance = min(
            abs(trap_row - path_row)
            + abs(trap_col - path_col)
            for path_row, path_col in path
        )

        trap_chance = 1 / (distance + 1)
        safe_chance *= 1 - trap_chance

    return round(1 - safe_chance, 4)


def calculate_difficulty_score(
    level: LevelManager,
) -> Optional[float]:
    """Calculeaza scorul final de dificultate."""

    path_length = calculate_path_length(level)

    if path_length is None:
        return None

    total = level.rows * level.columns
    walls = len(
        level.find_all_tiles(TileType.WALL)
    )
    free_cells = total - walls

    if total == 0 or free_cells == 0:
        return None

    path_ratio = path_length / total
    dead_ends_ratio = (
        count_dead_ends(level) / free_cells
    )
    intersections_ratio = (
        count_intersections(level) / free_cells
    )

    score = (
        path_ratio * 40
        + dead_ends_ratio * 15
        + intersections_ratio * 10
        + calculate_wall_density(level) * 10
        + calculate_trap_risk(level) * 25
    )

    return round(score, 2)
