from __future__ import annotations

from dataclasses import dataclass

from ..Graphics.Components.Circle import Circle as GraphicsCircle
from ..Graphics.Components.Rect import Rect
from ..Graphics.MlxDisplay import MlxDisplay
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

    def display(
        self, display: MlxDisplay, position: Vector2, color: int
    ) -> None:
        """Draw the AABB outline at its world-space center."""
        width = max(1, round(self.half_size.x * 2))
        height = max(1, round(self.half_size.y * 2))
        x = round(position.x - self.half_size.x)
        y = round(position.y - self.half_size.y)
        Rect(width, height, x, y, color).draw(display)


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

    def display(
        self, display: MlxDisplay, position: Vector2, color: int
    ) -> None:
        """Draw the circle outline at its world-space center."""
        diameter = max(1, round(self.radius * 2) + 1)
        top_left = round(position.x - (diameter - 1) / 2)
        top = round(position.y - (diameter - 1) / 2)
        GraphicsCircle(diameter, diameter, top_left, top, color).draw(display)


Shape = AABB | Circle
