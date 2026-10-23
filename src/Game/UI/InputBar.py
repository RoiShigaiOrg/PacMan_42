from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler.InputHandler import InputHandler
from .XpmAlphabet import XpmAlphabet
from Engine.InputHandler.KeyCode import (
    KEY_BACKSPACE, KEY_DELETE, KEY_RETURN
)

PADDING: int = 4
BORDER: int = 2
CURSOR_WIDTH: int = 3
WHITE: int = 0xFFFFFFFF


class InputBar:
    """A one-line text field the player types into with the keyboard.
    The text is drawn with an XPM alphabet, directly in the image."""

    def __init__(
            self, x: int, y: int, width: int,
            alphabet: XpmAlphabet, max_len: int = 30) -> None:
        """ Init Method of the InputBar Widget """
        if width <= 0:
            raise ValueError("input bar width must be positive")
        self.x = x
        self.y = y
        self.width = width
        self.height = alphabet.height + 2 * (PADDING + BORDER)
        self.max_len = max_len
        self.text = ""
        self.__alphabet = alphabet
        self.__drawn: str | None = None

    def reset(self) -> None:
        """ Empty the bar and force the next draw_text to redraw it """
        self.text = ""
        self.__drawn = None

    def update(self, input_handler: InputHandler) -> str | None:
        """
            Read the keys of the current frame.

            Return the typed text when Enter is pressed, None otherwise.
        """
        if input_handler.was_key_pressed(KEY_RETURN):
            validated = self.text.strip()
            self.text = ""
            return validated or None
        if input_handler.was_key_pressed(KEY_BACKSPACE):
            self.text = self.text[:-1]
            return None
        if input_handler.was_key_pressed(KEY_DELETE):
            self.text = ""
            return None
        for code in range(0x20, 0x7F):
            if (input_handler.was_key_pressed(code)
                    and len(self.text) < self.max_len):
                self.text += chr(code)
                return None
        return None

    def draw(self, display: MlxDisplay, background: int, border: int) -> None:
        """ Draw the frame of the bar in the image (before render()) """
        display.fill_rect(self.x + 2, self.y + 2,
                          self.width + 2, self.height + 2, border)
        display.fill_rect(self.x, self.y, self.width, self.height, WHITE)
        display.fill_rect(self.x + 2, self.y + 2,
                          self.width - 4, self.height - 4, background)

    def draw_text(self, display: MlxDisplay,
                  background: int,  cursor_color: int) -> None:
        """ Write the text in the window (after render()) """
        if self.text == self.__drawn:
            return
        inner = BORDER + PADDING
        display.fill_rect(self.x + BORDER, self.y + BORDER,
                          self.width - 2 * BORDER,
                          self.height - 2 * BORDER, background)
        self.__alphabet.write(display, self.x + inner, self.y + inner,
                              self.text)
        cursor_x = (self.x + inner + self.__alphabet.length_texte(self.text)
                    + 2)
        display.fill_rect(cursor_x, self.y + inner, CURSOR_WIDTH,
                          self.__alphabet.height, cursor_color)
        self.__drawn = self.text
