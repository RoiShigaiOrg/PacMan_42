from typing import Dict
from .Loader import ConfigLoader, ScoreLoader, SpriteLoader, Loader


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
        self.__parser: Dict[str, Loader] = {
                CONFIG_KEY: ConfigLoader(),
                SPRITE_KEY: SpriteLoader(),
                SCORE_KEY: ScoreLoader()
                }

    def load_config(self) -> dict:
        """ Return the config of the application """
        return self.__parser[CONFIG_KEY].load()

    def store_config(self, config: dict) -> None:
        """ Store the actual config in the Config file """
        self.__parser[CONFIG_KEY].store(config=config)
