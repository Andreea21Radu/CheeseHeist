"""Main game loop and application lifecycle."""

import pygame

from config import settings


class Game:
    """Controls the main loop of the Cheese Heist application."""

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        )

        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.is_running = True

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

        # the game does not have moving entities yet
        pass

    def draw(self) -> None:
        """Draw the current frame."""

        self.screen.fill(settings.BACKGROUND_COLOR)

        pygame.display.flip()

    def run(self) -> None:
        """Run the game until the player closes the window."""

        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(settings.FPS)

        pygame.quit()