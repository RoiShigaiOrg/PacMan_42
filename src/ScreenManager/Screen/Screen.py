from abc import ABC, abstractmethod

from Engine.Graphics import MlxScreen


class Screen(ABC):
    """
        Screen Abstract Class Definition

        This class is used to create different screen with their own behaviour
            and to be managed by the ScreenManager
    A screen only owns its rendering behavior. The manager owns the window,
    frame buffer, and frame lifecycle.
    """

    @abstractmethod
    def render(self, screen: MlxScreen) -> None:
        """Render this screen into the shared MLX screen buffer."""
        ...
