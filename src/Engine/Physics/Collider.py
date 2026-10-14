from __future__ import annotations

from dataclasses import dataclass, field

from .Shapes import Shape
from .Vector2 import Vector2


@dataclass
class Collider:
    """Attach a physics shape to a world-space position.

    The collider deliberately contains no rendering state. A graphics
    component may use the same position and dimensions, but it is not
    required to do so.

    Attributes:
        shape: The geometric shape used for collision detection.
        position: The world-space position of the shape center.
        offset: A local offset from the owning object's center.
    """

    shape: Shape
    position: Vector2
    offset: Vector2 = field(default_factory=lambda: Vector2(0.0, 0.0))

    @property
    def world_position(self) -> Vector2:
        """Return the shape center in world coordinates.

        Returns:
            The collider position plus its local offset.
        """
        return self.position + self.offset
