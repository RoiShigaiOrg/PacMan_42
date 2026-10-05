from typing import Callable
from .Components import Components
from typing import Tuple
import math


class Circle(Components):
    """
        Circle Object is a Components representing a Circle.
    """

    def __init__(self, x: int, y: int, color: int) -> None:
        """ Init Method for the Circle Object """
        if x <= 0 or y <= 0:
            raise ValueError("Circle: Negative dimension")
        self.__radius: Tuple[int, int] = Tuple(x, y)
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Circle: Not valid color value")
        self.__color = color

    def _draw(self, pos_x: int, pos_y: int, display_pixel_function: Callable) -> None:
        """
            Private method to draw the Circle on a Display object.
            This method is not meant to be called by any deveper,
                it is called inside the Display.draw(Circle Obj)
        """
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Rect: Negative Position")
        for i in range(100):
            theta = (2 * math.pi / 100) * i
            x = int(pos_x + self.__radius[0] * math.cos(theta))
            y = int(pos_y + self.__radius[1] * math.cos(theta))
            display_pixel_function(x, y, self.__color)

    def update_size(self, radius: Tuple[int, int]) -> None:
        """ Update the size of the object """
        if radius[0] <= 0 or radius[1] <= 0:
            raise ValueError("Circle: Negative radius")
        self.__radius = radius

    def update_color(self, color: int) -> None:
        """ Update the color of the Rect """
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Circle: Not valid color value")
        self.__color = color
