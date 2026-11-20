from typing import Any, Callable

from Engine.InputHandler import InputHandler


Callback = Callable[..., None]


class FakeMlx:
    def __init__(self) -> None:
        self.hooks: dict[int, Callback] = {}
        self.registered_windows: list[Any] = []
        self.loop_exit_calls: list[Any] = []

    def mlx_hook(
            self,
            window: Any,
            event: int,
            mask: int,
            callback: Callback,
            param: object,
    ) -> None:
        self.hooks[event] = callback
        self.registered_windows.append(window)

    def mlx_loop_exit(self, mlx_ptr: Any) -> None:
        self.loop_exit_calls.append(mlx_ptr)


def make_handler() -> tuple[InputHandler, FakeMlx]:
    session = FakeMlx()
    handler = InputHandler(session, "mlx", "window")
    handler.register_hooks()
    return handler, session


def test_registers_keyboard_mouse_and_close_hooks() -> None:
    _, session = make_handler()

    assert set(session.hooks) == {2, 3, 4, 5, 6, 33}


def test_mouse_state_tracks_position_and_button_transitions() -> None:
    handler, session = make_handler()

    session.hooks[6](40, 50, None)
    session.hooks[4](1, 40, 50, None)

    assert handler.mouse_position == (40, 50)
    assert handler.is_mouse_button_down(1)
    assert handler.was_mouse_button_pressed(1)

    session.hooks[5](1, 40, 50, None)

    assert not handler.is_mouse_button_down(1)
    assert handler.was_mouse_button_released(1)

    handler.end_frame()

    assert not handler.was_mouse_button_pressed(1)
    assert not handler.was_mouse_button_released(1)


def test_key_state_tracks_held_keys_and_transitions() -> None:
    handler, session = make_handler()

    session.hooks[2](119, None)

    assert handler.is_key_down(119)
    assert handler.was_key_pressed(119)
    assert handler.last_key_pressed == 119

    session.hooks[3](119, None)

    assert not handler.is_key_down(119)
    assert handler.was_key_released(119)

    handler.end_frame()
    assert handler.last_key_pressed is None


def test_close_requests_loop_exit() -> None:
    _, session = make_handler()

    session.hooks[33](None)

    assert session.loop_exit_calls == ["mlx"]


def test_attach_window_rebinds_hooks_and_clears_previous_input_state() -> None:
    handler, session = make_handler()
    session.hooks[2](119, None)

    handler.attach_window("replacement")

    assert session.registered_windows[-6:] == ["replacement"] * 6
    assert not handler.is_key_down(119)
    assert not handler.was_key_pressed(119)
