from pathlib import Path
from typing import Any, Literal
import json

import pytest

from Engine.FileManager.Loader.SpriteLoader import SpriteLoader
from Engine.Animation import Animation, AnimationHandler
from Engine.Sprite import (
    AsepriteMetadata,
    Sprite,
    SpriteFrame,
    SpriteSheet,
)


def make_pixel_buffer(
    pixel_rows: list[list[int]],
    stride: int,
    byte_order: Literal["little", "big"],
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


def make_aseprite_metadata(
    image: str = "sprites.png",
    width: int = 4,
    height: int = 2,
) -> dict[str, Any]:
    return {
        "frames": [
            {
                "filename": "walk 0.png",
                "frame": {"x": 0, "y": 0, "w": 2, "h": 2},
                "rotated": False,
                "trimmed": False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": 2, "h": 2},
                "sourceSize": {"w": 2, "h": 2},
                "duration": 100,
            },
            {
                "filename": "walk 1.png",
                "frame": {"x": 2, "y": 0, "w": 2, "h": 2},
                "rotated": False,
                "trimmed": False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": 2, "h": 2},
                "sourceSize": {"w": 2, "h": 2},
                "duration": 200,
            },
        ],
        "meta": {
            "image": image,
            "size": {"w": width, "h": height},
            "frameTags": [
                {
                    "name": "walk_right",
                    "from": 0,
                    "to": 1,
                    "direction": "forward",
                }
            ],
        },
    }


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


def test_sprite_sheet_extracts_tagged_frames_and_durations() -> None:
    metadata = AsepriteMetadata.model_validate(make_aseprite_metadata())
    pixels = [
        [0xFF000001, 0xFF000002, 0xFF000003, 0xFF000004],
        [0xFF000005, 0xFF000006, 0xFF000007, 0xFF000008],
    ]
    sheet = SpriteSheet(pixels, metadata)

    frames = sheet.get_sprite("walk_right")

    assert len(frames) == 2
    assert frames[0].sprite.pixels == (
        (0xFF000001, 0xFF000002),
        (0xFF000005, 0xFF000006),
    )
    assert frames[1].sprite.pixels == (
        (0xFF000003, 0xFF000004),
        (0xFF000007, 0xFF000008),
    )
    assert tuple(frame.duration_ms for frame in frames) == (100, 200)


def test_sprite_sheet_applies_reverse_tag_direction() -> None:
    metadata_data = make_aseprite_metadata()
    metadata_data["meta"]["frameTags"][0]["direction"] = "reverse"
    sheet = SpriteSheet(
        [[0xFFFFFFFF] * 4 for _ in range(2)],
        AsepriteMetadata.model_validate(metadata_data),
    )

    frames = sheet.get_sprite("walk_right")

    assert tuple(frame.duration_ms for frame in frames) == (200, 100)


def test_sprite_sheet_requires_metadata_for_tag_lookup() -> None:
    sheet = SpriteSheet([[0xFFFFFFFF]])

    with pytest.raises(RuntimeError, match="without Aseprite metadata"):
        sheet.get_sprite("walk_right")


def test_sprite_sheet_rejects_missing_tags_and_dimension_mismatches() -> None:
    metadata = AsepriteMetadata.model_validate(make_aseprite_metadata())
    sheet = SpriteSheet([[0xFFFFFFFF] * 4 for _ in range(2)], metadata)

    with pytest.raises(KeyError, match="unknown sprite tag"):
        sheet.get_sprite("walk_left")
    with pytest.raises(ValueError, match="dimensions do not match"):
        SpriteSheet([[0xFFFFFFFF]], metadata)


def test_aseprite_metadata_validates_tag_ranges_and_frame_bounds() -> None:
    invalid_tag = make_aseprite_metadata()
    invalid_tag["meta"]["frameTags"][0]["to"] = 2
    with pytest.raises(ValueError, match="missing frame"):
        AsepriteMetadata.model_validate(invalid_tag)

    invalid_frame = make_aseprite_metadata()
    invalid_frame["frames"][0]["frame"]["x"] = 3
    with pytest.raises(ValueError, match="outside the spritesheet"):
        AsepriteMetadata.model_validate(invalid_frame)


def test_ghost_spritesheet_metadata_does_not_require_frame_filenames() -> None:
    asset_paths = (
        Path(__file__).parents[1]
        / "assets" / "BlinkySprite" / "blinkysheet.json",
        Path(__file__).parents[1]
        / "assets" / "InkySprite" / "inkysheet.json",
        Path(__file__).parents[1]
        / "assets" / "Clyde" / "clydesheet.json",
    )

    for metadata_path in asset_paths:
        metadata = AsepriteMetadata.model_validate_json(
            metadata_path.read_text(encoding="utf-8")
        )
        assert len(metadata.frames) == 36
        assert metadata.tag("right").frame_indices() == tuple(range(30, 36))


def test_pacman_aseprite_file_builds_a_timed_animation() -> None:
    metadata_path = (
        Path(__file__).parents[1]
        / "assets"
        / "PacManSprite"
        / "pacman-sprites.json"
    )
    metadata = AsepriteMetadata.model_validate_json(
        metadata_path.read_text(encoding="utf-8")
    )
    width, height = metadata.meta.size.as_tuple()
    sheet = SpriteSheet(
        [[0xFFFFFFFF] * width for _ in range(height)], metadata
    )

    animation = Animation(sheet.get_sprite("walk_right"))

    assert animation.framerate == 10
    assert animation.current_sprite.size == (32, 32)
    assert len(metadata.tag("walk_right").frame_indices()) == 3


def test_animation_uses_per_frame_durations_and_loops() -> None:
    frames = (
        SpriteFrame(Sprite((1, 1), [[0xFF000001]]), 100),
        SpriteFrame(Sprite((1, 1), [[0xFF000002]]), 200),
    )
    animation = Animation(frames)

    assert animation.framerate is None
    animation.update(0.1)
    assert animation.current_index == 1
    animation.update(0.19)
    assert animation.current_index == 1
    animation.update(0.01)
    assert animation.current_index == 0


def test_animation_supports_fixed_framerate_and_non_looping() -> None:
    sprites = (
        Sprite((1, 1), [[0xFF000001]]),
        Sprite((1, 1), [[0xFF000002]]),
    )
    animation = Animation(sprites, framerate=10, loop=False)

    assert animation.framerate == 10
    animation.update(0.2)
    assert animation.current_index == 1
    assert animation.finished
    animation.reset()
    assert animation.current_index == 0
    assert not animation.finished
    with pytest.raises(ValueError, match="delta_time must be finite"):
        animation.update(float("inf"))


def test_animation_handler_updates_and_draws_active_animation() -> None:
    sprite_a = Sprite((1, 1), [[0xFF000001]])
    sprite_b = Sprite((1, 1), [[0xFF000002]])
    handler = AnimationHandler(
        {"walk": Animation((sprite_a, sprite_b), framerate=10)}
    )

    class RecordingDisplay:
        width = 1593
        height = 896

        def __init__(self) -> None:
            self.drawn: list[tuple[int, int, int]] = []

        def draw_pixel(self, x: int, y: int, color: int) -> None:
            self.drawn.append((x, y, color))

    display = RecordingDisplay()
    handler.update(0.1)
    handler.draw(display, (10, 20))

    assert display.drawn == [(10, 20, 0xFF000002)]


def test_sprite_loader_reads_typed_json_metadata(tmp_path: Path) -> None:
    pixels = [[0xFF000001, 0xFF000002], [0xFF000003, 0xFF000004]]
    session = FakeMlx(
        make_pixel_buffer(pixels, 8, "little"), 2, 2, 8
    )
    metadata_path = tmp_path / "sprites.json"
    metadata_path.write_text(
        json.dumps({
            "frames": [{
                "filename": "single.png",
                "frame": {"x": 0, "y": 0, "w": 2, "h": 2},
                "rotated": False,
                "trimmed": False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": 2, "h": 2},
                "sourceSize": {"w": 2, "h": 2},
                "duration": 100,
            }],
            "meta": {
                "image": "sprites.png",
                "size": {"w": 2, "h": 2},
                "frameTags": [{
                    "name": "idle",
                    "from": 0,
                    "to": 0,
                    "direction": "forward",
                }],
            },
        }),
        encoding="utf-8",
    )

    sheet = SpriteLoader(
        Path("sprites.png"), session, "mlx", metadata_path
    ).load()

    assert sheet.metadata is not None
    assert sheet.metadata.meta.size.as_tuple() == (2, 2)
    assert sheet.get_sprite("idle")[0].sprite.pixels == tuple(
        tuple(row) for row in pixels
    )


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
