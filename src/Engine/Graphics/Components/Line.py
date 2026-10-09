from .Components import Components
from .TextBox import TextBox
from .TextJustify import (
    TEXT_CENTER,
    TEXT_END,
    TEXT_START,
    VALID_TEXT_JUSTIFICATIONS,
)
from typing import Tuple, Any
import math


class Line(Components):
    """
        Line Object is a Components representing a Line or a square.
    """

    def __init__(
            self, x: Tuple[int, int], y: Tuple[int, int], color: int
    ) -> None:
        """ Init method for the Line object """
        if x[0] < 0 or x[1] < 0 or y[0] < 0 or y[1] < 0:
            raise ValueError("Line: Negative dimension")
        self.__start = x
        self.__end = y
        self.__text: TextBox | None = None
        self.__justify_text = TEXT_CENTER
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Line: Not valid color value")
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
            raise ValueError("Line: Negative Position")

        x1, y1 = self.__start
        x2, y2 = self.__end
        x1 += pos_x
        y1 += pos_y
        x2 += pos_x
        y2 += pos_y

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            display.draw_pixel(x1, y1, self.__color)

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx

            if e2 < dx:
                err += dx
                y1 += sy

        self.__draw_text(display, pos_x, pos_y)

    def add_text(self, text_box: TextBox, justify: int = TEXT_CENTER) -> None:
        """Link horizontal text to the line using its local directions."""
        if not isinstance(text_box, TextBox):
            raise ValueError("Line: Invalid TextBox Value")
        if justify not in VALID_TEXT_JUSTIFICATIONS:
            raise ValueError("Line: Invalid text justification")
        self.__text = text_box
        self.__justify_text = justify

    def __draw_text(self, display: Any, pos_x: int, pos_y: int) -> None:
        """Draw linked horizontal text relative to the line."""
        if self.__text is None:
            return

        start_x, start_y = self.__start
        end_x, end_y = self.__end
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.hypot(dx, dy)
        if length == 0:
            return

        text_width, _ = self.__text.text_size
        horizontal = self.__justify_text % 3
        if horizontal == TEXT_START:
            along = 0.0
        elif horizontal == TEXT_END:
            along = max(0, length - text_width)
        else:
            along = max(0, (length - text_width) / 2)

        unit_x = dx / length
        unit_y = dy / length
        text_x = start_x + unit_x * along
        text_y = start_y + unit_y * along

        vertical = self.__justify_text // 3
        if vertical == 2:
            text_x += unit_y * 5
            text_y -= unit_x * 5
        elif vertical == 1:
            text_x -= unit_y * 5
            text_y += unit_x * 5

        self.__text.draw(
            display,
            int(pos_x + text_x),
            int(pos_y + text_y),
        )
