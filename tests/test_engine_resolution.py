from typing import Any

import pytest

from Engine.Engine import Engine


class FakeWindow:
    def __init__(self, size: tuple[int, int]) -> None:
        self.current_size = size
        self.recreated: list[tuple[int, int]] = []
        self.fail = False

    def size(self) -> tuple[int, int]:
        return self.current_size

    def recreate(self, size: tuple[int, int], attach: Any) -> None:
        if self.fail:
            raise RuntimeError("window replacement failed")
        attach("replacement-window")
        self.current_size = size
        self.recreated.append(size)


class FakeInputHandler:
    def __init__(self) -> None:
        self.attached: list[Any] = []

    def attach_window(self, window: Any) -> None:
        self.attached.append(window)


class FakeSceneManager:
    def __init__(self) -> None:
        self.resolution_changes = 0

    def resolution_changed(self) -> None:
        self.resolution_changes += 1


def make_engine() -> tuple[Engine, FakeWindow, FakeInputHandler,
                           FakeSceneManager]:
    engine = Engine.__new__(Engine)
    window = FakeWindow((1920, 1080))
    input_handler = FakeInputHandler()
    scene_manager = FakeSceneManager()
    engine._window = window  # type: ignore[assignment]
    engine._input_handler = input_handler  # type: ignore[assignment]
    engine.scene_manager = scene_manager  # type: ignore[assignment]
    engine._Engine__config = {
        "dimension": [1920, 1080],
        "available_dimension": {
            "720": [1280, 720],
            "1080": [1920, 1080],
        },
    }
    return engine, window, input_handler, scene_manager


def test_apply_resolution_recreates_window_then_updates_config_and_scenes() -> None:
    engine, window, input_handler, scene_manager = make_engine()

    engine.apply_resolution((1280, 720))

    assert window.recreated == [(1280, 720)]
    assert input_handler.attached == ["replacement-window"]
    assert engine.get_config_key("dimension") == [1280, 720]
    assert scene_manager.resolution_changes == 1


def test_failed_window_replacement_keeps_config_and_scenes_unchanged() -> None:
    engine, window, input_handler, scene_manager = make_engine()
    window.fail = True

    with pytest.raises(RuntimeError, match="window replacement failed"):
        engine.apply_resolution((1280, 720))

    assert engine.get_config_key("dimension") == [1920, 1080]
    assert input_handler.attached == []
    assert scene_manager.resolution_changes == 0


def test_apply_resolution_rejects_a_size_not_in_available_dimensions() -> None:
    engine, window, input_handler, scene_manager = make_engine()

    with pytest.raises(ValueError, match="unsupported resolution"):
        engine.apply_resolution((800, 600))

    assert window.recreated == []
    assert input_handler.attached == []
    assert scene_manager.resolution_changes == 0
