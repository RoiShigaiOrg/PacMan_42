import pytest

from Engine.Physics import AABB, Vector2
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map


def make_map(width: int, height: int, walkable: bool = True) -> Map:
    actual_map = Map.__new__(Map)
    actual_map.width = width
    actual_map.height = height
    actual_map.grid = [
        [Cell((column, row), walkable) for column in range(width)]
        for row in range(height)
    ]
    return actual_map


class RecordingDisplay:
    def __init__(self) -> None:
        self.pixels: set[tuple[int, int]] = set()

    def draw_pixel(self, x: int, y: int, _color: int) -> None:
        self.pixels.add((x, y))


def test_map_layout_uses_centered_square_cells_and_square_colliders() -> None:
    actual_map = make_map(3, 2, walkable=False)

    actual_map.set_colliders(10, 20, 100, 80)

    assert actual_map.cell_size == (33, 33)
    assert actual_map.grid_origin == (10, 27)
    collider = actual_map.grid[1][2].collider
    assert collider is not None
    assert isinstance(collider.shape, AABB)
    assert collider.shape.half_size == Vector2(16.5, 16.5)
    assert collider.world_position == Vector2(92.5, 76.5)
    assert actual_map.cell_coordinates_at(collider.world_position) == (2, 1)


def test_map_draw_uses_the_same_square_layout_as_its_colliders() -> None:
    actual_map = make_map(2, 2)
    display = RecordingDisplay()
    actual_map.set_colliders(20, 30, 100, 80)

    actual_map.draw(display)

    assert actual_map.cell_size == (40, 40)
    assert actual_map.grid_origin == (30, 30)
    assert (30, 30) in display.pixels
    assert (70, 30) in display.pixels
    assert (109, 109) in display.pixels
    assert (29, 30) not in display.pixels
    assert (110, 30) not in display.pixels


def test_map_rejects_bounds_that_cannot_fit_a_square_cell() -> None:
    actual_map = make_map(3, 2)

    with pytest.raises(ValueError, match="too small"):
        actual_map.set_colliders(0, 0, 2, 1)
