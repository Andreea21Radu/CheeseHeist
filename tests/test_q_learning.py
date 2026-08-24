"""Teste pentru mediul si agentul Q-learning."""

from generation.level_manager import LevelManager
from generation.tile_type import TileType
from learning.environment import QLearningEnvironment
from learning.q_learning_agent import QLearningAgent
from learning.training import get_agent_path, train_agent


def create_small_level() -> LevelManager:
    wall = TileType.WALL
    floor = TileType.FLOOR

    return LevelManager([
        [wall, wall, wall, wall, wall],
        [wall, TileType.HOME, floor, TileType.CHEESE, wall],
        [wall, TileType.TRAP, floor, floor, wall],
        [wall, wall, wall, wall, wall],
    ])


def test_environment_rewards() -> None:
    environment = QLearningEnvironment(create_small_level())

    assert environment.step("up")[1] == -5
    environment.reset()
    assert environment.step("down")[1] == -15
    environment.reset()
    assert environment.step("right")[1] == -1
    assert environment.step("right")[1] == 30
    environment.step("left")
    _, reward, done = environment.step("left")

    assert reward == 100
    assert done is True
    assert environment.success is True


def test_q_value_update_uses_bellman_formula() -> None:
    agent = QLearningAgent(
        learning_rate=0.5,
        discount_factor=0.9,
        epsilon=0.0,
    )
    state = (1, 1, False)
    next_state = (1, 2, False)
    agent.q_table[next_state] = {"right": 10.0}

    agent.update_q_value(
        state,
        "right",
        2,
        next_state,
        False,
    )

    assert agent.get_q_value(state, "right") == 5.5


def test_agent_learns_complete_route() -> None:
    environment = QLearningEnvironment(
        create_small_level(),
        max_steps=30,
    )
    agent = QLearningAgent(
        epsilon_decay=0.98,
        seed=7,
    )

    stats = train_agent(environment, agent, episodes=400)
    path, success = get_agent_path(environment, agent)

    assert success is True
    assert len(path) <= 6
    assert stats.success_rate > 0


def test_q_table_can_be_saved_and_loaded(tmp_path) -> None:
    agent = QLearningAgent()
    state = (1, 1, False)
    agent.q_table[state] = {"right": 4.5}
    file_path = tmp_path / "q_table.json"

    agent.save_q_table(file_path)
    loaded_agent = QLearningAgent()
    loaded_agent.load_q_table(file_path)

    assert loaded_agent.q_table == agent.q_table
