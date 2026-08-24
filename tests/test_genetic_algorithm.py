"""Teste pentru algoritmul genetic."""

import random

from config import settings
from difficulty.genetic_algorithm import (
    INVALID_LEVEL_PENALTY,
    LevelIndividual,
    create_next_generation,
    evolve_level,
)
from generation.level_manager import LevelManager
from generation.maze_generator import MazeGenerator
from generation.tile_type import TileType


def create_level(seed: int = 1) -> LevelManager:
    """Creeaza un nivel valid pentru teste."""

    return MazeGenerator(
        rows=15,
        columns=21,
        seed=seed,
    ).generate_maze()


def test_valid_level_gets_positive_fitness() -> None:
    individual = LevelIndividual(create_level())

    assert individual.evaluate("medium") > 0
    assert individual.valid is True


def test_invalid_level_gets_penalty() -> None:
    wall = TileType.WALL
    individual = LevelIndividual(LevelManager([
        [wall, wall, wall],
        [wall, wall, wall],
        [wall, wall, wall],
    ]))

    assert individual.evaluate("easy") == -INVALID_LEVEL_PENALTY
    assert individual.valid is False


def test_next_generation_keeps_population_size() -> None:
    population = [
        LevelIndividual(create_level(seed))
        for seed in range(4)
    ]

    new_population = create_next_generation(
        population,
        "medium",
        rng=random.Random(3),
    )

    assert len(new_population) == len(population)
    assert all(item.valid for item in new_population)


def test_evolution_tracks_every_generation(monkeypatch) -> None:
    monkeypatch.setattr(settings, "GA_POPULATION_SIZE", 4)
    monkeypatch.setattr(settings, "GA_GENERATIONS", 2)

    _, best, history = evolve_level(create_level(), "hard")

    assert len(history) == 3
    assert history == sorted(history)
    assert best.valid is True
