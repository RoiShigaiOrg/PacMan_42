from .Sprite import Sprite
from .SpriteFrame import SpriteFrame
from .SpriteMetadata import AsepriteMetadata


class SpriteSheet:
    """A copied, row-major collection of pixels from a spritesheet image.

    Pixels are represented as packed ``0xAARRGGBB`` integers. The sheet owns
    its pixel data, so it does not depend on the lifetime of an MLX image.
    """

    def __init__(
            self,
            pixels: list[list[int]],
            metadata: AsepriteMetadata | dict | None = None) -> None:
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
        validated_metadata: AsepriteMetadata | None
        if isinstance(metadata, AsepriteMetadata):
            validated_metadata = metadata
        elif metadata is not None:
            validated_metadata = AsepriteMetadata.model_validate(metadata)
        else:
            validated_metadata = None
        if (
            validated_metadata is not None
            and validated_metadata.meta.size.as_tuple()
            != (self.__width, self.__height)
        ):
            raise ValueError(
                "spritesheet dimensions do not match metadata dimensions"
            )
        self.__metadata = validated_metadata

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

    @property
    def metadata(self) -> AsepriteMetadata | None:
        """Return validated Aseprite metadata, if the sheet has any."""
        return self.__metadata

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

    def get_sprite(self, tag_name: str) -> tuple[SpriteFrame, ...]:
        """Extract the ordered, duration-bearing frames of an Aseprite tag.

        Tag ranges are inclusive. Frame durations are kept in milliseconds,
        matching Aseprite's JSON representation.
        """
        if self.__metadata is None:
            raise RuntimeError(
                "cannot look up a sprite tag without Aseprite metadata"
            )

        try:
            tag = self.__metadata.tag(tag_name)
        except KeyError as error:
            raise KeyError(f"unknown sprite tag: {tag_name}") from error

        tagged_frames: list[SpriteFrame] = []
        for frame_index in tag.frame_indices():
            frame_metadata = self.__metadata.frames[frame_index]
            if frame_metadata.rotated or frame_metadata.trimmed:
                raise NotImplementedError(
                    "rotated or trimmed Aseprite frames are not supported"
                )
            rect = frame_metadata.frame
            sprite = self.extract_sprite(
                (rect.x, rect.y), (rect.width, rect.height)
            )
            tagged_frames.append(
                SpriteFrame(sprite, frame_metadata.duration_ms)
            )
        return tuple(tagged_frames)
