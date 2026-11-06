from __future__ import annotations

import pytest

from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import (
    HIGH_LEFT,
    HIGH_RIGHT,
    LOW_LEFT,
    LOW_RIGHT,
    Map,
)


def make_map(width: int, height: int) -> Map:
    actual_map = Map.__new__(Map)
    actual_map.width = width
    actual_map.height = height
    actual_map.grid = [
        [Cell((column, row), False) for column in range(width)]
        for row in range(height)
    ]
    return actual_map


@pytest.mark.parametrize(
    ("corner", "walkable", "expected"),
    [
        (HIGH_LEFT, (1, 0), (1, 0)),
        (HIGH_RIGHT, (2, 1), (2, 1)),
        (LOW_LEFT, (0, 1), (0, 1)),
        (LOW_RIGHT, (1, 2), (1, 2)),
    ],
)
def test_corner_search_returns_nearest_walkable_cell(
        corner: int,
        walkable: tuple[int, int],
        expected: tuple[int, int],
) -> None:
    actual_map = make_map(3, 3)
    column, row = walkable
    actual_map.grid[row][column].walkable = True

    assert actual_map.corner(corner) == expected


def test_corner_search_checks_corner_before_more_distant_cells() -> None:
    actual_map = make_map(3, 2)
    actual_map.grid[0][2].walkable = True
    actual_map.grid[1][1].walkable = True

    assert actual_map.corner(HIGH_RIGHT) == (2, 0)


def test_corner_search_uses_deterministic_order_for_equal_distance() -> None:
    actual_map = make_map(3, 3)
    actual_map.grid[0][1].walkable = True
    actual_map.grid[1][2].walkable = True

    # HIGH_RIGHT checks along the top edge before moving down the right edge.
    assert actual_map.corner(HIGH_RIGHT) == (1, 0)


def test_corner_search_rejects_unknown_corner_and_empty_maps() -> None:
    actual_map = make_map(2, 2)

    with pytest.raises(ValueError, match="Unknown map corner"):
        actual_map.corner(99)
    with pytest.raises(ValueError, match="no walkable cells"):
        actual_map.corner(HIGH_LEFT)
