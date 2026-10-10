from .TextBox import TextBox
from typing import Any, Tuple, List
from .Components import Components
from .TextJustify import (
    TEXT_CENTER,
    TEXT_CENTER_HIGH,
    TEXT_CENTER_LOW,
    TEXT_END,
    TEXT_END_HIGH,
    TEXT_END_LOW,
    TEXT_START,
    TEXT_START_HIGH,
    TEXT_START_LOW,
    VALID_TEXT_JUSTIFICATIONS,
)

TEXT_JUSTIFICATIONS = {
    TEXT_CENTER: ("center", "center"),
    TEXT_END: ("end", "center"),
    TEXT_START: ("start", "center"),
    TEXT_CENTER_LOW: ("center", "low"),
    TEXT_END_LOW: ("end", "low"),
    TEXT_START_LOW: ("start", "low"),
    TEXT_CENTER_HIGH: ("center", "high"),
    TEXT_END_HIGH: ("end", "high"),
    TEXT_START_HIGH: ("start", "high"),
}


class Rect(Components):
    """
        Rect Object is a Components representing a Rectangle or a square.
    """

    def __init__(
            self,
            x: int,
            y: int,
            pos_x: int,
            pos_y: int,
            color: int) -> None:
        """ Init method for the Rect Object """
        if x <= 0 or y <= 0:
            raise ValueError("Rect: Negative dimension")
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Rect: Negative Position")
        self.__text: TextBox | None = None
        self.__text_flag: bool = False
        self.__justify_text: int | None = None
        self.__width: int = x
        self.__height: int = y
        self.__pos: List[int] = [pos_x, pos_y]
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Rect: Not valid color value")
        self.__color = color

    @property
    def pos(self) -> Tuple[int, int]:
        """ Return the position of the Rect """
        return (self.__pos[0], self.__pos[1])

    @property
    def size(self) -> Tuple[int, int]:
        """ Return the size of the Rect """
        return (self.__width, self.__height)

    def draw(
            self,
            display: Any) -> None:
        """
            Private method to draw the Rect on a Display object.
            This method is not meant to be called by any deveper,
                it is called inside the Display.draw(Rect Obj)
        """
        for y in range(self.__pos[1], self.__pos[1] + self.__height):
            for x in range(self.__pos[0], self.__pos[0] + self.__width):
                display.draw_pixel(x, y, self.__color)
        if self.__text_flag:
            self.__draw_text(display)

    def draw_text(
            self,
            display: Any,
    ) -> None:
        """Draw the linked text after the rectangle is presented."""
        if self.__text_flag:
            self.__draw_text(display)

    def add_text(
            self,
            text_box: TextBox,
            justify: int = TEXT_CENTER) -> None:
        """ Link a TextBox Component to be display to the Rect """
        if not isinstance(text_box, TextBox):
            raise ValueError("Rect: Invalid TextBox Value")
        if justify not in VALID_TEXT_JUSTIFICATIONS:
            raise ValueError("Rect: Invalid text justification")
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

    def update_text(self, text: str) -> None:
        """ Update the text displayed in the Rect Component """
        if not self.__text_flag:
            raise ValueError("Rect: no text link with this object")
        self.__text.update_text(text)

    def update_pos(self, pos_x: int, pos_y: int) -> None:
        """ Update the Rect position """
        self.__pos[0] = pos_x
        self.__pos[1] = pos_y

    def __draw_text(self, display: Any) -> None:
        """Draw linked text at the requested position in the rectangle."""
        if self.__text is None or self.__justify_text is None:
            return
        text_width, text_height = self.__text.text_size
        horizontal, vertical = TEXT_JUSTIFICATIONS[self.__justify_text]
        if horizontal == "start":
            text_x = self.__pos[0]
        elif horizontal == "end":
            text_x = self.__pos[0] + self.__width - text_width
        else:
            text_x = self.__pos[0] + (self.__width - text_width) // 2

        if vertical == "high":
            text_y = self.__pos[1]
        elif vertical == "low":
            text_y = self.__pos[1] + self.__height - text_height
        else:
            text_y = self.__pos[1] + (self.__height - text_height) // 2
        self.__text.draw(display, text_x, text_y)
