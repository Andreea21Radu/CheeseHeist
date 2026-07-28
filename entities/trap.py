"""Trap entity placed inside the maze."""

from entities.entity import Entity, Position


class Trap(Entity):
    """Represent a trap that can affect the mouse."""

    def __init__(
        self,
        position: Position,
    ) -> None:
        super().__init__(
            position=position,
            sprite_name="trap",
        )

        self.is_triggered = False

    def trigger(self) -> None:
        """Mark the trap as triggered."""

        self.is_triggered = True

    def reset(self) -> None:
        """Reset the trap state."""

        self.is_triggered = False
        self.activate()