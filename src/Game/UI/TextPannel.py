from Engine import InputHandler
from Engine.InputHandler.KeyCode import KEY_ENTER
from .Component import Component
from Engine.Graphics import Rect
from Engine.Graphics import MlxDisplay
from typing import Callable, Tuple


class TextPannel(Component):
    """ TextPannel Class Definition

    Text Pannel is a simple UI Component mean to simply
        display text and work with the Component API features
        as holding selection easily react to any event easily.
    """

    def __init__(
            self,
            width: float, height: float,
            callback: Callable | None = None) -> None:
        """ Init Method of the TextPannel Object """
        if width <= 0.0 or height <= 0.0:
            raise ValueError("TextPannel: Invalid dimension")
        self.__dimension: Tuple[float, float] = (width, height)
        if callback:
            self.__callback = callback
        self.__shape: Rect | None = None
        self._label: str | None = None
        self._selected: bool = False

    def update(self, input_handler: InputHandler) -> None:
        """ Update Method of the TextPannel """
        if input_handler.was_key_pressed(KEY_ENTER):
            if self.__callback:
                self.__callback()
            else:
                raise ValueError(
                        "TextPannel: No Callback function associated"
                    )

    def render(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """ Render Method of the TextPannel Object """
        width = max(1, display.relative_width(self.__dimension[0]))
        height = max(1, display.relative_height(self.__dimension[1]))
        if not self.__shape:
            self.__shape = Rect(
                    width,
                    height,
                    pos[0], pos[1],
                    self.BORDER_COLOR,
                )
        else:
            self.__shape.update_size(width, height)
            self.__shape.update_pos(pos[0], pos[1])
        color: int = 0xFF0A0A0A if self._selected else 0xFF000000
        self.__shape.update_color(color)
        self.__shape.fill(display)

    def render_label(self, display: MlxDisplay, pos: Tuple[int, int]) -> None:
        """ Render label method of the TextPannel Object """
        if self._label:
            display.write_text(pos[0], pos[1], 0xFFFFFFFF, self._label)
