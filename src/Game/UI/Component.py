from Engine import InputHandler
from Engine.Graphics import MlxDisplay
from abc import ABC, abstractmethod
from typing import Tuple


class Component(ABC):
    """ Component Abstract Class Definition

    A Component is an Abstract Class that serve to create different
        UI experience obect within the Game. Component make sure that
        the abstract method are complete for easier implementation
        within the Program.
    """

    _label: str | None = None

    @abstractmethod
    def update(self, input_handler: InputHandler) -> None:
        """ Update Abstract Method of the Component Object """
        ...

    @abstractmethod
    def render(self, display: MlxDisplay, pos: Tuple[int, int]) -> None:
        """ Render Abstract Method of the Component Object """
        ...

    @abstractmethod
    def callback(self) -> None:
        """Activate the component from the option scene."""
        ...

    def add_label(self, text: str) -> None:
        """ Add text Label to this Selector """
        self._label: str = text

    def render_label(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int]) -> None:
        """Draw the label after the display image has been presented."""
        if self._label:
            display.write_text(pos[0], pos[1], 0xFFFFFFFF, self._label)
