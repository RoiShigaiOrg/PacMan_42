from abc import ABC
from typing import Any


class Entity(ABC):
    """
        Entity Abstract Class

        The Entity Class serve as a boase to represent any
            movable entity present in the project (Player, Ghost)
    """

    def __init__(
            self,
            name: str,
            coord: tuple[int, int],
            sprites: Any) -> None:
        """ Init Method of the Entity Class """
        self._name = name
        self._coord = coord
        self._sprites = sprites

    @property
    def coord(self) -> tuple[int, int]:
        """ Getter method for the Object position """
        return self._coord

    @coord.setter
    def coord(self, coord: tuple[int, int]) -> None:
        """ Setter method for the Object position """
        self._coord = coord

    @property
    def name(self) -> str:
        """ Getter method for the Object Name """
        return self._name
