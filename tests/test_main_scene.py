from typing import Any

from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler.KeyCode import KEY_ENTER
from Game.Scenes.MainScene import MainScene


class FakeMlx:
    def __init__(self) -> None:
        self.data = memoryview(bytearray(200 * 200 * 4))
        self.events: list[tuple[Any, ...]] = []

    def mlx_get_data_addr(
        self, image_ptr: Any
    ) -> tuple[memoryview, int, int, int]:
        return self.data, 32, 200 * 4, 0

    def mlx_put_image_to_window(
        self,
        mlx_ptr: Any,
        window: Any,
        image: Any,
        x: int,
        y: int,
    ) -> None:
        self.events.append(("image", mlx_ptr, window, image, x, y))

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


class FakeEngine:
    def __init__(self) -> None:
        self.scene_manager = FakeSceneManager()

    def get_config_key(self, key: str) -> int:
        return {"UP": ord("z"), "DOWN": ord("s")}[key]


class FakeSceneManager:
    def __init__(self) -> None:
        self.changed_scenes: list[str] = []

    def change_scene(self, scene_id: str) -> None:
        self.changed_scenes.append(scene_id)


class FakeInput:
    def __init__(self, key: int) -> None:
        self.key = key

    def was_key_pressed(self, key: int) -> bool:
        return self.key == key


def test_main_scene_defers_window_drawing_until_render() -> None:
    session = FakeMlx()
    display = MlxDisplay(session, "image", "mlx", "window", (200, 200))

    scene = MainScene(None, display)  # type: ignore[arg-type]

    assert session.events == []

    scene.render()

    assert session.events[0] == ("image", "mlx", "window", "image", 0, 0)
    assert [event[0] for event in session.events] == [
        "image", "text", "text", "text", "text"
    ]
    leaderboard_label = next(
        event for event in session.events if event[-1] == "LeaderBoard"
    )
    assert leaderboard_label[3:5] == (56, 107)


def test_main_scene_marks_old_and_new_panels_dirty_on_navigation() -> None:
    session = FakeMlx()
    display = MlxDisplay(session, "image", "mlx", "window", (200, 200))
    scene = MainScene(FakeEngine(), display)  # type: ignore[arg-type]
    scene.render()

    scene.update(0.0, FakeInput(ord("s")))  # Move down to LeaderBoard.

    assert scene.dirty_regions == (
        (60, 100, 80, 10),
        (60, 110, 80, 10),
    )

    scene.render()

    assert scene.dirty_regions == ()


def test_main_scene_activates_selected_panel() -> None:
    session = FakeMlx()
    display = MlxDisplay(session, "image", "mlx", "window", (200, 200))
    engine = FakeEngine()
    scene = MainScene(engine, display)  # type: ignore[arg-type]

    scene.update(0.0, FakeInput(KEY_ENTER))

    assert engine.scene_manager.changed_scenes == ["game_scene"]
