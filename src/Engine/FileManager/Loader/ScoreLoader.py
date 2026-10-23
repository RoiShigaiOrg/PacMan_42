from .Loader import Loader
from datetime import datetime
from pathlib import Path
from typing import Any, cast
import json

SCORE_FILE: Path = Path("scores.json")


class ScoreLoader(Loader):
    """
        ScoreLoader Class Definition

        The ScoreLoader Class is the loader specialized for
            loading and storing the Player Score leader Board
            in a JSON file.
    """

    def load(self, filename: Path = Path(".")) -> dict:
        """ Load method for the ScoreLoader """
        try:
            data = json.loads(filename.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"scores": []}
        if isinstance(data, list):
            data = {"scores": data}
        return cast(dict[str, Any], data)
        # raise NotImplementedError("ScoreLoader.load is not implemented")

    def store(
            self, filename: Path = SCORE_FILE,
            score: dict[str, Any] | None = None) -> None:
        """ Store the score into a JSON file """
        data = self.load(filename)
        entry: dict[str, Any] = {
            "date": datetime.now().isoformat(timespec="seconds")
        }
        entry.update(score or {})
        data["scores"].append(entry)
        filename.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
