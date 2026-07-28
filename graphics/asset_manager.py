"""Load and store the image assets used by the game."""

from pathlib import Path

import pygame

from config import settings


class AssetManager:
    """Load all game images from the assets folder."""

    def __init__(self) -> None:
        self.assets_path = Path("assets/images")

        self.wall = self._load_and_scale_image(
            "tiles/wall.png"
        )

        self.wall_alt = self._load_and_scale_image(
            "tiles/wall_alt.png"
        )

        self.floor = self._load_and_scale_image(
            "tiles/floor.png"
        )

        self.floor_alt = self._load_and_scale_image(
            "tiles/floor_alt.png"
        )

        self.cheese = self._load_and_scale_image(
            "items/cheese.png"
        )

        self.trap = self._load_and_scale_image(
            "items/trap.png"
        )

        self.mouse_home = self._load_and_scale_image(
            "environment/mouse_home.png"
        )

        self.mouse_spritesheet = self._load_image(
            "mouse/mouse_spritesheet.png"
        )

        # for now we use the first frame from the mouse spritesheet
        self.mouse = self._extract_sprite(
            sprite_sheet=self.mouse_spritesheet,
            x=0,
            y=0,
            width=settings.TILE_SIZE,
            height=settings.TILE_SIZE,
        )

    def _load_image(
        self,
        relative_path: str,
    ) -> pygame.Surface:
        """Load one image using a path relative to assets/images."""

        image_path = self.assets_path / relative_path

        if not image_path.exists():
            raise FileNotFoundError(
                f"Could not find image asset: {image_path}"
            )

        image = pygame.image.load(
            str(image_path)
        )

        # convert_alpha preserves transparent pixels
        return image.convert_alpha()

    def _load_and_scale_image(
        self,
        relative_path: str,
    ) -> pygame.Surface:
        """Load an image and resize it to one grid tile."""

        image = self._load_image(
            relative_path
        )

        return pygame.transform.scale(
            image,
            (
                settings.TILE_SIZE,
                settings.TILE_SIZE,
            ),
        )

    def _extract_sprite(
        self,
        sprite_sheet: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> pygame.Surface:
        """Extract and resize one frame from a sprite sheet."""

        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()

        frame_width = min(
            width,
            sheet_width,
        )

        frame_height = min(
            height,
            sheet_height,
        )

        frame = pygame.Surface(
            (
                frame_width,
                frame_height,
            ),
            pygame.SRCALPHA,
        )

        frame.blit(
            sprite_sheet,
            (0, 0),
            pygame.Rect(
                x,
                y,
                frame_width,
                frame_height,
            ),
        )

        return pygame.transform.scale(
            frame,
            (
                settings.TILE_SIZE,
                settings.TILE_SIZE,
            ),
        )

    def get_image(
        self,
        image_name: str,
    ) -> pygame.Surface:
        """Return an image stored as an asset manager attribute."""

        if not hasattr(self, image_name):
            raise KeyError(
                f"Unknown image asset: {image_name}"
            )

        image = getattr(
            self,
            image_name,
        )

        if not isinstance(image, pygame.Surface):
            raise TypeError(
                f"Asset is not an image: {image_name}"
            )

        return image