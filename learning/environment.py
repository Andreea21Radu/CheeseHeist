"""Mediul jocului folosit pentru Q-learning."""

from typing import Optional

from generation.level_manager import LevelManager
from generation.tile_type import TileType


State = tuple[int, int, bool]


class QLearningEnvironment:
    """Controleaza starea, actiunile si recompensele agentului."""

    ACTIONS = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    STEP_REWARD = -1
    WALL_REWARD = -5
    TRAP_REWARD = -15
    CHEESE_REWARD = 30
    WIN_REWARD = 100

    def __init__(
        self,
        level: LevelManager,
        max_steps: Optional[int] = None,
    ) -> None:
        self.level = level
        self.home_position = level.find_tile(TileType.HOME)
        self.cheese_position = level.find_tile(TileType.CHEESE)

        if self.home_position is None:
            raise ValueError("Nivelul nu are casa.")

        if self.cheese_position is None:
            raise ValueError("Nivelul nu are branza.")

        if max_steps is None:
            max_steps = level.rows * level.columns * 4

        if max_steps <= 0:
            raise ValueError("Numarul maxim de pasi trebuie sa fie pozitiv.")

        self.max_steps = max_steps
        self.mouse_position = self.home_position
        self.has_cheese = False
        self.steps = 0
        self.done = False
        self.success = False

    def get_state(self) -> State:
        """Returneaza pozitia si starea branzei."""

        row, column = self.mouse_position
        return row, column, self.has_cheese

    def reset(self) -> State:
        """Readuce mediul la starea initiala."""

        self.mouse_position = self.home_position
        self.has_cheese = False
        self.steps = 0
        self.done = False
        self.success = False

        return self.get_state()

    def step(self, action: str) -> tuple[State, int, bool]:
        """Executa o actiune si returneaza noua stare."""

        if action not in self.ACTIONS:
            raise ValueError("Actiunea nu este valida.")

        if self.done:
            return self.get_state(), 0, True

        self.steps += 1
        row_change, column_change = self.ACTIONS[action]
        row, column = self.mouse_position
        new_position = (
            row + row_change,
            column + column_change,
        )

        if not self.level.is_walkable(new_position):
            reward = self.WALL_REWARD
        else:
            self.mouse_position = new_position
            tile = self.level.get_tile(new_position)
            reward = self.STEP_REWARD

            if tile == TileType.TRAP:
                reward = self.TRAP_REWARD

            elif (
                new_position == self.cheese_position
                and not self.has_cheese
            ):
                self.has_cheese = True
                reward = self.CHEESE_REWARD

            if (
                new_position == self.home_position
                and self.has_cheese
            ):
                reward = self.WIN_REWARD
                self.done = True
                self.success = True

        if self.steps >= self.max_steps:
            self.done = True

        return self.get_state(), reward, self.done
