"""Load and store the image assets used by the game."""

from pathlib import Path

import pygame


class AssetManager:
    """Load all game images from the assets folder."""

    def __init__(self) -> None:
        self.assets_path = Path("assets/images")

        self.wall = self._load_image("tiles/wall.png")
        self.wall_alt = self._load_image("tiles/wall_alt.png")

        self.floor = self._load_image("tiles/floor.png")
        self.floor_alt = self._load_image("tiles/floor_alt.png")

        self.cheese = self._load_image("items/cheese.png")
        self.trap = self._load_image("items/trap.png")

        self.mouse_home = self._load_image(
            "environment/mouse_home.png"
        )

        self.mouse_spritesheet = self._load_image(
            "mouse/mouse_spritesheet.png"
        )

    def _load_image(self, relative_path: str) -> pygame.Surface:
        """Load one image using a path relative to assets/images."""

        image_path = self.assets_path / relative_path

        if not image_path.exists():
            raise FileNotFoundError(
                f"Could not find image asset: {image_path}"
            )

        image = pygame.image.load(str(image_path))

        # convert_alpha keeps transparent pixels and improves drawing speed
        return image.convert_alpha()