"""Generate playable maze layouts using recursive backtracking."""

import random
from typing import Optional

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
    ) -> None:
        self.rows = rows
        self.columns = columns

        # we use our own random generator so tests can reproduce a maze
        self.random = random.Random(seed)

        self._validate_dimensions()

    def _validate_dimensions(self) -> None:
        """Check that the maze dimensions can support the algorithm."""

        if self.rows < 5 or self.columns < 5:
            raise ValueError(
                "Maze dimensions must be at least 5 by 5."
            )

        if self.rows % 2 == 0 or self.columns % 2 == 0:
            raise ValueError(
                "Maze rows and columns must both be odd."
            )

    def generate_empty_grid(self) -> list[list[TileType]]:
        """Create a grid initially filled entirely with walls."""

        grid = []

        for _ in range(self.rows):
            row = []

            for _ in range(self.columns):
                row.append(TileType.WALL)

            grid.append(row)

        return grid

    def choose_start_cell(self) -> Position:
        """Choose a valid maze cell positioned on odd coordinates."""

        possible_rows = list(
            range(1, self.rows - 1, 2)
        )

        possible_columns = list(
            range(1, self.columns - 1, 2)
        )

        start_row = self.random.choice(possible_rows)
        start_column = self.random.choice(possible_columns)

        return start_row, start_column

    def get_unvisited_neighbors(
        self,
        grid: list[list[TileType]],
        position: Position,
    ) -> list[Position]:
        """Return unvisited cells located two steps away."""

        row, column = position

        possible_neighbors = [
            (row - 2, column),
            (row + 2, column),
            (row, column - 2),
            (row, column + 2),
        ]

        unvisited_neighbors = []

        for neighbor in possible_neighbors:
            neighbor_row, neighbor_column = neighbor

            is_inside_inner_area = (
                0 < neighbor_row < self.rows - 1
                and 0 < neighbor_column < self.columns - 1
            )

            if not is_inside_inner_area:
                continue

            # untouched maze cells are still represented as walls
            if grid[neighbor_row][neighbor_column] == TileType.WALL:
                unvisited_neighbors.append(neighbor)

        return unvisited_neighbors

    def carve_passage(
        self,
        grid: list[list[TileType]],
        current: Position,
        neighbor: Position,
    ) -> None:
        """Open the neighbor cell and the wall between both cells."""

        current_row, current_column = current
        neighbor_row, neighbor_column = neighbor

        wall_row = (
            current_row + neighbor_row
        ) // 2

        wall_column = (
            current_column + neighbor_column
        ) // 2

        grid[wall_row][wall_column] = TileType.FLOOR
        grid[neighbor_row][neighbor_column] = TileType.FLOOR

    def generate_paths(
        self,
        grid: list[list[TileType]],
        start: Position,
    ) -> None:
        """Carve connected maze paths using recursive backtracking."""

        start_row, start_column = start
        grid[start_row][start_column] = TileType.FLOOR

        stack = [start]

        while stack:
            current = stack[-1]

            unvisited_neighbors = self.get_unvisited_neighbors(
                grid,
                current,
            )

            if not unvisited_neighbors:
                # we return to the previous cell when this path is finished
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

            stack.append(next_cell)

    def get_floor_positions(
        self,
        grid: list[list[TileType]],
    ) -> list[Position]:
        """Return all currently walkable floor positions."""

        floor_positions = []

        for row in range(self.rows):
            for column in range(self.columns):
                if grid[row][column] == TileType.FLOOR:
                    floor_positions.append(
                        (row, column)
                    )

        return floor_positions

    def calculate_manhattan_distance(
        self,
        first: Position,
        second: Position,
    ) -> int:
        """Calculate the grid distance without considering maze walls."""

        first_row, first_column = first
        second_row, second_column = second

        row_distance = abs(
            first_row - second_row
        )

        column_distance = abs(
            first_column - second_column
        )

        return row_distance + column_distance

    def choose_cheese_position(
        self,
        floor_positions: list[Position],
        home_position: Position,
    ) -> Position:
        """Choose a floor position far away from the mouse home."""

        possible_positions = []

        for position in floor_positions:
            if position != home_position:
                possible_positions.append(position)

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
    ) -> None:
        """Place the mouse home and cheese inside the maze."""

        floor_positions = self.get_floor_positions(
            grid
        )

        cheese_position = self.choose_cheese_position(
            floor_positions,
            home_position,
        )

        home_row, home_column = home_position
        cheese_row, cheese_column = cheese_position

        grid[home_row][home_column] = TileType.HOME
        grid[cheese_row][cheese_column] = TileType.CHEESE

    def generate_maze(self) -> LevelManager:
        """Generate and return one complete maze level."""

        grid = self.generate_empty_grid()
        start_position = self.choose_start_cell()

        self.generate_paths(
            grid,
            start_position,
        )

        self.place_objectives(
            grid,
            start_position,
        )

        return LevelManager(grid)