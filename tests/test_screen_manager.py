import pytest

from Engine.SceneManager import Scene, SceneManager
from Engine.InputHandler import InputHandler


class RecordingScene(Scene):
    def __init__(self, marker: str) -> None:
        self.marker = marker
        self.render_count = 0
        self.change_render = 0

    def render(self) -> None:
        self.render_count += 1

    def render_on_change(self) -> None:
        self.change_render += 1

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        print("update")


def test_empty_manager_has_no_active_scene() -> None:
    assert SceneManager().actual_screen is None


def test_first_scene_in_initial_mapping_is_active() -> None:
    first = RecordingScene("first")
    second = RecordingScene("second")

    manager = SceneManager({"first": first, "second": second})

    assert manager.actual_screen is first


def test_add_scene_registers_scenes_and_preserves_current_scene() -> None:
    first = RecordingScene("first")
    second = RecordingScene("second")
    manager = SceneManager({"first": first})

    manager.add_scene({"second": second})

    assert manager.actual_screen is first
    manager.change_screen("second")
    assert manager.actual_screen is second


def test_render_calls_active_scene() -> None:
    scene = RecordingScene("scene")
    manager = SceneManager({"scene": scene})

    manager.render()
    manager.render()

    assert scene.render_count == 2


def test_change_screen_selects_registered_scene() -> None:
    first = RecordingScene("first")
    second = RecordingScene("second")
    manager = SceneManager({"first": first, "second": second})

    manager.change_screen("second")
    manager.render()

    assert manager.actual_screen is second
    assert first.render_count == 0
    assert second.render_count == 1


def test_render_without_a_scene_fails() -> None:
    with pytest.raises(RuntimeError, match="no active screen"):
        SceneManager().render()


def test_change_to_unknown_scene_fails() -> None:
    with pytest.raises(ValueError, match="missing"):
        SceneManager().change_screen("missing")


def test_update_is_available_without_affecting_rendering() -> None:
    scene = RecordingScene("scene")
    manager = SceneManager({"scene": scene})

    assert manager.update(0.016) is None
    assert scene.render_count == 0
