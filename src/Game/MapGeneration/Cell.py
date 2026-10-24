from Engine.Graphics import MlxDisplay
from Engine.Graphics import Rect
from Engine.Physics.Collider import Collider
from Engine.Physics.Shapes import AABB
from Engine.Physics.Vector2 import Vector2
from typing import Tuple


class Cell():
    """Class composing the map: coordinates and state"""

    def __init__(self, coordinate: Tuple[int, int], walkable: bool):
        self.coordinate: Tuple[int, int] = coordinate
        self.walkable: bool = walkable
        self.__rect: Rect | None = None
        self.__collider: Collider | None = None

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
        if self.__collider:
            self.__collider.debug_draw(display, 0xFFFFFFFF)

    def set_collider(
            self,
            pos_x: int, pos_y: int,
            width: int, height: int) -> None:
        """ Create a Collider for the cell if needed """
        if self.walkable:
            self.__collider = None
            return
        self.__collider = Collider(
                AABB(Vector2(
                    (width / 2) - 2, (height / 2) - 2)),
                Vector2(
                    pos_x + width / 2, pos_y + height / 2)
            )

    @property
    def collider(self) -> Collider | None:
        """Return the blocking collider, if this cell has one."""
        return self.__collider
