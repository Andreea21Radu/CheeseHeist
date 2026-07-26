"""Main game loop and application lifecycle."""

import pygame

from config import settings
from generation.level_manager import LevelManager
from generation.sample_level import SAMPLE_LEVEL
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

        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.is_running = True

        # we load every image only once
        self.assets = AssetManager()

        # we create a temporary static level for task 2
        self.level = LevelManager(SAMPLE_LEVEL)

        # the renderer receives everything needed for drawing
        self.renderer = Renderer(
            self.screen,
            self.assets,
        )

        self.font = pygame.font.Font(None, 34)

        # we print the map once for debugging
        print(self.level.to_text())

    def handle_events(self) -> None:
        """Handle window and keyboard events."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

    def update(self) -> None:
        """Update the current game state."""

        # the level is static during task 2
        pass

    def draw_title(self) -> None:
        """Draw the current development milestone title."""

        title_surface = self.font.render(
            "Task 2 - Static Grid Preview",
            True,
            settings.TEXT_COLOR,
        )

        self.screen.blit(
            title_surface,
            (settings.MAP_OFFSET_X, 30),
        )

    def draw(self) -> None:
        """Draw the current frame."""

        self.screen.fill(settings.BACKGROUND_COLOR)

        self.draw_title()
        self.renderer.draw_level(self.level)
        self.renderer.draw_grid_lines(self.level)

        pygame.display.flip()

    def run(self) -> None:
        """Run the game until the player closes the window."""

        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(settings.FPS)

        pygame.quit()