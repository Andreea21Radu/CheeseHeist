"""Player-controlled mouse entity."""

from entities.entity import Entity, Position


class Mouse(Entity):
    """Represent the mouse controlled by the player."""

    def __init__(
        self,
        position: Position,
    ) -> None:
        super().__init__(
            position=position,
            sprite_name="mouse",
        )

        self.has_cheese = False
        self.number_of_moves = 0

    def collect_cheese(self) -> None:
        """Mark the cheese as collected by the mouse."""

        self.has_cheese = True

    def drop_cheese(self) -> None:
        """Remove the cheese from the mouse inventory."""

        self.has_cheese = False

    def register_move(self) -> None:
        """Increase the number of completed movements."""

        self.number_of_moves += 1

    def reset(
        self,
        position: Position,
    ) -> None:
        """Reset the mouse for a new level."""

        self.set_position(position)
        self.has_cheese = False
        self.number_of_moves = 0
        self.activate()