from Engine.Graphics import MlxDisplay
from Engine.Entity.Entity import Entity
from Engine.Entity.PathFinding import PathFinding
from Engine.Entity.PathFinding.Node import Node
from ..MapGeneration.MapNode import MapNode
from ..MapGeneration import Map
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List
from enum import Enum

COLLIDER_DEBUG_COLOR: int = 0xFFFF0000
COLLIDER_SIZE_RATIO: float = 0.8


class Behaviour(Enum):
    """ Behaviour Enum Class to indicate the Behaviour State of each Ghost """
    CHASE: int = 1,
    FLEAT: int = 2,
    DEAD: int = 3


class Ghost(ABC, Entity):
    """
    Ghost Class Definition

    Abstract Class to create the different Ghost with unified method
    """

    def draw(self, display: MlxDisplay) -> None:
        """ draw Method of the Player Class """
        self.__graphical_shape.fill(display)
        self.__collider.debug_draw(display, COLLIDER_DEBUG_COLOR)

    @abstractmethod
    def init_ghost(self, display: MlxDisplay, actual_map: Map) -> None:
        ...

    def compute_path(
            self,
            position: Tuple[int, int],
            target: Tuple[int, int],
            graph: Dict[Tuple[int, int], MapNode]) -> None:
        """ Compute the Path for the Ghost """
        if target == self._actual_target:
            return
        if self._behaviour == Behaviour.CHASE:
            target = self._chase(target)
        if self._behaviour == Behaviour.FLEAT:
            target = self._fleat(target)
        if self._behaviour == Behaviour.DEAD:
            target = self._DEAD(target)
        self._path: List[Node] = PathFinding.a_star(position, target)

    @abstractmethod
    def _chase(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Chase Behaviour abstract method for Ghost Class """
        ...

    @abstractmethod
    def _fleat(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Fleat Behaviour abstract method for Ghost Class """
        ...

    @abstractmethod
    def _dead(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Dead Behaviour abstract method for Ghost Class """
        ...
