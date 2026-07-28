"""Create and manage the entities belonging to one level."""

from entities.cheese import Cheese
from entities.entity import Entity
from entities.mouse import Mouse
from entities.trap import Trap
from generation.level_manager import LevelManager
from generation.tile_type import TileType


class EntityManager:
    """Store and manage all entities from the current level."""

    def __init__(
        self,
        mouse: Mouse,
        cheese: Cheese,
        traps: list[Trap],
    ) -> None:
        self.mouse = mouse
        self.cheese = cheese
        self.traps = traps

    @classmethod
    def from_level(
        cls,
        level: LevelManager,
    ) -> "EntityManager":
        """Create entities using the special tiles from a level."""

        home_position = level.find_tile(
            TileType.HOME
        )

        cheese_position = level.find_tile(
            TileType.CHEESE
        )

        trap_positions = level.find_all_tiles(
            TileType.TRAP
        )

        if home_position is None:
            raise ValueError(
                "The level does not contain a mouse home."
            )

        if cheese_position is None:
            raise ValueError(
                "The level does not contain cheese."
            )

        mouse = Mouse(
            home_position
        )

        cheese = Cheese(
            cheese_position
        )

        traps = [
            Trap(position)
            for position in trap_positions
        ]

        return cls(
            mouse=mouse,
            cheese=cheese,
            traps=traps,
        )

    def get_active_entities(
        self,
    ) -> list[Entity]:
        """Return every entity that should currently be drawn."""

        active_entities: list[Entity] = []

        if self.cheese.is_active:
            active_entities.append(
                self.cheese
            )

        for trap in self.traps:
            if trap.is_active:
                active_entities.append(
                    trap
                )

        if self.mouse.is_active:
            active_entities.append(
                self.mouse
            )

        return active_entities