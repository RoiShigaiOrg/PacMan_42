from .Loader import ConfigLoader, ScoreLoader
from typing import Any


CONFIG_KEY: str = "config"
SPRITE_KEY: str = "sprite"
SCORE_KEY: str = "score"


class FileManager:
    """
        FileManager Class Definition

        The FileManager Class is the main API for file manipulation
            within the project.
        It is used for:
            load a config file for the Engine
            load sprite for Entity
            load/store player score within a JSON file

    """

    def __init__(self) -> None:
        """ Init Method of the FileManager """
        self.__config_loader = ConfigLoader()
        self.__score_loader = ScoreLoader()

    def load_config(self) -> dict:
        """ Return the config of the application """
        return self.__config_loader.load()

    def store_config(self, config: dict) -> None:
        """ Store the actual config in the Config file """
        self.__config_loader.store(config=config)

    def load_scores(self) -> list[dict[str, Any]]:
        """ Return every saved score of the leaderboard """
        scores: list[dict[str, Any]] = self.__score_loader.load()["scores"]
        return scores

    def store_score(self, login: str, score: int) -> None:
        """ Save the score of a player in the leaderboard file """
        self.__score_loader.store(score={"login": login, "score": score})
