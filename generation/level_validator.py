"""Validate generated levels and find paths using BFS."""

from collections import deque
from typing import Optional

from generation.level_manager import LevelManager
from generation.tile_type import TileType


Position = tuple[int, int]


class LevelValidator:
    """Check whether a level can be completed."""

    def __init__(self, level: LevelManager) -> None:
        self.level = level

    def breadth_first_search(
        self,
        start: Position,
        target: Position,
    ) -> list[Position]:
        """Return the shortest path between two positions."""

        if not self.level.is_walkable(start):
            return []

        if not self.level.is_walkable(target):
            return []

        positions_to_visit = deque([start])

        visited_positions = {start}

        previous_positions: dict[
            Position,
            Optional[Position],
        ] = {
            start: None,
        }

        while positions_to_visit:
            current_position = positions_to_visit.popleft()

            if current_position == target:
                return self.reconstruct_path(
                    previous_positions,
                    target,
                )

            neighbors = self.level.get_neighbors(
                current_position
            )

            for neighbor in neighbors:
                if neighbor in visited_positions:
                    continue

                visited_positions.add(neighbor)

                previous_positions[neighbor] = (
                    current_position
                )

                positions_to_visit.append(neighbor)

        # an empty list means that no path was found
        return []

    def reconstruct_path(
        self,
        previous_positions: dict[
            Position,
            Optional[Position],
        ],
        target: Position,
    ) -> list[Position]:
        """Rebuild the path by walking backwards from the target."""

        path = []
        current_position: Optional[Position] = target

        while current_position is not None:
            path.append(current_position)

            current_position = previous_positions[
                current_position
            ]

        # the path was created from target to start
        path.reverse()

        return path

    def get_home_position(self) -> Optional[Position]:
        """Return the mouse home position."""

        return self.level.find_tile(
            TileType.HOME
        )

    def get_cheese_position(self) -> Optional[Position]:
        """Return the cheese position."""

        return self.level.find_tile(
            TileType.CHEESE
        )

    def get_home_to_cheese_path(
        self,
    ) -> list[Position]:
        """Return the shortest path from home to cheese."""

        home_position = self.get_home_position()
        cheese_position = self.get_cheese_position()

        if home_position is None:
            return []

        if cheese_position is None:
            return []

        return self.breadth_first_search(
            home_position,
            cheese_position,
        )

    def get_cheese_to_home_path(
        self,
    ) -> list[Position]:
        """Return the shortest return path from cheese to home."""

        home_position = self.get_home_position()
        cheese_position = self.get_cheese_position()

        if home_position is None:
            return []

        if cheese_position is None:
            return []

        return self.breadth_first_search(
            cheese_position,
            home_position,
        )

    def get_shortest_path_length(self) -> Optional[int]:
        """Return the number of moves needed to reach the cheese."""

        path = self.get_home_to_cheese_path()

        if not path:
            return None

        # a path containing two positions requires one movement
        return len(path) - 1

    def is_level_playable(self) -> bool:
        """Return True when the complete mission can be finished."""

        home_position = self.get_home_position()
        cheese_position = self.get_cheese_position()

        if home_position is None:
            return False

        if cheese_position is None:
            return False

        home_to_cheese_path = (
            self.get_home_to_cheese_path()
        )

        cheese_to_home_path = (
            self.get_cheese_to_home_path()
        )

        can_reach_cheese = bool(
            home_to_cheese_path
        )

        can_return_home = bool(
            cheese_to_home_path
        )

        return can_reach_cheese and can_return_home