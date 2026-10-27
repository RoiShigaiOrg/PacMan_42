from __future__ import annotations

import pytest

from Engine.Physics import AABB, Collider, PhysicsEngine, Vector2
from Engine.Graphics import MlxDisplay
from Game.Ghosts.Ghost import Ghost
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.MapGeneration.MapNode import MapNode


class FakeShape:
    def update_pos(self, _x: int, _y: int) -> None:
        pass

    def fill(self, _display: MlxDisplay) -> None:
        pass


class MovementGhost(Ghost):
    def __init__(self, movement_speed: float = 10.0) -> None:
        super().__init__(movement_speed)
        self._width = 10
        self._height = 10
        self._graphical_shape = FakeShape()
        self._collider = Collider(
            AABB(Vector2(4.0, 4.0)), Vector2(15.0, 25.0)
        )

    def init_ghost(self, _display: MlxDisplay, _actual_map: Map) -> None:
        pass

    def _chase(self, target: tuple[int, int]) -> tuple[int, int]:
        return target

    def _fleat(self, target: tuple[int, int]) -> tuple[int, int]:
        return target

    def _dead(self, target: tuple[int, int]) -> tuple[int, int]:
        return target


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
        10, 20, actual_map.width * 10, actual_map.height * 10
    )
    return actual_map


def nodes(*coordinates: tuple[int, int]) -> list[MapNode]:
    return [MapNode(coordinate) for coordinate in coordinates]


def test_ghost_follows_turns_and_uses_remaining_frame_distance() -> None:
    actual_map = make_map([[True, True], [True, True]])
    ghost = MovementGhost(movement_speed=10.0)
    ghost.compute_path((0, 0), (1, 1), actual_map.build_graph())

    ghost.update_movement(actual_map, PhysicsEngine(), 2.0)

    assert ghost.collider.world_position == Vector2(25.0, 35.0)
    assert ghost.position == (20, 30)


def test_ghost_moves_smoothly_toward_next_cell_center() -> None:
    actual_map = make_map([[True, True]])
    ghost = MovementGhost(movement_speed=10.0)
    ghost.set_path(nodes((0, 0), (1, 0)))

    ghost.update_movement(actual_map, PhysicsEngine(), 0.25)

    assert ghost.collider.world_position == Vector2(17.5, 25.0)


def test_ghost_does_not_enter_a_non_walkable_waypoint() -> None:
    actual_map = make_map([[True, False]])
    ghost = MovementGhost()
    ghost.set_path(nodes((0, 0), (1, 0)))

    ghost.update_movement(actual_map, PhysicsEngine(), 1.0)

    assert ghost.collider.world_position == Vector2(15.0, 25.0)


def test_ghost_path_must_use_cardinally_adjacent_cells() -> None:
    ghost = MovementGhost()

    with pytest.raises(ValueError, match="cardinally adjacent"):
        ghost.set_path(nodes((0, 0), (1, 1)))


def test_ghost_rejects_non_positive_movement_speed() -> None:
    with pytest.raises(ValueError, match="movement_speed must be positive"):
        MovementGhost(0.0)
