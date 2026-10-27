from abc import ABC, abstractmethod
from typing import Iterable, TypeVar, Tuple


NodeType = TypeVar("NodeType", bound="Node")


class Node(ABC):
    """
    Node Abstract Class Definition

    This Node class can construct a graph for pathfinding or other graph
    algorithms.
    """

    @abstractmethod
    def neighbors(self: NodeType) -> Iterable[Tuple[NodeType, float]]:
        """ Return (neighbor, traversal_cost) pairs. """
        ...
