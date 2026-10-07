from typing import Any

from Engine.Graphics.Components.Line import Line


class RecordingDisplay:
    def __init__(self) -> None:
        self.pixels: list[tuple[int, int, int]] = []

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        self.pixels.append((x, y, color))


def draw_line(
    start: tuple[int, int],
    end: tuple[int, int],
    pos: tuple[int, int] = (0, 0),
) -> RecordingDisplay:
    display = RecordingDisplay()
    Line(start, end, 0xFFFFFFFF).draw(display, *pos)
    return display


def test_line_draws_both_endpoints_and_changes_y() -> None:
    display = draw_line((2, 2), (8, 5))

    assert display.pixels[0] == (2, 2, 0xFFFFFFFF)
    assert display.pixels[-1] == (8, 5, 0xFFFFFFFF)
    assert len({y for _, y, _ in display.pixels}) > 1


def test_line_handles_steep_and_reversed_endpoints() -> None:
    display = draw_line((7, 9), (3, 1))

    assert display.pixels[0] == (7, 9, 0xFFFFFFFF)
    assert display.pixels[-1] == (3, 1, 0xFFFFFFFF)
    assert len(display.pixels) == 9


def test_line_applies_draw_position_to_both_endpoints() -> None:
    display = draw_line((1, 2), (4, 3), (10, 20))

    assert display.pixels[0] == (11, 22, 0xFFFFFFFF)
    assert display.pixels[-1] == (14, 23, 0xFFFFFFFF)
