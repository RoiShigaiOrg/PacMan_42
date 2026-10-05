from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.Engine.Graphics import MlxWindow
else:
    try:
        from ...Engine.Graphics import MlxWindow
    except ImportError:
        from Engine.Graphics import MlxWindow


class Screen(ABC):
    """
        Screen Abstract Class Definition

        This class is used to create different screen with their own behaviour
            and to be managed by the ScreenManager
    A screen only owns its rendering behavior. The manager owns the window,
    frame buffer, and frame lifecycle.
    """

    @abstractmethod
    def render(self, screen: MlxWindow) -> None:
        """Render this screen into the shared MLX screen buffer."""
        ...
