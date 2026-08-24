"""Main game loop and application lifecycle."""

from typing import Optional

import pygame

from config import settings
from core.game_logic import GameLogic
from core.game_state import GameState
from difficulty.difficulty_metrics import (
    calculate_difficulty_score,
    get_level_difficulty,
)
from difficulty.genetic_algorithm import evolve_level, save_evolution_result
from entities.entity_manager import EntityManager
from generation.level_manager import LevelManager
from generation.level_validator import LevelValidator
from generation.maze_generator import MazeGenerator
from graphics.asset_manager import AssetManager
from graphics.renderer import Renderer
from graphics.ui import (
    AGENT_MODE,
    EVOLVE_MODE,
    HUMAN_MODE,
    MODE_LABELS,
    RANDOM_MODE,
    GameMenu,
    draw_evolution_progress,
    draw_training_progress,
)
from learning.environment import QLearningEnvironment, State
from learning.q_learning_agent import QLearningAgent
from learning.training import (
    TrainingStats,
    get_agent_path,
    save_training_results,
    train_agent,
)


class Game:
    """Control the main loop of the Cheese Heist application."""

    def __init__(self) -> None:
        pygame.init()
        self.target_difficulty = settings.DEFAULT_DIFFICULTY
        self.screen = pygame.display.set_mode(
            (
                settings.WINDOW_WIDTH,
                settings.WINDOW_HEIGHT,
            )
        )

        pygame.display.set_caption(
            settings.WINDOW_TITLE
        )

        self.clock = pygame.time.Clock()
        self.is_running = True
        self.has_started = False
        self.current_mode = HUMAN_MODE

        self.last_move_time = 0
        self.move_delay = settings.MOVE_DELAY
        self.last_agent_move_time = 0

        self.cheese_message_until = 0
        self.previous_cheese_state = False

        self.assets = AssetManager()

        self.agent: Optional[QLearningAgent] = None
        self.agent_environment: Optional[
            QLearningEnvironment
        ] = None
        self.agent_state: Optional[State] = None
        self.training_stats: Optional[TrainingStats] = None
        self.agent_path: list[tuple[int, int]] = []
        self.agent_success = False

        self.maze_generator = MazeGenerator(
            rows=settings.GRID_ROWS,
            columns=settings.GRID_COLUMNS,
            seed=settings.DEFAULT_MAZE_SEED,
        )

        self.level = self.generate_valid_level()
        self.update_level_components()

        self.renderer = Renderer(
            self.screen,
            self.assets,
        )
        self.game_menu = GameMenu(
            self.screen
        )

        self.print_level_information()

    def generate_valid_level(
        self,
    ) -> LevelManager:
        """Generate levels until one passes validation."""

        maximum_attempts = 100

        for attempt in range(
            1,
            maximum_attempts + 1,
        ):
            generated_level = (
                self.maze_generator.generate_maze()
            )

            validator = LevelValidator(
                generated_level
            )

            if validator.is_level_playable():
                print(
                    "Valid maze generated after "
                    f"{attempt} attempt(s)."
                )

                return generated_level

        raise RuntimeError(
            "Could not generate a playable maze."
        )

    def generate_level_for_difficulty(
        self,
        difficulty: str,
    ) -> LevelManager:
        """Genereaza un nivel din categoria aleasa."""

        options = {
            "easy": (1, 0.28),
            "medium": (5, 0.12),
            "hard": (8, 0.03),
        }
        target_scores = {
            "easy": 27.0,
            "medium": 30.5,
            "hard": 34.0,
        }
        trap_count, passage_ratio = options[difficulty]
        best_level = None
        best_difference = float("inf")

        for _ in range(100):
            generator = MazeGenerator(
                rows=settings.GRID_ROWS,
                columns=settings.GRID_COLUMNS,
                trap_count=trap_count,
                extra_passage_ratio=passage_ratio,
            )
            level = generator.generate_maze()
            score = calculate_difficulty_score(level)

            if score is None:
                continue

            difference = abs(score - target_scores[difficulty])
            if difference < best_difference:
                best_level = level
                best_difference = difference

            if get_level_difficulty(level) == difficulty:
                return level

        if best_level is None:
            raise RuntimeError("Nu s-a putut genera nivelul cerut.")

        return best_level

    def update_level_components(
        self,
    ) -> None:
        """Recreate everything dependent on the current level."""

        self.level_validator = LevelValidator(
            self.level
        )

        self.bfs_path = (
            self.level_validator
            .get_home_to_cheese_path()
        )

        return_path = (
            self.level_validator
            .get_cheese_to_home_path()
        )
        self.bfs_round_trip = (
            self.bfs_path + return_path[1:]
            if return_path
            else self.bfs_path
        )

        self.shortest_path_length = (
            self.level_validator
            .get_shortest_path_length()
            or 0
        )

        self.entity_manager = (
            EntityManager.from_level(
                self.level
            )
        )

        self.game_logic = GameLogic(
            self.level,
            self.entity_manager,
        )

        self.last_move_time = 0
        self.last_agent_move_time = 0
        self.cheese_message_until = 0
        self.previous_cheese_state = False
        self.show_bfs_path = settings.SHOW_BFS_PATH_BY_DEFAULT

    def clear_agent(self) -> None:
        """Sterge datele agentului de la rularea anterioara."""

        self.agent = None
        self.agent_environment = None
        self.agent_state = None
        self.training_stats = None
        self.agent_path = []
        self.agent_success = False

    def show_training_progress(
        self,
        episode: int,
        stats: TrainingStats,
    ) -> None:
        """Actualizeaza ecranul in timpul antrenarii."""

        if (
            episode % 50 != 0
            and episode != settings.Q_LEARNING_EPISODES
        ):
            return

        draw_training_progress(
            self.screen,
            episode,
            stats,
        )
        pygame.event.pump()

    def setup_agent(self) -> None:
        """Antreneaza si pregateste agentul pentru afisare."""

        environment = QLearningEnvironment(self.level)
        untrained_agent = QLearningAgent(seed=0)
        untrained_path, untrained_success = get_agent_path(
            environment,
            untrained_agent,
        )

        agent = QLearningAgent(seed=0)
        stats = train_agent(
            environment,
            agent,
            progress_callback=self.show_training_progress,
        )
        trained_path, trained_success = get_agent_path(
            environment,
            agent,
        )

        model_path = settings.SAVED_MODELS_DIRECTORY / (
            f"q_table_{self.target_difficulty}.json"
        )
        result_path = settings.RESULTS_DIRECTORY / (
            f"q_learning_{self.target_difficulty}.json"
        )
        agent.save_q_table(model_path)

        comparison = {
            "difficulty": self.target_difficulty,
            "untrained_success": untrained_success,
            "untrained_steps": len(untrained_path) - 1,
            "trained_success": trained_success,
            "trained_steps": len(trained_path) - 1,
            "bfs_steps": len(self.bfs_round_trip) - 1,
        }
        save_training_results(stats, result_path, comparison)

        self.agent = agent
        self.agent_environment = environment
        self.agent_state = environment.reset()
        self.training_stats = stats
        self.agent_path = [environment.mouse_position]
        self.agent_success = trained_success

        print("Comparatie Q-learning:", comparison)
        print("Rata de succes:", f"{stats.success_rate:.1f}%")

    def start_selected_mode(
        self,
        mode: str,
        difficulty: str,
    ) -> None:
        """Pregateste modul si dificultatea alese in meniu."""

        self.current_mode = mode
        self.target_difficulty = difficulty
        self.clear_agent()

        if mode == RANDOM_MODE:
            self.maze_generator = MazeGenerator(
                rows=settings.GRID_ROWS,
                columns=settings.GRID_COLUMNS,
            )
            self.level = self.generate_valid_level()
            self.update_level_components()

        elif mode == EVOLVE_MODE:
            self.maze_generator = MazeGenerator(
                rows=settings.GRID_ROWS,
                columns=settings.GRID_COLUMNS,
            )
            self.level = self.generate_valid_level()
            self.update_level_components()
            self.evolve_current_level()

        else:
            self.level = self.generate_level_for_difficulty(
                difficulty
            )
            self.update_level_components()

        if mode == AGENT_MODE:
            self.setup_agent()

        self.has_started = True
        self.print_level_information()

    def generate_new_level(self) -> None:
        """Reporneste modul curent pe un nivel nou."""

        self.start_selected_mode(
            self.current_mode,
            self.target_difficulty,
        )

    def print_level_information(
        self,
    ) -> None:
        """Print debugging information about the level."""

        print()
        print(
            self.level.to_text()
        )

        print(
            "Shortest path length:",
            self.shortest_path_length,
        )

        print(
            "Number of traps:",
            len(self.entity_manager.traps),
        )
        print("Mode:", MODE_LABELS[self.current_mode])
        print(
            "Difficulty:",
            get_level_difficulty(self.level),
            calculate_difficulty_score(self.level),
        )

    def evolve_current_level(self) -> None:
        """Evolueaza nivelul curent spre dificultatea aleasa."""

        self.current_mode = EVOLVE_MODE
        self.clear_agent()
        initial_score = calculate_difficulty_score(self.level) or 0

        def show_progress(generation, best):
            draw_evolution_progress(
                self.screen,
                initial_score,
                generation,
                best,
            )
            pygame.event.pump()

        initial, best, history = evolve_level(
            self.level,
            self.target_difficulty,
            show_progress,
        )

        save_evolution_result(initial, best, history)
        self.level = best.level
        self.update_level_components()
        self.print_level_information()
        print("Dificultate initiala:", initial.difficulty_score)
        print("Dificultate finala:", best.difficulty_score)

    def handle_events(
        self,
    ) -> None:
        """Handle window and keyboard events."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.is_running = False

            elif not self.has_started:
                selection = self.game_menu.handle_event(event)

                if selection is not None:
                    self.start_selected_mode(*selection)

            elif event.key == pygame.K_m:
                self.has_started = False
                self.entity_manager.mouse.stop_moving()

            elif event.key == pygame.K_r:
                self.generate_new_level()

            elif event.key == pygame.K_b:
                self.show_bfs_path = (
                    not self.show_bfs_path
                )

            elif event.key == pygame.K_e:
                self.evolve_current_level()

    def get_pressed_movement(
        self,
    ) -> tuple[int, int] | None:
        """Return the movement associated with a held key."""

        pressed_keys = pygame.key.get_pressed()

        if (
            pressed_keys[pygame.K_UP]
            or pressed_keys[pygame.K_w]
        ):
            return -1, 0

        if (
            pressed_keys[pygame.K_DOWN]
            or pressed_keys[pygame.K_s]
        ):
            return 1, 0

        if (
            pressed_keys[pygame.K_LEFT]
            or pressed_keys[pygame.K_a]
        ):
            return 0, -1

        if (
            pressed_keys[pygame.K_RIGHT]
            or pressed_keys[pygame.K_d]
        ):
            return 0, 1

        return None

    def update_mouse_animation_state(
        self,
        current_time: int,
    ) -> None:
        """Update whether the mouse should use walking frames."""

        if self.current_mode == AGENT_MODE:
            return

        mouse = self.entity_manager.mouse
        movement = self.get_pressed_movement()

        can_move = (
            self.has_started
            and self.game_logic.is_playing()
            and not self.game_logic.is_stunned(
                current_time
            )
        )

        if movement is None or not can_move:
            mouse.stop_moving()
            return

        row_change, column_change = movement

        mouse.set_direction_from_movement(
            row_change,
            column_change,
        )

        mouse.start_moving()

    def handle_continuous_movement(
        self,
        current_time: int,
    ) -> None:
        """Move continuously while a movement key is held."""

        if not self.has_started:
            return

        if self.current_mode == AGENT_MODE:
            return

        if not self.game_logic.is_playing():
            return

        if self.game_logic.is_stunned(
            current_time
        ):
            return

        movement = self.get_pressed_movement()

        if movement is None:
            return

        if (
            current_time - self.last_move_time
            < self.move_delay
        ):
            return

        row_change, column_change = movement

        self.game_logic.move_mouse(
            row_change,
            column_change,
            current_time,
        )

        self.last_move_time = current_time

    def update_agent(self, current_time: int) -> None:
        """Executa urmatoarea actiune a agentului antrenat."""

        if (
            self.agent is None
            or self.agent_environment is None
            or self.agent_state is None
        ):
            return

        mouse = self.entity_manager.mouse

        if self.agent_environment.done:
            mouse.stop_moving()
            return

        elapsed = current_time - self.last_agent_move_time
        if elapsed < settings.AGENT_MOVE_DELAY:
            if elapsed > settings.AGENT_MOVE_DELAY // 2:
                mouse.stop_moving()
            return

        action = self.agent.choose_action(
            self.agent_state,
            training=False,
        )
        row_change, column_change = (
            self.agent_environment.ACTIONS[action]
        )
        old_position = self.agent_environment.mouse_position
        had_cheese = self.agent_environment.has_cheese
        next_state, _, done = self.agent_environment.step(action)
        new_position = self.agent_environment.mouse_position

        mouse.set_direction_from_movement(
            row_change,
            column_change,
        )

        if new_position != old_position:
            mouse.set_position(new_position)
            mouse.register_move()
            mouse.start_moving()
            self.agent_path.append(new_position)

            for trap in self.entity_manager.traps:
                if trap.position == new_position and trap.is_active:
                    trap.trigger()
                    break
        else:
            mouse.stop_moving()

        if self.agent_environment.has_cheese and not had_cheese:
            self.entity_manager.cheese.collect()
            mouse.collect_cheese()

        if done:
            self.agent_success = self.agent_environment.success

            if self.agent_success:
                self.game_logic.state = GameState.WON

        self.agent_state = next_state
        self.last_agent_move_time = current_time

    def update_cheese_message(
        self,
        current_time: int,
    ) -> None:
        """Show a temporary message after cheese collection."""

        has_cheese = (
            self.entity_manager.mouse.has_cheese
        )

        if (
            has_cheese
            and not self.previous_cheese_state
        ):
            self.cheese_message_until = (
                current_time
                + settings.CHEESE_MESSAGE_DURATION
            )

        self.previous_cheese_state = has_cheese

    def update(
        self,
    ) -> None:
        """Update the current game state."""

        if not self.has_started:
            return

        current_time = pygame.time.get_ticks()

        if self.current_mode == AGENT_MODE:
            self.update_agent(current_time)
        else:
            self.game_logic.update(current_time)
            self.update_mouse_animation_state(current_time)
            self.handle_continuous_movement(current_time)

        self.update_cheese_message(
            current_time
        )

    def get_game_status(
        self,
        current_time: int,
    ) -> str:
        """Return the current status text."""

        if self.game_logic.state == GameState.WON:
            return "YOU WON"

        if (
            self.current_mode == AGENT_MODE
            and self.agent_environment is not None
            and self.agent_environment.done
        ):
            return "AGENT STOPPED"

        if self.game_logic.is_stunned(
            current_time
        ):
            return "STUNNED"

        if self.game_logic.is_release_message_visible(
            current_time
        ):
            return "FREE AGAIN"

        return "PLAYING"

    def draw_game(
        self,
        current_time: int,
    ) -> None:
        """Draw the active game screen."""

        self.screen.fill(
            settings.BACKGROUND_COLOR
        )

        self.renderer.draw_title()

        self.renderer.draw_level(
            self.level
        )

        if self.show_bfs_path:
            path = (
                self.bfs_round_trip
                if self.current_mode == AGENT_MODE
                else self.bfs_path
            )
            self.renderer.draw_debug_path(
                path
            )

            if self.agent_path:
                self.renderer.draw_agent_path(
                    self.agent_path
                )

        self.renderer.draw_entities(
            self.entity_manager
            .get_active_entities(),
            current_time,
        )

        if settings.SHOW_GRID_LINES:
            self.renderer.draw_grid_lines(
                self.level
            )

        stun_seconds = (
            self.game_logic
            .get_stun_seconds_remaining(
                current_time
            )
        )

        active_traps = sum(
            1
            for trap in self.entity_manager.traps
            if trap.is_active
        )

        self.renderer.draw_sidebar(
            shortest_path_length=(
                self.shortest_path_length
            ),
            moves=(
                self.entity_manager
                .mouse
                .number_of_moves
            ),
            has_cheese=(
                self.entity_manager
                .mouse
                .has_cheese
            ),
            active_traps=active_traps,
            mode=MODE_LABELS[self.current_mode],
            difficulty=self.target_difficulty,
            status=self.get_game_status(
                current_time
            ),
            stun_seconds=stun_seconds,
            has_won=self.game_logic.has_won(),
        )

        self.renderer.draw_mouse_countdown(
            self.entity_manager.mouse,
            stun_seconds,
        )

        if (
            current_time
            < self.cheese_message_until
            and not self.game_logic.has_won()
        ):
            self.renderer.draw_cheese_message()

        if self.game_logic.has_won():
            self.renderer.draw_victory_overlay()

    def draw(
        self,
    ) -> None:
        """Draw the current frame."""

        if not self.has_started:
            self.game_menu.draw()

        else:
            current_time = pygame.time.get_ticks()

            self.draw_game(
                current_time
            )

        pygame.display.flip()

    def run(
        self,
    ) -> None:
        """Run the game until the window is closed."""

        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(
                settings.FPS
            )

        pygame.quit()
