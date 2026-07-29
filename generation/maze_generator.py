"""Generate playable maze layouts using recursive backtracking."""

import random
from collections import deque
from typing import Optional

from config import settings
from generation.level_manager import LevelManager
from generation.tile_type import TileType


Position = tuple[int, int]


class MazeGenerator:
    """Generate connected maze levels for Cheese Heist."""

    def __init__(
        self,
        rows: int,
        columns: int,
        seed: Optional[int] = None,
        trap_count: int = settings.TRAP_COUNT,
        extra_passage_ratio: Optional[float] = None,
    ) -> None:
        self.rows = rows
        self.columns = columns
        self.trap_count = trap_count

        if extra_passage_ratio is None:
            extra_passage_ratio = getattr(
                settings,
                "EXTRA_PASSAGE_RATIO",
                0.12,
            )

        self.extra_passage_ratio = (
            extra_passage_ratio
        )

        # use an independent random generator for reproducible tests
        self.random = random.Random(seed)

        self._validate_dimensions()
        self._validate_trap_count()
        self._validate_extra_passage_ratio()

    def _validate_dimensions(self) -> None:
        """Check that the maze dimensions support the algorithm."""

        if self.rows < 5 or self.columns < 5:
            raise ValueError(
                "Maze dimensions must be at least 5 by 5."
            )

        if (
            self.rows % 2 == 0
            or self.columns % 2 == 0
        ):
            raise ValueError(
                "Maze rows and columns must both be odd."
            )

    def _validate_trap_count(self) -> None:
        """Check that the requested trap count is valid."""

        if self.trap_count < 0:
            raise ValueError(
                "Trap count cannot be negative."
            )

    def _validate_extra_passage_ratio(
        self,
    ) -> None:
        """Check the percentage used for additional routes."""

        if not 0 <= self.extra_passage_ratio <= 1:
            raise ValueError(
                "Extra passage ratio must be between 0 and 1."
            )

    def generate_empty_grid(
        self,
    ) -> list[list[TileType]]:
        """Create a grid initially filled with walls."""

        grid = []

        for _ in range(self.rows):
            row = []

            for _ in range(self.columns):
                row.append(
                    TileType.WALL
                )

            grid.append(
                row
            )

        return grid

    def choose_start_cell(
        self,
    ) -> Position:
        """Choose a valid maze cell on odd coordinates."""

        possible_rows = list(
            range(
                1,
                self.rows - 1,
                2,
            )
        )

        possible_columns = list(
            range(
                1,
                self.columns - 1,
                2,
            )
        )

        start_row = self.random.choice(
            possible_rows
        )

        start_column = self.random.choice(
            possible_columns
        )

        return start_row, start_column

    def get_unvisited_neighbors(
        self,
        grid: list[list[TileType]],
        position: Position,
    ) -> list[Position]:
        """Return unvisited cells located two steps away."""

        row, column = position

        possible_neighbors = [
            (
                row - 2,
                column,
            ),
            (
                row + 2,
                column,
            ),
            (
                row,
                column - 2,
            ),
            (
                row,
                column + 2,
            ),
        ]

        unvisited_neighbors = []

        for neighbor in possible_neighbors:
            neighbor_row, neighbor_column = (
                neighbor
            )

            is_inside_inner_area = (
                0
                < neighbor_row
                < self.rows - 1
                and 0
                < neighbor_column
                < self.columns - 1
            )

            if not is_inside_inner_area:
                continue

            if (
                grid[neighbor_row][neighbor_column]
                == TileType.WALL
            ):
                unvisited_neighbors.append(
                    neighbor
                )

        return unvisited_neighbors

    def carve_passage(
        self,
        grid: list[list[TileType]],
        current: Position,
        neighbor: Position,
    ) -> None:
        """Open a cell and the wall connecting it."""

        current_row, current_column = (
            current
        )

        neighbor_row, neighbor_column = (
            neighbor
        )

        wall_row = (
            current_row + neighbor_row
        ) // 2

        wall_column = (
            current_column + neighbor_column
        ) // 2

        grid[wall_row][wall_column] = (
            TileType.FLOOR
        )

        grid[neighbor_row][neighbor_column] = (
            TileType.FLOOR
        )

    def generate_paths(
        self,
        grid: list[list[TileType]],
        start: Position,
    ) -> None:
        """Carve connected paths using recursive backtracking."""

        start_row, start_column = start

        grid[start_row][start_column] = (
            TileType.FLOOR
        )

        stack = [
            start
        ]

        while stack:
            current = stack[-1]

            unvisited_neighbors = (
                self.get_unvisited_neighbors(
                    grid,
                    current,
                )
            )

            if not unvisited_neighbors:
                stack.pop()
                continue

            next_cell = self.random.choice(
                unvisited_neighbors
            )

            self.carve_passage(
                grid,
                current,
                next_cell,
            )

            stack.append(
                next_cell
            )

    def is_floor(
        self,
        grid: list[list[TileType]],
        position: Position,
    ) -> bool:
        """Return whether a position currently contains floor."""

        row, column = position

        if not (
            0 <= row < self.rows
            and 0 <= column < self.columns
        ):
            return False

        return (
            grid[row][column]
            == TileType.FLOOR
        )

    def get_extra_passage_candidates(
        self,
        grid: list[list[TileType]],
    ) -> list[Position]:
        """Return walls that can connect existing corridors."""

        candidates = []

        for row in range(
            1,
            self.rows - 1,
        ):
            for column in range(
                1,
                self.columns - 1,
            ):
                if (
                    grid[row][column]
                    != TileType.WALL
                ):
                    continue

                left_position = (
                    row,
                    column - 1,
                )

                right_position = (
                    row,
                    column + 1,
                )

                upper_position = (
                    row - 1,
                    column,
                )

                lower_position = (
                    row + 1,
                    column,
                )

                connects_horizontal_paths = (
                    self.is_floor(
                        grid,
                        left_position,
                    )
                    and self.is_floor(
                        grid,
                        right_position,
                    )
                )

                connects_vertical_paths = (
                    self.is_floor(
                        grid,
                        upper_position,
                    )
                    and self.is_floor(
                        grid,
                        lower_position,
                    )
                )

                if (
                    connects_horizontal_paths
                    or connects_vertical_paths
                ):
                    candidates.append(
                        (
                            row,
                            column,
                        )
                    )

        return candidates

    def create_extra_passages(
        self,
        grid: list[list[TileType]],
    ) -> None:
        """Remove selected walls to create alternative routes."""

        candidates = (
            self.get_extra_passage_candidates(
                grid
            )
        )

        if not candidates:
            return

        self.random.shuffle(
            candidates
        )

        passage_count = round(
            len(candidates)
            * self.extra_passage_ratio
        )

        passage_count = max(
            1,
            passage_count,
        )

        passage_count = min(
            passage_count,
            len(candidates),
        )

        for row, column in candidates[
            :passage_count
        ]:
            grid[row][column] = (
                TileType.FLOOR
            )

    def get_floor_positions(
        self,
        grid: list[list[TileType]],
    ) -> list[Position]:
        """Return all currently available floor positions."""

        floor_positions = []

        for row in range(self.rows):
            for column in range(
                self.columns
            ):
                if (
                    grid[row][column]
                    == TileType.FLOOR
                ):
                    floor_positions.append(
                        (
                            row,
                            column,
                        )
                    )

        return floor_positions

    def calculate_manhattan_distance(
        self,
        first: Position,
        second: Position,
    ) -> int:
        """Calculate distance without considering walls."""

        first_row, first_column = first
        second_row, second_column = second

        row_distance = abs(
            first_row - second_row
        )

        column_distance = abs(
            first_column - second_column
        )

        return (
            row_distance
            + column_distance
        )

    def choose_cheese_position(
        self,
        floor_positions: list[Position],
        home_position: Position,
    ) -> Position:
        """Choose a floor position far from the home."""

        possible_positions = [
            position
            for position in floor_positions
            if position != home_position
        ]

        if not possible_positions:
            raise ValueError(
                "The maze does not contain enough floor positions."
            )

        cheese_position = max(
            possible_positions,
            key=lambda position: (
                self.calculate_manhattan_distance(
                    home_position,
                    position,
                )
            ),
        )

        return cheese_position

    def place_objectives(
        self,
        grid: list[list[TileType]],
        home_position: Position,
    ) -> Position:
        """Place the mouse home and cheese."""

        floor_positions = (
            self.get_floor_positions(
                grid
            )
        )

        cheese_position = (
            self.choose_cheese_position(
                floor_positions,
                home_position,
            )
        )

        home_row, home_column = (
            home_position
        )

        cheese_row, cheese_column = (
            cheese_position
        )

        grid[home_row][home_column] = (
            TileType.HOME
        )

        grid[cheese_row][cheese_column] = (
            TileType.CHEESE
        )

        return cheese_position

    def is_inside_grid(
        self,
        position: Position,
    ) -> bool:
        """Check whether a position is inside the grid."""

        row, column = position

        return (
            0 <= row < self.rows
            and 0 <= column < self.columns
        )

    def is_walkable(
        self,
        grid: list[list[TileType]],
        position: Position,
    ) -> bool:
        """Check whether a position can be visited."""

        if not self.is_inside_grid(
            position
        ):
            return False

        row, column = position

        return (
            grid[row][column]
            != TileType.WALL
        )

    def get_walkable_neighbors(
        self,
        grid: list[list[TileType]],
        position: Position,
    ) -> list[Position]:
        """Return walkable adjacent positions."""

        row, column = position

        possible_neighbors = [
            (
                row - 1,
                column,
            ),
            (
                row + 1,
                column,
            ),
            (
                row,
                column - 1,
            ),
            (
                row,
                column + 1,
            ),
        ]

        walkable_neighbors = []

        for neighbor in possible_neighbors:
            if self.is_walkable(
                grid,
                neighbor,
            ):
                walkable_neighbors.append(
                    neighbor
                )

        return walkable_neighbors

    def find_shortest_path(
        self,
        grid: list[list[TileType]],
        start: Position,
        destination: Position,
    ) -> list[Position]:
        """Find the shortest path using BFS."""

        queue = deque(
            [
                start,
            ]
        )

        previous_positions: dict[
            Position,
            Optional[Position],
        ] = {
            start: None,
        }

        while queue:
            current = queue.popleft()

            if current == destination:
                break

            neighbors = (
                self.get_walkable_neighbors(
                    grid,
                    current,
                )
            )

            for neighbor in neighbors:
                if neighbor in previous_positions:
                    continue

                previous_positions[neighbor] = (
                    current
                )

                queue.append(
                    neighbor
                )

        if destination not in previous_positions:
            raise RuntimeError(
                "No path exists between home and cheese."
            )

        path = []

        current_position: Optional[Position] = (
            destination
        )

        while current_position is not None:
            path.append(
                current_position
            )

            current_position = (
                previous_positions[
                    current_position
                ]
            )

        path.reverse()

        return path

    def get_available_trap_positions(
        self,
        grid: list[list[TileType]],
        protected_path: list[Position],
    ) -> list[Position]:
        """Return floor cells that can contain traps."""

        protected_positions = set(
            protected_path
        )

        available_positions = []

        for row in range(self.rows):
            for column in range(
                self.columns
            ):
                position = (
                    row,
                    column,
                )

                if position in protected_positions:
                    continue

                if (
                    grid[row][column]
                    != TileType.FLOOR
                ):
                    continue

                available_positions.append(
                    position
                )

        return available_positions

    def place_traps(
        self,
        grid: list[list[TileType]],
        home_position: Position,
        cheese_position: Position,
    ) -> None:
        """Place traps outside the shortest safe path."""

        if self.trap_count == 0:
            return

        shortest_path = (
            self.find_shortest_path(
                grid,
                home_position,
                cheese_position,
            )
        )

        available_positions = (
            self.get_available_trap_positions(
                grid,
                shortest_path,
            )
        )

        if (
            len(available_positions)
            < self.trap_count
        ):
            raise ValueError(
                "The maze does not contain enough valid "
                "positions for the requested traps."
            )

        trap_positions = self.random.sample(
            available_positions,
            self.trap_count,
        )

        for row, column in trap_positions:
            grid[row][column] = (
                TileType.TRAP
            )

    def generate_maze(
        self,
    ) -> LevelManager:
        """Generate and return one complete maze level."""

        grid = self.generate_empty_grid()

        home_position = (
            self.choose_start_cell()
        )

        self.generate_paths(
            grid,
            home_position,
        )

        # create loops and alternative routes after the base maze
        self.create_extra_passages(
            grid
        )

        cheese_position = (
            self.place_objectives(
                grid,
                home_position,
            )
        )

        self.place_traps(
            grid,
            home_position,
            cheese_position,
        )

        return LevelManager(
            grid
        )