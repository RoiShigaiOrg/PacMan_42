from .Components import Components
from typing import Tuple, Any
import math


class Circle(Components):
    """
        Circle Object is a Components representing a Circle.
    """

    def __init__(self, x: int, y: int, color: int) -> None:
        """ Init Method for the Circle Object """
        if x <= 0 or y <= 0:
            raise ValueError("Circle: Negative dimension")
        self.__radius: Tuple[int, int] = (x, y)
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Circle: Not valid color value")
        self.__color = color

    def draw(
            self,
            display: Any,
            pos_x: int,
            pos_y: int) -> None:
        """Draw only the circle circumference."""
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Circle: Negative Position")

        radius_x, radius_y = self.__radius

        for i in range(500):
            theta = (2 * math.pi / 500) * i
            x = int(pos_x + radius_x * math.cos(theta))
            y = int(pos_y + radius_y * math.sin(theta))
            display.draw_pixel(x, y, self.__color)

    def fill(
            self,
            display: Any,
            pos_x: int,
            pos_y: int) -> None:
        """Draw a filled circle or ellipse."""
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Circle: Negative Position")

        radius_x, radius_y = self.__radius

        for y in range(pos_y - radius_y, pos_y + radius_y + 1):
            for x in range(pos_x - radius_x, pos_x + radius_x + 1):
                normalized_x = (x - pos_x) / radius_x
                normalized_y = (y - pos_y) / radius_y

                if normalized_x ** 2 + normalized_y ** 2 <= 1:
                    display.draw_pixel(x, y, self.__color)

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
