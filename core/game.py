"""Main game loop and application lifecycle."""

import pygame

from config import settings
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

        # we load every image only once
        self.assets = AssetManager()

        # we generate the first procedural maze
        self.maze_generator = MazeGenerator(
            rows=settings.GRID_ROWS,
            columns=settings.GRID_COLUMNS,
            seed=settings.DEFAULT_MAZE_SEED,
        )

        self.level = (
            self.maze_generator.generate_maze()
        )

        # the renderer receives everything needed for drawing
        self.renderer = Renderer(
            self.screen,
            self.assets,
        )

        self.font = pygame.font.Font(
            None,
            34,
        )

        # we print the first generated map for debugging
        print(self.level.to_text())

    def generate_new_level(self) -> None:
        """Generate and display a new procedural maze."""

        self.maze_generator = MazeGenerator(
            rows=settings.GRID_ROWS,
            columns=settings.GRID_COLUMNS,
        )

        self.level = (
            self.maze_generator.generate_maze()
        )

        print()
        print("Generated a new maze:")
        print(self.level.to_text())

    def handle_events(self) -> None:
        """Handle window and keyboard events."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                if event.key == pygame.K_r:
                    self.generate_new_level()

    def update(self) -> None:
        """Update the current game state."""

        # there are no moving entities during task 3
        pass

    def draw_title(self) -> None:
        """Draw the current development milestone title."""

        title_surface = self.font.render(
            (
                "Task 3 - Procedural Maze | "
                "Press R to regenerate"
            ),
            True,
            settings.TEXT_COLOR,
        )

        self.screen.blit(
            title_surface,
            (
                settings.MAP_OFFSET_X,
                30,
            ),
        )

    def draw(self) -> None:
        """Draw the current frame."""

        self.screen.fill(
            settings.BACKGROUND_COLOR
        )

        self.draw_title()
        self.renderer.draw_level(
            self.level
        )

        self.renderer.draw_grid_lines(
            self.level
        )

        pygame.display.flip()

    def run(self) -> None:
        """Run the game until the player closes the window."""

        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(
                settings.FPS
            )

        pygame.quit()