class Sprite:
    """A sprite containing a copied grid of packed ARGB pixels.

    A sprite is the graphical representation of an entity in the game and can
    be extracted from a section of a SpriteSheet Class.
    """

    def __init__(self, size: tuple[int, int], data: list[list[int]]) -> None:
        """Initialize a sprite with dimensions and packed ARGB pixel rows."""
        width, height = size
        if width <= 0 or height <= 0:
            raise ValueError("sprite dimensions must be positive")
        if len(data) != height or any(len(row) != width for row in data):
            raise ValueError("sprite pixel data does not match its dimensions")
        if any(
            pixel < 0 or pixel > 0xFFFFFFFF
            for row in data
            for pixel in row
        ):
            raise ValueError("sprite pixels must be 32-bit values")

        self.__size = size
        self.__pixels = tuple(tuple(row) for row in data)

    @property
    def size(self) -> tuple[int, int]:
        """Return the sprite dimensions as ``(width, height)``."""
        return self.__size

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        """Set dimensions when they continue to match the pixel data."""
        width, height = value
        if width <= 0 or height <= 0:
            raise ValueError("sprite dimensions must be positive")
        if (
            height != len(self.__pixels)
            or width != len(self.__pixels[0])
        ):
            raise ValueError("sprite dimensions must match its pixel data")
        self.__size = value

    @property
    def pixels(self) -> tuple[tuple[int, ...], ...]:
        """Return the immutable rows of packed ``0xAARRGGBB`` pixels."""
        return self.__pixels
