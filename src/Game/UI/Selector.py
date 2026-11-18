from Engine.Engine import Engine
from Engine.Graphics import MlxDisplay, Rect
from Engine.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import (KEY_RIGHT, KEY_LEFT)
from typing import Callable, Any, List, Tuple
from .Component import Component


class Selector(Component):
    """ Selector Class Definition

    The Selector is the Component UI Object serving to display
        multiple KEY within the same Object.
    """

    def __init__(
            self,
            engine: Engine,
            width: float, height: float,
            key: Any,
            first_key: Any | None = None,
            callback: Callable | None = None) -> None:
        """ Init method of the Selector Component. """
        if width <= 0.0 or height <= 0.0:
            raise ValueError("Selector: Negative dimension")
        self.__engine: Engine = engine
        self.__dimension: Tuple[float, float] = (width, height)
        if isinstance(key, dict):
            self.__key: Any = [key.keys()]
        else:
            self.__key: Any = key
        self.__callback()
        if first_key:
            self.__display_key: Any = first_key
        elif isinstance(key, List):
            self.__display_key: Any = key[0]
        else:
            raise ValueError("Selector: first key not given")
        self.__shape: Rect = None

    def update(self, input_handler: InputHandler) -> None:
        """ Update the selector by referring on the user inputs """
        if input_handler.was_key_pressed(KEY_RIGHT):
            self.__selector = self.__selector + 1 % len(self.__key)
        if input_handler.was_key_pressed(KEY_LEFT):
            self.__selector = self.__selector - 1
            if self.__selector < 0:
                self.__selector = len(self.__key)

    def callback(self) -> None:
        """ Run the callback method associated to the selector. """
        if not self.__callback():
            raise ValueError("Selector: No callback function")
        if isinstance(self.__key, dict):
            self.__callback(self.__key[self.__display_key])
        elif isinstance(self.__key, list):
            self.__callback(self.__key[self.__selector])
        else:
            raise ValueError("Selector: Error key format")

    def render(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """ Render Method of the Selector Object """
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

    def add_label(self, text: str) -> None:
        """ Add text Label to this Selector """
        self.__label: str = text
