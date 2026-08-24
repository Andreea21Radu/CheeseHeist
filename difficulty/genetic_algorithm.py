"""Reprezentarea individului si calcularea fitness-ului."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

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
