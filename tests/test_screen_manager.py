from typing import Any

import pytest

from ScreenManager import ScreenManager
from ScreenManager.Screen import Screen


class FakeScreenBuffer:
    def __init__(self) -> None:
        self.operations: list[str] = []

    def clear(self) -> None:
        self.operations.append("clear")

    def screen_update(self) -> None:
        self.operations.append("update")


class RecordingScreen(Screen):
    def __init__(self, marker: str) -> None:
        self.marker = marker
        self.rendered_on: Any = None

    def render(self, screen: Any) -> None:
        self.rendered_on = screen


def test_first_registered_screen_becomes_active_and_renders() -> None:
    buffer = FakeScreenBuffer()
    scene = RecordingScreen("scene")
    manager = ScreenManager(buffer)  # type: ignore[arg-type]

    manager.add_screen("scene", scene)
    manager.render()

    assert manager.actual_screen is scene
    assert scene.rendered_on is buffer
    assert buffer.operations == ["clear", "update"]


def test_change_screen_renders_the_selected_screen() -> None:
    buffer = FakeScreenBuffer()
    first = RecordingScreen("first")
    second = RecordingScreen("second")
    manager = ScreenManager(buffer)  # type: ignore[arg-type]
    manager.add_screen("first", first)
    manager.add_screen("second", second)

    manager.change_screen("second")
    manager.render()

    assert manager.actual_screen is second
    assert first.rendered_on is None
    assert second.rendered_on is buffer


def test_render_without_a_screen_fails() -> None:
    manager = ScreenManager(FakeScreenBuffer())  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="no active screen"):
        manager.render()


def test_change_to_unknown_screen_fails() -> None:
    manager = ScreenManager(FakeScreenBuffer())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="missing"):
        manager.change_screen("missing")
