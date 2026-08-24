"""Antrenarea agentului Q-learning."""

from dataclasses import dataclass, field

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
