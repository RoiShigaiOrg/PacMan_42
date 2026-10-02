from FileManager import FileManager, CONFIG_KEY, SCORE_KEY, SPRITE_KEY


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

        self.__file_manager: FileManager()
