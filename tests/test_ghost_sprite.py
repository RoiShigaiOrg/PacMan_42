from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from Engine.Physics import AABB, Collider, PhysicsEngine, Vector2
from Engine.SceneManager.Scene.Scene import Scene
from Engine.Sprite import Sprite, SpriteFrame
from Game.Ghosts.Blinky import Blinky
from Game.Ghosts.Clyde import Clyde
from Game.Ghosts.Ghost import Behaviour, Ghost
from Game.Ghosts.Inky import Inky
from Game.Ghosts.Pinky import Pinky
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.Scenes.MapScene import MapScene
from Game.GameState.ArcadeMode import ArcadeMode


class FakeShape:
    def update_pos(self, _x: int, _y: int) -> None:
        pass

    def fill(self, _display: object) -> None:
        pass


class FakeSpriteSheet:
    def get_sprite(self, _tag: str) -> tuple[SpriteFrame, ...]:
        sprite = Sprite((1, 1), [[0xFFFFFFFF]])
        return (SpriteFrame(sprite, 100), SpriteFrame(sprite, 100))


class FakeEngine:
    def __init__(self) -> None:
        self.sheet_loads: list[tuple[Path, Path]] = []

    def load_sprite_sheet(
            self, image_path: Path, metadata_path: Path,
    ) -> FakeSpriteSheet:
        self.sheet_loads.append((image_path, metadata_path))
        return FakeSpriteSheet()


class MovementGhost(Ghost):
    def __init__(self, engine: Any) -> None:
        super().__init__(engine=engine, sprite_sheet_paths=(
            Path("sheet.png"), Path("sheet.json")
        ))
        self._width = 10
        self._height = 10
        self._graphical_shape = FakeShape()
        self._collider = Collider(AABB(Vector2(4, 4)), Vector2(5, 5))

    def init_ghost(self, _display: object, _actual_map: object) -> None:
        pass


def make_ghosts(engine: FakeEngine) -> tuple[Ghost, ...]:
    ghosts: tuple[Ghost, ...] = (
        Blinky(engine),
        Pinky(engine=engine),
        Inky(engine=engine),
        Clyde(engine=engine),
    )
    for ghost in ghosts:
        ghost._width = 10
        ghost._height = 10
        ghost._graphical_shape = FakeShape()
        ghost._collider = Collider(AABB(Vector2(4, 4)), Vector2(5, 5))
    return ghosts


@pytest.mark.parametrize(
    ("delta", "expected"),
    (
        (Vector2(1, 0), "right"),
        (Vector2(-1, 0), "left"),
        (Vector2(0, -1), "up"),
        (Vector2(0, 1), "down"),
    ),
)
def test_ghost_directional_animation_uses_actual_movement(
        delta: Vector2, expected: str,
) -> None:
    ghost = MovementGhost(FakeEngine())

    ghost._move(delta)
    ghost.update_movement(None, None, 0.05)  # type: ignore[arg-type]

    assert ghost.direction == expected
    assert ghost.visual_state == (expected, 0)


def test_all_ghosts_load_their_directional_spritesheets() -> None:
    engine = FakeEngine()

    ghosts = make_ghosts(engine)

    assert len(ghosts) == 4
    assert [image.name for image, _metadata in engine.sheet_loads] == [
        "blinkysheet.png",
        "Pinkysheet.png",
        "inkysheet.png",
        "clydesheet.png",
    ]
    assert all(ghost.visual_state == ("right", 0) for ghost in ghosts)


def test_fleeing_uses_roam_and_stationary_ghost_keeps_facing() -> None:
    ghost = MovementGhost(FakeEngine())
    ghost._move(Vector2(-1, 0))
    ghost.update_movement(None, None, 0.05)  # type: ignore[arg-type]
    assert ghost.visual_state == ("left", 0)

    ghost.change_behaviour(Behaviour.FLEAT)
    assert ghost.visual_state == ("roam", 0)

    ghost.update_movement(None, None, 0.1)  # type: ignore[arg-type]
    assert ghost.direction == "left"
    assert ghost.visual_state == ("roam", 1)

    ghost.change_behaviour(Behaviour.DEAD)
    assert ghost.visual_state == ("left", 0)


def test_idle_ghost_animation_frame_change_invalidates_its_region() -> None:
    actual_map = Map.__new__(Map)
    actual_map.width = 1
    actual_map.height = 1
    actual_map.grid = [[Cell((0, 0), True)]]
    actual_map.set_colliders(0, 0, 10, 10)
    actual_map.graph = actual_map.build_graph()
    ghost = MovementGhost(FakeEngine())
    ghost._collider = Collider(AABB(Vector2(4, 4)), Vector2(5, 5))

    scene = MapScene.__new__(MapScene)
    Scene.__init__(scene)
    scene.map = actual_map
    scene.stats = ArcadeMode()
    scene._MapScene__player = SimpleNamespace(
        collider=Collider(AABB(Vector2(4, 4)), Vector2(5, 5))
    )
    scene._MapScene__ghosts = {"ghost": ghost}
    scene._MapScene__ghost_targets = {}
    scene._MapScene__physics = PhysicsEngine()

    scene._MapScene__update_ghosts(0.1)

    assert ghost.position == (0, 0)
    assert ghost.visual_state == ("right", 1)
    assert scene.dirty_regions == ((0, 0, 10, 10),)
