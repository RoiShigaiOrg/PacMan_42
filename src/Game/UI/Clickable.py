from Engine.Graphics import MlxDisplay
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_ENTER
from Engine.Graphics import Rect
from .Component import Component
from typing import Tuple


class Clickable(Component):
    """ Clickable Class Definition

    The Clickable is the UI Object serving to toggle an Option
        to True/False.
    """

    ENABLED_COLOR: int = 0xFF00FF00
    DISABLED_COLOR: int = 0xFFFF0000
    BORDER_COLOR: int = 0xFF808080
    MAX_INDICATOR_SIZE: int = 20

    def __init__(
            self,
            width: float, height: float,
            value: bool = False) -> None:
        """ Init method of the Clickable Component """
        if width <= 0.0 or height <= 0.0:
            raise ValueError("Clickable: Negative dimension")
        self.__dimension: Tuple[float, float] = (width, height)
        self.__shape: Rect | None = None
        self.__square: Rect | None = None
        self.__value: bool = value
        self._label: str | None = None
        self._selected: bool = False

    def read_value(self) -> bool:
        """ Read the current toggle value hold by the Clickable. """
        return self.__value

    def update(self, input_handler: InputHandler) -> None:
        """ Update the Clickable by referring on the user inputs. """
        if input_handler.was_key_pressed(KEY_ENTER):
            self.callback()

    def callback(self) -> None:
        """Toggle the value when the option scene activates this component."""
        self.__value = not self.__value

    def render(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """ Render Method of the Clickable Object """
        shape_width = max(1, display.relative_width(self.__dimension[0]))
        shape_height = max(1, display.relative_height(self.__dimension[1]))
        if not self.__shape:
            self.__shape = Rect(
                    shape_width,
                    shape_height,
                    pos[0], pos[1],
                    self.BORDER_COLOR,
                )
        else:
            self.__shape.update_pos(pos[0], pos[1])

        visible_width = max(1, min(shape_width, display.width - pos[0]))
        indicator_size = max(1, min(
            self.MAX_INDICATOR_SIZE,
            shape_height // 3,
            visible_width // 3,
        ))
        margin = min(4, max(0, visible_width - indicator_size))
        square_x = pos[0] + visible_width - indicator_size - margin
        square_y = pos[1] + max(0, (shape_height - indicator_size) // 2)
        color: int = self.ENABLED_COLOR if self.__value else self.DISABLED_COLOR

        if not self.__square:
            self.__square = Rect(
                    indicator_size, indicator_size,
                    square_x, square_y,
                    color,
                )
        else:
            self.__square.update_size(indicator_size, indicator_size)
            self.__square.update_pos(square_x, square_y)
            self.__square.update_color(color)

        color = 0xFF0A0A0A if self._selected else 0xFF000000
        self.__shape.update_color(color)
        self.__shape.fill(display)
        self.__square.fill(display)
