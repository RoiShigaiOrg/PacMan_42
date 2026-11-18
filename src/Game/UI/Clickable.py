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

    def __init__(
            self,
            width: float, height: float,
            value: bool = False) -> None:
        """ Init method of the Clickable Component """
        if width <= 0.0 or height <= 0.0:
            raise ValueError("Clickable: Negative dimension")
        self.__dimension: Tuple[float, float] = (width, height)
        self.__shape: Rect | None = None
        self.__value: bool = value

    def read_value(self) -> None:
        """ Read the current toggle value hold by the Clickable. """
        return self.__value

    def update(self, input_handler: InputHandler) -> None:
        """ Update the Clickable by referring on the user inputs. """
        if input_handler.was_key_pressed(KEY_ENTER):
            self.__value = not self.__value

    def render(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """ Render Method of the Clickable Object """
        if not self.__shape:
            self.__shape = Rect(
                    display.relative_width(self.__dimension[0]),
                    display.relative_height(self.__dimension[1]),
                    pos[0], pos[1],
                    0xFF000000
                )
        self.__shape.draw(display)
        if self.__label:
            display.write_text(pos[0], pos[1], 0xFFFFFFFF, self.__label)
