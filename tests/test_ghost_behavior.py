from types import SimpleNamespace

from Engine.Physics import AABB, Collider, Vector2
from Game.GameState import GameState, PacManState
from Game.Ghosts.Blinky import Blinky
from Game.Ghosts.Clyde import Clyde
from Game.Ghosts.Ghost import Behaviour
from Game.Ghosts.Inky import Inky
from Game.Ghosts.Pinky import Pinky
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


def make_collider(cell: tuple[int, int]) -> Collider:
    return Collider(
        AABB(Vector2(4.0, 4.0)),
        Vector2(cell[0] * 10 + 5, cell[1] * 10 + 5),
    )


def make_player(
        cell: tuple[int, int],
        direction: Vector2 = Vector2(0.0, 0.0),
) -> SimpleNamespace:
    return SimpleNamespace(collider=make_collider(cell), direction=direction)


def make_ghost(
        cell: tuple[int, int], origin: tuple[int, int] = (0, 0),
) -> Blinky:
    ghost = Blinky()
    ghost._origin = origin
    ghost._collider = make_collider(cell)
    return ghost


def make_game_state(
        state: PacManState = PacManState.NORMAL,
) -> GameState:
    game_state = GameState()
    game_state.state = state
    return game_state


def test_ghost_chases_player_outside_super_mode() -> None:
    actual_map = make_map([[True] * 7 for _ in range(3)])
    ghost = make_ghost((1, 1))

    target = ghost.select_target(
        make_player((4, 1)), actual_map, make_game_state()
    )

    assert target == (4, 1)
    assert ghost.behaviour is Behaviour.CHASE


def test_each_ghost_uses_its_own_chase_strategy() -> None:
    actual_map = make_map([[True] * 9 for _ in range(3)])
    player = make_player((1, 1), Vector2(1.0, 0.0))
    blinky = make_ghost((2, 1))

    assert Blinky().select_target(
        player, actual_map, make_game_state()
    ) == (1, 1)
    assert Pinky().select_target(
        player, actual_map, make_game_state()
    ) == (5, 1)
    assert Inky().select_target(
        player, actual_map, make_game_state(), {"blinky": blinky}
    ) == (8, 1)

    clyde_map = make_map([[True] * 12])
    clyde = Clyde()
    clyde._origin = (0, 0)
    clyde._collider = make_collider((1, 0))
    clyde.set_roam_territory(((0, 0), (1, 0), (2, 0)))
    clyde_target = clyde.select_target(
        make_player((11, 0)), clyde_map, make_game_state()
    )

    assert clyde.behaviour is Behaviour.CHASE
    assert clyde_target in clyde.roam_territory


def test_dead_pacman_sends_ghost_home_then_roaming_until_recovery_ends(
) -> None:
    actual_map = make_map([[True] * 7 for _ in range(3)])
    ghost = make_ghost((1, 1), origin=(3, 1))
    territory = ((3, 1), (4, 1))
    ghost.set_roam_territory(territory)
    game_state = make_game_state()
    game_state.lose_life()
    player = make_player((5, 1))

    return_plan = ghost.compute_target(
        ghost.behaviour_context(player, actual_map, game_state)
    )

    assert ghost.behaviour is Behaviour.RECOVERY
    assert return_plan.target == ghost.origin
    assert return_plan.allowed_cells is None

    ghost.collider.position = Vector2(35.0, 15.0)
    roam_plan = ghost.compute_target(
        ghost.behaviour_context(player, actual_map, game_state)
    )

    assert roam_plan.target in territory
    assert roam_plan.allowed_cells == frozenset(territory)

    game_state.update_death_recovery(3.0)
    ghost.compute_target(
        ghost.behaviour_context(player, actual_map, game_state)
    )

    assert game_state.state is PacManState.NORMAL
    assert ghost.behaviour is Behaviour.CHASE


def test_ghost_flees_in_super_mode_when_player_is_within_five_cells() -> None:
    actual_map = make_map([[True] * 7 for _ in range(3)])
    ghost = make_ghost((4, 1))

    target = ghost.select_target(
        make_player((3, 1)), actual_map, make_game_state(PacManState.SUPER)
    )

    assert target == (5, 1)
    assert ghost.behaviour is Behaviour.FLEAT


def test_ghost_returns_to_origin_when_player_is_far_in_super_mode() -> None:
    actual_map = make_map([[True] * 8])
    ghost = make_ghost((1, 0), origin=(7, 0))

    target = ghost.select_target(
        make_player((7, 0)), actual_map, make_game_state(PacManState.SUPER)
    )

    assert target == ghost.origin
    assert ghost.behaviour is Behaviour.FLEAT


def test_ghost_flees_at_the_five_cell_threshold() -> None:
    actual_map = make_map([[True] * 8])
    ghost = make_ghost((1, 0), origin=(7, 0))

    target = ghost.select_target(
        make_player((6, 0)), actual_map, make_game_state(PacManState.SUPER)
    )

    assert target == (0, 0)
    assert ghost.behaviour is Behaviour.FLEAT


def test_flee_target_falls_back_if_reflected_cell_is_blocked() -> None:
    actual_map = make_map([[True, True, False, True, True]])
    ghost = make_ghost((3, 0))

    target = ghost.select_target(
        make_player((4, 0)), actual_map, make_game_state(PacManState.SUPER)
    )

    assert target == (3, 0)
