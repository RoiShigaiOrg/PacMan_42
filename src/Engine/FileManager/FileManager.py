from .Loader.Loader import Loader
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
        pass

    def load(self, loader: Loader) -> Any:
        """
        Load method of the FileManager
        Take a Loader type of loader and call it's load method
        """
        return loader.load()

    def store(self, loader: Loader) -> None:
        """
        Store method of the FileManager
        Take a Loader type of loader and call it's store method
        """
        loader.store()
