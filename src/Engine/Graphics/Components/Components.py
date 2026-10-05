from abc import abstractmethod, ABC


class Components(ABC):
    """
        Components Class Definition

        The component Class is the base model of any components
            available by this wrapper. (Rect, Line, TextBox...)
    """

    @abstractmethod
    def _draw(self, pos_x: int, pos_y: int) -> None:
        """ Main method to draw the component """
        ...
