from .Components import Components
from typing import Any


class TextBox(Components):
    """
        TextBox Class definition

        TextBox is a Component type object mainly used to display text.
    """

    def __init__(self, text: str, color: int) -> None:
        """ Init Method of the TextBox component """
        self.__text = text
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("TextBox: Not valid color value")
        self.__color = color

    def draw(self, display: Any, pos_x: int, pos_y: int) -> None:
        """ Draw method for TextBox """
        display.write_text(pos_x, pos_y, self.__color, self.__text)

    def update_color(self, color: int) -> None:
        """ Update color value of the TextBox Components """
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("TextBox: Not valid color value")
        self.__color = color

    def update_text(self, text: str) -> None:
        """ Update the text value of the TextBox Component """
        self.__text = text
