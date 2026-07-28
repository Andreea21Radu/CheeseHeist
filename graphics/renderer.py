"""Draw the game level and its entities."""

import pygame

from config import settings
from entities.entity import Entity
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

        # floor, home, cheese and trap are all walkable cells
        self.draw_floor(
            row,
            column,
        )

        # home remains part of the level and stays visible
        if tile_type == TileType.HOME:
            self.screen.blit(
                self.assets.mouse_home,
                tile_position,
            )

        # cheese and traps are not drawn here
        # they are drawn separately as entities

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

    def draw_entity(
        self,
        entity: Entity,
    ) -> None:
        """Draw one active entity at its grid position."""

        if not entity.is_active:
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
    ) -> None:
        """Draw all active entities from the current level."""

        for entity in entities:
            self.draw_entity(
                entity
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
        """Draw the BFS path without covering the mouse home."""

        if len(path) <= 1:
            return

        # skip only the first position because it represents the home
        path_without_home = path[1:]

        for row, column in path_without_home:
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
                5,
            )