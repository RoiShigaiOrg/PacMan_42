from .Loader import Loader
from pathlib import Path


class ScoreLoader(Loader):
    """
        ScoreLoader Class Definition

        The ScoreLoader Class is the loader specialized for
            loading and storing the Player Score leader Board
            in a JSON file.
    """

    def load(self, filename: Path) -> None:
        """ Load method for the ScoreLoader """
        print("Load from ScoreLoader class not implemented yet")

    def store(self, filename: Path, score: dict) -> None:
        """ Store the score into a JSON file """
        print("Store from ScoreLoader class not implemented yet")
