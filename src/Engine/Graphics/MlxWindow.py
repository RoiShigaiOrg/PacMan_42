from collections.abc import Callable
from typing import Any, Tuple
from .MlxDisplay import MlxDisplay


class MlxWindow:
    """
    Main application window and its persistent Mlx drawing buffer.

    This object is used to represent a window where we can draw any
        Graphical object using its buffer. The goal of this object is to mimic
        the pygame display object.
    """

    def __init__(
        self,
        session: Any,
        mlx_ptr: Any,
        dimension: tuple[int, int] | int,
        title: str | int,
        legacy_title: str | None = None,
    ) -> None:
        """ Init Method of the MlxWindow object """
        if isinstance(dimension, int):
            if not isinstance(title, int) or legacy_title is None:
                raise TypeError("invalid screen dimensions")
            dimension = (dimension, title)
            title = legacy_title
        else:
            if not isinstance(title, str) or legacy_title is not None:
                raise TypeError("invalid screen title")

        if dimension[0] <= 0 or dimension[1] <= 0:
            raise ValueError("screen dimensions must be positive")

        self.__session = session
        self.__mlx_ptr = mlx_ptr
        self.__width = dimension[0]
        self.__height = dimension[1]
        self.__title = title
        self.__closed = False
        self.__window_ptr = session.mlx_new_window(
            mlx_ptr,
            self.__width,
            self.__height,
            title,
        )
        self.__display_list: list[MlxDisplay] = []
        if not self.__window_ptr:
            raise RuntimeError("failed to create MLX window")

    @property
    def width(self) -> int:
        """Return the screen width in pixels."""
        return self.__width

    @property
    def height(self) -> int:
        """Return the screen height in pixels."""
        return self.__height

    @property
    def title(self) -> str:
        """Return the screen title."""
        return self.__title

    @property
    def native_ptr(self) -> Any:
        """Return the native MLX window pointer for engine services."""
        return self.__window_ptr

    def size(self) -> tuple[int, int]:
        """Return ``(width, height)`` in pixels."""
        return self.__width, self.__height

    def draw(self, image: Any, x: int, y: int) -> None:
        """Draw an MLX image into the window at ``(x, y)``."""
        self.__session.mlx_put_image_to_window(
            self.__mlx_ptr,
            self.__window_ptr,
            image,
            x,
            y,
        )

    def close(self) -> None:
        """Release the native window owned by this object."""
        if self.__closed:
            return

        for display in self.__display_list:
            display.destroy_image()
        self.__display_list.clear()
        self.__session.mlx_destroy_window(self.__mlx_ptr, self.__window_ptr)
        self.__closed = True

    def recreate(
            self,
            size: tuple[int, int],
            on_window_ready: Callable[[Any], None] | None = None,
    ) -> None:
        """Replace the native window and all attached display buffers.

        New resources are prepared before the old window is touched. If
        preparation fails, the old window and displays remain usable.
        """
        width, height = size
        if width <= 0 or height <= 0:
            raise ValueError("screen dimensions must be positive")
        if self.__closed:
            raise RuntimeError("cannot recreate a closed window")
        if size == self.size():
            return

        replacement_window = self.__session.mlx_new_window(
            self.__mlx_ptr, width, height, self.__title
        )
        if not replacement_window:
            raise RuntimeError("failed to create replacement MLX window")

        replacements: list[MlxDisplay] = []
        try:
            for display in self.__display_list:
                old_width, old_height = display.size()
                display_size = (
                    max(1, round(old_width * width / self.__width)),
                    max(1, round(old_height * height / self.__height)),
                )
                image_ptr = self.__session.mlx_new_image(
                    self.__mlx_ptr, display_size[0], display_size[1]
                )
                if not image_ptr:
                    raise RuntimeError("failed to create MLX display buffer")
                replacements.append(MlxDisplay(
                    self.__session,
                    image_ptr,
                    self.__mlx_ptr,
                    replacement_window,
                    display_size,
                ))

            if on_window_ready is not None:
                on_window_ready(replacement_window)
        except Exception:
            for display in replacements:
                display.destroy_image()
            self.__session.mlx_destroy_window(
                self.__mlx_ptr, replacement_window
            )
            raise

        old_window = self.__window_ptr
        self.__window_ptr = replacement_window
        self.__width = width
        self.__height = height
        for current, replacement in zip(self.__display_list, replacements):
            current.swap_buffer(replacement)
            replacement.destroy_image()
        self.__session.mlx_destroy_window(self.__mlx_ptr, old_window)

    def create_display(self, size: Tuple[int, int]) -> MlxDisplay:
        """Create a subwindow where drawing can happen before presentation."""

        if (
            size[0] <= 0
            or size[1] <= 0
            or size[0] > self.__width
            or size[1] > self.__height
        ):
            raise ValueError(
                "display dimensions must be positive and fit window"
            )

        if self.__closed:
            raise RuntimeError("cannot create a display for a closed window")

        image_ptr = self.__session.mlx_new_image(
            self.__mlx_ptr, size[0], size[1]
        )
        if not image_ptr:
            raise RuntimeError("failed to create MLX display buffer")

        display = MlxDisplay(
            self.__session,
            image_ptr,
            self.__mlx_ptr,
            self.__window_ptr,
            size,
        )
        self.__display_list.append(display)
        return display
