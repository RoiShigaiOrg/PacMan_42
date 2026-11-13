from .Loader import Loader
from pathlib import Path
from typing import Any, cast
import json


class ScoreLoader(Loader):
    """
        ScoreLoader Class Definition

        The ScoreLoader Class is the loader specialized for
            loading and storing the Player Score leader Board
            in a JSON file.
    """
    def __init__(
            self,
            score_file: Path,
            score: dict[str, Any] | None = None) -> None:
        """ Init Method of the ScoreLoader """
        self.__file: Path = score_file
        self.__score: dict[str, Any] | None = score

    def load(self) -> dict:
        """ Load method for the ScoreLoader """
        try:
            with open(self.__file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            data = {"scores": []}
        if isinstance(data, list):
            data = {"scores": data}
        if not self.__file.exists():
            self.__write(data)
        return cast(dict[str, Any], data)

    def store(self) -> None:
        """ Store the score into a JSON file """
        if self.__score is None:
            raise ValueError("ScoreLoader: Score is None")
        data = self.load()
        scores = data["scores"]
        scores.append(dict(self.__score))
        scores.sort(key=lambda entry: int(entry.get("score", 0)),
                    reverse=True)
        data["scores"] = scores[:10]
        self.__write(data)

    def __write(self, data: dict[str, Any]) -> None:
        """ Save the leaderboard in the JSON file """
        self.__file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.__file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
