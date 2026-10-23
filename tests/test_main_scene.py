from typing import Any

from Engine.Graphics.MlxDisplay import MlxDisplay
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


def test_main_scene_defers_window_drawing_until_render() -> None:
    session = FakeMlx()
    display = MlxDisplay(session, "image", "mlx", "window", (200, 200))

    scene = MainScene(None, display)  # type: ignore[arg-type]

    assert session.events == []

    scene.render()

    assert session.events[0] == ("image", "mlx", "window", "image", 0, 0)
    assert [event[0] for event in session.events] == [
        "image", "text", "text", "text"
    ]
