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

        # control the speed of continuous movement
        self.last_move_time = 0
        self.move_delay = 160

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

        self.font = pygame.font.Font(
            None,
            30,
        )

        self.large_font = pygame.font.Font(
            None,
            44,
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

        # allow immediate movement after generating a new level
        self.last_move_time = 0

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

            elif event.key == pygame.K_r:
                self.generate_new_level()

            elif event.key == pygame.K_b:
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

    def handle_continuous_movement(
        self,
        current_time: int,
    ) -> None:
        """Move continuously while a movement key is held."""

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

        # delay both valid and blocked movement attempts
        self.last_move_time = current_time

    def update(
        self,
    ) -> None:
        """Update the current game state."""

        current_time = pygame.time.get_ticks()

        self.game_logic.update(
            current_time
        )

        self.handle_continuous_movement(
            current_time
        )

    def draw_title(
        self,
    ) -> None:
        """Draw the current gameplay controls."""

        title_text = (
            "Cheese Heist | "
            "WASD/Arrows: move | "
            "R: new maze | B: path"
        )

        title_surface = self.font.render(
            title_text,
            True,
            settings.TEXT_COLOR,
        )

        self.screen.blit(
            title_surface,
            (
                settings.MAP_OFFSET_X,
                25,
            ),
        )

    def get_game_status(
        self,
        current_time: int,
    ) -> str:
        """Return the current status text."""

        if self.game_logic.state == GameState.WON:
            return "Status: YOU WON!"

        if self.game_logic.is_stunned(
            current_time
        ):
            return "Status: STUNNED"

        if self.game_logic.is_release_message_visible(
            current_time
        ):
            return "Status: YOU ARE FREE!"

        return "Status: playing"

    def draw_level_information(
        self,
    ) -> None:
        """Draw gameplay and level information."""

        current_time = pygame.time.get_ticks()
        mouse = self.entity_manager.mouse

        path_text = (
            "Shortest path: "
            f"{self.shortest_path_length} steps"
        )

        moves_text = (
            f"Moves: {mouse.number_of_moves}"
        )

        cheese_status = (
            "Cheese: collected"
            if mouse.has_cheese
            else "Cheese: not collected"
        )

        game_status = self.get_game_status(
            current_time
        )

        active_traps = sum(
            1
            for trap in self.entity_manager.traps
            if trap.is_active
        )

        information = [
            path_text,
            moves_text,
            cheese_status,
            game_status,
            (
                "Active traps: "
                f"{active_traps}"
            ),
        ]

        if self.game_logic.is_stunned(
            current_time
        ):
            seconds_remaining = (
                self.game_logic
                .get_stun_seconds_remaining(
                    current_time
                )
            )

            information.append(
                "Trap penalty: "
                f"{seconds_remaining}"
            )

        elif (
            self.game_logic
            .is_release_message_visible(
                current_time
            )
        ):
            information.append(
                "You can move again!"
            )

        information_x = (
            settings.MAP_OFFSET_X
            + settings.GRID_COLUMNS
            * settings.TILE_SIZE
            + 35
        )

        for index, text in enumerate(
            information
        ):
            text_color = settings.TEXT_COLOR

            if index >= 3:
                text_color = settings.ACCENT_COLOR

            text_surface = self.font.render(
                text,
                True,
                text_color,
            )

            self.screen.blit(
                text_surface,
                (
                    information_x,
                    settings.MAP_OFFSET_Y
                    + index * 42,
                ),
            )

    def draw_trap_penalty_overlay(
        self,
    ) -> None:
        """Draw a countdown above the stunned mouse."""

        current_time = pygame.time.get_ticks()

        if not self.game_logic.is_stunned(
            current_time
        ):
            return

        seconds_remaining = (
            self.game_logic
            .get_stun_seconds_remaining(
                current_time
            )
        )

        mouse = self.entity_manager.mouse

        center_x = (
            settings.MAP_OFFSET_X
            + mouse.column
            * settings.TILE_SIZE
            + settings.TILE_SIZE // 2
        )

        text_y = (
            settings.MAP_OFFSET_Y
            + mouse.row
            * settings.TILE_SIZE
            - 35
        )

        countdown_surface = (
            self.large_font.render(
                str(seconds_remaining),
                True,
                settings.ACCENT_COLOR,
            )
        )

        countdown_rectangle = (
            countdown_surface.get_rect(
                center=(
                    center_x,
                    text_y,
                )
            )
        )

        self.screen.blit(
            countdown_surface,
            countdown_rectangle,
        )

    def draw(
        self,
    ) -> None:
        """Draw the current frame."""

        self.screen.fill(
            settings.BACKGROUND_COLOR
        )

        self.draw_title()

        self.renderer.draw_level(
            self.level
        )

        self.renderer.draw_entities(
            self.entity_manager
            .get_active_entities()
        )

        if settings.SHOW_GRID_LINES:
            self.renderer.draw_grid_lines(
                self.level
            )

        if self.show_bfs_path:
            self.renderer.draw_debug_path(
                self.bfs_path
            )

        self.draw_trap_penalty_overlay()
        self.draw_level_information()

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