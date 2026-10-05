from typing import Callable
from .Components import Components


class Rect(Components):
    """
        Rect Object is a Components representing a Rectangle or a square.
    """

    def __init__(self, x: int, y: int, color: int) -> None:
        """ Init method for the Rect Object """
        if x <= 0 or y <= 0:
            raise ValueError("Rect: Negative dimension")
        self.__width: int = x
        self.__height: int = y
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Rect: Not valid color value")
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
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Rect: Negative Position")
        for y in range(pos_y):
            for x in range(pos_x):
                display_pixel_function(x, y, self.__color)

    def update_size(self, x: int, y: int) -> None:
        """ Update the size of the object """
        if x < 0 or y < 0:
            raise ValueError("Rect: Negative dimension")
        self.__width = x
        self.__height = y

    def update_color(self, color: int) -> None:
        """ Update the color of the Rect """
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Rect: Not valid color value")
        self.__color = color
