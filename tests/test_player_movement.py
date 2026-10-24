from __future__ import annotations

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

    def __init__(self, walls: tuple[Collider, ...] = ()) -> None:
        self._walls = walls

    @staticmethod
    def center() -> tuple[int, int]:
        return 1, 1

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def wall_colliders(self) -> tuple[Collider, ...]:
        return self._walls


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
        0.15,
    )

    assert player.direction == Vector2(0.0, -1.0)
    assert player.collider.world_position.x > 35.0
    assert player.collider.world_position.y < 25.0


def test_map_exposes_only_non_walkable_cell_colliders() -> None:
    wall = Cell((0, 0), False)
    floor = Cell((1, 0), True)
    wall.set_collider(0, 0, 10, 10)
    floor.set_collider(10, 0, 10, 10)
    actual_map = Map.__new__(Map)
    actual_map.grid = [[wall, floor]]

    assert actual_map.wall_colliders() == (wall.collider,)
