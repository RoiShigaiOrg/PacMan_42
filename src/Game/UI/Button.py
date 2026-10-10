from Engine.InputHandler.InputHandler import InputHandler
from Engine.Graphics.Components.Rect import Rect
from Engine.Graphics.Components.TextBox import TextBox
from typing import Any


class Button:
    """A rectangular UI control that reacts to the left mouse button."""

    def __init__(
            self,
            width: int,
            height: int,
            color_1: int,
            color_2: int,
            text: str | None = None) -> None:
        """ Init Method of the Button Widget """
        raise NotImplementedError("Need to implement Button Class First")
        if width <= 0 or height <= 0:
            raise ValueError("button dimensions must be positive")
        self.width = width
        self.height = height
        self.rect = Rect(width, height, color_1)
        if text:
            self.rect.add_text(TextBox(text, color_2))
        self.hovered = False
        self.color = [color_1, color_2]

    def contains(self, position: tuple[int, int]) -> bool:
        """Return whether a window-coordinate position is inside the button."""
        mouse_x, mouse_y = position
        return (
            self.x <= mouse_x < self.x + self.width
            and self.y <= mouse_y < self.y + self.height
        )

    def draw(self, display: Any) -> None:
        color = self.__color[0] if self.hovered  else self.__color[1]
        raise NotImplementedError("Need to implement Button Class First")

    def update(self, input_handler: InputHandler) -> bool:
        """Update hover state and return whether the button was clicked."""
        self.hovered = self.contains(input_handler.mouse_position)
        return self.hovered and input_handler.was_mouse_button_pressed(1)
