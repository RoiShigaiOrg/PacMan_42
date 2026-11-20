from abc import ABC, abstractmethod
from typing import Protocol, Tuple

from ...InputHandler import InputHandler


Region = tuple[int, int, int, int]


class _DirtyRegionDisplay(Protocol):
    @property
    def width(self) -> int:
        ...

    @property
    def height(self) -> int:
        ...

    def restore_region(
            self,
            snapshot: bytes,
            x: int,
            y: int,
            width: int,
            height: int,
    ) -> None:
        ...


class Scene(ABC):
    """
        Screen Abstract Class Definition

        This class is used to create different screen with their own behaviour
            and to be managed by the ScreenManager
    A screen only owns its rendering behavior. The manager owns the window,
    frame buffer, and frame lifecycle.
    """

    def __init__(self) -> None:
        """Initialize shared state for scenes that render dirty regions."""
        self.__dirty_regions: list[Region] = []

    @abstractmethod
    def render(self) -> None:
        """Render this screen into the shared MLX screen buffer."""
        ...

    @abstractmethod
    def render_on_change(self) -> None:
        """
            Render method called when scene Manager change the scene
            This method is used to optimize performance,
                avoiding to render background element/unchanged elements
                infinitely in the render loop method.
        """
        ...

    @abstractmethod
    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """Update this screen using the current frame's input state."""
        ...

    def movement_region(
            self,
            size: Tuple[int, int],
            pos: Tuple[int, int]) -> Region:
        """Return the rectangle occupied by the moving object."""
        return (pos[0], pos[1], size[0], size[1])

    @property
    def dirty_regions(self) -> tuple[Region, ...]:
        """Return the independent regions pending restoration and redraw."""
        return tuple(self.__dirty_regions)

    def mark_dirty(self, *regions: Region) -> None:
        """Record changed rectangles, merging only overlapping areas."""
        for region in regions:
            if region[2] <= 0 or region[3] <= 0:
                continue

            pending = region
            index = 0
            while index < len(self.__dirty_regions):
                existing = self.__dirty_regions[index]
                overlaps = (
                    pending[0] < existing[0] + existing[2]
                    and existing[0] < pending[0] + pending[2]
                    and pending[1] < existing[1] + existing[3]
                    and existing[1] < pending[1] + pending[3]
                )
                if not overlaps:
                    index += 1
                    continue

                pending = self.union_regions(pending, existing)
                self.__dirty_regions.pop(index)
                index = 0
            self.__dirty_regions.append(pending)

    def mark_full_screen_dirty(self, display: _DirtyRegionDisplay) -> None:
        """Invalidate the complete display, for initialization or reset."""
        self.mark_dirty((0, 0, display.width, display.height))

    def restore_dirty_regions(
            self, display: _DirtyRegionDisplay, snapshot: bytes
    ) -> tuple[Region, ...]:
        """Restore and return every pending region without clearing them."""
        regions = self.dirty_regions
        for x, y, width, height in regions:
            display.restore_region(snapshot, x, y, width, height)
        return regions

    def clear_dirty_regions(self) -> None:
        """Clear invalidated regions after their contents have been redrawn."""
        self.__dirty_regions.clear()

    def union_regions(
            self,
            current: Region | None,
            *regions: Region,
    ) -> Region:
        """Return one region containing all supplied dirty regions."""
        all_regions = list(regions)
        if current is not None:
            all_regions.append(current)

        left = min(region[0] for region in all_regions)
        top = min(region[1] for region in all_regions)
        right = max(region[0] + region[2] for region in all_regions)
        bottom = max(region[1] + region[3] for region in all_regions)
        return left, top, right - left, bottom - top
