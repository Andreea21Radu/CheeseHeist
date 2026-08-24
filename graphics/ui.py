"""Meniul pentru selectarea dificultatii."""

from typing import Optional

import pygame

from config import settings


class DifficultyMenu:
    """Permite utilizatorului sa aleaga dificultatea."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.options = settings.DIFFICULTY_LEVELS

        self.selected_index = self.options.index(
            settings.DEFAULT_DIFFICULTY
        )

        self.title_font = pygame.font.Font(None, 55)
        self.option_font = pygame.font.Font(None, 32)

    @property
    def selected_difficulty(self) -> str:
        return self.options[self.selected_index]

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> Optional[str]:
        """Schimba sau confirma dificultatea."""

        if event.type != pygame.KEYDOWN:
            return None

        if event.key in {
            pygame.K_LEFT,
            pygame.K_UP,
        }:
            self.selected_index = (
                self.selected_index - 1
            ) % len(self.options)

        elif event.key in {
            pygame.K_RIGHT,
            pygame.K_DOWN,
        }:
            self.selected_index = (
                self.selected_index + 1
            ) % len(self.options)

        elif event.key in {
            pygame.K_RETURN,
            pygame.K_SPACE,
        }:
            return self.selected_difficulty

        return None

    def draw(self) -> None:
        """Deseneaza optiunile de dificultate."""

        self.screen.fill(settings.BACKGROUND_COLOR)

        center_x = self.screen.get_width() // 2

        title = self.title_font.render(
            "SELECT DIFFICULTY",
            True,
            settings.ACCENT_COLOR,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(center_x, 180)
            ),
        )

        option_width = 180
        gap = 20

        total_width = (
            len(self.options) * option_width
            + (len(self.options) - 1) * gap
        )

        start_x = center_x - total_width // 2

        for index, difficulty in enumerate(
            self.options
        ):
            rectangle = pygame.Rect(
                start_x + index * (option_width + gap),
                290,
                option_width,
                60,
            )

            selected = index == self.selected_index

            color = (
                settings.ACCENT_COLOR
                if selected
                else settings.PANEL_COLOR
            )

            pygame.draw.rect(
                self.screen,
                color,
                rectangle,
                border_radius=6,
            )

            text_color = (
                settings.BACKGROUND_COLOR
                if selected
                else settings.TEXT_COLOR
            )

            text = self.option_font.render(
                difficulty.upper(),
                True,
                text_color,
            )

            self.screen.blit(
                text,
                text.get_rect(
                    center=rectangle.center
                ),
            )
