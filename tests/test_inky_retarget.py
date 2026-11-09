from Game.Ghosts.Inky import Inky
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map


def make_map(walkability: list[list[bool]]) -> Map:
    actual_map = Map.__new__(Map)
    actual_map.height = len(walkability)
    actual_map.width = len(walkability[0])
    actual_map.grid = [
        [
            Cell((column, row), walkable)
            for column, walkable in enumerate(row_values)
        ]
        for row, row_values in enumerate(walkability)
    ]
    actual_map.set_colliders(
        0, 0, actual_map.width * 10, actual_map.height * 10
    )
    actual_map.graph = actual_map.build_graph()
    return actual_map


def test_inky_retarget_reflects_blinky_across_phase_one_target() -> None:
    actual_map = make_map([[True] * 7 for _ in range(7)])

    target = Inky().retarget((3, 3), (1, 2), actual_map)

    assert target == (5, 4)


def test_inky_retarget_uses_nearest_walkable_cell_outside_map() -> None:
    actual_map = make_map([
        [True, True, True, True],
        [True, True, True, False],
        [True, True, True, True],
    ])

    target = Inky().retarget((2, 1), (0, 1), actual_map)

    # The reflected cell is (4, 1); (3, 0) and (3, 2) tie, so row wins.
    assert target == (3, 0)


def test_inky_retarget_uses_nearest_walkable_cell_for_blocked_result() -> None:
    actual_map = make_map([
        [True, True, True],
        [True, True, False],
        [True, True, True],
    ])

    target = Inky().retarget((1, 1), (0, 1), actual_map)

    # The reflected cell is blocked at (2, 1); closest options tie vertically.
    assert target == (2, 0)
