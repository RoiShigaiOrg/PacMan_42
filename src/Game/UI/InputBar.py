from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import (
    KEY_BACKSPACE, KEY_DELETE, KEY_ENTER, KEY_ESC, KEY_UP, KEY_DOWN,
    KEY_LEFT, KEY_RIGHT, KEY_TAB,
)
from .Component import Component
from typing import Tuple, Callable

WHITE: int = 0xFFFFFFFF
BACKGROUND: int = 0xFF101010
BORDER_COLOR: int = 0xFFFFFFFF
PADDING: int = 8


class InputBar(Component):
    """A text field that can also capture a single key binding."""

    def __init__(
            self, width: float, height: float,
            callback: Callable[[str], None] | None = None,
            max_len: int = 10) -> None:
        """ Init Method of the InputBar Widget """
        if width <= 0 or height <= 0:
            raise ValueError("InputBar: Invalid dimension values")
        if max_len <= 0:
            raise ValueError("InputBar: max_len must be positive")
        self.__dimension: Tuple[float, float] = (width, height)
        self.max_len = max_len
        self._label: str | None = None
        self.__callback: Callable[[str], None] | None = callback
        self.inputed_text = ""
        self.__capture_target: str | None = None
        self.__current_key: int | None = None

    @property
    def key_capture_active(self) -> bool:
        """Whether this bar is currently waiting for a key press."""
        return self.__capture_target is not None

    def begin_key_capture(self, target: str, current_key: int) -> None:
        """Show a prompt and prepare to capture a key for ``target``."""
        if not target:
            raise ValueError("InputBar: key capture target cannot be empty")
        if current_key < 0:
            raise ValueError("InputBar: key code cannot be negative")
        self.__capture_target = target
        self.__current_key = current_key

    def end_key_capture(self) -> None:
        """Hide the key-capture prompt without changing the typed text."""
        self.__capture_target = None
        self.__current_key = None

    def capture_key(self, input_handler: InputHandler) -> int | None:
        """Return the newest key press while key-capture mode is active."""
        if not self.key_capture_active:
            return None
        keycode: int | None = input_handler.last_key_pressed
        return keycode

    def reset(self) -> None:
        """ Empty the bar and force the next draw_text to redraw it """
        self.inputed_text = ""

    def update(self, input_handler: InputHandler) -> str | None:
        """
            Read the keys of the current frame.

            Return the typed text when Enter is pressed, None otherwise.
        """
        if input_handler.was_key_pressed(KEY_ENTER):
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
            char = chr(code)
            if not (char.isalnum() or char == " "):
                continue
            if (input_handler.was_key_pressed(code)
                    and len(self.inputed_text) < self.max_len):
                self.inputed_text += chr(code)
                return None
        return None

    def render(self, display: MlxDisplay, pos: Tuple[int, int]) -> None:
        """Draw the bar background into the display buffer."""
        shape_width = max(1, display.relative_width(self.__dimension[0]))
        shape_height = max(1, display.relative_height(self.__dimension[1]))
        display.fill_rect(
            pos[0], pos[1], shape_width, shape_height, BORDER_COLOR
        )
        display.fill_rect(
            pos[0] + 2, pos[1] + 2,
            max(1, shape_width - 4), max(1, shape_height - 4),
            BACKGROUND,
        )

    def render_text(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """Draw the prompt or typed text after presenting the display."""
        if self.key_capture_active:
            target = self.__capture_target
            current = self.format_keycode(self.__current_key)
            text = (
                f"Set {target} (currently {current}) - press a key; "
                "Esc cancels"
            )
        else:
            text = self.inputed_text + "_"
        text_x = pos[0] + PADDING
        text_y = pos[1] + max(12, display.relative_height(0.025))
        if text_x < display.width and text_y < display.height:
            display.write_text(text_x, text_y, WHITE, text)

    @staticmethod
    def format_keycode(keycode: int | None) -> str:
        """Return a readable label for a keysym, falling back to its number."""
        if keycode is None:
            return "?"
        special_keys = {
            KEY_ENTER: "ENTER",
            KEY_ESC: "ESC",
            KEY_TAB: "TAB",
            KEY_UP: "UP ARROW",
            KEY_DOWN: "DOWN ARROW",
            KEY_LEFT: "LEFT ARROW",
            KEY_RIGHT: "RIGHT ARROW",
            KEY_BACKSPACE: "BACKSPACE",
            KEY_DELETE: "DELETE",
        }
        if keycode in special_keys:
            return special_keys[keycode]
        if 0x20 <= keycode <= 0x7E:
            return chr(keycode).upper()
        return f"KEY {keycode}"

    def callback(self) -> None:
        """Call the callback function associated with."""
        if self.__callback:
            self.__callback(self.inputed_text)
        else:
            raise ValueError("InputBar: No Callback function associated with.")
