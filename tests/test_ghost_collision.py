from Engine.Graphics import MlxDisplay
from Engine.Physics import AABB, Collider, PhysicsEngine, Vector2
from Game.GameState import GameState, PacManState
from Game.Ghosts.Ghost import Behaviour, Ghost
from Game.MapGeneration.MapGeneration import Map
from Game.Scenes.MapScene import MapScene


class CollisionGhost(Ghost):
    def __init__(
            self,
            position: Vector2,
            behaviour: Behaviour = Behaviour.CHASE,
    ) -> None:
        super().__init__()
        self._collider = Collider(AABB(Vector2(5.0, 5.0)), position)
        self.change_behaviour(behaviour)

    def init_ghost(self, _display: MlxDisplay, _actual_map: Map) -> None:
        pass

    def _chase(self, target: tuple[int, int]) -> tuple[int, int]:
        return target


def make_scene(
        ghosts: dict[str, CollisionGhost],
        player_position: Vector2 = Vector2(10.0, 10.0),
) -> MapScene:
    scene = MapScene.__new__(MapScene)
    scene._MapScene__ghosts = ghosts
    scene._MapScene__player = type(
        "PlayerStub", (), {"collider": Collider(
            AABB(Vector2(5.0, 5.0)), player_position
        )}
    )()
    scene._MapScene__physics = PhysicsEngine()
    scene.stats = GameState()
    return scene


def check_collisions(scene: MapScene) -> None:
    scene._MapScene__check_player_ghost_collision()


def test_non_overlapping_ghost_does_not_affect_pacman() -> None:
    ghost = CollisionGhost(Vector2(30.0, 10.0))
    scene = make_scene({"blinky": ghost})

    check_collisions(scene)

    assert scene.stats.lives == 3
    assert scene.stats.state is PacManState.NORMAL
    assert ghost.behaviour is Behaviour.CHASE


def test_chasing_ghost_collision_costs_one_life() -> None:
    ghost = CollisionGhost(Vector2(18.0, 10.0))
    scene = make_scene({"blinky": ghost})

    check_collisions(scene)

    assert scene.stats.lives == 2
    assert scene.stats.state is PacManState.DEAD
    assert ghost.behaviour is Behaviour.CHASE


def test_fleeing_ghost_collision_awards_points_and_kills_ghost() -> None:
    ghost = CollisionGhost(Vector2(18.0, 10.0), Behaviour.FLEAT)
    scene = make_scene({"blinky": ghost})
    scene.stats.state = PacManState.SUPER

    check_collisions(scene)

    assert scene.stats.scores == 200
    assert scene.stats.lives == 3
    assert ghost.behaviour is Behaviour.DEAD


def test_dead_ghost_collision_has_no_effect() -> None:
    ghost = CollisionGhost(Vector2(18.0, 10.0), Behaviour.DEAD)
    scene = make_scene({"blinky": ghost})
    scene.stats.state = PacManState.SUPER

    check_collisions(scene)

    assert scene.stats.scores == 0
    assert scene.stats.lives == 3
    assert ghost.behaviour is Behaviour.DEAD


def test_overlapping_chase_ghost_does_not_cost_lives_after_death() -> None:
    ghost = CollisionGhost(Vector2(18.0, 10.0))
    scene = make_scene({"blinky": ghost})

    check_collisions(scene)
    check_collisions(scene)

    assert scene.stats.lives == 2
    assert scene.stats.state is PacManState.DEAD
