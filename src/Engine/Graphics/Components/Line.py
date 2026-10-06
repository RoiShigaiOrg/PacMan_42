from .Components import Components
from typing import Tuple, Callable


class Line(Components):
    """
        Line Object is a Components representing a Line or a square.
    """

    def __init__(self, x: Tuple[int, int], y: Tuple[int, int], color: int) -> None:
        """ Init method for the Line object """
        if x <= 0 or y <= 0:
            raise ValueError("Line: Negative dimension")
        self.__start = x
        self.__end = y
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Line: Not valid color value")
        self.__color = color

    def _draw(
            self,
            pos_x: int,
            pos_y: int,
            display_pixel_function: Callable) -> None:
        """
            Private method to draw the Rect on a Display object.
            This method is not meant to be called by any deveper,
                it is called inside the Display.draw(Rect Obj)
        """
        x1, y1 = self.__start
        x2, y2 = self.__end
        if x1 < pos_x or y1 < pos_y:
            raise ValueError("Line: Start outside window range")
        dx = abs(x2 - (x1 + pos_x))
        dy = abs(y2 - (y1 + pos_y))

        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            display_pixel_function(x1, y1)

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
