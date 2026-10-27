from abc import ABC, abstractmethod
from typing import Iterable, TypeVar, Tuple


NodeType = TypeVar("NodeType", bound="Node")


class Node(ABC):
    """
    Node Abstract Class Definition

    This Node Class is meant to be use to construct a Graph for the Pathfinding algorithm or any else algorithm requiring a Graph.
    """

    @abstractmethod
    def neighbors(self: NodeType) -> Iterable[Tuple[NodeType, float]]:
        """ Return (neighbor, traversal_cost) pairs. """
        ...
