from typing import Any, Literal, overload, Tuple
from .MlxDisplay import MlxDisplay


class MlxWindow:
    """
    Main application window and its persistent Mlx drawing buffer.

    This object is used to represent a window where we can draw any
        Graphical object using its buffer. The goal of this object is to mimic
        the pygame display object.
    """

    @overload
    def __init__(
        self,
        session: Any,
        mlx_ptr: Any,
        dimension: tuple[int, int],
        title: str,
    ) -> None: ...

    @overload
    def __init__(
        self,
        session: Any,
        mlx_ptr: Any,
        dimension: int,
        title: int,
        legacy_title: str,
    ) -> None: ...

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
        if not self.__window_ptr:
            raise RuntimeError("failed to create MLX window")

        self.clear()

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

    def screen_update(self) -> None:
        """Display the complete persistent buffer in the main window."""
        self.__session.mlx_put_image_to_window(
            self.__mlx_ptr,
            self.__window_ptr,
            self.__image_ptr,
            0,
            0,
        )

    def close(self) -> None:
        """Release the image buffer and window owned by this screen."""
        if self.__closed:
            return

        self.__session.mlx_destroy_image(self.__mlx_ptr, self.__image_ptr)
        self.__session.mlx_destroy_window(self.__mlx_ptr, self.__window_ptr)
        self.__closed = True

    def create_display(self, size: Tuple[int, int]) -> MlxDisplay:
        """ Create a Subwindow where we can draw in before pushing to the window """

        if size[0] > self.__width or size[1] > self.__height:
            self.__session.mlx_destroy_window(
                    self.__mlx_ptr, self.__window_ptr
                    )
            raise RuntimeError("Invalide SubWindow Size")
        image_ptr = self.__session.mlx_new_image(
                self.__mlx_ptr,
                size[0],
                size[1]
                )
        if not image_ptr:
            self.__session.mlx_destroy_window(
                    self.__mlx_ptr, self.__window_ptr
                    )
            raise RuntimeError("failed to create MLX screen buffer")

        try:
            subwindow = MlxDisplay(self.__session, image_ptr, self.__mlx_ptr, self.__window_ptr, size)
            return subwindow
        except:
            self.__session.mlx_destroy_window(
                    self.__window_ptr
                    )
            self.__closed = True
            raise RuntimeError("Failed to create Subwindow")
