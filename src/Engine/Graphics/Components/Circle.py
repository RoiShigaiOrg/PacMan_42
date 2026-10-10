from .Components import Components
from .TextBox import TextBox
from .TextJustify import TEXT_CENTER, VALID_TEXT_JUSTIFICATIONS
from typing import Tuple, Any, List
import math


class Circle(Components):
    """
        Circle Object is a Components representing a Circle.
    """

    def __init__(
            self,
            x: int,
            y: int,
            pos_x: int,
            pos_y: int,
            color: int) -> None:
        """ Init Method for the Circle Object """
        if x <= 0 or y <= 0:
            raise ValueError("Circle: Negative dimension")
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Circle: Negative Position")
        self.__size: Tuple[int, int] = (x, y)
        self.__pos: List[int] = [pos_x, pos_y]
        self.__text: TextBox | None = None
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Circle: Not valid color value")
        self.__color = color

    @property
    def pos(self) -> Tuple[int, int]:
        """Return the top-left position of the circle bounding box."""
        return self.__pos[0], self.__pos[1]

    @property
    def size(self) -> Tuple[int, int]:
        """Return the size of the circle bounding box."""
        return self.__size

    def draw(self, display: Any) -> None:
        """Draw only the circle circumference."""
        width, height = self.__size
        radius_x, radius_y = (width - 1) / 2, (height - 1) / 2
        center_x = self.__pos[0] + radius_x
        center_y = self.__pos[1] + radius_y

        for i in range(500):
            theta = (2 * math.pi / 500) * i
            x = int(center_x + radius_x * math.cos(theta))
            y = int(center_y + radius_y * math.sin(theta))
            display.draw_pixel(x, y, self.__color)
        self.draw_text(display)

    def fill(self, display: Any) -> None:
        """Draw a filled circle or ellipse."""
        width, height = self.__size
        radius_x, radius_y = (width - 1) / 2, (height - 1) / 2
        center_x = self.__pos[0] + radius_x
        center_y = self.__pos[1] + radius_y

        for y in range(self.__pos[1], self.__pos[1] + height):
            for x in range(self.__pos[0], self.__pos[0] + width):
                normalized_x = (x - center_x) / radius_x
                normalized_y = (y - center_y) / radius_y

                if normalized_x ** 2 + normalized_y ** 2 <= 1:
                    display.draw_pixel(x, y, self.__color)

        self.draw_text(display)

    def add_text(
            self, text_box: TextBox, justify: int = TEXT_CENTER
    ) -> None:
        """Link text to the center of the circle or ellipse."""
        if not isinstance(text_box, TextBox):
            raise ValueError("Circle: Invalid TextBox Value")
        if justify not in VALID_TEXT_JUSTIFICATIONS:
            raise ValueError("Circle: Invalid text justification")
        self.__text = text_box

    def draw_text(self, display: Any) -> None:
        """Draw linked text at the circle's center."""
        if self.__text is None:
            return
        text_width, text_height = self.__text.text_size
        text_x = self.__pos[0] + (self.__size[0] - text_width) // 2
        text_y = self.__pos[1] + (self.__size[1] - text_height) // 2
        self.__text.draw(display, text_x, text_y)

    def update_size(self, size: Tuple[int, int]) -> None:
        """ Update the size of the object """
        if size[0] <= 0 or size[1] <= 0:
            raise ValueError("Circle: Negative dimension")
        self.__size = size

    def update_pos(self, pos_x: int, pos_y: int) -> None:
        """Update the top-left position of the circle bounding box."""
        if pos_x < 0 or pos_y < 0:
            raise ValueError("Circle: Negative Position")
        self.__pos[0] = pos_x
        self.__pos[1] = pos_y

    def update_color(self, color: int) -> None:
        """ Update the color of the Rect """
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("Circle: Not valid color value")
        self.__color = color
