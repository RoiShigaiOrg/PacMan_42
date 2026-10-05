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


    def __draw_pixel(self, x: int, y: int, color: int) -> None:
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
