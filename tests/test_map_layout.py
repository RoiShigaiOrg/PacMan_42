import pytest

from Engine.Physics import AABB, Vector2
from Engine.Sprite import Sprite
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import (
    DOWN,
    LEFT,
    RIGHT,
    TOP,
    WALL_MASK_TO_TAG,
    Map,
    wall_neighbor_mask,
)


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
        self.colors: dict[tuple[int, int], int] = {}

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        self.pixels.add((x, y))
        self.colors[(x, y)] = color


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


@pytest.mark.parametrize(
    ("mask", "tag"),
    [
        (0, "solo"),
        (TOP, "bottom"),
        (RIGHT, "left"),
        (DOWN, "top"),
        (LEFT, "right"),
        (TOP | DOWN, "vertical"),
        (RIGHT | LEFT, "horizontal"),
        (TOP | RIGHT, "corner_top_right"),
        (TOP | LEFT, "corner_top_left"),
        (DOWN | RIGHT, "corner_bot_right"),
        (DOWN | LEFT, "corner_bottom_left"),
        (TOP | RIGHT | LEFT, "horizontal_top"),
        (DOWN | RIGHT | LEFT, "horizontal_bot"),
        (TOP | DOWN | RIGHT, "vertical_right"),
        (TOP | DOWN | LEFT, "vertical_left"),
        (TOP | RIGHT | DOWN | LEFT, "center"),
    ],
)
def test_wall_neighbor_masks_dispatch_to_all_sprite_tags(
        mask: int, tag: str
) -> None:
    assert WALL_MASK_TO_TAG[mask] == tag


@pytest.mark.parametrize("mask", range(16))
def test_wall_neighbor_mask_reads_only_in_bounds_cardinal_walls(
        mask: int,
) -> None:
    actual_map = make_map(3, 3)
    actual_map.grid[1][1].walkable = False
    neighbors = (
        (TOP, 1, 0),
        (RIGHT, 2, 1),
        (DOWN, 1, 2),
        (LEFT, 0, 1),
    )
    for direction, column, row in neighbors:
        if mask & direction:
            actual_map.grid[row][column].walkable = False

    assert wall_neighbor_mask(actual_map.grid, 1, 1) == mask


def test_map_draws_the_cached_sprite_for_each_wall_neighbor_mask() -> None:
    actual_map = make_map(3, 3)
    actual_map.grid[1][1].walkable = False
    actual_map.grid[0][1].walkable = False
    actual_map.grid[1][0].walkable = False
    actual_map.grid[1][2].walkable = False
    actual_map.set_colliders(0, 0, 30, 30)
    actual_map._Map__wall_sprites = {
        mask: Sprite((1, 1), [[0xFF000100 | mask]])
        for mask in WALL_MASK_TO_TAG
    }
    display = RecordingDisplay()

    actual_map.draw(display)

    assert display.colors[(10, 10)] == 0xFF000100 | (
        TOP | RIGHT | LEFT
    )
