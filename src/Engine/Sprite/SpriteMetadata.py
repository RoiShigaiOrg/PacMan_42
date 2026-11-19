from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
)
from pydantic import model_validator


class _AsepriteModel(BaseModel):
    """Base model for the Aseprite JSON format used by this engine."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        populate_by_name=True,
    )


class AsepriteSize(_AsepriteModel):
    width: StrictInt = Field(alias="w", gt=0)
    height: StrictInt = Field(alias="h", gt=0)

    def as_tuple(self) -> tuple[int, int]:
        """Return the dimensions as ``(width, height)``."""
        return self.width, self.height


class AsepriteRectangle(AsepriteSize):
    x: StrictInt = Field(ge=0)
    y: StrictInt = Field(ge=0)


class AsepriteFrameMetadata(_AsepriteModel):
    frame: AsepriteRectangle
    rotated: StrictBool = False
    trimmed: StrictBool = False
    sprite_source_size: AsepriteRectangle = Field(alias="spriteSourceSize")
    source_size: AsepriteSize = Field(alias="sourceSize")
    duration_ms: StrictInt = Field(alias="duration", gt=0)


class AsepriteFrameTag(_AsepriteModel):
    name: StrictStr
    from_frame: StrictInt = Field(alias="from", ge=0)
    to_frame: StrictInt = Field(alias="to", ge=0)
    direction: Literal[
        "forward", "reverse", "pingpong", "pingpong_reverse"
    ] = "forward"

    @model_validator(mode="after")
    def validate_frame_range(self) -> "AsepriteFrameTag":
        if not self.name:
            raise ValueError("frame tag name cannot be empty")
        if self.from_frame > self.to_frame:
            raise ValueError("frame tag 'from' must not exceed 'to'")
        return self

    def frame_indices(self) -> tuple[int, ...]:
        """Return inclusive frame indices in the tag's playback order."""
        forward = tuple(range(self.from_frame, self.to_frame + 1))
        if self.direction == "reverse":
            return tuple(reversed(forward))
        if self.direction == "pingpong":
            return forward + tuple(reversed(forward[1:-1]))
        if self.direction == "pingpong_reverse":
            reverse = tuple(reversed(forward))
            return reverse + forward[1:-1]
        return forward


class AsepriteMeta(_AsepriteModel):
    image: StrictStr
    size: AsepriteSize
    frame_tags: tuple[AsepriteFrameTag, ...] = Field(
        default=(), alias="frameTags"
    )


class AsepriteMetadata(_AsepriteModel):
    """Validated subset of Aseprite's array-frame JSON export."""

    frames: tuple[AsepriteFrameMetadata, ...]
    meta: AsepriteMeta

    @model_validator(mode="after")
    def validate_sheet(self) -> "AsepriteMetadata":
        if not self.frames:
            raise ValueError("spritesheet metadata must contain frames")

        width, height = self.meta.size.as_tuple()
        for frame_index, frame_metadata in enumerate(self.frames):
            rect = frame_metadata.frame
            if rect.x + rect.width > width or rect.y + rect.height > height:
                raise ValueError(
                    f"frame {frame_index} rectangle "
                    "is outside the spritesheet"
                )

        tag_names = [tag.name for tag in self.meta.frame_tags]
        if len(tag_names) != len(set(tag_names)):
            raise ValueError("spritesheet frame tag names must be unique")
        for tag in self.meta.frame_tags:
            if tag.to_frame >= len(self.frames):
                raise ValueError(
                    f"frame tag {tag.name!r} references a missing frame"
                )
        return self

    def tag(self, name: str) -> AsepriteFrameTag:
        """Return a frame tag by name or raise ``KeyError``."""
        for tag in self.meta.frame_tags:
            if tag.name == name:
                return tag
        raise KeyError(name)
