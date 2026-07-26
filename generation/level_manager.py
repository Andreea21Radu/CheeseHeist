"""Store and manage the grid used by one game level."""

from typing import Optional

from generation.tile_type import TileType


Position = tuple[int, int]


class LevelManager:
    """Store the level grid and provide useful grid operations."""

    def __init__(self, grid: list[list[TileType]]) -> None:
        self.grid = grid
        self.rows = len(grid)
        self.columns = len(grid[0]) if grid else 0

        self._validate_grid_shape()

    def _validate_grid_shape(self) -> None:
        """Check that every row has the same number of columns."""

        if not self.grid:
            raise ValueError("The level grid cannot be empty.")

        expected_columns = len(self.grid[0])

        for row in self.grid:
            if len(row) != expected_columns:
                raise ValueError(
                    "Every grid row must have the same length."
                )

    def is_inside_grid(self, position: Position) -> bool:
        """Return True when a position is inside the level boundaries."""

        row, column = position

        row_is_valid = 0 <= row < self.rows
        column_is_valid = 0 <= column < self.columns

        return row_is_valid and column_is_valid

    def get_tile(self, position: Position) -> TileType:
        """Return the tile stored at a given position."""

        if not self.is_inside_grid(position):
            raise IndexError(
                f"Position is outside the grid: {position}"
            )

        row, column = position
        return self.grid[row][column]

    def set_tile(
        self,
        position: Position,
        tile_type: TileType,
    ) -> None:
        """Change the tile stored at a given position."""

        if not self.is_inside_grid(position):
            raise IndexError(
                f"Position is outside the grid: {position}"
            )

        row, column = position
        self.grid[row][column] = tile_type

    def is_walkable(self, position: Position) -> bool:
        """Return True when the mouse can enter the selected cell."""

        if not self.is_inside_grid(position):
            return False

        tile_type = self.get_tile(position)

        walkable_tiles = {
            TileType.FLOOR,
            TileType.HOME,
            TileType.CHEESE,
            TileType.TRAP,
        }

        return tile_type in walkable_tiles

    def get_neighbors(self, position: Position) -> list[Position]:
        """Return the walkable neighbors in the four main directions."""

        row, column = position

        possible_neighbors = [
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        ]

        walkable_neighbors = []

        for neighbor in possible_neighbors:
            if self.is_walkable(neighbor):
                walkable_neighbors.append(neighbor)

        return walkable_neighbors

    def find_tile(
        self,
        tile_type: TileType,
    ) -> Optional[Position]:
        """Return the first position containing the requested tile."""

        for row_index, row in enumerate(self.grid):
            for column_index, current_tile in enumerate(row):
                if current_tile == tile_type:
                    return row_index, column_index

        return None

    def find_all_tiles(
        self,
        tile_type: TileType,
    ) -> list[Position]:
        """Return every position containing the requested tile."""

        found_positions = []

        for row_index, row in enumerate(self.grid):
            for column_index, current_tile in enumerate(row):
                if current_tile == tile_type:
                    found_positions.append(
                        (row_index, column_index)
                    )

        return found_positions

    def to_text(self) -> str:
        """Return an ASCII representation useful for debugging."""

        tile_symbols = {
            TileType.WALL: "#",
            TileType.FLOOR: ".",
            TileType.HOME: "H",
            TileType.CHEESE: "C",
            TileType.TRAP: "T",
        }

        text_rows = []

        for row in self.grid:
            symbols = []

            for tile_type in row:
                symbols.append(tile_symbols[tile_type])

            text_rows.append("".join(symbols))

        return "\n".join(text_rows)