"""Base class shared by all game entities."""

from dataclasses import dataclass


Position = tuple[int, int]


@dataclass
class Entity:
    """Represent an object positioned inside the level grid."""

    position: Position
    sprite_name: str
    is_active: bool = True

    @property
    def row(self) -> int:
        """Return the entity row."""

        return self.position[0]

    @property
    def column(self) -> int:
        """Return the entity column."""

        return self.position[1]

    def set_position(
        self,
        position: Position,
    ) -> None:
        """Move the entity to another grid position."""

        self.position = position

    def activate(self) -> None:
        """Make the entity active."""

        self.is_active = True

    def deactivate(self) -> None:
        """Remove the entity from active gameplay."""

        self.is_active = False