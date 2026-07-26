"""Tests for the game image assets."""

from pathlib import Path


def test_required_assets_exist() -> None:
    """Check that every required image exists in the project."""

    required_assets = [
        "assets/images/tiles/wall.png",
        "assets/images/tiles/wall_alt.png",
        "assets/images/tiles/floor.png",
        "assets/images/tiles/floor_alt.png",
        "assets/images/items/cheese.png",
        "assets/images/items/trap.png",
        "assets/images/environment/mouse_home_tileset.png",
        "assets/images/mouse/mouse_spritesheet.png",
    ]

    for asset_path in required_assets:
        assert Path(asset_path).exists(), (
            f"Missing required asset: {asset_path}"
        )