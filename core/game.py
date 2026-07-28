"""Main game loop and application lifecycle."""

import pygame

from config import settings
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
        """Recreate everything that depends on the current level."""

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
        """Print debugging information about the current level."""

        print()
        print(self.level.to_text())

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

            if event.key == pygame.K_r:
                self.generate_new_level()

            if event.key == pygame.K_b:
                self.show_bfs_path = (
                    not self.show_bfs_path
                )

    def update(
        self,
    ) -> None:
        """Update the current game state."""

        # movement and collision logic will be added in task 6
        pass

    def draw_title(
        self,
    ) -> None:
        """Draw the current development milestone title."""

        title_text = (
            "Task 5 - Entity System | "
            "R: new maze | B: show path"
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

    def draw_level_information(
        self,
    ) -> None:
        """Draw information about the current level."""

        path_length_text = (
            "Shortest path: "
            f"{self.shortest_path_length} steps"
        )

        playability_text = (
            "Playable level: yes"
        )

        trap_count_text = (
            "Traps: "
            f"{len(self.entity_manager.traps)}"
        )

        path_length_surface = self.font.render(
            path_length_text,
            True,
            settings.TEXT_COLOR,
        )

        playability_surface = self.font.render(
            playability_text,
            True,
            settings.ACCENT_COLOR,
        )

        trap_count_surface = self.font.render(
            trap_count_text,
            True,
            settings.TEXT_COLOR,
        )

        information_x = (
            settings.MAP_OFFSET_X
            + settings.GRID_COLUMNS
            * settings.TILE_SIZE
            + 35
        )

        self.screen.blit(
            path_length_surface,
            (
                information_x,
                settings.MAP_OFFSET_Y,
            ),
        )

        self.screen.blit(
            playability_surface,
            (
                information_x,
                settings.MAP_OFFSET_Y + 45,
            ),
        )

        self.screen.blit(
            trap_count_surface,
            (
                information_x,
                settings.MAP_OFFSET_Y + 90,
            ),
        )

    def draw(
        self,
    ) -> None:
        """Draw the current frame."""

        self.screen.fill(
            settings.BACKGROUND_COLOR
        )

        self.draw_title()

        # draw the maze background first
        self.renderer.draw_level(
            self.level
        )

        # draw cheese, traps and mouse over the maze
        self.renderer.draw_entities(
            self.entity_manager
            .get_active_entities()
        )

        # draw grid lines over the level and entities
        if settings.SHOW_GRID_LINES:
            self.renderer.draw_grid_lines(
                self.level
            )

        # draw BFS last so the point remains visible on the cheese
        if self.show_bfs_path:
            self.renderer.draw_debug_path(
                self.bfs_path
            )

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