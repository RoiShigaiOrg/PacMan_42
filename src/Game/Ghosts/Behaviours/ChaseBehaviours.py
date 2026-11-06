from __future__ import annotations

from ...MapGeneration.MapGeneration import Map
from .Behaviour import BehaviourContext, GhostBehaviour, TargetPlan
from .TerritoryRoamer import TerritoryRoamer


class ChaseBehaviour(GhostBehaviour):
    """Base class for the distinct chase policy of each ghost."""


class PlayerChaseBehaviour(ChaseBehaviour):
    """Simple default chase behavior for test or custom ghost subclasses."""

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        return TargetPlan(_player_cell(context))


def _player_cell(context: BehaviourContext) -> tuple[int, int]:
    if context.player is None:
        raise ValueError("Chase behavior requires a player")
    return context.actual_map.cell_coordinates_at(
        context.player.collider.world_position
    )


def _player_ahead_target(
        context: BehaviourContext,
) -> tuple[int, int]:
    if context.player is None:
        raise ValueError("Chase behavior requires a player")
    player_cell = _player_cell(context)
    direction = context.player.direction * 4.0
    target = (
        player_cell[0] + int(direction.x),
        player_cell[1] + int(direction.y),
    )
    return target if target in context.actual_map.graph else player_cell


class BlinkyChaseBehaviour(ChaseBehaviour):
    """Blinky targets Pac-Man's current cell."""

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        return TargetPlan(_player_cell(context))


class PinkyChaseBehaviour(ChaseBehaviour):
    """Pinky targets four cells ahead of Pac-Man's direction."""

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        return TargetPlan(_player_ahead_target(context))


class InkyChaseBehaviour(ChaseBehaviour):
    """Inky reflects its phase-one target across Blinky's position."""

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        target = _player_ahead_target(context)
        if context.ghosts is None or "blinky" not in context.ghosts:
            return TargetPlan(target)
        blinky_cell = context.actual_map.cell_coordinates_at(
            context.ghosts["blinky"].collider.world_position
        )
        return TargetPlan(
            self.retarget(target, blinky_cell, context.actual_map)
        )

    @staticmethod
    def retarget(
            target: tuple[int, int],
            blinky_position: tuple[int, int],
            actual_map: Map,
    ) -> tuple[int, int]:
        """Reflect a target around Blinky, clamping to a walkable cell."""
        reflected_target = (
            2 * target[0] - blinky_position[0],
            2 * target[1] - blinky_position[1],
        )
        if reflected_target in actual_map.graph:
            return reflected_target
        if not actual_map.graph:
            raise ValueError("Map has no walkable cells")
        return min(
            actual_map.graph,
            key=lambda cell: (
                (cell[0] - reflected_target[0]) ** 2
                + (cell[1] - reflected_target[1]) ** 2,
                cell[1],
                cell[0],
            ),
        )


class ClydeChaseBehaviour(ChaseBehaviour):
    """Clyde chases nearby Pac-Man and roams his territory at a distance."""

    def __init__(self, chase_threshold: int = 8) -> None:
        self._chase_threshold = chase_threshold
        self._roamer = TerritoryRoamer()

    def on_enter(self) -> None:
        self._roamer.reset()

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        ghost_cell = context.actual_map.cell_coordinates_at(
            context.ghost.collider.world_position
        )
        player_cell = _player_cell(context)
        distance = (
            abs(ghost_cell[0] - player_cell[0])
            + abs(ghost_cell[1] - player_cell[1])
        )
        if distance <= self._chase_threshold:
            return TargetPlan(player_cell)
        target, allowed_cells = self._roamer.target_plan(context, ghost_cell)
        return TargetPlan(target, allowed_cells)
