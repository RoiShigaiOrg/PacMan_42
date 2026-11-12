from .Sprite import Sprite


class SpriteSheet:
    """A copied, row-major collection of pixels from a spritesheet image.

    Pixels are represented as packed ``0xAARRGGBB`` integers. The sheet owns
    its pixel data, so it does not depend on the lifetime of an MLX image.
    """

    def __init__(
            self,
            pixels: list[list[int]],
            metadata: dict | None = None) -> None:
        """Create a spritesheet from rows of packed ARGB pixel values."""
        if not pixels or not pixels[0]:
            raise ValueError("spritesheet pixels cannot be empty")

        width = len(pixels[0])
        if any(len(row) != width for row in pixels):
            raise ValueError("spritesheet rows must have equal width")
        if any(
            pixel < 0 or pixel > 0xFFFFFFFF
            for row in pixels
            for pixel in row
        ):
            raise ValueError("spritesheet pixels must be 32-bit values")

        self.__pixels = [row.copy() for row in pixels]
        self.__width = width
        self.__height = len(pixels)
        self.__metadata: dict | None = metadata

    @property
    def width(self) -> int:
        """Return the spritesheet width in pixels."""
        return self.__width

    @property
    def height(self) -> int:
        """Return the spritesheet height in pixels."""
        return self.__height

    @property
    def size(self) -> tuple[int, int]:
        """Return the spritesheet dimensions as ``(width, height)``."""
        return self.__width, self.__height

    def extract_sprite(
        self,
        pos: tuple[int, int],
        size: tuple[int, int],
    ) -> Sprite:
        """Copy and return a sprite at ``(x, y)`` with ``(width, height)``."""
        x, y = pos
        width, height = size
        if (
            x < 0
            or y < 0
            or width <= 0
            or height <= 0
            or x + width > self.__width
            or y + height > self.__height
        ):
            raise ValueError("sprite rectangle is outside the spritesheet")

        sprite_pixels = [
            self.__pixels[row][x:x + width]
            for row in range(y, y + height)
        ]
        return Sprite(size, sprite_pixels)
