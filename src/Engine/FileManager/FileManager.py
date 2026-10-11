from .Loader import ConfigLoader


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

    def load_config(self) -> dict:
        """ Return the config of the application """
        return self.__config_loader.load()

    def store_config(self, config: dict) -> None:
        """ Store the actual config in the Config file """
        self.__config_loader.store(config=config)
