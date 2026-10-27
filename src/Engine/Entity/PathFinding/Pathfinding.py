from typing import List, Callable, Tuple, Dict
from heapq import heappop, heappush
from itertools import count
from math import inf
from .Node import Node


class PathFinding:

    @staticmethod
    def a_star(
            start: Node,
            goal: Node,
            heuristic: Callable[[Node, Node], float]) -> List[Node]:
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
        sequence = count()
        frontier: List[Tuple[float, int, float, Node]] = []

        came_from: Dict[Node, Node] = {}
        g_score: Dict[Node, float] = {start: 0.0}

        heappush(
            frontier,
            (heuristic(start, goal), next(sequence), 0.0, start),
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

                priority = tentative_cost + heuristic(neighbor, goal)
                heappush(
                        frontier,
                        (priority, next(sequence),
                         tentative_cost, neighbor)
                    )
        return []
