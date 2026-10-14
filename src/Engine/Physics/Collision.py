from __future__ import annotations

from dataclasses import dataclass

from .Vector2 import Vector2


@dataclass(frozen=True)
class Collision:
    """Describe the overlap between two colliders.

    The normal points in the direction that the first collider must move to
    separate it from the second collider. The penetration is the minimum
    translation distance along that normal.

    Attributes:
        normal: A unit vector pointing out of the second collider and into
            the first collider.
        penetration: The overlap distance along the collision normal.
        contact_point: An optional point where the shapes meet.
    """

    normal: Vector2
    penetration: float
    contact_point: Vector2 | None = None
