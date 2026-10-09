from typing import Any, Tuple, Literal


class MlxDisplay:
    """
        MlxDisplay is where we can construct an image
            before pushing it into the MlxWindow
    """

    def __init__(
            self,
            session: Any,
            image_ptr: Any,
            mlx_ptr: Any,
            window_ptr: Any,
            dimension: Tuple[int, int]) -> None:
        """ Init Method of the MlxDisplay Class """
        self.__session = session
        self.__dimension = dimension
        self.__mlx_ptr = mlx_ptr
        self.__image = image_ptr
        self.__window_ptr = window_ptr
        self.__width = dimension[0]
        self.__height = dimension[1]
        (
            self.__data,
            self.__bits_per_pixel,
            self.__stride,
            self.__format,
        ) = self.__session.mlx_get_data_addr(image_ptr)
        if self.__bits_per_pixel != 32:
            self.__session.mlx_destroy_image(
                    mlx_ptr, image_ptr
                    )
            raise RuntimeError("MLX screen buffer is not a 32-bit image")

    @property
    def width(self) -> int:
        """Return the screen width in pixels."""
        return self.__width

    @property
    def height(self) -> int:
        """Return the screen height in pixels."""
        return self.__height

    def size(self) -> tuple[int, int]:
        """Return ``(width, height)`` in pixels."""
        return self.__width, self.__height

    def render(self) -> None:
        """ Render the actual image to the window """
        self.__session.mlx_put_image_to_window(
                self.__mlx_ptr,
                self.__window_ptr,
                self.__image,
                0, 0
                )

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        """Write one ARGB pixel to the persistent screen buffer."""
        if not 0 <= x < self.__width or not 0 <= y < self.__height:
            return
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

    def fill_rect(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            color: int,
    ) -> None:
        """Fill a clipped rectangle using row-sized memory writes."""
        if not 0 <= color <= 0xFFFFFFFF:
            raise ValueError("color must be a 32-bit unsigned integer")
        if width <= 0 or height <= 0:
            return

        left = max(0, x)
        top = max(0, y)
        right = min(self.__width, x + width)
        bottom = min(self.__height, y + height)
        if left >= right or top >= bottom:
            return

        byte_order: Literal["little", "big"] = (
            "little" if self.__format == 0 else "big"
        )
        pixel = color.to_bytes(4, byte_order)
        row_pixels = pixel * (right - left)
        for row in range(top, bottom):
            row_start = row * self.__stride + left * 4
            self.__data[row_start:row_start + len(row_pixels)] = row_pixels

    def snapshot(self) -> bytes:
        """Return a copy of the complete image buffer for layer caching."""
        return bytes(self.__data)

    def write_text(
            self,
            pos_x: int,
            pos_y: int,
            color: int,
            text: str) -> None:
        """ Method to write string to the display """
        if not 0 <= pos_x < self.__width or not 0 <= pos_y < self.__height:
            raise ValueError("'write text': No valid coordonates...")
        if not text:
            raise ValueError("'write text: Empty string'")
        self.__session.mlx_string_put(self.__mlx_ptr, self.__window_ptr, pos_x, pos_y, color, text)

    def restore_region(
            self,
            snapshot: bytes,
            x: int,
            y: int,
            width: int,
            height: int,
    ) -> None:
        """Restore a clipped region from a compatible image snapshot."""
        if len(snapshot) != len(self.__data):
            raise ValueError("snapshot does not match display size")
        if width <= 0 or height <= 0:
            return

        left = max(0, x)
        top = max(0, y)
        right = min(self.__width, x + width)
        bottom = min(self.__height, y + height)
        if left >= right or top >= bottom:
            return

        row_width = (right - left) * 4
        for row in range(top, bottom):
            row_start = row * self.__stride + left * 4
            self.__data[row_start:row_start + row_width] = snapshot[
                row_start:row_start + row_width
            ]

    def close(self) -> None:
        """ Close the Window link to this Display """
        self.__session.mlx_loop_exit(self.__mlx_ptr)

    def fill(self, color: int) -> None:
        """ Fill the entire Display with a given color """
        for y in range(self.__height):
            for x in range(self.__width):
                self.draw_pixel(x, y, color)
