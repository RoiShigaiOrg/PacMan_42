from __future__ import annotations

from Engine.Physics.Vector2 import Vector2
from ...GameState import PacManState
from .Behaviour import (
    Behaviour,
    BehaviourContext,
    GhostBehaviour,
    MovementResult,
    TargetPlan,
)
from .TerritoryRoamer import TerritoryRoamer

FLEE_DISTANCE_THRESHOLD: int = 5
DEATH_MOVEMENT_SPEED: float = 140.0
RESPAWN_WAIT_DURATION: float = 3.0
GRID_CENTER_TOLERANCE: float = 1e-6


class FleatBehaviour(GhostBehaviour):
    """Flee nearby Pac-Man; otherwise roam inside the ghost's territory."""

    def __init__(self) -> None:
        self._roamer = TerritoryRoamer()

    def on_enter(self) -> None:
        self._roamer.reset()

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        if context.player is None:
            raise ValueError("Fleat behavior requires a player")
        actual_map = context.actual_map
        ghost_cell = actual_map.cell_coordinates_at(
            context.ghost.collider.world_position
        )
        player_cell = actual_map.cell_coordinates_at(
            context.player.collider.world_position
        )
        distance = (
            abs(ghost_cell[0] - player_cell[0])
            + abs(ghost_cell[1] - player_cell[1])
        )
        if distance > FLEE_DISTANCE_THRESHOLD:
            target, allowed_cells = self._roamer.target_plan(
                context, ghost_cell
            )
            return TargetPlan(target, allowed_cells)
        self._roamer.reset()
        return TargetPlan(self._flee_target(ghost_cell, player_cell, context))

    @staticmethod
    def _flee_target(
            ghost_cell: tuple[int, int],
            player_cell: tuple[int, int],
            context: BehaviourContext,
    ) -> tuple[int, int]:
        """Choose a reachable walkable cell away from Pac-Man."""
        start = context.actual_map.graph.get(ghost_cell)
        if start is None:
            return ghost_cell

        reachable: list[tuple[int, int]] = []
        visited = {start}
        pending = [start]
        while pending:
            node = pending.pop()
            reachable.append(node.coordinate)
            for neighbor, _cost in node.neighbors():
                if neighbor not in visited:
                    visited.add(neighbor)
                    pending.append(neighbor)

        direction_x = ghost_cell[0] - player_cell[0]
        direction_y = ghost_cell[1] - player_cell[1]
        if direction_x == 0 and direction_y == 0:
            return max(
                reachable,
                key=lambda cell: (
                    abs(cell[0] - player_cell[0])
                    + abs(cell[1] - player_cell[1]),
                    -cell[1],
                    -cell[0],
                ),
            )

        ideal_x = ghost_cell[0] + direction_x
        ideal_y = ghost_cell[1] + direction_y
        ideal_target = (ideal_x, ideal_y)
        if ideal_target in reachable:
            return ideal_target

        def away_score(
                cell: tuple[int, int],
        ) -> tuple[int, int, int, int, int, int]:
            offset_x = cell[0] - player_cell[0]
            offset_y = cell[1] - player_cell[1]
            projection = offset_x * direction_x + offset_y * direction_y
            cross_product = abs(
                offset_x * direction_y - offset_y * direction_x
            )
            player_distance = abs(offset_x) + abs(offset_y)
            ideal_distance = (
                abs(cell[0] - ideal_x) + abs(cell[1] - ideal_y)
            )
            return (
                projection,
                -cross_product,
                player_distance,
                -ideal_distance,
                -cell[1],
                -cell[0],
            )

        return max(reachable, key=away_score)


class RecoveryBehaviour(GhostBehaviour):
    """Return to the home territory, then roam there during Pac-Man's death."""

    def __init__(self) -> None:
        self._roamer = TerritoryRoamer()

    def on_enter(self) -> None:
        self._roamer.reset()

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        ghost_cell = context.actual_map.cell_coordinates_at(
            context.ghost.collider.world_position
        )
        target, allowed_cells = self._roamer.target_plan(context, ghost_cell)
        return TargetPlan(target, allowed_cells)


class EatenBehaviour(GhostBehaviour):
    """Return directly through walls, wait at home, then respawn."""

    def __init__(self, wait_duration: float = RESPAWN_WAIT_DURATION) -> None:
        self._wait_duration = wait_duration
        self._wait_remaining: float | None = None

    def on_enter(self) -> None:
        self._wait_remaining = None

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        return TargetPlan(context.ghost.origin, pathfinding=False)

    def update_movement(
            self, context: BehaviourContext, delta_time: float
    ) -> MovementResult:
        ghost = context.ghost
        actual_map = context.actual_map
        if delta_time <= 0:
            return MovementResult(handled=True)

        if self._wait_remaining is not None:
            self._wait_remaining -= delta_time
            if self._wait_remaining <= 0:
                game_state = context.game_state
                if (
                    game_state is not None
                    and game_state.state is PacManState.DEAD
                ):
                    next_behaviour = Behaviour.RECOVERY
                elif (
                    game_state is not None
                    and game_state.state is PacManState.SUPER
                ):
                    next_behaviour = Behaviour.FLEAT
                else:
                    next_behaviour = Behaviour.CHASE
                return MovementResult(
                    handled=True, next_behaviour=next_behaviour
                )
            return MovementResult(handled=True)

        cell_width, cell_height = actual_map.cell_size
        grid_origin_x, grid_origin_y = actual_map.grid_origin
        target = Vector2(
            grid_origin_x + (ghost.origin[0] + 0.5) * cell_width,
            grid_origin_y + (ghost.origin[1] + 0.5) * cell_height,
        )
        displacement = target - ghost.collider.world_position
        distance = displacement.length()
        if distance <= GRID_CENTER_TOLERANCE:
            self._wait_remaining = self._wait_duration
            return MovementResult(handled=True)

        step = min(DEATH_MOVEMENT_SPEED * delta_time, distance)
        ghost._move(displacement.normalized() * step)
        if step >= distance:
            self._wait_remaining = self._wait_duration
        return MovementResult(handled=True)
