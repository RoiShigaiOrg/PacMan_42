from Engine.Graphics import MlxDisplay
from ..MapGeneration import Map
from abc import ABC, abstractmethod

COLLIDER_DEBUG_COLOR: int = 0xFFFF0000
COLLIDER_SIZE_RATIO: float = 0.8


class Ghost(ABC):
    """
    Ghost Class Definition

    Abstract Class to create the different Ghost with unified method
    """

    def draw(self, display: MlxDisplay) -> None:
        """ draw Method of the Player Class """
        self.__graphical_shape.fill(display)
        self.__collider.debug_draw(display, COLLIDER_DEBUG_COLOR)

    @abstractmethod
    def Init_Ghost(self, display: MlxDisplay, actual_map: Map) -> None:
        ...
