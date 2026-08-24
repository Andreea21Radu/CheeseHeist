"""Agentul care invata folosind algoritmul Q-learning."""

import json
import random
from pathlib import Path
from typing import Optional

from config import settings
from learning.environment import QLearningEnvironment, State


class QLearningAgent:
    """Pastreaza Q-table-ul si alege actiunile agentului."""

    def __init__(
        self,
        learning_rate: float = settings.Q_LEARNING_RATE,
        discount_factor: float = settings.Q_DISCOUNT_FACTOR,
        epsilon: float = settings.Q_INITIAL_EPSILON,
        min_epsilon: float = settings.Q_MIN_EPSILON,
        epsilon_decay: float = settings.Q_EPSILON_DECAY,
        seed: Optional[int] = None,
    ) -> None:
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = epsilon_decay
        self.actions = tuple(QLearningEnvironment.ACTIONS)
        self.q_table: dict[State, dict[str, float]] = {}
        self.random = random.Random(seed)

    def get_q_value(self, state: State, action: str) -> float:
        """Returneaza valoarea unei actiuni dintr-o stare."""

        return self.q_table.get(state, {}).get(action, 0.0)

    def choose_action(
        self,
        state: State,
        training: bool = True,
    ) -> str:
        """Alege intre explorare si cea mai buna actiune invatata."""

        if training and self.random.random() < self.epsilon:
            return self.random.choice(self.actions)

        best_value = max(
            self.get_q_value(state, action)
            for action in self.actions
        )

        best_actions = [
            action
            for action in self.actions
            if self.get_q_value(state, action) == best_value
        ]

        return self.random.choice(best_actions)

    def update_q_value(
        self,
        state: State,
        action: str,
        reward: int,
        next_state: State,
        done: bool,
    ) -> None:
        """Actualizeaza valoarea Q dupa o actiune."""

        old_value = self.get_q_value(state, action)
        next_value = 0.0

        if not done:
            next_value = max(
                self.get_q_value(next_state, next_action)
                for next_action in self.actions
            )

        target = reward + self.discount_factor * next_value
        new_value = old_value + self.learning_rate * (
            target - old_value
        )

        self.q_table.setdefault(state, {})[action] = new_value

    def decay_epsilon(self) -> None:
        """Reduce treptat explorarea agentului."""

        self.epsilon = max(
            self.min_epsilon,
            self.epsilon * self.epsilon_decay,
        )

    def save_q_table(self, file_path: str | Path) -> None:
        """Salveaza Q-table-ul in format JSON."""

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        values = []

        for state, actions in self.q_table.items():
            for action, value in actions.items():
                values.append({
                    "state": list(state),
                    "action": action,
                    "value": value,
                })

        data = {
            "epsilon": self.epsilon,
            "q_values": values,
        }

        path.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8",
        )

    def load_q_table(self, file_path: str | Path) -> None:
        """Incarca Q-table-ul dintr-un fisier JSON."""

        data = json.loads(
            Path(file_path).read_text(encoding="utf-8")
        )
        self.q_table = {}
        self.epsilon = float(data.get("epsilon", self.epsilon))

        for item in data.get("q_values", []):
            row, column, has_cheese = item["state"]
            state = (int(row), int(column), bool(has_cheese))
            action = str(item["action"])
            value = float(item["value"])
            self.q_table.setdefault(state, {})[action] = value
