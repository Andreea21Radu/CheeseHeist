"""Entry point for the Cheese Heist game."""

from core.game import Game


def main() -> None:
    """Create and start the game."""

    game = Game()
    game.run()


if __name__ == "__main__":
    main()