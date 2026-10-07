from typing import Any

import pytest

from Engine.Graphics import MlxDisplay, MlxWindow


class FakeMlx:
    def __init__(self, image_format: int = 0) -> None:
        self.image_format = image_format
        self.fail_window = False
        self.fail_image = False
        self.data = memoryview(bytearray(64))
        self.windows: list[tuple[Any, int, int, str]] = []
        self.images: list[tuple[Any, int, int]] = []
        self.presented: list[tuple[Any, Any, Any, int, int]] = []
        self.destroyed: list[tuple[str, Any]] = []

    def mlx_new_window(
        self, mlx_ptr: Any, width: int, height: int, title: str
    ) -> object:
        self.windows.append((mlx_ptr, width, height, title))
        return None if self.fail_window else "window"

    def mlx_new_image(self, mlx_ptr: Any, width: int, height: int) -> object:
        self.images.append((mlx_ptr, width, height))
        return None if self.fail_image else "image"

    def mlx_get_data_addr(
        self, image_ptr: Any
    ) -> tuple[memoryview, int, int, int]:
        return self.data, 32, 16, self.image_format

    def mlx_put_image_to_window(
        self, mlx_ptr: Any, window: Any, image: Any, x: int, y: int
    ) -> None:
        self.presented.append((mlx_ptr, window, image, x, y))

    def mlx_destroy_image(self, mlx_ptr: Any, image: Any) -> None:
        self.destroyed.append(("image", image))

    def mlx_destroy_window(self, mlx_ptr: Any, window: Any) -> None:
        self.destroyed.append(("window", window))


def test_window_supports_new_constructor_and_metadata() -> None:
    session = FakeMlx()
    window = MlxWindow(session, "mlx", (640, 480), "Pac-Man")

    assert window.size() == (640, 480)
    assert window.width == 640
    assert window.height == 480
    assert window.title == "Pac-Man"
    assert session.windows == [("mlx", 640, 480, "Pac-Man")]


def test_window_supports_legacy_constructor() -> None:
    window = MlxWindow(FakeMlx(), "mlx", 640, 480, "Pac-Man")

    assert window.size() == (640, 480)
    assert window.title == "Pac-Man"


def test_window_rejects_native_window_creation_failure() -> None:
    session = FakeMlx()
    session.fail_window = True

    with pytest.raises(RuntimeError, match="failed to create MLX window"):
        MlxWindow(session, "mlx", (640, 480), "Pac-Man")


@pytest.mark.parametrize(
    "args, message",
    [
        (((0, 10), "title"), "positive"),
        (((10, -1), "title"), "positive"),
        (((10, 10), 12), "title"),
    ],
)
def test_window_rejects_invalid_constructor_values(
    args: tuple[tuple[int, int], str | int], message: str
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        MlxWindow(FakeMlx(), "mlx", *args)


def test_draw_forwards_image_to_native_window() -> None:
    session = FakeMlx()
    window = MlxWindow(session, "mlx", (10, 10), "title")

    window.draw("image", 4, 7)

    assert session.presented == [("mlx", "window", "image", 4, 7)]


def test_create_display_creates_a_subwindow_display() -> None:
    session = FakeMlx()
    window = MlxWindow(session, "mlx", (10, 8), "title")

    display = window.create_display((4, 3))

    assert isinstance(display, MlxDisplay)
    assert display.size() == (4, 3)
    assert session.images == [("mlx", 4, 3)]


@pytest.mark.parametrize("size", [(0, 3), (4, 0), (11, 8), (10, 9)])
def test_create_display_rejects_invalid_size(size: tuple[int, int]) -> None:
    session = FakeMlx()
    window = MlxWindow(session, "mlx", (10, 8), "title")

    with pytest.raises(ValueError):
        window.create_display(size)

    assert session.destroyed == []


def test_create_display_rejects_native_image_creation_failure() -> None:
    session = FakeMlx()
    session.fail_image = True
    window = MlxWindow(session, "mlx", (10, 8), "title")

    with pytest.raises(RuntimeError, match="failed to create MLX display buffer"):
        window.create_display((4, 3))

    assert session.destroyed == []


def test_close_only_destroys_the_window_and_is_idempotent() -> None:
    session = FakeMlx()
    window = MlxWindow(session, "mlx", (10, 8), "title")

    window.close()
    window.close()

    assert session.destroyed == [("window", "window")]
