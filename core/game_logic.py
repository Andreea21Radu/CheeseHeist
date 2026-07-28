"""Control movement, interactions and win conditions."""

from core.game_state import GameState
from entities.entity_manager import EntityManager
from generation.level_manager import LevelManager
from generation.tile_type import TileType


class GameLogic:
    """Manage gameplay rules independently from rendering."""

    def __init__(
        self,
        level: LevelManager,
        entity_manager: EntityManager,
    ) -> None:
        self.level = level
        self.entity_manager = entity_manager
        self.state = GameState.PLAYING

    @property
    def mouse(self):
        """Return the player-controlled mouse."""

        return self.entity_manager.mouse

    def move_mouse(
        self,
        row_change: int,
        column_change: int,
    ) -> bool:
        """Try to move the mouse by one grid cell."""

        if self.state != GameState.PLAYING:
            return False

        current_row, current_column = (
            self.mouse.position
        )

        target_position = (
            current_row + row_change,
            current_column + column_change,
        )

        if not self.level.is_walkable(
            target_position
        ):
            return False

        self.mouse.set_position(
            target_position
        )

        self.mouse.register_move()

        self.handle_mouse_interactions()

        return True

    def handle_mouse_interactions(
        self,
    ) -> None:
        """Handle objects found at the mouse position."""

        self.try_collect_cheese()
        self.try_trigger_trap()
        self.try_finish_level()

    def try_collect_cheese(
        self,
    ) -> None:
        """Collect the cheese when the mouse reaches it."""

        cheese = self.entity_manager.cheese

        if not cheese.is_active:
            return

        if self.mouse.position != cheese.position:
            return

        cheese.collect()
        self.mouse.collect_cheese()

    def try_trigger_trap(
        self,
    ) -> None:
        """End the game when the mouse reaches a trap."""

        for trap in self.entity_manager.traps:
            if not trap.is_active:
                continue

            if self.mouse.position != trap.position:
                continue

            trap.trigger()
            self.state = GameState.LOST
            return

    def try_finish_level(
        self,
    ) -> None:
        """Win after returning home with the cheese."""

        if not self.mouse.has_cheese:
            return

        home_position = self.level.find_tile(
            TileType.HOME
        )

        if home_position is None:
            return

        if self.mouse.position == home_position:
            self.state = GameState.WON

    def is_playing(self) -> bool:
        """Return whether the current level is active."""

        return self.state == GameState.PLAYING

    def has_won(self) -> bool:
        """Return whether the player completed the mission."""

        return self.state == GameState.WON

    def has_lost(self) -> bool:
        """Return whether the player touched a trap."""

        return self.state == GameState.LOST