from Game.GameState import GameState, SUPER
from Game.Ghosts.Blinky import Blinky
from Game.Ghosts.Ghost import Behaviour
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.Scenes.MapScene import MapScene


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


def make_scene(
        walkability: list[list[bool]], state: str = "normal",
) -> MapScene:
    scene = MapScene.__new__(MapScene)
    scene.map = make_map(walkability)
    scene.stats = GameState()
    scene.stats.state = state
    return scene


def test_ghost_chases_player_outside_super_mode() -> None:
    scene = make_scene([[True] * 7 for _ in range(3)])
    ghost = Blinky()

    target = scene._MapScene__target_for_ghost(ghost, (1, 1), (4, 1))

    assert target == (4, 1)
    assert ghost.behaviour is Behaviour.CHASE


def test_ghost_flees_in_super_mode_when_player_is_within_five_cells() -> None:
    scene = make_scene([[True] * 7 for _ in range(3)], SUPER)
    ghost = Blinky()

    target = scene._MapScene__target_for_ghost(
        ghost, (4, 1), (3, 1)
    )

    assert target == (5, 1)
    assert ghost.behaviour is Behaviour.FLEAT


def test_ghost_returns_to_origin_when_player_is_far_in_super_mode() -> None:
    scene = make_scene([[True] * 8], SUPER)
    ghost = Blinky()
    ghost._origin = (7, 0)

    target = scene._MapScene__target_for_ghost(ghost, (1, 0), (7, 0))

    assert target == ghost.origin
    assert ghost.behaviour is Behaviour.FLEAT


def test_ghost_flees_at_the_five_cell_threshold() -> None:
    scene = make_scene([[True] * 8], SUPER)
    ghost = Blinky()
    ghost._origin = (7, 0)

    target = scene._MapScene__target_for_ghost(ghost, (1, 0), (6, 0))

    assert target == (0, 0)
    assert ghost.behaviour is Behaviour.FLEAT


def test_flee_target_falls_back_if_reflected_cell_is_blocked() -> None:
    scene = make_scene([[True, True, False, True, True]])

    target = scene._MapScene__flee_target((3, 0), (4, 0))

    assert target == (3, 0)
