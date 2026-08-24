"""Meniul principal si ecranele de progres."""

from typing import Optional

import pygame

from config import settings


HUMAN_MODE = "human"
AGENT_MODE = "agent"
RANDOM_MODE = "random"
EVOLVE_MODE = "evolve"

MODE_OPTIONS = (
    (HUMAN_MODE, "Human Play"),
    (AGENT_MODE, "Watch Trained Agent"),
    (RANDOM_MODE, "Generate Random Level"),
    (EVOLVE_MODE, "Evolve Level"),
)

MODE_LABELS = dict(MODE_OPTIONS)


class GameMenu:
    """Permite alegerea modului si a dificultatii."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.selected_mode = 0
        self.selected_difficulty = settings.DIFFICULTY_LEVELS.index(
            settings.DEFAULT_DIFFICULTY
        )

        self.title_font = pygame.font.Font(None, 55)
        self.heading_font = pygame.font.Font(None, 28)
        self.option_font = pygame.font.Font(None, 32)

    @property
    def mode(self) -> str:
        return MODE_OPTIONS[self.selected_mode][0]

    @property
    def difficulty(self) -> str:
        return settings.DIFFICULTY_LEVELS[
            self.selected_difficulty
        ]

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> Optional[tuple[str, str]]:
        """Schimba optiunile sau confirma selectia."""

        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_UP:
            self.selected_mode = (
                self.selected_mode - 1
            ) % len(MODE_OPTIONS)

        elif event.key == pygame.K_DOWN:
            self.selected_mode = (
                self.selected_mode + 1
            ) % len(MODE_OPTIONS)

        elif event.key == pygame.K_LEFT:
            self.selected_difficulty = (
                self.selected_difficulty - 1
            ) % len(settings.DIFFICULTY_LEVELS)

        elif event.key == pygame.K_RIGHT:
            self.selected_difficulty = (
                self.selected_difficulty + 1
            ) % len(settings.DIFFICULTY_LEVELS)

        elif event.key in {
            pygame.K_RETURN,
            pygame.K_SPACE,
        }:
            return self.mode, self.difficulty

        return None

    def draw(self) -> None:
        """Deseneaza modurile si dificultatile disponibile."""

        self.screen.fill(settings.BACKGROUND_COLOR)

        center_x = self.screen.get_width() // 2

        title = self.title_font.render(
            "CHEESE HEIST",
            True,
            settings.ACCENT_COLOR,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(center_x, 55)
            ),
        )

        mode_heading = self.heading_font.render(
            "MODE",
            True,
            settings.SECONDARY_TEXT_COLOR,
        )
        self.screen.blit(
            mode_heading,
            mode_heading.get_rect(center=(center_x, 105)),
        )

        for index, (_, label) in enumerate(MODE_OPTIONS):
            rectangle = pygame.Rect(
                center_x - 215,
                130 + index * 55,
                430,
                44,
            )
            self.draw_option(
                rectangle,
                label,
                index == self.selected_mode,
            )

        difficulty_heading = self.heading_font.render(
            "DIFFICULTY",
            True,
            settings.SECONDARY_TEXT_COLOR,
        )
        self.screen.blit(
            difficulty_heading,
            difficulty_heading.get_rect(center=(center_x, 380)),
        )

        option_width = 150
        start_x = center_x - 235

        for index, difficulty in enumerate(
            settings.DIFFICULTY_LEVELS
        ):
            rectangle = pygame.Rect(
                start_x + index * (option_width + 10),
                405,
                option_width,
                48,
            )
            self.draw_option(
                rectangle,
                difficulty.upper(),
                index == self.selected_difficulty,
            )

        start_text = self.heading_font.render(
            "ENTER / SPACE TO START",
            True,
            settings.SUCCESS_COLOR,
        )
        self.screen.blit(
            start_text,
            start_text.get_rect(center=(center_x, 525)),
        )

    def draw_option(
        self,
        rectangle: pygame.Rect,
        text: str,
        selected: bool,
    ) -> None:
        """Deseneaza o optiune a meniului."""

        color = (
            settings.ACCENT_COLOR
            if selected
            else settings.PANEL_COLOR
        )
        text_color = (
            settings.BACKGROUND_COLOR
            if selected
            else settings.TEXT_COLOR
        )
        pygame.draw.rect(
            self.screen,
            color,
            rectangle,
            border_radius=6,
        )
        surface = self.option_font.render(
            text,
            True,
            text_color,
        )
        self.screen.blit(
            surface,
            surface.get_rect(center=rectangle.center),
        )


def draw_evolution_progress(
    screen: pygame.Surface,
    initial_score: float,
    generation: int,
    best,
) -> None:
    """Afiseaza progresul algoritmului genetic."""

    screen.fill(settings.BACKGROUND_COLOR)
    font = pygame.font.Font(None, 32)
    current_score = best.difficulty_score or 0.0

    lines = [
        f"Dificultate initiala: {initial_score:.2f}",
        f"Generatia: {generation}/{settings.GA_GENERATIONS}",
        f"Cel mai bun fitness: {best.fitness:.2f}",
        f"Dificultate curenta: {current_score:.2f}",
    ]

    for index, line in enumerate(lines):
        text = font.render(line, True, settings.TEXT_COLOR)
        screen.blit(text, (100, 150 + index * 45))

    pygame.display.flip()


def draw_training_progress(
    screen: pygame.Surface,
    episode: int,
    stats,
) -> None:
    """Afiseaza progresul antrenarii agentului."""

    screen.fill(settings.BACKGROUND_COLOR)
    font = pygame.font.Font(None, 32)
    recent_successes = sum(stats.successes[-100:])
    recent_episodes = len(stats.successes[-100:])
    recent_rate = recent_successes / max(1, recent_episodes) * 100

    lines = [
        f"Episod: {episode}/{settings.Q_LEARNING_EPISODES}",
        f"Rata de succes: {stats.success_rate:.1f}%",
        f"Ultimele 100: {recent_rate:.1f}%",
        f"Epsilon: {stats.epsilon_values[-1]:.3f}",
    ]

    for index, line in enumerate(lines):
        text = font.render(line, True, settings.TEXT_COLOR)
        screen.blit(text, (100, 150 + index * 45))

    pygame.display.flip()
