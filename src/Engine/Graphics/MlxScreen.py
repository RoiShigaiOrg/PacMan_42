from typing import Any, Literal, Tuple


class MlxScreen:
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
        dimension: Tuple[int, int],
        title: str,
    ) -> None:
        """ Init Method of the MlxScreen object """
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

        self.__image_ptr = session.mlx_new_image(
                mlx_ptr,
                self.__width,
                self.__height
                )
        if not self.__image_ptr:
            session.mlx_destroy_window(mlx_ptr, self.__window_ptr)
            raise RuntimeError("failed to create MLX screen buffer")

        (
            self.__data,
            self.__bits_per_pixel,
            self.__stride,
            self.__format,
        ) = session.mlx_get_data_addr(self.__image_ptr)
        if self.__bits_per_pixel != 32:
            session.mlx_destroy_image(mlx_ptr, self.__image_ptr)
            session.mlx_destroy_window(mlx_ptr, self.__window_ptr)
            self.__closed = True
            raise RuntimeError("MLX screen buffer is not a 32-bit image")

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

    def pixel(self, x: int, y: int, color: int) -> None:
        """Write one ARGB pixel to the persistent screen buffer."""
        if not 0 <= x < self.__width or not 0 <= y < self.__height:
            raise ValueError("pixel coordinates are outside the screen")
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("color must be a 32-bit unsigned integer")

        offset = y * self.__stride + x * (self.__bits_per_pixel // 8)
        byte_order: Literal["little", "big"] = (
            "little" if self.__format == 0 else "big"
        )
        self.__data[offset:offset + 4] = color.to_bytes(4, byte_order)

    def clear(self, color: int = 0x00000000) -> None:
        """Fill the entire persistent buffer with an ARGB color."""
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("color must be a 32-bit unsigned integer")

        byte_order: Literal["little", "big"] = (
            "little" if self.__format == 0 else "big"
        )
        pixel = color.to_bytes(4, byte_order)
        for y in range(self.__height):
            row_start = y * self.__stride
            row_end = row_start + self.__width * 4
            self.__data[row_start:row_end] = pixel * self.__width

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
