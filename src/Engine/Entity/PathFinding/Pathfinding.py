from typing import List
import heapq


class PathFinding:

    @classmethod
    def A_star(
            start: Node,
            goal: Node,
            path_lenght: int | None = None) -> List[Node]:
        """ A_star Algorithm use for the Pathfinding of Any Entity Object of the Engine """
