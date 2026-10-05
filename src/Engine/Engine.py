from .FileManager import FileManager
from typing import Any


class Engine:
    """
        Engine Class Definition

        The Engine is the backbone of the whole backend of the project.
        Handle the files operation for map creation,
            score storage and assets/sprites loading.
        Handle the coordonate of the whole Entity present in the project,
            Pathfinding algorithm and position updates

    """

    def __init__(self) -> None:
        """ Init method for the Engine """

        self.__file_manager: FileManager = FileManager()
        self.__config = self.__file_manager.load_config()

    def get_config_key(self, key: str) -> Any:
        """ Return the value stored in the given key from the config """
        return self.__config[key]

    def update_config(self, data: dict) -> None:
        """ Update the config with the new value """
        self.__config.update(data)
