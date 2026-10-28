from collections.abc import Iterable
from Engine.Entity.PathFinding.Node import Node
from typing import Tuple, List


class MapNode(Node):
    """
        MapNode Class Definition

        MapNode are the Node representation of a Cell in the Map object.
        It is derived from the Node Abstract Class from the Engine
            and it is meant to be use for the PathFinding algorithm
            for the AI(Ghost).
    """

    def __init__(self, coordinate: Tuple[int, int]) -> None:
        """ Init Method of the MapNode """
        self.coordinate = coordinate
        self._neighbors: List[Tuple[MapNode, float]] = []

    def neighbors(self) -> Iterable[Tuple["MapNode", float]]:
        """ Return the neighbors of  this Node """
        return tuple(self._neighbors)

    def connect(self, neighbor: "MapNode", cost: float = 1.0) -> None:
        """ Add a neighbor Node to this MapNode """
        self._neighbors.append((neighbor, cost))

    def __repr__(self):
        return f"{self.coordinate}"
