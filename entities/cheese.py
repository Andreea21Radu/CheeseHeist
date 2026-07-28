"""Collectible cheese entity."""

from entities.entity import Entity, Position


class Cheese(Entity):
    """Represent the cheese collected by the mouse."""

    def __init__(
        self,
        position: Position,
    ) -> None:
        super().__init__(
            position=position,
            sprite_name="cheese",
        )

        self.is_collected = False

    def collect(self) -> None:
        """Mark the cheese as collected."""

        self.is_collected = True
        self.deactivate()

    def reset(
        self,
        position: Position,
    ) -> None:
        """Reset the cheese for a new level."""

        self.set_position(position)
        self.is_collected = False
        self.activate()