from pathlib import Path
from typing import ClassVar

from .GameState import GameMode, GameState


class ArcadeMode(GameState):
    """
        ArcadeMode Class Definition

        The normal game: it is won after MAX_LEVEL levels.
    """

    SCORE_FILE: ClassVar[Path] = Path("score/scores_normal.json")

    @property
    def mode(self) -> GameMode:
        """ This class is the NORMAL mode """
        return GameMode.ARCADE

    def has_won(self) -> bool:
        """ Won after the last level """
        return self.level > int(self.engine.get_config_key("max_level"))
