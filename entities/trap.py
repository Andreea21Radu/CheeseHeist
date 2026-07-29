"""Trap entity placed inside the maze."""

from entities.entity import Entity, Position


class Trap(Entity):
    """Represent a trap that can temporarily stun the mouse."""

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
        """Trigger and deactivate the trap."""

        self.is_triggered = True
        self.deactivate()

    def reset(self) -> None:
        """Reset the trap state."""

        self.is_triggered = False
        self.activate()