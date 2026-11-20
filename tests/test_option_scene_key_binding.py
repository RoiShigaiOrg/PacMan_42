from Engine.InputHandler.KeyCode import KEY_ENTER, KEY_ESC
from Game.Scenes.OptionScene import OptionScene


class FakeDisplay:
    width = 1000
    height = 800

    def __init__(self) -> None:
        self.render_calls = 0
        self.snapshot_calls = 0
        self.restored_regions: list[tuple[int, int, int, int]] = []
        self.filled_regions: list[tuple[int, int, int, int, int]] = []
        self.text: list[str] = []

    def relative_width(self, value: float) -> int:
        return int(1000 * value)

    def relative_height(self, value: float) -> int:
        return int(800 * value)

    def clear_window(self) -> None:
        pass

    def clear(self, _color: int) -> None:
        pass

    def draw_pixel(self, _x: int, _y: int, _color: int) -> None:
        pass

    def fill_rect(
            self, x: int, y: int, width: int, height: int, color: int
    ) -> None:
        self.filled_regions.append((x, y, width, height, color))

    def snapshot(self) -> bytes:
        self.snapshot_calls += 1
        return b"static option layer"

    def restore_region(
            self,
            _snapshot: bytes,
            x: int,
            y: int,
            width: int,
            height: int,
    ) -> None:
        self.restored_regions.append((x, y, width, height))

    def render(self) -> None:
        self.render_calls += 1

    def write_text(
            self, _x: int, _y: int, _color: int, text: str
    ) -> None:
        self.text.append(text)


class FakeSceneManager:
    def __init__(self) -> None:
        self.last_scene_calls = 0

    def last_scene(self) -> None:
        self.last_scene_calls += 1


class FakeEngine:
    def __init__(self) -> None:
        self.config: dict[str, object] = {
            "dimension": [1920, 1080],
            "available_dimension": {
                "720": [1280, 720],
                "1080": [1920, 1080],
            },
            "UP": ord("z"),
            "DOWN": ord("s"),
            "LEFT": ord("q"),
            "RIGHT": ord("d"),
            "debug": False,
        }
        self.scene_manager = FakeSceneManager()
        self.updated_keys: list[tuple[str, object]] = []
        self.applied_resolutions: list[tuple[int, int]] = []

    def get_config_key(self, key: str) -> object:
        return self.config[key]

    def set_config_key(self, key: str, value: object) -> None:
        self.config[key] = value
        self.updated_keys.append((key, value))

    def apply_resolution(self, size: tuple[int, int]) -> None:
        if list(size) == self.config["dimension"]:
            return
        self.applied_resolutions.append(size)
        self.config["dimension"] = list(size)


class FakeInput:
    def __init__(self, key: int | None = None) -> None:
        self.last_key_pressed = key
        self._pressed = {key} if key is not None else set()

    def was_key_pressed(self, key: int) -> bool:
        return key in self._pressed


def make_scene() -> tuple[OptionScene, FakeEngine]:
    engine = FakeEngine()
    return OptionScene(engine, FakeDisplay()), engine  # type: ignore[arg-type]


def test_enter_captures_and_saves_key_for_selected_movement_binding() -> None:
    scene, engine = make_scene()

    scene.update(0.0, FakeInput(ord("s")))  # Select MOVEMENT.
    scene.update(0.0, FakeInput(KEY_ENTER))  # Begin UP binding capture.
    scene.update(0.0, FakeInput(ord("i")))

    assert engine.config["UP"] == ord("i")
    assert engine.updated_keys == [("UP", ord("i"))]


def test_escape_cancels_capture_without_changing_the_binding() -> None:
    scene, engine = make_scene()

    scene.update(0.0, FakeInput(ord("s")))
    scene.update(0.0, FakeInput(KEY_ENTER))
    scene.update(0.0, FakeInput(KEY_ESC))

    assert engine.config["UP"] == ord("z")
    assert engine.updated_keys == []


def test_resolution_selection_is_pending_until_enter() -> None:
    scene, engine = make_scene()

    scene.update(0.0, FakeInput(ord("q")))

    assert engine.config["dimension"] == [1920, 1080]
    assert engine.applied_resolutions == []

    scene.update(0.0, FakeInput(KEY_ENTER))

    assert engine.config["dimension"] == [1280, 720]
    assert engine.applied_resolutions == [(1280, 720)]


def test_resolution_selection_applies_when_leaving_options() -> None:
    scene, engine = make_scene()
    scene.update(0.0, FakeInput(ord("q")))

    scene.on_exit()

    assert engine.config["dimension"] == [1280, 720]
    assert engine.applied_resolutions == [(1280, 720)]


def test_option_scene_blits_only_when_dirty_and_restores_bar_region() -> None:
    display = FakeDisplay()
    engine = FakeEngine()
    scene = OptionScene(engine, display)  # type: ignore[arg-type]

    scene.render_on_change()
    assert display.snapshot_calls == 1
    scene.render()
    assert display.render_calls == 1

    # No dirty regions means there is no repeated full-image blit.
    scene.render()
    assert display.render_calls == 1

    scene.update(0.0, FakeInput(ord("s")))  # Select MOVEMENT.
    scene.render()
    assert (210, 560, 580, 40) not in display.restored_regions
    assert (350, 320, 300, 40) in display.restored_regions
    assert (350, 360, 300, 40) in display.restored_regions

    scene.update(0.0, FakeInput(KEY_ENTER))
    scene.render()
    assert display.restored_regions[-1] == (210, 560, 580, 40)
    assert any("Set UP" in text for text in display.text)
    render_calls_while_capturing = display.render_calls

    # The stationary capture prompt remains visible without another blit.
    scene.render()
    assert display.render_calls == render_calls_while_capturing

    scene.update(0.0, FakeInput(ord("i")))
    scene.render()
    assert display.restored_regions[-1] == (210, 560, 580, 40)
    assert engine.config["UP"] == ord("i")
