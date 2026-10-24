import pytest

from Engine.Physics import AABB, Circle, Collider, PhysicsEngine, Vector2


class RecordingDisplay:
    """Record drawn pixels for collider debug-drawing tests."""

    def __init__(self) -> None:
        self.pixels: list[tuple[int, int, int]] = []

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        self.pixels.append((x, y, color))


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


def test_debug_draw_renders_aabb_outline_at_world_position() -> None:
    display = RecordingDisplay()
    collider = Collider(
        AABB(Vector2(2, 1)), Vector2(5, 4), Vector2(1, 0)
    )

    collider.debug_draw(display, 0xFF00FF00)  # type: ignore[arg-type]

    assert set(display.pixels) == {
        (4, 3, 0xFF00FF00),
        (5, 3, 0xFF00FF00),
        (6, 3, 0xFF00FF00),
        (7, 3, 0xFF00FF00),
        (4, 4, 0xFF00FF00),
        (5, 4, 0xFF00FF00),
        (6, 4, 0xFF00FF00),
        (7, 4, 0xFF00FF00),
    }


def test_debug_draw_renders_circle_outline_at_world_position() -> None:
    display = RecordingDisplay()
    collider = Collider(Circle(2), Vector2(5, 5))

    collider.debug_draw(display, 0xFFFF0000)  # type: ignore[arg-type]

    assert (7, 5, 0xFFFF0000) in display.pixels
    assert (5, 7, 0xFFFF0000) in display.pixels
    assert all(pixel[2] == 0xFFFF0000 for pixel in display.pixels)


def test_can_move_allows_movement_away_from_a_collider() -> None:
    """A movement that creates no overlap should be allowed."""
    collider = box(0, 0, 10, 10)

    assert PhysicsEngine().can_move(
        collider, Vector2(-2.0, 0.0), box(10, 0, 10, 10)
    ) is True


def test_can_move_blocks_movement_into_a_collider() -> None:
    """A movement that would overlap a collider should be refused."""
    collider = box(0, 0, 10, 10)

    assert PhysicsEngine().can_move(
        collider, Vector2(2.0, 0.0), box(10, 0, 10, 10)
    ) is False


def test_can_move_restores_position_after_a_blocked_move() -> None:
    """A refused movement must leave the collider position untouched."""
    collider = box(0, 0, 10, 10)

    PhysicsEngine().can_move(collider, Vector2(2.0, 0.0), box(10, 0, 10, 10))

    assert collider.position == Vector2(5.0, 5.0)


def test_can_move_allows_perpendicular_sliding() -> None:
    """A collider blocked on one axis should still slide along the wall."""
    collider = box(0, 0, 10, 10)

    assert PhysicsEngine().can_move(
        collider, Vector2(0.0, 5.0), box(10, 0, 10, 10)
    ) is True


def test_can_move_checks_every_other_collider() -> None:
    """The movement must avoid all listed colliders, not just the first."""
    collider = box(0, 0, 10, 10)

    assert PhysicsEngine().can_move(
        collider,
        Vector2(2.0, 0.0),
        box(30, 0, 10, 10),
        box(10, 0, 10, 10),
    ) is False
