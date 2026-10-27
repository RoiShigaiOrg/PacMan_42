from __future__ import annotations

from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.MapGeneration.MapNode import MapNode
from Engine.Entity.PathFinding import PathFinding


def make_map(grid: list[list[Cell]]) -> Map:
    """Create a Map with a controlled grid, bypassing random generation."""
    actual_map = Map.__new__(Map)
    actual_map.grid = grid
    return actual_map


def manhattan_distance(start: MapNode, goal: MapNode) -> float:
    return float(
        abs(start.coordinate[0] - goal.coordinate[0])
        + abs(start.coordinate[1] - goal.coordinate[1])
    )


def test_build_graph_creates_nodes_only_for_walkable_cells() -> None:
    actual_map = make_map([
        [Cell((0, 0), True), Cell((1, 0), False)],
        [Cell((0, 1), True), Cell((1, 1), True)],
    ])

    graph = actual_map.build_graph()

    assert set(graph) == {(0, 0), (0, 1), (1, 1)}
    assert all(isinstance(node, MapNode) for node in graph.values())


def test_build_graph_connects_cardinal_neighbors_in_both_directions() -> None:
    actual_map = make_map([
        [Cell((0, 0), True), Cell((1, 0), True)],
        [Cell((0, 1), True), Cell((1, 1), False)],
    ])

    graph = actual_map.build_graph()
    start_neighbors = {
        neighbor.coordinate: cost
        for neighbor, cost in graph[(0, 0)].neighbors()
    }

    assert start_neighbors == {(1, 0): 1.0, (0, 1): 1.0}
    assert graph[(1, 0)].neighbors() == ((graph[(0, 0)], 1.0),)
    assert graph[(0, 1)].neighbors() == ((graph[(0, 0)], 1.0),)


def test_a_star_finds_path_across_map_graph_around_wall() -> None:
    actual_map = make_map([
        [Cell((0, 0), True), Cell((1, 0), True), Cell((2, 0), False)],
        [Cell((0, 1), True), Cell((1, 1), True), Cell((2, 1), True)],
    ])
    graph = actual_map.build_graph()
    start = graph[(0, 0)]
    goal = graph[(2, 1)]

    path = PathFinding.a_star(start, goal, manhattan_distance)

    assert path[0] is start
    assert path[-1] is goal
    assert len(path) == 4
    assert all(node.coordinate != (2, 0) for node in path)
    for first, second in zip(path, path[1:]):
        assert any(
            neighbor is second
            for neighbor, _ in first.neighbors()
        )
