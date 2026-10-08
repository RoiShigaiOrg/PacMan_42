from .TextBox import TextBox
from typing import Any
from .Components import Components

TEXT_CENTER: int = 0
TEXT_RIGHT: int = 1
TEXT_LEFT: int = 2

TEXT_CENTER_LOW: int = 3
TEXT_RIGHT_LOW: int = 4
TEXT_LEFT_LOW: int = 5

TEXT_CENTER_HIGH: int = 6
TEXT_RIGHT_HIGH: int = 7
TEXT_LEFT_HIGH: int = 8


class Rect(Components):
    """
        Rect Object is a Components representing a Rectangle or a square.
    """

    def __init__(self, x: int, y: int, color: int) -> None:
        """ Init method for the Rect Object """
        if x <= 0 or y <= 0:
            raise ValueError("Rect: Negative dimension")
        self.__text: TextBox | None = None
        self.__text_flag: bool = False
        self.__justify_text: int | None = None
        self.__width: int = x
        self.__height: int = y
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Rect: Not valid color value")
        self.__color = color

    def draw(
            self,
            display: Any,
            pos_x: int,
            pos_y: int) -> None:
        """
            Private method to draw the Rect on a Display object.
            This method is not meant to be called by any deveper,
                it is called inside the Display.draw(Rect Obj)
        """
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Rect: Negative Position")
        for y in range(pos_y, pos_y + self.__height):
            for x in range(pos_x, pos_x + self.__width):
                display.draw_pixel(x, y, self.__color)
        if self.__text_flag:
            self.__draw_text()

    def add_text(
            self,
            text_box: TextBox,
            justify: int = TEXT_CENTER) -> None:
        """ Link a TextBox Component to be display to the Rect """
        if text_box is None:
            raise ValueError("Rect: Invalid TextBox Value")
        self.__text = text_box
        self.__text_flag = True
        self.__justify_text = justify

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

    def draw_text(self) -> None:
        """ Draw Method to display text on Rect """
        raise NotImplementedError("Draw Text on components not implemented yet")
        if self.__justify_text == TEXT_CENTER:
            ...
