from dataclasses import dataclass
import math

from .Sprite import Sprite


@dataclass(frozen=True)
class SpriteFrame:
    """A sprite and its Aseprite frame duration, expressed in milliseconds."""

    sprite: Sprite
    duration_ms: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.duration_ms) or self.duration_ms <= 0:
            raise ValueError("sprite frame duration must be positive")

    @property
    def duration_seconds(self) -> float:
        """Return the frame duration in seconds for the engine clock."""
        return self.duration_ms / 1000.0
