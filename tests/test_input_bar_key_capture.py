from Engine.InputHandler.KeyCode import KEY_UP
from Game.UI.InputBar import InputBar


class FakeInput:
    def __init__(self, last_key_pressed: int | None) -> None:
        self.last_key_pressed = last_key_pressed


def test_input_bar_captures_a_key_and_exposes_prompt_state() -> None:
    input_bar = InputBar(0.5, 0.1)
    input_bar.begin_key_capture("UP", ord("z"))

    assert input_bar.key_capture_active
    assert input_bar.capture_key(
        FakeInput(KEY_UP)  # type: ignore[arg-type]
    ) == KEY_UP
    assert input_bar.format_keycode(ord("z")) == "Z"
    assert input_bar.format_keycode(KEY_UP) == "UP ARROW"

    input_bar.end_key_capture()

    assert not input_bar.key_capture_active
    assert input_bar.capture_key(
        FakeInput(KEY_UP)  # type: ignore[arg-type]
    ) is None
