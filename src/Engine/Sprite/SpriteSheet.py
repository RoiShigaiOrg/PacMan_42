from .Sprite import Sprite
from typing import List, Tuple


class SpriteSheet:
    """
    SpriteSheet class definition

    A SpriteSheet is a optional structure to handle
        multiple sprite within on file.
    These type of structure is often used to save memory and
        file management compute.
    """

    def __init__(self, spritesheet: List[List[int]]) -> None:
        """ Init Method for the SpriteSheet Object """
        self.__data: List[List[int]] = spritesheet

    def extract_sprite(
            self,
            pos: Tuple[int, int],
            size: Tuple[int, int]) -> Sprite:
        """
        Extract a Sprite from the SpriteSheet
        """
        data: List[List[int]] = []

        for y in range(pos[1], pos[1] + size[1] - 1):
            data.append([])
            for x in range(pos[0], pos[0] + size[0] - 1):
                data[y - size[1]] = self.__data[y][x]
        return Sprite(size, data)
