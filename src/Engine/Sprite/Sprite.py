from typing import List, Tuple


class Sprite:
    """ Sprite Object Class definition
    A Sprite is the graphical representation of an entity within the Game.

    Generaly a Sprite can be a copy of pixels from a section of a SpriteSheet
    """

    def __init__(self, size: Tuple[int, int], data: List[List[int]]) -> None:
        """ Init method of the Sprite Object """
        self.__size: Tuple[int, int] = size
        self.__data: List[List[int]] = data

    @property
    def size(self) -> Tuple[int, int]:
        """
        Getter method to return the dimension of the actual Sprite Object
        """
        return self.__size

    @size.setter
    def size(self, value: Tuple[int, int]) -> None:
        """ Setter Method for the size attribute of this Sprite Object """
        if not value:
            raise ValueError("Sprite size cannot be None")
        if value[0] == 0 or value[1] == 0:
            raise ValueError("Sprite siwe attribute cannot be null")
        self.__size = value
