from typing import Protocol

from ..InputHandler import InputHandler


class Application(Protocol):
    """
        Application Class Definition

        The Application Class is a template representing
            what should be a GameClass / Project that can
            be run by the engine.

        The philosophy of this is to separate the engine that run
            the game from the game being run by the engine.
    """

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """
            Update method of the Application

            This method is used to update the current scene
                of the SceneManager class within a delta time
                to maintain a stable frame generation and display (FPS)
        """
        ...

    def render(self) -> None:
        """
            Render method to render the actual frame in the window
        """
        ...
