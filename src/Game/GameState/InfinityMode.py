from pathlib import Path
from typing import ClassVar

from .GameState import GameMode, GameState


class InfinityMode(GameState):
    """
        InfinityMode Class Definition

        The levels never stop: the game ends only with the lives.
    """

    SCORE_FILE: ClassVar[Path] = Path("score/scores_infinit.json")

    @property
    def mode(self) -> GameMode:
        """ This class is the INFINITE mode """
        return GameMode.INFINITE

    def has_won(self) -> bool:
        """ An infinite game is never won """
        return False
