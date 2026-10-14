import pytest

from Engine.Physics import AABB, Circle, Collider, PhysicsEngine, Vector2


def box(x: float, y: float, width: float, height: float) -> Collider:
    """Create a centered AABB collider from top-left-style dimensions."""
    return Collider(
        AABB(Vector2(width / 2, height / 2)),
        Vector2(x + width / 2, y + height / 2),
    )


def circle(x: float, y: float, radius: float) -> Collider:
    """Create a circle collider at a world-space center."""
    return Collider(Circle(radius), Vector2(x, y))


def test_aabb_collision_returns_minimum_separation_axis() -> None:
    """AABB overlap should return its shallowest penetration axis."""
    collision = PhysicsEngine().handle_collision(
        box(0, 0, 10, 10), box(8, 2, 10, 10)
    )

    assert collision is not None
    assert collision.normal == Vector2(-1.0, 0.0)
    assert collision.penetration == pytest.approx(2.0)


def test_aabb_edge_contact_is_not_overlap() -> None:
    """Boxes sharing only an edge should not be reported as overlapping."""
    collision = PhysicsEngine().handle_collision(
        box(0, 0, 10, 10), box(10, 0, 10, 10)
    )

    assert collision is None


def test_aabb_containment_uses_smallest_escape_axis() -> None:
    """Contained boxes should use the shortest translation out of the box."""
    collision = PhysicsEngine().handle_collision(
        box(0, 0, 20, 20), box(5, 5, 5, 5)
    )

    assert collision is not None
    assert collision.normal == Vector2(1.0, 0.0)
    assert collision.penetration == pytest.approx(10.0)


def test_circle_collision_returns_separation_normal() -> None:
    """Circle overlap should return a normalized separation direction."""
    collision = PhysicsEngine().handle_collision(
        circle(0, 0, 5), circle(8, 0, 5)
    )

    assert collision is not None
    assert collision.normal == Vector2(-1.0, 0.0)
    assert collision.penetration == pytest.approx(2.0)


def test_circle_contact_is_not_overlap() -> None:
    """Circles sharing exactly one point should not be reported as overlap."""
    collision = PhysicsEngine().handle_collision(
        circle(0, 0, 5), circle(10, 0, 5)
    )

    assert collision is None


def test_circle_aabb_corner_collision() -> None:
    """Circle-AABB detection should handle a rounded corner correctly."""
    collision = PhysicsEngine().handle_collision(
        circle(12, 12, 5), box(0, 0, 10, 10)
    )

    assert collision is not None
    assert collision.normal.x == pytest.approx(1 / 2**0.5)
    assert collision.normal.y == pytest.approx(1 / 2**0.5)
    assert collision.penetration == pytest.approx(5 - 2**0.5 * 2)


def test_reversed_circle_aabb_pair_reverses_normal() -> None:
    """Reversing a supported pair should reverse only its normal."""
    collision = PhysicsEngine().handle_collision(
        box(0, 0, 10, 10), circle(12, 5, 5)
    )

    assert collision is not None
    assert collision.normal == Vector2(-1.0, 0.0)


def test_unsupported_shape_pair_is_reported() -> None:
    """Unsupported shape combinations should fail explicitly."""
    with pytest.raises(TypeError, match="Unsupported collision pair"):
        PhysicsEngine().handle_collision(
            Collider(AABB(Vector2(1, 1)), Vector2(0, 0)),
            Collider("unsupported", Vector2(0, 0)),  # type: ignore[arg-type]
        )
