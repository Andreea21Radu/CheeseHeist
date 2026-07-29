"""Control movement, interactions and win conditions."""

import math

from core.game_state import GameState
from entities.entity_manager import EntityManager
from entities.mouse import Mouse
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

        # trap penalty duration in milliseconds
        self.trap_penalty_duration = 5000

        # timestamp when the current trap penalty ends
        self.stunned_until = 0

        # briefly display a message after the mouse is released
        self.release_message_duration = 1500
        self.release_message_until = 0

    @property
    def mouse(self) -> Mouse:
        """Return the player-controlled mouse."""

        return self.entity_manager.mouse

    def update(
        self,
        current_time: int,
    ) -> None:
        """Update temporary gameplay states."""

        if (
            self.stunned_until > 0
            and current_time >= self.stunned_until
        ):
            self.stunned_until = 0

            self.release_message_until = (
                current_time
                + self.release_message_duration
            )

        if (
            self.release_message_until > 0
            and current_time >= self.release_message_until
        ):
            self.release_message_until = 0

    def move_mouse(
        self,
        row_change: int,
        column_change: int,
        current_time: int = 0,
    ) -> bool:
        """Try to move the mouse by one grid cell."""

        if self.state != GameState.PLAYING:
            return False

        self.mouse.set_direction_from_movement(
            row_change,
            column_change,
        )

        if self.is_stunned(current_time):
            return False

        current_row, current_column = self.mouse.position

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

        self.handle_mouse_interactions(
            current_time
        )

        return True

    def handle_mouse_interactions(
        self,
        current_time: int,
    ) -> None:
        """Handle objects found at the mouse position."""

        self.try_collect_cheese()
        self.try_trigger_trap(current_time)
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
        current_time: int,
    ) -> None:
        """Temporarily stun the mouse when it reaches a trap."""

        for trap in self.entity_manager.traps:
            if not trap.is_active:
                continue

            if self.mouse.position != trap.position:
                continue

            trap.trigger()

            self.stunned_until = (
                current_time
                + self.trap_penalty_duration
            )

            self.release_message_until = 0
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

    def is_stunned(
        self,
        current_time: int,
    ) -> bool:
        """Return whether the mouse is currently blocked."""

        return self.stunned_until > current_time

    def get_stun_seconds_remaining(
        self,
        current_time: int,
    ) -> int:
        """Return the remaining trap penalty in seconds."""

        if not self.is_stunned(current_time):
            return 0

        milliseconds_remaining = (
            self.stunned_until
            - current_time
        )

        return math.ceil(
            milliseconds_remaining / 1000
        )

    def is_release_message_visible(
        self,
        current_time: int,
    ) -> bool:
        """Return whether the release message should be shown."""

        return self.release_message_until > current_time

    def is_playing(self) -> bool:
        """Return whether the current level is active."""

        return self.state == GameState.PLAYING

    def has_won(self) -> bool:
        """Return whether the player completed the mission."""

        return self.state == GameState.WON