"""Main game loop and application lifecycle."""

import pygame

from config import settings
from core.game_logic import GameLogic
from core.game_state import GameState
from entities.entity_manager import EntityManager
from generation.level_manager import LevelManager
from generation.level_validator import LevelValidator
from generation.maze_generator import MazeGenerator
from graphics.asset_manager import AssetManager
from graphics.renderer import Renderer


class Game:
    """Control the main loop of the Cheese Heist application."""

    def __init__(self) -> None:
        pygame.init()

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

        self.last_move_time = 0
        self.move_delay = settings.MOVE_DELAY

        self.cheese_message_until = 0
        self.previous_cheese_state = False

        self.assets = AssetManager()

        self.maze_generator = MazeGenerator(
            rows=settings.GRID_ROWS,
            columns=settings.GRID_COLUMNS,
            seed=settings.DEFAULT_MAZE_SEED,
        )

        self.level = self.generate_valid_level()

        self.level_validator = LevelValidator(
            self.level
        )

        self.bfs_path = (
            self.level_validator
            .get_home_to_cheese_path()
        )

        self.shortest_path_length = (
            self.level_validator
            .get_shortest_path_length()
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

        self.show_bfs_path = (
            settings.SHOW_BFS_PATH_BY_DEFAULT
        )

        self.renderer = Renderer(
            self.screen,
            self.assets,
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

        self.shortest_path_length = (
            self.level_validator
            .get_shortest_path_length()
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
        self.cheese_message_until = 0
        self.previous_cheese_state = False

    def generate_new_level(
        self,
    ) -> None:
        """Generate and validate a new procedural maze."""

        self.maze_generator = MazeGenerator(
            rows=settings.GRID_ROWS,
            columns=settings.GRID_COLUMNS,
        )

        self.level = self.generate_valid_level()

        self.update_level_components()
        self.print_level_information()

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

            elif (
                event.key == pygame.K_SPACE
                and not self.has_started
            ):
                self.has_started = True

            elif (
                event.key == pygame.K_r
                and self.has_started
            ):
                self.generate_new_level()

            elif (
                event.key == pygame.K_b
                and self.has_started
            ):
                self.show_bfs_path = (
                    not self.show_bfs_path
                )

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

        self.game_logic.update(
            current_time
        )

        self.update_mouse_animation_state(
            current_time
        )

        self.handle_continuous_movement(
            current_time
        )

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
            self.renderer.draw_debug_path(
                self.bfs_path
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
            self.renderer.draw_start_screen()

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