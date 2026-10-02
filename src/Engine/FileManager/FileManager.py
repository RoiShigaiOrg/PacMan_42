from typing import Dict
from .Loader import ConfigLoader, SpriteLoader, SpriteLoader


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
        self.__parser: Dict[str, Parser] = {
                "config": ConfigLoader(),
                "sprite": SpriteLoader(),
                "score": ScoreLoader()
                }
