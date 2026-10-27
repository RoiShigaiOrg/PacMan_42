from __future__ import annotations

from collections.abc import Iterable

import pytest

from Engine.Entity.PathFinding import Node, PathFinding


class GraphNode(Node):
    """Small graph node used to exercise the generic A* implementation."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._neighbors: list[tuple[GraphNode, float]] = []

    def neighbors(self) -> Iterable[tuple[GraphNode, float]]:
        return tuple(self._neighbors)

    def connect(self, neighbor: GraphNode, cost: float) -> None:
        self._neighbors.append((neighbor, cost))


def zero_heuristic(_: Node, __: Node) -> float:
    return 0.0


def test_a_star_returns_the_lowest_cost_path() -> None:
    start = GraphNode("start")
    expensive = GraphNode("expensive")
    detour = GraphNode("detour")
    goal = GraphNode("goal")

    start.connect(expensive, 5.0)
    start.connect(detour, 1.0)
    detour.connect(expensive, 1.0)
    expensive.connect(goal, 1.0)
    detour.connect(goal, 10.0)

    path = PathFinding.a_star(start, goal, zero_heuristic)

    assert path == [start, detour, expensive, goal]


def test_a_star_returns_empty_path_when_goal_is_unreachable() -> None:
    start = GraphNode("start")
    goal = GraphNode("goal")

    assert PathFinding.a_star(start, goal, zero_heuristic) == []


def test_a_star_returns_single_node_when_start_is_goal() -> None:
    start_and_goal = GraphNode("start-and-goal")

    assert PathFinding.a_star(
        start_and_goal, start_and_goal, zero_heuristic
    ) == [start_and_goal]


def test_a_star_rejects_negative_edge_costs() -> None:
    start = GraphNode("start")
    goal = GraphNode("goal")
    start.connect(goal, -1.0)

    with pytest.raises(
        ValueError, match=r"A\* edge costs must be non-negative"
    ):
        PathFinding.a_star(start, goal, zero_heuristic)


def test_a_star_handles_equal_priority_nodes_without_comparing_nodes() -> None:
    start = GraphNode("start")
    first = GraphNode("first")
    second = GraphNode("second")
    goal = GraphNode("goal")

    start.connect(first, 1.0)
    start.connect(second, 1.0)
    first.connect(goal, 1.0)
    second.connect(goal, 1.0)

    path = PathFinding.a_star(start, goal, zero_heuristic)

    assert path in ([start, first, goal], [start, second, goal])
