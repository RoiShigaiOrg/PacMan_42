from Engine.InputHandler.InputHandler import InputHandler


class Button:
    """A rectangular UI control that reacts to the left mouse button."""

    def __init__(
            self, x: int, y: int, width: int, height: int
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("button dimensions must be positive")
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hovered = False

    def contains(self, position: tuple[int, int]) -> bool:
        """Return whether a window-coordinate position is inside the button."""
        mouse_x, mouse_y = position
        return (
            self.x <= mouse_x < self.x + self.width
            and self.y <= mouse_y < self.y + self.height
        )

    def update(self, input_handler: InputHandler) -> bool:
        """Update hover state and return whether the button was clicked."""
        self.hovered = self.contains(input_handler.mouse_position)
        return self.hovered and input_handler.was_mouse_button_pressed(1)
