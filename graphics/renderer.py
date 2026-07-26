"""Draw the level grid and its visual elements."""

import pygame

from config import settings
from generation.level_manager import LevelManager
from generation.tile_type import TileType
from graphics.asset_manager import AssetManager


class Renderer:
    """Draw the current game level using the loaded image assets."""

    def __init__(
        self,
        screen: pygame.Surface,
        assets: AssetManager,
    ) -> None:
        self.screen = screen
        self.assets = assets

    def draw_level(self, level: LevelManager) -> None:
        """Draw every tile stored inside the level grid."""

        for row in range(level.rows):
            for column in range(level.columns):
                position = (row, column)
                tile_type = level.get_tile(position)

                self._draw_tile(
                    tile_type,
                    row,
                    column,
                )

    def _draw_tile(
        self,
        tile_type: TileType,
        row: int,
        column: int,
    ) -> None:
        """Draw one tile at its corresponding screen position."""

        x = settings.MAP_OFFSET_X + column * settings.TILE_SIZE
        y = settings.MAP_OFFSET_Y + row * settings.TILE_SIZE

        screen_position = (x, y)

        if tile_type == TileType.WALL:
            self.screen.blit(
                self.assets.wall,
                screen_position,
            )
            return

        # we draw the floor below every walkable object
        self.screen.blit(
            self.assets.floor,
            screen_position,
        )

        if tile_type == TileType.HOME:
            self.screen.blit(
                self.assets.mouse_home,
                screen_position,
            )

        elif tile_type == TileType.CHEESE:
            self.screen.blit(
                self.assets.cheese,
                screen_position,
            )

        elif tile_type == TileType.TRAP:
            self.screen.blit(
                self.assets.trap,
                screen_position,
            )

    def draw_grid_lines(self, level: LevelManager) -> None:
        """Draw subtle grid lines used while debugging the map."""

        for row in range(level.rows):
            for column in range(level.columns):
                x = settings.MAP_OFFSET_X + column * settings.TILE_SIZE
                y = settings.MAP_OFFSET_Y + row * settings.TILE_SIZE

                tile_rectangle = pygame.Rect(
                    x,
                    y,
                    settings.TILE_SIZE,
                    settings.TILE_SIZE,
                )

                pygame.draw.rect(
                    self.screen,
                    settings.GRID_LINE_COLOR,
                    tile_rectangle,
                    width=1,
                )