from pathlib import Path
from typing import Any

import pytest

from Engine.FileManager.Loader.SpriteLoader import SpriteLoader
from Engine.Sprite import SpriteSheet


def make_pixel_buffer(
    pixel_rows: list[list[int]],
    stride: int,
    byte_order: str,
) -> bytearray:
    width = len(pixel_rows[0])
    buffer = bytearray([0xAA] * (stride * len(pixel_rows)))
    for y, row in enumerate(pixel_rows):
        for x, pixel in enumerate(row):
            offset = y * stride + x * 4
            buffer[offset:offset + 4] = pixel.to_bytes(4, byte_order)
    assert stride >= width * 4
    return buffer


class FakeMlx:
    def __init__(
        self,
        image_data: bytearray,
        width: int,
        height: int,
        stride: int,
        bits_per_pixel: int = 32,
        image_format: int = 0,
        image: object | None = "image",
    ) -> None:
        self.image_data = memoryview(image_data)
        self.width = width
        self.height = height
        self.stride = stride
        self.bits_per_pixel = bits_per_pixel
        self.image_format = image_format
        self.image = image
        self.load_calls: list[tuple[Any, str]] = []
        self.destroy_calls: list[tuple[Any, Any]] = []

    def mlx_png_file_to_image(
        self, mlx_ptr: Any, filename: str
    ) -> tuple[object | None, int, int]:
        self.load_calls.append((mlx_ptr, filename))
        return self.image, self.width, self.height

    def mlx_get_data_addr(
        self, image: Any
    ) -> tuple[memoryview, int, int, int]:
        return (
            self.image_data,
            self.bits_per_pixel,
            self.stride,
            self.image_format,
        )

    def mlx_destroy_image(self, mlx_ptr: Any, image: Any) -> None:
        self.destroy_calls.append((mlx_ptr, image))


def test_sprite_sheet_extracts_exact_rectangle_including_edges() -> None:
    pixels = [
        [0xFF000001, 0xFF000002, 0xFF000003],
        [0xFF000004, 0xFF000005, 0xFF000006],
    ]
    sheet = SpriteSheet(pixels)

    sprite = sheet.extract_sprite((1, 0), (2, 2))

    assert sheet.size == (3, 2)
    assert sprite.size == (2, 2)
    assert sprite.pixels == (
        (0xFF000002, 0xFF000003),
        (0xFF000005, 0xFF000006),
    )


def test_sprite_sheet_rejects_invalid_rectangles() -> None:
    sheet = SpriteSheet([[0xFFFFFFFF, 0xFFFFFFFF], [0xFFFFFFFF, 0xFFFFFFFF]])

    with pytest.raises(ValueError, match="outside the spritesheet"):
        sheet.extract_sprite((1, 0), (2, 1))
    with pytest.raises(ValueError, match="outside the spritesheet"):
        sheet.extract_sprite((0, 0), (0, 1))


def test_sprite_sheet_owns_its_pixel_rows() -> None:
    pixels = [[0xFF123456]]
    sheet = SpriteSheet(pixels)
    pixels[0][0] = 0

    assert sheet.extract_sprite((0, 0), (1, 1)).pixels == ((0xFF123456,),)


def test_sprite_loader_copies_argb_pixels_and_respects_stride(
    tmp_path: Path,
) -> None:
    expected = [
        [0xFF112233, 0x80445566],
        [0xFF778899, 0x00AABBCC],
    ]
    stride = 12
    data = make_pixel_buffer(expected, stride, "little")
    session = FakeMlx(data, 2, 2, stride)
    mlx_ptr = object()
    filename = tmp_path / "sprites.png"

    sheet = SpriteLoader(filename, session, mlx_ptr).load()
    data[:] = b"\x00" * len(data)

    assert sheet.size == (2, 2)
    assert sheet.extract_sprite((0, 0), (2, 2)).pixels == tuple(
        tuple(row) for row in expected
    )
    assert session.load_calls == [(mlx_ptr, str(filename))]
    assert session.destroy_calls == [(mlx_ptr, "image")]


def test_sprite_loader_converts_big_endian_image_format() -> None:
    expected = [[0xFF123456]]
    session = FakeMlx(
        make_pixel_buffer(expected, 4, "big"),
        1,
        1,
        4,
        image_format=1,
    )

    sheet = SpriteLoader(Path("sprites.png"), session, "mlx").load()

    assert sheet.extract_sprite((0, 0), (1, 1)).pixels == ((0xFF123456,),)
    assert session.destroy_calls == [("mlx", "image")]


def test_sprite_loader_rejects_missing_image() -> None:
    session = FakeMlx(bytearray(), 0, 0, 0, image=None)

    with pytest.raises(RuntimeError, match="Could not load spritesheet"):
        SpriteLoader(Path("missing.png"), session, "mlx").load()

    assert session.destroy_calls == []


def test_sprite_loader_destroys_image_when_bpp_is_unsupported() -> None:
    session = FakeMlx(bytearray(4), 1, 1, 4, bits_per_pixel=24)

    with pytest.raises(RuntimeError, match="Expected 32-bit pixels"):
        SpriteLoader(Path("sprites.png"), session, "mlx").load()

    assert session.destroy_calls == [("mlx", "image")]
