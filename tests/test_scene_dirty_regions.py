from Engine.InputHandler import InputHandler
from Engine.SceneManager.Scene.Scene import Scene


class DirtyRegionScene(Scene):
    def render(self) -> None:
        pass

    def render_on_change(self) -> None:
        pass

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        pass


class RecordingDisplay:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.restored: list[tuple[bytes, int, int, int, int]] = []

    def restore_region(
            self,
            snapshot: bytes,
            x: int,
            y: int,
            width: int,
            height: int,
    ) -> None:
        self.restored.append((snapshot, x, y, width, height))


def test_scene_merges_overlapping_regions_but_keeps_separate_areas() -> None:
    scene = DirtyRegionScene()

    scene.mark_dirty(
        (0, 0, 10, 10),
        (20, 0, 10, 10),
        (8, 0, 15, 10),
        (50, 50, 0, 10),
    )

    assert scene.dirty_regions == ((0, 0, 30, 10),)


def test_scene_keeps_disjoint_regions_separate() -> None:
    scene = DirtyRegionScene()

    scene.mark_dirty((0, 0, 10, 10), (20, 20, 10, 10))

    assert scene.dirty_regions == (
        (0, 0, 10, 10),
        (20, 20, 10, 10),
    )


def test_full_screen_invalidation_supersedes_existing_regions() -> None:
    scene = DirtyRegionScene()
    display = RecordingDisplay(80, 60)
    scene.mark_dirty((10, 10, 5, 5), (30, 20, 5, 5))

    scene.mark_full_screen_dirty(display)

    assert scene.dirty_regions == ((0, 0, 80, 60),)


def test_scene_restores_all_regions_and_clears_them_after_redraw() -> None:
    scene = DirtyRegionScene()
    display = RecordingDisplay(80, 60)
    snapshot = b"static layer"
    regions = ((0, 0, 10, 10), (30, 20, 5, 5))
    scene.mark_dirty(*regions)

    restored = scene.restore_dirty_regions(
        display, snapshot
    )

    assert restored == regions
    assert display.restored == [
        (snapshot, 0, 0, 10, 10),
        (snapshot, 30, 20, 5, 5),
    ]
    assert scene.dirty_regions == regions

    scene.clear_dirty_regions()

    assert scene.dirty_regions == ()
