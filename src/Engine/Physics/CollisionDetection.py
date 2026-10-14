from __future__ import annotations

from collections.abc import Callable
import math

from .Collision import Collision
from .Collider import Collider
from .Shapes import AABB, Circle
from .Vector2 import Vector2


CollisionTest = Callable[[Collider, Collider], Collision | None]


def _sign_or_positive(value: float) -> float:
    """Return the sign of a value, choosing positive for zero."""
    return -1.0 if value < 0 else 1.0


def _aabb_bounds(collider: Collider) -> tuple[float, float, float, float]:
    """Return the left, top, right, and bottom bounds of an AABB collider."""
    shape = collider.shape
    if not isinstance(shape, AABB):
        raise TypeError("Collider does not contain an AABB")
    center = collider.world_position
    return (
        center.x - shape.half_size.x,
        center.y - shape.half_size.y,
        center.x + shape.half_size.x,
        center.y + shape.half_size.y,
    )


def _test_aabb_aabb(first: Collider, second: Collider) -> Collision | None:
    """Detect strict overlap between two axis-aligned boxes."""
    first_shape = first.shape
    second_shape = second.shape
    if not isinstance(first_shape, AABB) or not isinstance(second_shape, AABB):
        raise TypeError("AABB test requires two AABB shapes")

    delta = first.world_position - second.world_position
    overlap_x = (
        first_shape.half_size.x + second_shape.half_size.x - abs(delta.x)
    )
    overlap_y = (
        first_shape.half_size.y + second_shape.half_size.y - abs(delta.y)
    )
    if overlap_x <= 0 or overlap_y <= 0:
        return None

    if overlap_x <= overlap_y:
        normal = Vector2(_sign_or_positive(delta.x), 0.0)
        penetration = overlap_x
    else:
        normal = Vector2(0.0, _sign_or_positive(delta.y))
        penetration = overlap_y
    return Collision(normal, penetration)


def _test_circle_circle(first: Collider, second: Collider) -> Collision | None:
    """Detect strict overlap between two circles."""
    first_shape = first.shape
    second_shape = second.shape
    if (
        not isinstance(first_shape, Circle)
        or not isinstance(second_shape, Circle)
    ):
        raise TypeError("Circle test requires two Circle shapes")

    delta = first.world_position - second.world_position
    distance_squared = delta.length_squared()
    radius_sum = first_shape.radius + second_shape.radius
    if distance_squared >= radius_sum * radius_sum:
        return None

    if distance_squared == 0:
        return Collision(Vector2(1.0, 0.0), radius_sum)

    distance = math.sqrt(distance_squared)
    return Collision(delta * (1.0 / distance), radius_sum - distance)


def _test_circle_aabb(first: Collider, second: Collider) -> Collision | None:
    """Detect strict overlap between a circle and an axis-aligned box."""
    first_shape = first.shape
    if (
        not isinstance(first_shape, Circle)
        or not isinstance(second.shape, AABB)
    ):
        raise TypeError("Circle-AABB test requires a Circle and an AABB")

    left, top, right, bottom = _aabb_bounds(second)
    circle_center = first.world_position
    closest = Vector2(
        min(max(circle_center.x, left), right),
        min(max(circle_center.y, top), bottom),
    )
    away_from_box = circle_center - closest
    distance_squared = away_from_box.length_squared()
    radius = first_shape.radius

    if distance_squared > 0:
        if distance_squared >= radius * radius:
            return None
        distance = math.sqrt(distance_squared)
        return Collision(
            away_from_box * (1.0 / distance),
            radius - distance,
            closest,
        )

    distances = (
        (circle_center.x - left, Vector2(-1.0, 0.0)),
        (right - circle_center.x, Vector2(1.0, 0.0)),
        (circle_center.y - top, Vector2(0.0, -1.0)),
        (bottom - circle_center.y, Vector2(0.0, 1.0)),
    )
    distance_to_face, normal = min(distances, key=lambda item: item[0])
    return Collision(normal, radius + distance_to_face)


def _reverse_collision(collision: Collision | None) -> Collision | None:
    """Reverse a collision normal when swapping shape order."""
    if collision is None:
        return None
    return Collision(
        Vector2(-collision.normal.x, -collision.normal.y),
        collision.penetration,
        collision.contact_point,
    )


_COLLISION_TESTS: dict[tuple[type, type], CollisionTest] = {
    (AABB, AABB): _test_aabb_aabb,
    (Circle, Circle): _test_circle_circle,
    (Circle, AABB): _test_circle_aabb,
}


def detect_collision(first: Collider, second: Collider) -> Collision | None:
    """Detect overlap between two supported colliders.

    Args:
        first: The first collider. Collision normals point away from the
            second collider and into this collider.
        second: The second collider.

    Returns:
        A collision manifold when the shapes strictly overlap, otherwise
        ``None``.

    Raises:
        TypeError: If either argument is not a collider or the shape pair is
            not supported.
    """
    if not isinstance(first, Collider) or not isinstance(second, Collider):
        raise TypeError("detect_collision expects two Collider instances")

    pair = (type(first.shape), type(second.shape))
    test = _COLLISION_TESTS.get(pair)
    if test is not None:
        return test(first, second)

    reverse_test = _COLLISION_TESTS.get((pair[1], pair[0]))
    if reverse_test is not None:
        return _reverse_collision(reverse_test(second, first))

    raise TypeError(
        f"Unsupported collision pair: {type(first.shape).__name__} vs "
        f"{type(second.shape).__name__}"
    )
