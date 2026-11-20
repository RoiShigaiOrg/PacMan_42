from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import (
    KEY_BACKSPACE, KEY_DELETE, KEY_RETURN
)
from .Component import Component
from typing import Tuple

PADDING: int = 4
BORDER: int = 2
CURSOR_WIDTH: int = 3
WHITE: int = 0xFFFFFFFF


class InputBar(Component):
    """A one-line text field the player types into with the keyboard."""

    def __init__(
            self, width: int, height: int,
            max_len: int = 30) -> None:
        """ Init Method of the InputBar Widget """
        if width <= 0 or height <= 0:
            raise ValueError("InputBar: Invalid dimension values")
        self.__dimension: Tuple[int, int] = (width, height)
        self.max_len = max_len
        self._label: str | None = None
        self.inputed_text = ""

    def reset(self) -> None:
        """ Empty the bar and force the next draw_text to redraw it """
        self.inputed_text = ""

    def update(self, input_handler: InputHandler) -> str | None:
        """
            Read the keys of the current frame.

            Return the typed text when Enter is pressed, None otherwise.
        """
        if input_handler.was_key_pressed(KEY_RETURN):
            validated = self.inputed_text.strip()
            self.inputed_text = ""
            return validated or None
        if input_handler.was_key_pressed(KEY_BACKSPACE):
            self.inputed_text = self.inputed_text[:-1]
            return None
        if input_handler.was_key_pressed(KEY_DELETE):
            self.inputed_text = ""
            return None
        for code in range(0x20, 0x7F):
            if (input_handler.was_key_pressed(code)
                    and len(self.inputed_text) < self.max_len):
                self.inputed_text += chr(code)
                return None
        return None

    def render(self, display:MlxDisplay, pos: Tuple[int, int]) -> None:
        """ Render Method of the InputHandler."""
        raise NotImplementedError("Input Handle not implemented with the proper logic.")

    def draw(self, display: MlxDisplay, background: int, border: int) -> None:
        """ Draw the frame of the bar in the image (before render()) """
        display.fill_rect(self.x + 2, self.y + 2,
                          self.width + 2, self.height + 2, border)
        display.fill_rect(self.x, self.y, self.width, self.height, WHITE)
        display.fill_rect(self.x + 2, self.y + 2,
                          self.width - 4, self.height - 4, background)

    def render_label(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """
            Write the text in the window (AFTER render()).

            Call it at every frame: the MLX only stays correct when the
                same short text is written again each frame.
        """
        display.write_text(self.x + 6, self.y + 4, 0xFFFFFFFF, self.inputed_text + "_")

    def callback(self) -> None:
        """Activate the component from the option scene."""
        pass
