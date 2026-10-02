from .Loader import Loader
from pathlib import Path


class ScoreLoader(Loader):
    """
        ScoreLoader Class Definition

        The ScoreLoader Class is the loader specialized for
            loading and storing the Player Score leader Board
            in a JSON file.
    """

    def load(self, filename: Path) -> dict:
        """ Load method for the ScoreLoader """
        ...

    def store(self, filename: Path, score: dict) -> dict:
        """ Store the score into a JSON file """
        ...
