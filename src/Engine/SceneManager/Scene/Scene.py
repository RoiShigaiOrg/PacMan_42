from abc import ABC, abstractmethod

from ...InputHandler import InputHandler


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
