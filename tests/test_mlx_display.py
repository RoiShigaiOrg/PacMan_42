from typing import Any

import pytest

from Engine.Graphics import MlxDisplay


class FakeMlx:
    def __init__(self, image_format: int = 0, bits_per_pixel: int = 32) -> None:
        self.data = memoryview(bytearray(32))
        self.image_format = image_format
        self.bits_per_pixel = bits_per_pixel
        self.presented: list[tuple[Any, Any, Any, int, int]] = []
        self.destroyed: list[tuple[Any, Any]] = []

    def mlx_get_data_addr(
        self, image_ptr: Any
    ) -> tuple[memoryview, int, int, int]:
        return self.data, self.bits_per_pixel, 16, self.image_format

    def mlx_put_image_to_window(
        self, mlx_ptr: Any, window: Any, image: Any, x: int, y: int
    ) -> None:
        self.presented.append((mlx_ptr, window, image, x, y))

    def mlx_destroy_image(self, mlx_ptr: Any, image: Any) -> None:
        self.destroyed.append((mlx_ptr, image))


def make_display(
    session: FakeMlx | None = None,
) -> tuple[MlxDisplay, FakeMlx]:
    actual_session = session or FakeMlx()
    return (
        MlxDisplay(actual_session, "image", "mlx", "window", (3, 2)),
        actual_session,
    )


def test_display_exposes_dimensions() -> None:
    display, _ = make_display()

    assert display.width == 3
    assert display.height == 2
    assert display.size() == (3, 2)


def test_draw_pixel_writes_little_endian_argb_bytes() -> None:
    display, session = make_display()

    display.draw_pixel(1, 0, 0xFF112233)

    assert bytes(session.data[4:8]) == bytes.fromhex("332211FF")


def test_draw_pixel_writes_big_endian_argb_bytes() -> None:
    display, session = make_display(FakeMlx(image_format=1))

    display.draw_pixel(1, 0, 0xFF112233)

    assert bytes(session.data[4:8]) == bytes.fromhex("FF112233")


def test_draw_pixel_ignores_out_of_bounds_coordinates() -> None:
    display, session = make_display()
    before = bytes(session.data)

    display.draw_pixel(-1, 0, 0xFFFFFFFF)
    display.draw_pixel(3, 0, 0xFFFFFFFF)
    display.draw_pixel(0, 2, 0xFFFFFFFF)

    assert bytes(session.data) == before


@pytest.mark.parametrize("color", [-1, 0x100000000])
def test_display_rejects_colors_outside_32_bits(color: int) -> None:
    display, _ = make_display()

    with pytest.raises(ValueError):
        display.draw_pixel(0, 0, color)


@pytest.mark.parametrize("operation", ["clear", "fill"])
def test_clear_and_fill_reject_colors_outside_32_bits(operation: str) -> None:
    display, _ = make_display()

    with pytest.raises(ValueError):
        getattr(display, operation)(-1)


def test_clear_fills_rows_without_overwriting_stride_padding() -> None:
    display, session = make_display()
    session.data[:] = b"\xAA" * len(session.data)

    display.clear(0xFF445566)

    assert bytes(session.data[0:12]) == bytes.fromhex("665544FF" * 3)
    assert bytes(session.data[16:28]) == bytes.fromhex("665544FF" * 3)
    assert session.data[12] == 0xAA
    assert session.data[28] == 0xAA


def test_fill_writes_every_pixel() -> None:
    display, session = make_display()

    display.fill(0xFF010203)

    assert bytes(session.data[0:12]) == bytes.fromhex("030201FF" * 3)
    assert bytes(session.data[16:28]) == bytes.fromhex("030201FF" * 3)


def test_fill_rect_writes_only_the_requested_pixels() -> None:
    display, session = make_display()
    session.data[:] = b"\xAA" * len(session.data)

    display.fill_rect(1, 0, 2, 1, 0xFF010203)

    assert bytes(session.data[0:4]) == b"\xAA" * 4
    assert bytes(session.data[4:12]) == bytes.fromhex("030201FF" * 2)
    assert bytes(session.data[12:16]) == b"\xAA" * 4


def test_restore_region_restores_only_the_requested_pixels() -> None:
    display, session = make_display()
    session.data[:] = bytes(range(32))
    snapshot = display.snapshot()
    session.data[:] = b"\xFF" * 32

    display.restore_region(snapshot, 1, 0, 1, 1)

    assert bytes(session.data[0:4]) == b"\xFF" * 4
    assert bytes(session.data[4:8]) == bytes(range(4, 8))
    assert bytes(session.data[8:]) == b"\xFF" * 24


def test_render_presents_the_display_image() -> None:
    display, session = make_display()

    display.render()

    assert session.presented == [("mlx", "window", "image", 0, 0)]


def test_non_32_bit_images_are_destroyed_and_rejected() -> None:
    session = FakeMlx(bits_per_pixel=24)

    with pytest.raises(RuntimeError, match="32-bit"):
        MlxDisplay(session, "image", "mlx", "window", (3, 2))

    assert session.destroyed == [("mlx", "image")]
