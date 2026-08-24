"""Reprezentarea individului si calcularea fitness-ului."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import json
from pathlib import Path

from config import settings
from generation.maze_generator import MazeGenerator

from difficulty.difficulty_metrics import (
    calculate_difficulty_score,
    calculate_wall_density,
    classify_difficulty,
)
from generation.level_manager import LevelManager
from generation.level_validator import LevelValidator
from generation.tile_type import TileType


TARGET_SCORES = {
    "easy": 26.0,
    "medium": 30.5,
    "hard": 36.0,
}

INVALID_LEVEL_PENALTY = 1000.0


def copy_level(level: LevelManager) -> LevelManager:
    """Copiaza nivelul fara a pastra aceeasi grila."""

    grid_copy = [
        row.copy()
        for row in level.grid
    ]

    return LevelManager(grid_copy)


def is_valid_level(level: LevelManager) -> bool:
    """Verifica daca nivelul poate fi terminat."""

    homes = level.find_all_tiles(
        TileType.HOME
    )

    cheeses = level.find_all_tiles(
        TileType.CHEESE
    )

    if len(homes) != 1:
        return False

    if len(cheeses) != 1:
        return False

    validator = LevelValidator(level)

    return validator.is_level_playable()


@dataclass
class LevelIndividual:
    """Reprezinta un nivel din populatia algoritmului genetic."""

    level: LevelManager
    fitness: float = 0.0
    difficulty_score: Optional[float] = None
    valid: bool = False

    def copy(self) -> "LevelIndividual":
        """Creeaza o copie independenta a individului."""

        return LevelIndividual(
            level=copy_level(self.level),
            fitness=self.fitness,
            difficulty_score=self.difficulty_score,
            valid=self.valid,
        )

    def evaluate(
        self,
        target_difficulty: str,
    ) -> float:
        """Calculeaza fitness-ul individului."""

        if target_difficulty not in TARGET_SCORES:
            raise ValueError(
                "Dificultatea ceruta nu este valida."
            )

        self.valid = is_valid_level(self.level)

        if not self.valid:
            self.difficulty_score = None
            self.fitness = -INVALID_LEVEL_PENALTY
            return self.fitness

        score = calculate_difficulty_score(
            self.level
        )

        if score is None:
            self.difficulty_score = None
            self.fitness = -INVALID_LEVEL_PENALTY
            return self.fitness

        target_score = TARGET_SCORES[
            target_difficulty
        ]

        difference = abs(
            score - target_score
        )

        closeness_bonus = max(
            0.0,
            100.0 - difference * 8.0,
        )

        playability_bonus = 50.0

        wall_density = calculate_wall_density(
            self.level
        )

        balance_bonus = max(
            0.0,
            10.0 - abs(wall_density - 0.5) * 20,
        )

        category_bonus = 0.0

        if classify_difficulty(score) == target_difficulty:
            category_bonus = 20.0

        self.difficulty_score = score

        self.fitness = round(
            closeness_bonus
            + playability_bonus
            + balance_bonus
            + category_bonus,
            2,
        )

        return self.fitness


def calculate_fitness(
    individual: LevelIndividual,
    target_difficulty: str,
) -> float:
    """Evalueaza si returneaza fitness-ul unui individ."""

    return individual.evaluate(
        target_difficulty
    )

import random


def clean_grid(
    level: LevelManager,
) -> list[list[TileType]]:
    """Elimina elementele speciale din grila copiata."""

    special_tiles = {
        TileType.HOME,
        TileType.CHEESE,
        TileType.TRAP,
    }

    return [
        [
            TileType.FLOOR
            if tile in special_tiles
            else tile
            for tile in row
        ]
        for row in level.grid
    ]


def regenerate_special_tiles(
    grid: list[list[TileType]],
    trap_count: int,
    rng: random.Random,
) -> Optional[LevelManager]:
    """Adauga din nou casa, branza si capcanele."""

    floor_positions = [
        (row, col)
        for row in range(len(grid))
        for col in range(len(grid[0]))
        if grid[row][col] == TileType.FLOOR
    ]

    if len(floor_positions) < 2:
        return None

    for _ in range(30):
        new_grid = [
            row.copy()
            for row in grid
        ]

        home, cheese = rng.sample(
            floor_positions,
            2,
        )

        home_row, home_col = home
        cheese_row, cheese_col = cheese

        new_grid[home_row][home_col] = TileType.HOME
        new_grid[cheese_row][cheese_col] = TileType.CHEESE

        available_traps = [
            position
            for position in floor_positions
            if position not in {
                home,
                cheese,
            }
        ]

        traps = rng.sample(
            available_traps,
            min(trap_count, len(available_traps)),
        )

        for trap_row, trap_col in traps:
            new_grid[trap_row][trap_col] = TileType.TRAP

        level = LevelManager(new_grid)

        if is_valid_level(level):
            return level

    return None


def select_parent(
    population: list[LevelIndividual],
    tournament_size: int = 3,
    rng: Optional[random.Random] = None,
) -> LevelIndividual:
    """Selecteaza un parinte prin turneu."""

    rng = rng or random.Random()

    candidates = rng.sample(
        population,
        min(tournament_size, len(population)),
    )

    return max(
        candidates,
        key=lambda individual: individual.fitness,
    )


def crossover_levels(
    first_parent: LevelIndividual,
    second_parent: LevelIndividual,
    rng: Optional[random.Random] = None,
) -> LevelIndividual:
    """Combina jumatatile a doua niveluri."""

    rng = rng or random.Random()

    first_grid = clean_grid(first_parent.level)
    second_grid = clean_grid(second_parent.level)

    cut = rng.randint(
        1,
        first_parent.level.rows - 2,
    )

    child_grid = (
        first_grid[:cut]
        + second_grid[cut:]
    )

    first_traps = len(
        first_parent.level.find_all_tiles(
            TileType.TRAP
        )
    )

    second_traps = len(
        second_parent.level.find_all_tiles(
            TileType.TRAP
        )
    )

    trap_count = round(
        (first_traps + second_traps) / 2
    )

    child_level = regenerate_special_tiles(
        child_grid,
        trap_count,
        rng,
    )

    if child_level is None:
        if first_parent.fitness >= second_parent.fitness:
            return first_parent.copy()

        return second_parent.copy()

    return LevelIndividual(child_level)


def mutate_level(
    individual: LevelIndividual,
    mutation_rate: float = 0.08,
    rng: Optional[random.Random] = None,
) -> LevelIndividual:
    """Modifica o celula si numarul capcanelor."""

    rng = rng or random.Random()

    if rng.random() >= mutation_rate:
        return individual.copy()

    level = individual.level
    grid = clean_grid(level)

    row = rng.randint(1, level.rows - 2)
    col = rng.randint(1, level.columns - 2)

    if grid[row][col] == TileType.WALL:
        grid[row][col] = TileType.FLOOR
    else:
        grid[row][col] = TileType.WALL

    trap_count = len(
        level.find_all_tiles(TileType.TRAP)
    )

    trap_count = max(
        0,
        trap_count + rng.choice((-1, 0, 1)),
    )

    mutated_level = regenerate_special_tiles(
        grid,
        trap_count,
        rng,
    )

    if mutated_level is None:
        return individual.copy()

    return LevelIndividual(mutated_level)


def preserve_elite(
    population: list[LevelIndividual],
    elite_count: int = 2,
) -> list[LevelIndividual]:
    """Pastreaza cei mai buni indivizi."""

    ordered = sorted(
        population,
        key=lambda individual: individual.fitness,
        reverse=True,
    )

    return [
        individual.copy()
        for individual in ordered[:elite_count]
    ]


def create_next_generation(
    population: list[LevelIndividual],
    target_difficulty: str,
    mutation_rate: float = 0.08,
    elite_count: int = 2,
    rng: Optional[random.Random] = None,
) -> list[LevelIndividual]:
    """Creeaza urmatoarea generatie."""

    rng = rng or random.Random()

    for individual in population:
        individual.evaluate(target_difficulty)

    new_population = preserve_elite(
        population,
        elite_count,
    )

    while len(new_population) < len(population):
        first_parent = select_parent(
            population,
            rng=rng,
        )

        second_parent = select_parent(
            population,
            rng=rng,
        )

        child = crossover_levels(
            first_parent,
            second_parent,
            rng,
        )

        child = mutate_level(
            child,
            mutation_rate,
            rng,
        )

        child.evaluate(target_difficulty)

        new_population.append(child)

    return new_population


def evolve_level(
    initial_level: LevelManager,
    target_difficulty: str,
    show_progress=None,
):
    """Evolueaza nivelul spre dificultatea aleasa."""

    population = [LevelIndividual(copy_level(initial_level))]

    while len(population) < settings.GA_POPULATION_SIZE:
        generator = MazeGenerator(initial_level.rows, initial_level.columns)
        level = generator.generate_maze()
        population.append(LevelIndividual(level))

    for individual in population:
        individual.evaluate(target_difficulty)

    initial = population[0].copy()
    best = max(population, key=lambda item: item.fitness).copy()
    history = [best.fitness]

    for generation in range(1, settings.GA_GENERATIONS + 1):
        population = create_next_generation(
            population,
            target_difficulty,
        )

        generation_best = max(
            population,
            key=lambda item: item.fitness,
        )

        if generation_best.fitness > best.fitness:
            best = generation_best.copy()

        history.append(best.fitness)

        if show_progress:
            show_progress(generation, best)

    return initial, best, history


def save_evolution_result(initial, best, history) -> None:
    """Salveaza nivelul final si rezultatele evolutiei."""

    project_folder = Path(__file__).resolve().parents[1]
    results_folder = project_folder / "data" / "results"
    levels_folder = project_folder / "data" / "generated_levels"

    results_folder.mkdir(parents=True, exist_ok=True)
    levels_folder.mkdir(parents=True, exist_ok=True)

    level_data = [
        [tile.name for tile in row]
        for row in best.level.grid
    ]

    (levels_folder / "evolved_level.json").write_text(
        json.dumps(level_data, indent=4),
        encoding="utf-8",
    )

    result_data = {
        "initial_difficulty": initial.difficulty_score,
        "final_difficulty": best.difficulty_score,
        "best_fitness": best.fitness,
        "fitness_history": history,
    }

    (results_folder / "evolution_result.json").write_text(
        json.dumps(result_data, indent=4),
        encoding="utf-8",
    )
