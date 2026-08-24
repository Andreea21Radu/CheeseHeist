"""Draw the game level, entities and interface."""

import pygame

from config import settings
from entities.entity import Entity
from entities.mouse import Mouse
from generation.level_manager import LevelManager
from generation.tile_type import TileType
from graphics.asset_manager import AssetManager


class Renderer:
    """Draw the current game state."""

    def __init__(
        self,
        screen: pygame.Surface,
        assets: AssetManager,
    ) -> None:
        self.screen = screen
        self.assets = assets

        self.large_font = pygame.font.Font(
            None,
            58,
        )

        self.medium_font = pygame.font.Font(
            None,
            31,
        )

        self.normal_font = pygame.font.Font(
            None,
            24,
        )

        self.small_font = pygame.font.Font(
            None,
            20,
        )

    def get_tile_position(
        self,
        row: int,
        column: int,
    ) -> tuple[int, int]:
        """Convert a grid position into screen coordinates."""

        screen_x = (
            settings.MAP_OFFSET_X
            + column * settings.TILE_SIZE
        )

        screen_y = (
            settings.MAP_OFFSET_Y
            + row * settings.TILE_SIZE
        )

        return screen_x, screen_y

    def choose_floor_image(
        self,
        row: int,
        column: int,
    ) -> pygame.Surface:
        """Choose one of the available floor variants."""

        if (row + column) % 5 == 0:
            return self.assets.floor_alt

        return self.assets.floor

    def choose_wall_image(
        self,
        row: int,
        column: int,
    ) -> pygame.Surface:
        """Choose one of the available wall variants."""

        if (row + column) % 7 == 0:
            return self.assets.wall_alt

        return self.assets.wall

    def draw_floor(
        self,
        row: int,
        column: int,
    ) -> None:
        """Draw one floor tile."""

        floor_image = self.choose_floor_image(
            row,
            column,
        )

        tile_position = self.get_tile_position(
            row,
            column,
        )

        self.screen.blit(
            floor_image,
            tile_position,
        )

    def draw_tile(
        self,
        tile_type: TileType,
        row: int,
        column: int,
    ) -> None:
        """Draw one level tile."""

        tile_position = self.get_tile_position(
            row,
            column,
        )

        if tile_type == TileType.WALL:
            wall_image = self.choose_wall_image(
                row,
                column,
            )

            self.screen.blit(
                wall_image,
                tile_position,
            )

            return

        self.draw_floor(
            row,
            column,
        )

        if tile_type == TileType.HOME:
            self.screen.blit(
                self.assets.mouse_home,
                tile_position,
            )

    def draw_level(
        self,
        level: LevelManager,
    ) -> None:
        """Draw every tile in the current level."""

        for row in range(level.rows):
            for column in range(level.columns):
                tile_type = level.get_tile(
                    (
                        row,
                        column,
                    )
                )

                self.draw_tile(
                    tile_type,
                    row,
                    column,
                )

    def draw_mouse(
        self,
        mouse: Mouse,
        current_time: int,
    ) -> None:
        """Draw the mouse using its directional animation."""

        if not mouse.is_active:
            return

        frame_index = 0

        if mouse.is_moving:
            animation_delay = getattr(
                settings,
                "MOUSE_ANIMATION_DELAY",
                110,
            )

            frame_index = (
                current_time
                // animation_delay
            ) % 4

        mouse_image = self.assets.get_mouse_frame(
            mouse.direction,
            frame_index,
        )

        screen_position = self.get_tile_position(
            mouse.row,
            mouse.column,
        )

        self.screen.blit(
            mouse_image,
            screen_position,
        )

    def draw_entity(
        self,
        entity: Entity,
        current_time: int,
    ) -> None:
        """Draw one active entity at its grid position."""

        if not entity.is_active:
            return

        if isinstance(entity, Mouse):
            self.draw_mouse(
                entity,
                current_time,
            )
            return

        entity_image = self.assets.get_image(
            entity.sprite_name
        )

        screen_position = self.get_tile_position(
            entity.row,
            entity.column,
        )

        self.screen.blit(
            entity_image,
            screen_position,
        )

    def draw_entities(
        self,
        entities: list[Entity],
        current_time: int,
    ) -> None:
        """Draw all active entities from the current level."""

        for entity in entities:
            self.draw_entity(
                entity,
                current_time,
            )

    def draw_grid_lines(
        self,
        level: LevelManager,
    ) -> None:
        """Draw lines separating the grid tiles."""

        grid_width = (
            level.columns
            * settings.TILE_SIZE
        )

        grid_height = (
            level.rows
            * settings.TILE_SIZE
        )

        for column in range(
            level.columns + 1
        ):
            x_position = (
                settings.MAP_OFFSET_X
                + column * settings.TILE_SIZE
            )

            pygame.draw.line(
                self.screen,
                settings.GRID_LINE_COLOR,
                (
                    x_position,
                    settings.MAP_OFFSET_Y,
                ),
                (
                    x_position,
                    settings.MAP_OFFSET_Y
                    + grid_height,
                ),
            )

        for row in range(
            level.rows + 1
        ):
            y_position = (
                settings.MAP_OFFSET_Y
                + row * settings.TILE_SIZE
            )

            pygame.draw.line(
                self.screen,
                settings.GRID_LINE_COLOR,
                (
                    settings.MAP_OFFSET_X,
                    y_position,
                ),
                (
                    settings.MAP_OFFSET_X
                    + grid_width,
                    y_position,
                ),
            )

    def draw_debug_path(
        self,
        path: list[tuple[int, int]],
    ) -> None:
        """Draw the shortest BFS path."""

        if len(path) <= 1:
            return

        circle_radius = max(
            3,
            settings.TILE_SIZE // 7,
        )

        for row, column in path[1:]:
            center_x = (
                settings.MAP_OFFSET_X
                + column * settings.TILE_SIZE
                + settings.TILE_SIZE // 2
            )

            center_y = (
                settings.MAP_OFFSET_Y
                + row * settings.TILE_SIZE
                + settings.TILE_SIZE // 2
            )

            pygame.draw.circle(
                self.screen,
                settings.DEBUG_PATH_COLOR,
                (
                    center_x,
                    center_y,
                ),
                circle_radius,
            )

    def draw_title(
        self,
    ) -> None:
        """Draw the game title and controls."""

        title_surface = self.medium_font.render(
            "CHEESE HEIST",
            True,
            settings.ACCENT_COLOR,
        )

        controls_surface = self.small_font.render(
            (
                "WASD / Arrows: move    R: new maze    "
                "B: shortest path    E: evolve    M: menu"
            ),
            True,
            settings.SECONDARY_TEXT_COLOR,
        )

        self.screen.blit(
            title_surface,
            (
                settings.MAP_OFFSET_X,
                20,
            ),
        )

        self.screen.blit(
            controls_surface,
            (
                settings.MAP_OFFSET_X + 175,
                27,
            ),
        )

    def render_fitted_text(
        self,
        text: str,
        color: tuple[int, int, int],
        maximum_width: int,
        initial_size: int = 24,
        minimum_size: int = 16,
    ) -> pygame.Surface:
        """Render text small enough to fit inside a width."""

        font_size = initial_size

        while font_size >= minimum_size:
            font = pygame.font.Font(
                None,
                font_size,
            )

            surface = font.render(
                text,
                True,
                color,
            )

            if surface.get_width() <= maximum_width:
                return surface

            font_size -= 1

        font = pygame.font.Font(
            None,
            minimum_size,
        )

        return font.render(
            text,
            True,
            color,
        )

    def calculate_efficiency(
        self,
        shortest_path_length: int,
        moves: int,
        has_won: bool,
    ) -> str:
        """Calculate the final round-trip efficiency."""

        if not has_won or moves <= 0:
            return "--"

        optimal_round_trip = (
            shortest_path_length
            * 2
        )

        efficiency = (
            optimal_round_trip
            / moves
            * 100
        )

        efficiency = min(
            efficiency,
            100.0,
        )

        return f"{efficiency:.0f}%"

    def draw_sidebar_item(
        self,
        panel_x: int,
        item_y: int,
        panel_width: int,
        label: str,
        value: str,
        value_color: tuple[int, int, int],
    ) -> None:
        """Draw one label and value inside the sidebar."""

        horizontal_padding = 22

        maximum_width = (
            panel_width
            - horizontal_padding * 2
        )

        label_surface = self.small_font.render(
            label,
            True,
            settings.SECONDARY_TEXT_COLOR,
        )

        value_surface = self.render_fitted_text(
            value,
            value_color,
            maximum_width,
        )

        self.screen.blit(
            label_surface,
            (
                panel_x + horizontal_padding,
                item_y,
            ),
        )

        self.screen.blit(
            value_surface,
            (
                panel_x + horizontal_padding,
                item_y + 18,
            ),
        )

    def draw_sidebar(
        self,
        shortest_path_length: int,
        moves: int,
        has_cheese: bool,
        active_traps: int,
        status: str,
        stun_seconds: int,
        has_won: bool,
    ) -> None:
        """Draw gameplay information inside the sidebar."""

        map_width = (
            settings.GRID_COLUMNS
            * settings.TILE_SIZE
        )

        panel_x = (
            settings.MAP_OFFSET_X
            + map_width
            + settings.SIDEBAR_GAP
        )

        panel_y = settings.MAP_OFFSET_Y

        available_width = (
            self.screen.get_width()
            - panel_x
            - 20
        )

        panel_width = max(
            220,
            available_width,
        )

        map_height = (
            settings.GRID_ROWS
            * settings.TILE_SIZE
        )

        available_height = (
            self.screen.get_height()
            - panel_y
            - 20
        )

        panel_height = min(
            map_height,
            available_height,
        )

        panel_rectangle = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height,
        )

        pygame.draw.rect(
            self.screen,
            settings.PANEL_COLOR,
            panel_rectangle,
            border_radius=12,
        )

        heading_surface = self.medium_font.render(
            "MISSION",
            True,
            settings.ACCENT_COLOR,
        )

        self.screen.blit(
            heading_surface,
            (
                panel_x + 22,
                panel_y + 18,
            ),
        )

        cheese_text = (
            "Collected"
            if has_cheese
            else "Not collected"
        )

        cheese_color = (
            settings.SUCCESS_COLOR
            if has_cheese
            else settings.TEXT_COLOR
        )

        status_color = settings.TEXT_COLOR

        if status == "STUNNED":
            status_color = settings.WARNING_COLOR

        elif status == "YOU WON":
            status_color = settings.SUCCESS_COLOR

        efficiency_text = self.calculate_efficiency(
            shortest_path_length,
            moves,
            has_won,
        )

        efficiency_color = (
            settings.SUCCESS_COLOR
            if has_won
            else settings.SECONDARY_TEXT_COLOR
        )

        information = [
            (
                "Goal",
                "Collect cheese, return home",
                settings.TEXT_COLOR,
            ),
            (
                "Best path",
                f"{shortest_path_length} moves",
                settings.TEXT_COLOR,
            ),
            (
                "Your moves",
                str(moves),
                settings.TEXT_COLOR,
            ),
            (
                "Efficiency",
                efficiency_text,
                efficiency_color,
            ),
            (
                "Cheese",
                cheese_text,
                cheese_color,
            ),
            (
                "Active traps",
                str(active_traps),
                settings.TEXT_COLOR,
            ),
            (
                "Status",
                status,
                status_color,
            ),
        ]

        item_spacing = 50
        start_y = panel_y + 61

        for index, (
            label,
            value,
            value_color,
        ) in enumerate(information):
            item_y = (
                start_y
                + index * item_spacing
            )

            self.draw_sidebar_item(
                panel_x=panel_x,
                item_y=item_y,
                panel_width=panel_width,
                label=label,
                value=value,
                value_color=value_color,
            )

        if stun_seconds > 0:
            penalty_surface = self.render_fitted_text(
                f"Free in {stun_seconds} seconds",
                settings.WARNING_COLOR,
                panel_width - 44,
            )

            self.screen.blit(
                penalty_surface,
                (
                    panel_x + 22,
                    panel_y
                    + panel_height
                    - 30,
                ),
            )

    def draw_mouse_countdown(
        self,
        mouse: Mouse,
        seconds_remaining: int,
    ) -> None:
        """Draw a countdown above a stunned mouse."""

        if seconds_remaining <= 0:
            return

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
            - 25
        )

        countdown_surface = self.medium_font.render(
            str(seconds_remaining),
            True,
            settings.WARNING_COLOR,
        )

        countdown_rectangle = countdown_surface.get_rect(
            center=(
                center_x,
                text_y,
            )
        )

        self.screen.blit(
            countdown_surface,
            countdown_rectangle,
        )

    def draw_center_message(
        self,
        title: str,
        subtitle: str,
        title_color: tuple[int, int, int],
    ) -> None:
        """Draw a centered translucent message overlay."""

        overlay = pygame.Surface(
            self.screen.get_size(),
            pygame.SRCALPHA,
        )

        overlay.fill(
            settings.OVERLAY_COLOR
        )

        self.screen.blit(
            overlay,
            (0, 0),
        )

        title_surface = self.large_font.render(
            title,
            True,
            title_color,
        )

        subtitle_surface = self.medium_font.render(
            subtitle,
            True,
            settings.TEXT_COLOR,
        )

        center_x = (
            self.screen.get_width()
            // 2
        )

        center_y = (
            self.screen.get_height()
            // 2
        )

        title_rectangle = title_surface.get_rect(
            center=(
                center_x,
                center_y - 35,
            )
        )

        subtitle_rectangle = subtitle_surface.get_rect(
            center=(
                center_x,
                center_y + 30,
            )
        )

        self.screen.blit(
            title_surface,
            title_rectangle,
        )

        self.screen.blit(
            subtitle_surface,
            subtitle_rectangle,
        )

    def draw_start_screen(
        self,
    ) -> None:
        """Draw the initial game screen."""

        self.screen.fill(
            settings.BACKGROUND_COLOR
        )

        title_surface = self.large_font.render(
            "CHEESE HEIST",
            True,
            settings.ACCENT_COLOR,
        )

        mission_surface = self.medium_font.render(
            "Find the cheese and bring it home.",
            True,
            settings.TEXT_COLOR,
        )

        controls_surface = self.normal_font.render(
            "Move with WASD or the arrow keys",
            True,
            settings.SECONDARY_TEXT_COLOR,
        )

        start_surface = self.medium_font.render(
            "Press SPACE to start",
            True,
            settings.SUCCESS_COLOR,
        )

        center_x = (
            self.screen.get_width()
            // 2
        )

        center_y = (
            self.screen.get_height()
            // 2
        )

        surfaces = [
            (
                title_surface,
                center_y - 105,
            ),
            (
                mission_surface,
                center_y - 30,
            ),
            (
                controls_surface,
                center_y + 15,
            ),
            (
                start_surface,
                center_y + 85,
            ),
        ]

        for surface, y_position in surfaces:
            rectangle = surface.get_rect(
                center=(
                    center_x,
                    y_position,
                )
            )

            self.screen.blit(
                surface,
                rectangle,
            )

    def draw_victory_overlay(
        self,
    ) -> None:
        """Draw the victory message."""

        self.draw_center_message(
            title="YOU WON!",
            subtitle="Press R to generate a new maze",
            title_color=settings.SUCCESS_COLOR,
        )

    def draw_cheese_message(
        self,
    ) -> None:
        """Draw a temporary cheese collection message."""

        message_surface = self.normal_font.render(
            "Cheese collected! Return home!",
            True,
            settings.ACCENT_COLOR,
        )

        message_rectangle = message_surface.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() - 30,
            )
        )

        self.screen.blit(
            message_surface,
            message_rectangle,
        )
