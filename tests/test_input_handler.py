from typing import Any, Callable

from Engine.InputHandler import InputHandler


Callback = Callable[..., None]


class FakeMlx:
    def __init__(self) -> None:
        self.hooks: dict[int, Callback] = {}
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

    session.hooks[3](119, None)

    assert not handler.is_key_down(119)
    assert handler.was_key_released(119)


def test_close_requests_loop_exit() -> None:
    _, session = make_handler()

    session.hooks[33](None)

    assert session.loop_exit_calls == ["mlx"]
