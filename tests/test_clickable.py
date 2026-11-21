from dataclasses import dataclass

import pytest

from Game.UI.Clickable import Clickable


@dataclass(frozen=True)
class Pixel:
    x: int
    y: int
    color: int


class RecordingDisplay:
    width = 1000
    height = 600

    def __init__(self) -> None:
        self.pixels: list[Pixel] = []
        self.text: list[tuple[int, int, int, str]] = []

    def relative_width(self, value: float) -> int:
        return int(self.width * value)

    def relative_height(self, value: float) -> int:
        return int(self.height * value)

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        self.pixels.append(Pixel(x, y, color))

    def write_text(self, x: int, y: int, color: int, text: str) -> None:
        self.text.append((x, y, color, text))


@pytest.mark.parametrize(
    ("value", "color"),
    [
        (False, Clickable.DISABLED_COLOR),
        (True, Clickable.ENABLED_COLOR),
    ],
)
def test_clickable_draws_a_small_state_indicator(
    value: bool,
    color: int,
) -> None:
    display = RecordingDisplay()
    clickable = Clickable(0.9, 0.1, value)

    clickable.render(display, (300, 420))

    assert Pixel(976, 440, color) in display.pixels
    indicator_pixels = [
        pixel for pixel in display.pixels if pixel.color == color
    ]
    assert len(indicator_pixels) == 20 * 20


def test_component_label_can_be_drawn_after_display_presentation() -> None:
    display = RecordingDisplay()
    clickable = Clickable(0.9, 0.1)
    clickable.add_label("DEBUG MODE")

    clickable.render_label(display, (300, 420))

    assert display.text == [(300, 420, 0xFFFFFFFF, "DEBUG MODE")]


def test_clickable_callback_toggles_the_rendered_state() -> None:
    display = RecordingDisplay()
    clickable = Clickable(0.9, 0.1)

    clickable.callback()
    clickable.render(display, (300, 420))

    assert clickable.read_value() is True
    assert Pixel(976, 440, Clickable.ENABLED_COLOR) in display.pixels
