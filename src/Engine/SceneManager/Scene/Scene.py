from abc import ABC, abstractmethod
from typing import Tuple

from ...InputHandler import InputHandler


Region = tuple[int, int, int, int]


class Scene(ABC):
    """
        Screen Abstract Class Definition

        This class is used to create different screen with their own behaviour
            and to be managed by the ScreenManager
    A screen only owns its rendering behavior. The manager owns the window,
    frame buffer, and frame lifecycle.
    """

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

    def movement_region(self, size: Tuple[int, int], pos: Tuple[int, int]) -> Region:
        """Return the rectangle occupied by the moving object."""
        return (pos[0], pos[1], size[0], size[1])

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
