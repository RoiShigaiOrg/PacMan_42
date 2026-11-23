from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from Engine.Animation import Animation, AnimationHandler
from Engine.Physics import Vector2
from Engine.SceneManager.Scene.Scene import Scene
from Engine.Sprite import Sprite, SpriteFrame
from Game.GameState.GameStateFactory import GameStateFactory
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.Scenes.MapScene import MapScene


class RecordingDisplay:
    def __init__(self) -> None:
        self.pixels: dict[tuple[int, int], int] = {}

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        self.pixels[(x, y)] = color


def make_frames() -> tuple[SpriteFrame, SpriteFrame]:
    return (
        SpriteFrame(Sprite((1, 1), [[0xFFFF0000]]), 100),
        SpriteFrame(Sprite((1, 1), [[0xFF00FF00]]), 100),
    )


def make_map(
        walkable: list[list[bool]],
        frames: tuple[SpriteFrame, ...] | None = None,
) -> Map:
    actual_map = Map.__new__(Map)
    actual_map.height = len(walkable)
    actual_map.width = len(walkable[0])
    actual_map.grid = [
        [Cell((column, row), state) for column, state in enumerate(line)]
        for row, line in enumerate(walkable)
    ]
    actual_map._Map__corner_coordinates = actual_map._find_corner_coordinates()
    actual_map._Map__corner_cells = frozenset(
        actual_map._Map__corner_coordinates.values()
    )
    actual_map._Map__pellet = [
        cell for row in actual_map.grid for cell in row if cell.walkable
    ]
    actual_map._Map__pacgum_sprite = Sprite((1, 1), [[0xFF0000FF]])
    actual_map._Map__animation_handler = AnimationHandler({
        "pellet": Animation(frames or make_frames()),
    })
    actual_map._Map__grid_origin = None
    actual_map._Map__cell_size = None
    actual_map.set_colliders(
        0, 0, actual_map.width * 10, actual_map.height * 10
    )
    return actual_map


def test_map_creates_a_pellet_for_every_walkable_cell_after_opening_center(
        monkeypatch: Any,
) -> None:
    map_module = importlib.import_module("Game.MapGeneration.MapGeneration")

    class ClosedMaze:
        def __init__(self, **_kwargs: Any) -> None:
            self.maze = [[15]]

        def generate(self, **_kwargs: Any) -> None:
            pass

    class FakeSpriteSheet:
        @staticmethod
        def get_sprite(_tag: str) -> tuple[SpriteFrame, ...]:
            return make_frames()

        @staticmethod
        def extract_sprite(
                _position: tuple[int, int], _size: tuple[int, int]
        ) -> Sprite:
            return Sprite((1, 1), [[0xFF0000FF]])

    class FakeEngine:
        @staticmethod
        def load_sprite_sheet(
                _image_path: Path,
                _metadata_path: Path | None = None,
        ) -> FakeSpriteSheet:
            return FakeSpriteSheet()

    monkeypatch.setattr(map_module, "MazeGenerator", ClosedMaze)

    actual_map = Map(FakeEngine())

    walkable_cells = {
        cell.coordinate
        for row in actual_map.grid
        for cell in row
        if cell.walkable
    }
    assert set(actual_map.pellet_cells) == walkable_cells
    assert len(actual_map.pellet_cells) == 9


def test_consuming_a_pellet_removes_it_from_the_map() -> None:
    actual_map = make_map([[True, True]])
    actual_map.set_colliders(0, 0, 20, 10)

    consumed = actual_map.consume_pellet_at(Vector2(15, 5))

    assert consumed is not None
    assert consumed.coordinate == (1, 0)
    assert actual_map.pellet_cells == ((0, 0),)
    assert actual_map.consume_pellet_at(Vector2(15, 5)) is None


def test_only_corner_pellets_animate_and_other_cells_use_pacgum() -> None:
    actual_map = make_map([[True, True, True]] * 3)
    display = RecordingDisplay()

    actual_map.render_pellets(display)
    assert display.pixels[(5, 5)] == 0xFFFF0000
    assert display.pixels[(15, 5)] == 0xFF0000FF
    assert display.pixels[(25, 25)] == 0xFFFF0000

    assert actual_map.update_pellet_animation(0.1)
    display.pixels.clear()
    actual_map.render_pellets(display)

    assert display.pixels[(5, 5)] == 0xFF00FF00
    assert display.pixels[(15, 5)] == 0xFF0000FF
    assert display.pixels[(25, 25)] == 0xFF00FF00


def test_scene_scores_only_a_pellet_that_was_removed() -> None:
    actual_map = make_map([[True, True, True]] * 3)
    scene = MapScene.__new__(MapScene)
    Scene.__init__(scene)
    scene.map = actual_map
    scene.game = GameStateFactory()
    stats = scene.game.state
    scene._MapScene__player = type(
        "PlayerStub",
        (),
        {"collider": type("ColliderStub", (), {
            "world_position": Vector2(15, 15),
        })()},
    )()

    scene._MapScene__consume_player_pellet()
    scene._MapScene__consume_player_pellet()

    assert stats.scores == 10
    assert (1, 1) not in actual_map.pellet_cells
    assert len(actual_map.pellet_cells) == 8
    assert scene.dirty_regions == ((10, 10, 10, 10),)
