from __future__ import annotations

import random as ghost_random
from typing import Tuple

import pytest

from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Physics import AABB, Collider, Vector2
from Game.GameState import GameState, PacManState
from Game.Ghosts.Ghost import Behaviour, Ghost
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.Player import Player


class RoamingGhost(Ghost):
    def init_ghost(self, _display: MlxDisplay, _actual_map: Map) -> None:
        pass

    def _chase(
            self,
            _player: Player,
            _actual_map: Map,
            ghost_cell: Tuple[int, int],
    ) -> Tuple[int, int]:
        return ghost_cell


def make_map(width: int, height: int = 1) -> Map:
    actual_map = Map.__new__(Map)
    actual_map.width = width
    actual_map.height = height
    actual_map.grid = [
        [Cell((column, row), True) for column in range(width)]
        for row in range(height)
    ]
    actual_map.set_colliders(0, 0, width * 10, height * 10)
    actual_map.graph = actual_map.build_graph()
    return actual_map


def test_graph_territories_are_disjoint_and_limited_by_graph_distance(
) -> None:
    actual_map = make_map(9)

    territories = actual_map.graph_territories(
        {"left": (0, 0), "right": (8, 0)},
        max_distance=2,
    )

    assert territories == {
        "left": {(0, 0), (1, 0), (2, 0)},
        "right": {(6, 0), (7, 0), (8, 0)},
    }
    assert territories["left"].isdisjoint(territories["right"])


def test_graph_territory_ties_follow_origin_order() -> None:
    actual_map = make_map(5)

    territories = actual_map.graph_territories(
        {"left": (0, 0), "right": (4, 0)},
        max_distance=3,
    )

    assert (2, 0) in territories["left"]
    assert (2, 0) not in territories["right"]


def test_flea_roaming_keeps_target_until_arrival_then_selects_another(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    actual_map = make_map(9)
    ghost = RoamingGhost()
    ghost._origin = (0, 0)
    ghost._collider = Collider(AABB(Vector2(4.0, 4.0)), Vector2(5.0, 5.0))
    ghost.set_roam_territory(((0, 0), (1, 0), (2, 0)))

    class PlayerStub:
        collider = Collider(AABB(Vector2(4.0, 4.0)), Vector2(85.0, 5.0))

    game_state = GameState()
    game_state.state = PacManState.SUPER
    monkeypatch.setattr(ghost_random, "choice", lambda cells: cells[0])

    target = ghost.select_target(PlayerStub(), actual_map, game_state)
    ghost.compute_path((0, 0), target, actual_map.graph)
    repeated_target = ghost.select_target(PlayerStub(), actual_map, game_state)

    assert ghost.behaviour is Behaviour.FLEAT
    assert target == (1, 0)
    assert repeated_target == target

    ghost.collider.position = Vector2(15.0, 5.0)
    ghost._path_index = len(ghost._path)
    next_target = ghost.select_target(PlayerStub(), actual_map, game_state)

    assert next_target == (0, 0)
    assert next_target in ghost._roam_territory


def test_flea_roaming_path_stays_inside_territory() -> None:
    actual_map = make_map(3, 2)
    territory = {
        (0, 0), (0, 1), (1, 1), (2, 1), (2, 0),
    }
    ghost = RoamingGhost()
    ghost._origin = (0, 0)
    ghost._collider = Collider(AABB(Vector2(4.0, 4.0)), Vector2(5.0, 5.0))
    ghost.set_roam_territory(territory)
    ghost.change_behaviour(Behaviour.FLEAT)

    ghost.compute_path(
        (0, 0), (2, 0), actual_map.graph, frozenset(territory)
    )

    path = [node.coordinate for node in ghost._path]
    assert path == [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)]
    assert all(coordinate in territory for coordinate in path)
