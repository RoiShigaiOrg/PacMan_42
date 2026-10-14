from __future__ import annotations

from dataclasses import dataclass

from .Vector2 import Vector2


@dataclass(frozen=True)
class AABB:
    """Represent an axis-aligned box centered on a collider position.

    Attributes:
        half_size: The distance from the center to each pair of box edges.

    Raises:
        ValueError: If either half-size is not positive.
    """

    half_size: Vector2

    def __post_init__(self) -> None:
        """Validate that the box has a positive area."""
        if self.half_size.x <= 0 or self.half_size.y <= 0:
            raise ValueError("AABB half-size must be positive")


@dataclass(frozen=True)
class Circle:
    """Represent a circle centered on a collider position.

    Attributes:
        radius: The circle radius in world units.

    Raises:
        ValueError: If the radius is not positive.
    """

    radius: float

    def __post_init__(self) -> None:
        """Validate that the circle has a positive radius."""
        if self.radius <= 0:
            raise ValueError("Circle radius must be positive")


Shape = AABB | Circle
