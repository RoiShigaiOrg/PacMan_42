from __future__ import annotations

import math

from Engine.Physics import AABB, Collider, PhysicsEngine, Vector2
from Engine.InputHandler.KeyCode import KEY_D, KEY_Z
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.Player.Player import Player


class FakeDisplay:
    """Provide stable 100-pixel relative dimensions for Player setup."""

    @staticmethod
    def relative_width(ratio: float) -> int:
        return round(ratio * 100)

    @staticmethod
    def relative_height(ratio: float) -> int:
        return round(ratio * 100)


class FakeMap:
    """Small map stub with an injectable set of blocking colliders."""

    width = 8
    height = 8
    grid_origin = (10, 10)
    cell_size = (10, 10)

    def __init__(self, walls: tuple[Collider, ...] = ()) -> None:
        self._walls = walls
        self._blocked_cells = {
            (
                round((wall.world_position.x - 15) / 10),
                round((wall.world_position.y - 15) / 10),
            )
            for wall in walls
        }

    @staticmethod
    def center() -> tuple[int, int]:
        return 1, 1

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def wall_colliders(self) -> tuple[Collider, ...]:
        return self._walls

    def cell_coordinates_at(self, position: Vector2) -> tuple[int, int]:
        return (
            math.floor((position.x - self.grid_origin[0]) / self.cell_size[0]),
            math.floor((position.y - self.grid_origin[1]) / self.cell_size[1]),
        )

    def is_walkable_cell(self, column: int, row: int) -> bool:
        return (
            0 <= column < self.width
            and 0 <= row < self.height
            and (column, row) not in self._blocked_cells
        )

    def next_cell_is_walkable(
            self, position: Vector2, direction: Vector2
    ) -> bool:
        column, row = self.cell_coordinates_at(position)
        return self.is_walkable_cell(
            column + int(direction.x), row + int(direction.y)
        )

    def is_cell_centered(
            self, position: Vector2, tolerance: float = 1e-6
    ) -> bool:
        column, row = self.cell_coordinates_at(position)
        if not self.is_walkable_cell(column, row):
            return False
        center_x = self.grid_origin[0] + (column + 0.5) * self.cell_size[0]
        center_y = self.grid_origin[1] + (row + 0.5) * self.cell_size[1]
        return (
            abs(position.x - center_x) <= tolerance
            and abs(position.y - center_y) <= tolerance
        )


class FakeInput:
    """Provide pressed and held key state without an MLX window."""

    def __init__(
            self,
            pressed: set[int] | None = None,
            down: set[int] | None = None,
    ) -> None:
        self._pressed = pressed or set()
        self._down = down or set()

    def was_key_pressed(self, key: int) -> bool:
        return key in self._pressed

    def is_key_down(self, key: int) -> bool:
        return key in self._down


def make_player(walls: tuple[Collider, ...] = ()) -> Player:
    player = Player(movement_speed=120.0)
    player.InitPlayer(FakeDisplay(), FakeMap(walls))  # type: ignore[arg-type]
    return player


def wall_at(x: float, y: float) -> Collider:
    return Collider(AABB(Vector2(5.0, 5.0)), Vector2(x, y))


def test_player_moves_smoothly_and_graphics_follow_collider() -> None:
    player = make_player()

    player.update_direction(
        FakeInput(pressed={KEY_D}, down={KEY_D}),
        FakeMap(),  # type: ignore[arg-type]
        PhysicsEngine(),
        0.05,
    )

    assert player.collider.world_position == Vector2(31.0, 25.0)
    assert player.position == (26, 20)
    assert player.direction == Vector2(1.0, 0.0)


def test_player_collider_is_smaller_than_a_map_cell() -> None:
    player = make_player()

    shape = player.collider.shape

    assert isinstance(shape, AABB)
    assert shape.half_size == Vector2(4.0, 4.0)


def test_player_does_not_shift_sideways_when_a_turn_is_blocked() -> None:
    walls = (wall_at(35.0, 15.0),)
    actual_map = FakeMap(walls)
    player = make_player(walls)

    player.update_direction(
        FakeInput(pressed={KEY_D}, down={KEY_D}),
        actual_map,  # type: ignore[arg-type]
        PhysicsEngine(),
        0.025,
    )
    player.update_direction(
        FakeInput(pressed={KEY_Z}),
        actual_map,  # type: ignore[arg-type]
        PhysicsEngine(),
        0.1,
    )

    assert player.direction == Vector2(1.0, 0.0)
    assert player.collider.world_position == Vector2(40.0, 25.0)


def test_buffered_turn_waits_for_a_walkable_neighbor_cell() -> None:
    walls = (wall_at(35.0, 15.0),)
    actual_map = FakeMap(walls)
    player = make_player(walls)

    player.update_direction(
        FakeInput(pressed={KEY_D}, down={KEY_D}),
        actual_map,  # type: ignore[arg-type]
        PhysicsEngine(),
        0.025,
    )
    player.update_direction(
        FakeInput(pressed={KEY_Z}),
        actual_map,  # type: ignore[arg-type]
        PhysicsEngine(),
        0.1,
    )
    assert player.collider.world_position == Vector2(40.0, 25.0)

    player.update_direction(
        FakeInput(),
        actual_map,  # type: ignore[arg-type]
        PhysicsEngine(),
        0.05,
    )

    assert player.direction == Vector2(0.0, -1.0)
    assert player.collider.world_position == Vector2(45.0, 24.0)


def test_player_stops_at_center_before_a_blocked_next_cell() -> None:
    walls = (wall_at(45.0, 25.0),)
    actual_map = FakeMap(walls)
    player = make_player(walls)

    player.update_direction(
        FakeInput(pressed={KEY_D}, down={KEY_D}),
        actual_map,  # type: ignore[arg-type]
        PhysicsEngine(),
        0.2,
    )

    assert player.collider.world_position == Vector2(35.0, 25.0)
    assert player.direction == Vector2(0.0, 0.0)


def test_perpendicular_turn_waits_for_next_grid_center() -> None:
    player = make_player()
    actual_map = FakeMap()
    physics = PhysicsEngine()

    player.update_direction(
        FakeInput(pressed={KEY_D}, down={KEY_D}),
        actual_map,  # type: ignore[arg-type]
        physics,
        0.025,
    )
    player.update_direction(
        FakeInput(pressed={KEY_Z}),
        actual_map,  # type: ignore[arg-type]
        physics,
        0.1,
    )

    assert player.direction == Vector2(0.0, -1.0)
    assert player.collider.world_position.x == 35.0
    assert player.collider.world_position.y < 25.0


def test_player_stops_when_candidate_move_overlaps_a_wall() -> None:
    walls = (wall_at(35.0, 25.0),)
    actual_map = FakeMap(walls)
    player = make_player(walls)

    player.update_direction(
        FakeInput(pressed={KEY_D}, down={KEY_D}),
        actual_map,  # type: ignore[arg-type]
        PhysicsEngine(),
        0.05,
    )

    assert player.collider.world_position == Vector2(25.0, 25.0)
    assert player.direction == Vector2(0.0, 0.0)


def test_buffered_turn_is_taken_when_the_wall_clears() -> None:
    walls = (wall_at(25.0, 15.0),)
    actual_map = FakeMap(walls)
    player = make_player(walls)
    physics = PhysicsEngine()

    player.update_direction(
        FakeInput(pressed={KEY_D}, down={KEY_D}),
        actual_map,  # type: ignore[arg-type]
        physics,
        0.025,
    )
    player.update_direction(
        FakeInput(pressed={KEY_Z}),
        actual_map,  # type: ignore[arg-type]
        physics,
        0.075,
    )

    assert player.direction == Vector2(0.0, -1.0)
    assert player.collider.world_position.x == 35.0
    assert player.collider.world_position.y < 25.0


def test_map_exposes_only_non_walkable_cell_colliders() -> None:
    wall = Cell((0, 0), False)
    floor = Cell((1, 0), True)
    wall.set_collider(0, 0, 10, 10)
    floor.set_collider(10, 0, 10, 10)
    actual_map = Map.__new__(Map)
    actual_map.grid = [[wall, floor]]

    assert actual_map.wall_colliders() == (wall.collider,)


def test_map_checks_neighbor_walkability_from_world_position() -> None:
    actual_map = Map.__new__(Map)
    actual_map.grid = [[
        Cell((0, 0), True),
        Cell((1, 0), False),
        Cell((2, 0), True),
    ]]
    actual_map.width = 3
    actual_map.height = 1
    actual_map.set_colliders(10, 20, 30, 10)
    current_center = Vector2(15.0, 25.0)

    assert actual_map.cell_coordinates_at(current_center) == (0, 0)
    assert actual_map.is_cell_centered(current_center)
    assert not actual_map.next_cell_is_walkable(
        current_center, Vector2(1.0, 0.0)
    )
    assert not actual_map.is_walkable_cell(-1, 0)
