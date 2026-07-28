"""Define the possible states of a game session."""

from enum import Enum, auto


class GameState(Enum):
    """Represent the current state of the game."""

    PLAYING = auto()
    WON = auto()
    LOST = auto()