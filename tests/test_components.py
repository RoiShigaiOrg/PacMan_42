from dataclasses import dataclass

import pytest

from Engine.Graphics import (
    Circle,
    Line,
    Rect,
    TextBox,
    TEXT_CENTER,
    TEXT_END,
    TEXT_START_HIGH,
)


@dataclass(frozen=True)
class Pixel:
    x: int
    y: int
    color: int


class RecordingDisplay:
    def __init__(self) -> None:
        self.pixels: list[Pixel] = []
        self.text: list[tuple[int, int, int, str]] = []

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        self.pixels.append(Pixel(x, y, color))

    def write_text(self, x: int, y: int, color: int, text: str) -> None:
        self.text.append((x, y, color, text))


def test_text_box_draws_and_updates_text_and_color() -> None:
    display = RecordingDisplay()
    text_box = TextBox("Hi", 0xFFFFFFFF)

    text_box.draw(display, 3, 4)
    text_box.update_text("Bye")
    text_box.update_color(0xFF00FF00)
    text_box.draw(display, 5, 6)

    assert display.text == [
        (3, 4, 0xFFFFFFFF, "Hi"),
        (5, 6, 0xFF00FF00, "Bye"),
    ]
    assert text_box.text_size == (24, 16)


def test_rect_draws_centered_linked_text() -> None:
    display = RecordingDisplay()
    rect = Rect(100, 50, 0, 0, 0xFF000000)
    rect.add_text(TextBox("Hi", 0xFFFFFFFF), TEXT_CENTER)

    rect.draw(display)

    assert display.text == [(42, 17, 0xFFFFFFFF, "Hi")]


def test_circle_draws_linked_text_at_its_center() -> None:
    display = RecordingDisplay()
    circle = Circle(20, 10, 40, 25, 0xFF000000)
    circle.add_text(TextBox("Hi", 0xFFFFFFFF))

    circle.draw(display)

    assert display.text == [(42, 22, 0xFFFFFFFF, "Hi")]


def test_line_draws_text_from_start_and_above_line() -> None:
    display = RecordingDisplay()
    line = Line((0, 0), (100, 0), 10, 20, 0xFF000000)
    line.add_text(TextBox("Hi", 0xFFFFFFFF), TEXT_START_HIGH)

    line.draw(display)

    assert display.text == [(10, 15, 0xFFFFFFFF, "Hi")]


def test_line_end_justification_uses_line_endpoint() -> None:
    display = RecordingDisplay()
    line = Line((0, 0), (100, 0), 10, 20, 0xFF000000)
    line.add_text(TextBox("Hi", 0xFFFFFFFF), TEXT_END)

    line.draw(display)

    assert display.text == [(94, 20, 0xFFFFFFFF, "Hi")]


def test_rect_draws_all_pixels_at_position() -> None:
    display = RecordingDisplay()

    Rect(3, 2, 4, 5, 0xFF112233).draw(display)

    assert display.pixels == [
        Pixel(4, 5, 0xFF112233),
        Pixel(5, 5, 0xFF112233),
        Pixel(6, 5, 0xFF112233),
        Pixel(4, 6, 0xFF112233),
        Pixel(5, 6, 0xFF112233),
        Pixel(6, 6, 0xFF112233),
    ]


def test_rect_updates_size_and_color() -> None:
    display = RecordingDisplay()
    rect = Rect(1, 1, 0, 0, 0xFF000000)

    rect.update_size(2, 1)
    rect.update_color(0xFFFFFFFF)
    rect.draw(display)

    assert display.pixels == [Pixel(0, 0, 0xFFFFFFFF), Pixel(1, 0, 0xFFFFFFFF)]


def test_rect_rejects_invalid_updates() -> None:
    rect = Rect(1, 1, 0, 0, 0)

    with pytest.raises(ValueError):
        rect.update_size(-1, 1)
    with pytest.raises(ValueError):
        rect.update_color(-1)


@pytest.mark.parametrize("dimensions", [(0, 1, 0, 0), (-1, 1, 0, 0), (1, 0, 0, 0)])
def test_rect_rejects_non_positive_dimensions(
    dimensions: tuple[int, int],
) -> None:
    with pytest.raises(ValueError):
        Rect(*dimensions, 0xFFFFFFFF)


def test_circle_draws_a_circumference_from_top_left_position() -> None:
    display = RecordingDisplay()

    circle = Circle(7, 5, 7, 8, 0xFF123456)
    circle.draw(display)

    assert circle.pos == (7, 8)
    assert circle.size == (7, 5)
    assert len(display.pixels) == 500
    assert Pixel(13, 10, 0xFF123456) in display.pixels
    assert Pixel(10, 12, 0xFF123456) in display.pixels
    assert all(pixel.color == 0xFF123456 for pixel in display.pixels)


def test_circle_fill_draws_only_pixels_inside_ellipse() -> None:
    display = RecordingDisplay()

    Circle(5, 3, 3, 4, 0xFFABCDEF).fill(display)

    assert Pixel(5, 5, 0xFFABCDEF) in display.pixels
    assert Pixel(3, 5, 0xFFABCDEF) in display.pixels
    assert Pixel(5, 4, 0xFFABCDEF) in display.pixels
    assert Pixel(3, 4, 0xFFABCDEF) not in display.pixels
    assert all(3 <= pixel.x <= 7 and 4 <= pixel.y <= 6 for pixel in display.pixels)


def test_circle_updates_size_and_color() -> None:
    display = RecordingDisplay()
    circle = Circle(1, 1, 0, 0, 0xFF000000)

    circle.update_size((5, 5))
    circle.update_color(0xFFFFFFFF)
    circle.fill(display)

    assert Pixel(3, 3, 0xFFFFFFFF) in display.pixels


def test_circle_rejects_invalid_updates() -> None:
    circle = Circle(1, 1, 0, 0, 0)

    with pytest.raises(ValueError):
        circle.update_size((0, 1))
    with pytest.raises(ValueError):
        circle.update_color(0x100000000)


def test_line_draws_endpoints_and_applies_position() -> None:
    display = RecordingDisplay()

    line = Line((1, 2), (4, 3), 10, 20, 0xFF00FF00)
    line.draw(display)

    assert line.pos == (10, 20)
    assert line.size == (3, 1)
    assert display.pixels[0] == Pixel(10, 20, 0xFF00FF00)
    assert display.pixels[-1] == Pixel(13, 21, 0xFF00FF00)
    assert len(display.pixels) == 4


def test_line_handles_steep_reversed_endpoints() -> None:
    display = RecordingDisplay()

    Line((7, 9), (3, 1), 0, 0, 0xFFFFFFFF).draw(display)

    assert display.pixels[0] == Pixel(4, 8, 0xFFFFFFFF)
    assert display.pixels[-1] == Pixel(0, 0, 0xFFFFFFFF)
    assert len(display.pixels) == 9


@pytest.mark.parametrize(
    "component",
    [
        lambda: Rect(1, 1, 0, 0, -1),
        lambda: Circle(1, 1, 0, 0, 0x100000000),
        lambda: Line((0, 0), (1, 1), 0, 0, -1),
    ],
)
def test_components_reject_invalid_colors(component: object) -> None:
    with pytest.raises(ValueError):
        component()  # type: ignore[operator]
