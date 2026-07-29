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

        self.mouse_animations = (
            self._load_mouse_animations()
        )

        # compatibility with generic entity rendering
        self.mouse = self.mouse_animations[
            "down"
        ][0]

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
        column: int,
        row: int,
    ) -> pygame.Surface:
        """Extract one 32 by 32 frame from a sprite sheet."""

        source_size = 32

        source_x = column * source_size
        source_y = row * source_size

        frame = pygame.Surface(
            (
                source_size,
                source_size,
            ),
            pygame.SRCALPHA,
        )

        frame.blit(
            sprite_sheet,
            (0, 0),
            pygame.Rect(
                source_x,
                source_y,
                source_size,
                source_size,
            ),
        )

        return pygame.transform.scale(
            frame,
            (
                settings.TILE_SIZE,
                settings.TILE_SIZE,
            ),
        )

    def _extract_animation(
        self,
        columns: list[int],
        row: int,
    ) -> list[pygame.Surface]:
        """Extract several animation frames from one row."""

        return [
            self._extract_sprite(
                self.mouse_spritesheet,
                column,
                row,
            )
            for column in columns
        ]

    def _load_mouse_animations(
        self,
    ) -> dict[str, list[pygame.Surface]]:
        """Load directional mouse walking animations."""

        right_frames = self._extract_animation(
            columns=[12, 13, 14, 15],
            row=1,
        )

        left_frames = [
            pygame.transform.flip(
                frame,
                True,
                False,
            )
            for frame in right_frames
        ]

        down_frames = self._extract_animation(
            columns=[0, 1, 2, 3],
            row=0,
        )

        up_frames = self._extract_animation(
            columns=[16, 17, 18, 19],
            row=2,
        )

        return {
            "up": up_frames,
            "down": down_frames,
            "left": left_frames,
            "right": right_frames,
        }

    def get_mouse_frame(
        self,
        direction: str,
        frame_index: int,
    ) -> pygame.Surface:
        """Return one directional mouse animation frame."""

        frames = self.mouse_animations.get(
            direction,
            self.mouse_animations["down"],
        )

        safe_frame_index = (
            frame_index % len(frames)
        )

        return frames[safe_frame_index]

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