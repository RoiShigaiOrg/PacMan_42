from abc import abstractmethod, ABC
from typing import Any


class Components(ABC):
    """
        Components Class Definition

        The component Class is the base model of any components
            available by this wrapper. (Rect, Line, TextBox...)
    """

    @abstractmethod
    def draw(self, display: Any, pos_x: int, pos_y: int) -> None:
        """ Main method to draw the component """
        ...
