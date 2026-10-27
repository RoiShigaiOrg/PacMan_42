from __future__ import annotations

from collections.abc import Iterable

import pytest

from Engine.Entity.PathFinding import HeuristicType, Node, PathFinding


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


def test_a_star_defaults_to_dijkstra_when_no_heuristic_is_given() -> None:
    start = GraphNode("start")
    detour = GraphNode("detour")
    goal = GraphNode("goal")
    start.connect(goal, 5.0)
    start.connect(detour, 1.0)
    detour.connect(goal, 1.0)

    assert PathFinding.a_star(start, goal) == [start, detour, goal]


def test_builtin_heuristics_support_coordinate_extractors() -> None:
    first = GraphNode("first")
    second = GraphNode("second")
    coordinates = {
        first: (1.0, 2.0),
        second: (4.0, 6.0),
    }
    coordinate_getter = lambda node: coordinates[node]  # noqa: E731

    manhattan = PathFinding.make_heuristic(
        HeuristicType.MANHATTAN, coordinate_getter
    )
    euclidean = PathFinding.make_heuristic(
        HeuristicType.EUCLIDEAN, coordinate_getter
    )
    dijkstra = PathFinding.make_heuristic(HeuristicType.DIJKSTRA)

    assert manhattan(first, second) == 7.0
    assert euclidean(first, second) == pytest.approx(5.0)
    assert dijkstra(first, second) == 0.0


def test_a_star_accepts_a_builtin_heuristic_type() -> None:
    start = GraphNode("start")
    goal = GraphNode("goal")
    start.coordinate = (0, 0)
    goal.coordinate = (2, 3)
    start.connect(goal, 1.0)

    assert PathFinding.a_star(
        start, goal, HeuristicType.MANHATTAN
    ) == [start, goal]


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
