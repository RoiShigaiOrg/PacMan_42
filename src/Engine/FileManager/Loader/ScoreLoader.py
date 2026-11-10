from .Loader import Loader
from pathlib import Path
from typing import Any, cast
import json

SCORE_FILE: Path = Path("score/scores.json")


class ScoreLoader(Loader):
    """
        ScoreLoader Class Definition

        The ScoreLoader Class is the loader specialized for
            loading and storing the Player Score leader Board
            in a JSON file.
    """
    def __init__(
            self,
            score_file: Path = SCORE_FILE,
            score: dict[str, Any] | None = None) -> None:
        """ Init Method of the ScoreLoader """
        self.__file: Path = score_file
        self.__score: dict[str, Any] | None = score

    def load(self, filename: Path = SCORE_FILE) -> dict:
        """ Load method for the ScoreLoader """
        try:
            with open(self.__file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return {"scores": []}
        if isinstance(data, list):
            data = {"scores": data}
        return cast(dict[str, Any], data)

    def store(
            self, filename: Path = SCORE_FILE,
            score: dict[str, Any] | None = None) -> None:
        """ Store the score into a JSON file """
        if self.__score is None:
            raise ValueError("ScoreLoader: Score is None")
        data = self.load()
        entry: dict[str, Any] = {}
        entry.update(self.__score)
        data["scores"].append(entry)
        self.__file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.__file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
