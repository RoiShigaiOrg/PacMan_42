from typing import Any

import pytest

from Engine.Graphics.MlxWindow import MlxWindow


class FakeMlx:
    def __init__(self, image_format: int = 0) -> None:
        self.image_format = image_format
        self.data = memoryview(bytearray(24))
        self.presented: list[tuple[Any, Any, Any, int, int]] = []
        self.destroyed: list[tuple[str, Any]] = []

    def mlx_new_window(
        self, mlx_ptr: Any, width: int, height: int, title: str
    ) -> object:
        return "window"

    def mlx_new_image(self, mlx_ptr: Any, width: int, height: int) -> object:
        return "image"

    def mlx_get_data_addr(
        self, image_ptr: Any
    ) -> tuple[memoryview, int, int, int]:
        return self.data, 32, 12, self.image_format

    def mlx_put_image_to_window(
        self, mlx_ptr: Any, window: Any, image: Any, x: int, y: int
    ) -> None:
        self.presented.append((mlx_ptr, window, image, x, y))

    def mlx_destroy_image(self, mlx_ptr: Any, image: Any) -> None:
        self.destroyed.append(("image", image))

    def mlx_destroy_window(self, mlx_ptr: Any, window: Any) -> None:
        self.destroyed.append(("window", window))


def test_screen_metadata_and_size() -> None:
    session = FakeMlx()
    screen = MlxWindow(session, "mlx", 2, 2, "Pac-Man")

    assert screen.width == 2
    assert screen.height == 2
    assert screen.title == "Pac-Man"
    assert screen.size() == (2, 2)


def test_pixel_and_clear_write_to_persistent_buffer() -> None:
    session = FakeMlx()
    screen = MlxWindow(session, "mlx", 2, 2, "Pac-Man")

    screen.pixel(1, 0, 0xFF112233)
    assert bytes(session.data[4:8]) == bytes.fromhex("332211FF")

    screen.clear(0xFF445566)
    assert bytes(session.data[0:8]) == bytes.fromhex("665544FF" * 2)
    assert bytes(session.data[12:20]) == bytes.fromhex("665544FF" * 2)


def test_format_one_uses_big_endian_argb_bytes() -> None:
    session = FakeMlx(image_format=1)
    screen = MlxWindow(session, "mlx", 1, 1, "Pac-Man")

    screen.pixel(0, 0, 0xFF112233)

    assert bytes(session.data[:4]) == bytes.fromhex("FF112233")


def test_screen_update_presents_buffer() -> None:
    session = FakeMlx()
    screen = MlxWindow(session, "mlx", 2, 2, "Pac-Man")

    screen.screen_update()

    assert session.presented[-1] == ("mlx", "window", "image", 0, 0)


def test_close_is_idempotent() -> None:
    session = FakeMlx()
    screen = MlxWindow(session, "mlx", 2, 2, "Pac-Man")

    screen.close()
    screen.close()

    assert session.destroyed == [("image", "image"), ("window", "window")]


@pytest.mark.parametrize("coordinates", [(-1, 0), (0, -1), (2, 0), (0, 2)])
def test_pixel_rejects_coordinates_outside_screen(
    coordinates: tuple[int, int],
) -> None:
    session = FakeMlx()
    screen = MlxWindow(session, "mlx", 2, 2, "Pac-Man")

    with pytest.raises(ValueError):
        screen.pixel(*coordinates, 0xFFFFFFFF)
