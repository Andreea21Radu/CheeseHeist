"""Antrenarea agentului Q-learning."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from config import settings
from learning.environment import QLearningEnvironment
from learning.q_learning_agent import QLearningAgent


@dataclass
class TrainingStats:
    """Pastreaza rezultatele fiecarui episod."""

    rewards: list[int] = field(default_factory=list)
    steps: list[int] = field(default_factory=list)
    successes: list[bool] = field(default_factory=list)
    epsilon_values: list[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Returneaza procentul episoadelor reusite."""

        if not self.successes:
            return 0.0

        return sum(self.successes) / len(self.successes) * 100


def train_agent(
    environment: QLearningEnvironment,
    agent: QLearningAgent,
    episodes: int = settings.Q_LEARNING_EPISODES,
    progress_callback=None,
) -> TrainingStats:
    """Antreneaza agentul pentru numarul cerut de episoade."""

    if episodes <= 0:
        raise ValueError("Numarul de episoade trebuie sa fie pozitiv.")

    stats = TrainingStats()

    for episode in range(1, episodes + 1):
        state = environment.reset()
        total_reward = 0

        while not environment.done:
            action = agent.choose_action(state)
            next_state, reward, done = environment.step(action)

            agent.update_q_value(
                state,
                action,
                reward,
                next_state,
                done,
            )

            state = next_state
            total_reward += reward

        agent.decay_epsilon()
        stats.rewards.append(total_reward)
        stats.steps.append(environment.steps)
        stats.successes.append(environment.success)
        stats.epsilon_values.append(agent.epsilon)

        if progress_callback is not None:
            progress_callback(episode, stats)

    return stats


def get_agent_path(
    environment: QLearningEnvironment,
    agent: QLearningAgent,
) -> tuple[list[tuple[int, int]], bool]:
    """Ruleaza politica invatata si returneaza traseul ei."""

    state = environment.reset()
    path = [environment.mouse_position]

    while not environment.done:
        action = agent.choose_action(state, training=False)
        state, _, _ = environment.step(action)
        path.append(environment.mouse_position)

    return path, environment.success


def save_training_results(
    stats: TrainingStats,
    file_path: str | Path,
    comparison: dict,
) -> None:
    """Salveaza statisticile si comparatia cu BFS."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "rewards": stats.rewards,
        "steps": stats.steps,
        "success_rate": stats.success_rate,
        "comparison": comparison,
    }
    path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )
