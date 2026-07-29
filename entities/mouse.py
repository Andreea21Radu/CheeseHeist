"""Player-controlled mouse entity."""

from entities.entity import Entity, Position


class Mouse(Entity):
    """Represent the mouse controlled by the player."""

    VALID_DIRECTIONS = {
        "up",
        "down",
        "left",
        "right",
    }

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

        self.direction = "down"
        self.is_moving = False

    def collect_cheese(self) -> None:
        """Mark the cheese as collected by the mouse."""

        self.has_cheese = True

    def drop_cheese(self) -> None:
        """Remove the cheese from the mouse inventory."""

        self.has_cheese = False

    def register_move(self) -> None:
        """Increase the number of completed movements."""

        self.number_of_moves += 1

    def set_direction(
        self,
        direction: str,
    ) -> None:
        """Set the direction in which the mouse is facing."""

        if direction not in self.VALID_DIRECTIONS:
            raise ValueError(
                f"Unknown mouse direction: {direction}"
            )

        self.direction = direction

    def set_direction_from_movement(
        self,
        row_change: int,
        column_change: int,
    ) -> None:
        """Update direction using a grid movement."""

        if row_change < 0:
            self.set_direction("up")

        elif row_change > 0:
            self.set_direction("down")

        elif column_change < 0:
            self.set_direction("left")

        elif column_change > 0:
            self.set_direction("right")

    def start_moving(self) -> None:
        """Mark the mouse as currently moving."""

        self.is_moving = True

    def stop_moving(self) -> None:
        """Mark the mouse as currently standing still."""

        self.is_moving = False

    def reset(
        self,
        position: Position,
    ) -> None:
        """Reset the mouse for a new level."""

        self.set_position(position)

        self.has_cheese = False
        self.number_of_moves = 0
        self.direction = "down"
        self.is_moving = False

        self.activate()