from Engine.Engine import Engine
from Engine.Graphics import MlxDisplay, Rect
from Engine.InputHandler import InputHandler
from typing import Callable, Any, Tuple
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
            callback: Callable[[Any], None] | None = None) -> None:
        """ Init method of the Selector Component. """
        if width <= 0.0 or height <= 0.0:
            raise ValueError("Selector: Negative dimension")
        self.__engine: Engine = engine
        self.__dimension: Tuple[float, float] = (width, height)
        self._label: str | None = None
        self.__key: Any = list(key.keys()) if isinstance(key, dict) else key
        self.__callback: Callable[[Any], None] | None = callback
        if first_key is not None:
            self.__display_key: Any = first_key
        elif isinstance(self.__key, list) and self.__key:
            self.__display_key = self.__key[0]
        else:
            raise ValueError("Selector: first key not given")
        self.__shape: Rect | None = None
        self.__selector: int = self.__init_selector()
        self._selected: bool = False

    def update(self, input_handler: InputHandler) -> None:
        """ Update the selector by referring on the user inputs """
        if input_handler.was_key_pressed(
                self.__engine.get_config_key("RIGHT")):
            self.__selector = (self.__selector + 1) % len(self.__key)
        if input_handler.was_key_pressed(
                self.__engine.get_config_key("LEFT")):
            self.__selector = (self.__selector - 1)
            if self.__selector < 0:
                self.__selector = len(self.__key) - 1
        self.__display_key = str(self.__key[self.__selector])

    def read_value(self) -> Any:
        """Return the currently selected value (for example, ``UP``)."""
        return self.__key[self.__selector]

    def callback(self) -> None:
        """ Run the callback method associated to the selector. """
        if self.__callback is None:
            return
        if isinstance(self.__key, list):
            self.__callback(self.__key[self.__selector])
        else:
            raise ValueError("Selector: Error key format")

    def render(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """ Render Method of the Selector Object """
        width = max(1, display.relative_width(self.__dimension[0]))
        height = max(1, display.relative_height(self.__dimension[1]))
        if not self.__shape:
            self.__shape = Rect(
                    width,
                    height,
                    pos[0], pos[1],
                    0xFF000000
                )
        else:
            self.__shape.update_size(width, height)
            self.__shape.update_pos(pos[0], pos[1])
        color: int = 0xFF0A0A0A if self._selected else 0xFF000000
        self.__shape.update_color(color)
        self.__shape.fill(display)

    def render_label(self, display: MlxDisplay, pos: Tuple[int, int]) -> None:
        """ Render label method of the Selector class """
        text_x: int = int(display.relative_width(self.__dimension[0]) * 0.7)
        select_text: str = f"<  {self.__display_key}  >"
        if self._label:
            display.write_text(pos[0], pos[1], 0xFFFFFFFF, self._label)
            display.write_text(
                pos[0] + text_x, pos[1], 0xFFFFFFFF, select_text
            )

    def __init_selector(self) -> int:
        for i, key in enumerate(self.__key):
            if key == self.__display_key:
                return i
        return 0
