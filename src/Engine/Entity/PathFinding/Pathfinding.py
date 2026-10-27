from collections.abc import Callable
from enum import Enum
from math import hypot, inf
from typing import Dict, List, Tuple
from heapq import heappop, heappush
from itertools import count
from .Node import Node


Coordinate = tuple[float, float]
CoordinateGetter = Callable[[Node], Coordinate]


class HeuristicType(Enum):
    """Built-in heuristic choices for A* pathfinding."""

    MANHATTAN = "manhattan"
    EUCLIDEAN = "euclidean"
    DIJKSTRA = "dijkstra"


class PathFinding:

    @staticmethod
    def make_heuristic(
            heuristic_type: HeuristicType,
            coordinate_getter: CoordinateGetter | None = None,
    ) -> Callable[[Node, Node], float]:
        """Create a heuristic callable for the requested distance metric.

        Manhattan and Euclidean distance need coordinates on each node. By
        default, nodes are expected to expose a ``coordinate`` pair; callers
        using another node representation can provide ``coordinate_getter``.
        Dijkstra's algorithm uses a zero heuristic and needs no coordinates.
        """
        if heuristic_type is HeuristicType.DIJKSTRA:
            return lambda _node, _goal: 0.0

        if coordinate_getter is None:
            coordinate_getter = PathFinding._coordinate

        if heuristic_type is HeuristicType.MANHATTAN:
            return lambda node, goal: float(sum(
                abs(first - second)
                for first, second in zip(
                    coordinate_getter(node), coordinate_getter(goal)
                )
            ))

        if heuristic_type is HeuristicType.EUCLIDEAN:
            return lambda node, goal: hypot(
                coordinate_getter(node)[0] - coordinate_getter(goal)[0],
                coordinate_getter(node)[1] - coordinate_getter(goal)[1],
            )

        raise ValueError(f"Unsupported heuristic: {heuristic_type!r}")

    @staticmethod
    def _coordinate(node: Node) -> Coordinate:
        """Read a 2D ``coordinate`` attribute from a pathfinding node."""
        coordinate = getattr(node, "coordinate", None)
        if (
            not isinstance(coordinate, (tuple, list))
            or len(coordinate) != 2
        ):
            raise TypeError(
                "Built-in distance heuristics require nodes with a 2D "
                "coordinate, or an explicit coordinate_getter"
            )
        return float(coordinate[0]), float(coordinate[1])

    @staticmethod
    def a_star(
            start: Node,
            goal: Node,
            heuristic: (
                Callable[[Node, Node], float] | HeuristicType | None
            ) = None,
    ) -> List[Node]:
        """
        A_star Algorithm use for the Pathfinding of Any kind of action
            requiring to search through a graph.

        This Algorithm definition is meant to be highly versatil,
            the heuristic can be defined by the developper will
            as a Callable function.
        Node are any kind of Object derived by the Node abstract
            Class of the Engine.

        Return the lowest-cost path, or [] if no path exists.
        """
        if heuristic is None:
            estimate: Callable[[Node, Node], float] = (
                PathFinding.make_heuristic(HeuristicType.DIJKSTRA)
            )
        elif isinstance(heuristic, HeuristicType):
            estimate = PathFinding.make_heuristic(heuristic)
        else:
            estimate = heuristic

        sequence = count()
        frontier: List[Tuple[float, int, float, Node]] = []

        came_from: Dict[Node, Node] = {}
        g_score: Dict[Node, float] = {start: 0.0}

        heappush(
            frontier,
            (estimate(start, goal), next(sequence), 0.0, start),
        )

        while frontier:
            _, _, queued_cost, current = heappop(frontier)

            if queued_cost > g_score.get(current, inf):
                continue
            if current == goal:
                path = [goal]
                while path[-1] != start:
                    path.append(came_from[path[-1]])
                path.reverse()
                return path

            for neighbor, edge_cost in current.neighbors():
                if edge_cost < 0:
                    raise ValueError("A* edge costs must be non-negative")

                tentative_cost = queued_cost + edge_cost
                if tentative_cost >= g_score.get(neighbor, inf):
                    continue
                came_from[neighbor] = current
                g_score[neighbor] = tentative_cost

                priority = tentative_cost + estimate(neighbor, goal)
                heappush(
                        frontier,
                        (priority, next(sequence),
                         tentative_cost, neighbor)
                    )
        return []
