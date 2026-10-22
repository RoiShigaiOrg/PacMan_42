from Engine.Graphics import MlxDisplay
from Engine.Graphics import Rect
from typing import Tuple


class Cell():
    """Class composing the map: coordinates and state"""

    def __init__(self, coordinate: Tuple[int, int], walkable: bool):
        self.coordinate: Tuple[int, int] = coordinate
        self.walkable: bool = walkable
        self.__rect: Rect | None = None

    def draw(
            self,
            display: MlxDisplay,
            pos_x: int, pos_y: int,
            width: int, height: int) -> None:
        """ Draw method of the Cell Object """
        if not self.__rect:
            color: int = 0xFF00FF00 if self.walkable else 0xFF0000FF
            self.__rect = Rect(width, height, pos_x, pos_y, color)
        self.__rect.fill(display)
