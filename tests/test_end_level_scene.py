from typing import Any

from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler.KeyCode import KEY_ESC
from Game.GameState import GameState
from Game.Scenes.EndLevelScene import EndLevel


class FakeMlx:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.data = memoryview(bytearray(width * height * 4))
        self.events: list[tuple[Any, ...]] = []

    def mlx_get_data_addr(
            self, image_ptr: Any) -> tuple[memoryview, int, int, int]:
        return self.data, 32, self.width * 4, 0

    def mlx_put_image_to_window(
            self,
            mlx_ptr: Any,
            window: Any,
            image: Any,
            x: int,
            y: int,
    ) -> None:
        self.events.append(("image", mlx_ptr, window, image, x, y))

    def mlx_clear_window(self, mlx_ptr: Any, window: Any) -> None:
        self.events.append(("clear", mlx_ptr, window))

    def mlx_string_put(
            self,
            mlx_ptr: Any,
            window: Any,
            x: int,
            y: int,
            color: int,
            text: str,
    ) -> None:
        self.events.append(("text", mlx_ptr, window, x, y, color, text))


class FakeSceneManager:
    def __init__(self) -> None:
        self.changes: list[str] = []

    def change_scene(self, scene_id: str) -> None:
        self.changes.append(scene_id)


class FakeEngine:
    def __init__(self, level_time: int = 120) -> None:
        self.scene_manager = FakeSceneManager()
        self.config = {"level_time": level_time}

    def get_config_key(self, key: str) -> Any:
        return self.config[key]


class FakeInputHandler:
    def __init__(self, pressed: set[int] | None = None) -> None:
        self.pressed = pressed or set()

    def was_key_pressed(self, key: int) -> bool:
        return key in self.pressed


def make_scene(
        stats: GameState,
        level_time: int = 120,
) -> tuple[EndLevel, FakeEngine, FakeMlx]:
    engine = FakeEngine(level_time)
    session = FakeMlx(400, 300)
    display = MlxDisplay(session, "image", "mlx", "window", (400, 300))
    return EndLevel(engine, display, stats), engine, session


def displayed_text(session: FakeMlx) -> list[str]:
    return [
        str(event[6]) for event in session.events if event[0] == "text"
    ]


def test_end_level_applies_time_and_life_bonus_once() -> None:
    stats = GameState(lives=2)
    stats.scores = 500
    stats.level_time = 90.5
    scene, _, _ = make_scene(stats)

    scene.render_on_change()

    assert stats.scores == 500 + (90 * 10) + (2 * 200)
    stats.scores += 50
    scene.render_on_change()
    assert stats.scores == 500 + (90 * 10) + (2 * 200) + 50


def test_end_level_animates_time_then_lives_then_final_score() -> None:
    stats = GameState(lives=2)
    stats.scores = 500
    stats.level_time = 90.5
    scene, _, session = make_scene(stats)
    scene.render_on_change()

    scene.render()
    texts = displayed_text(session)
    assert any("Time  00:00:30 / 00:02:00  +0" in text for text in texts)
    assert not any("Lives" in text or "Score" in text for text in texts)

    scene.update(8.0, FakeInputHandler())
    scene.render()
    texts = displayed_text(session)
    assert any("+900" in text for text in texts)
    assert any("Lives  2  +0" in text for text in texts)
    assert not any("Score" in text for text in texts)

    scene.update(0.7, FakeInputHandler())
    scene.render()
    texts = displayed_text(session)
    assert any("Lives  2  +400" in text for text in texts)
    assert any("Score  500" in text for text in texts)

    scene.update(1.0, FakeInputHandler())
    scene.render()
    assert any("Score  1800" in text for text in displayed_text(session))
    assert stats.scores == 1800


def test_escaping_end_level_keeps_the_bonus_already_awarded() -> None:
    stats = GameState(lives=1)
    stats.scores = 300
    stats.level_time = 100.0
    scene, engine, _ = make_scene(stats)
    scene.render_on_change()

    scene.update(0.0, FakeInputHandler({KEY_ESC}))

    assert engine.scene_manager.changes == ["main_scene"]
    assert stats.scores == 300 + (100 * 10) + 200
