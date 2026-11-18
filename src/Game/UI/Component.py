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

    @abstractmethod
    def update(self, input_handler: InputHandler) -> None:
        """ Update Abstract Method of the Component Object """
        ...

    @abstractmethod
    def render(self, display: MlxDisplay, pos: Tuple[int, int]) -> None:
        """ Render Abstract Method of the Component Object """
        ...

    def add_label(self, text: str) -> None:
        """ Add text Label to this Selector """
        self._label: str = text
