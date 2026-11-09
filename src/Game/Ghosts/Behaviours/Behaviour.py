from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...GameState import GameState
    from ...MapGeneration.MapGeneration import Map
    from ...Player import Player
    from ..Ghost import Ghost


class Behaviour(Enum):
    """Current decision or lifecycle mode of a ghost."""

    CHASE = 1
    FLEAT = 2
    DEAD = 3
    RECOVERY = 4


@dataclass(frozen=True)
class BehaviourContext:
    """World data needed by behavior strategies for one decision."""

    ghost: Ghost
    actual_map: Map
    player: Player | None = None
    game_state: GameState | None = None
    ghosts: Mapping[str, Ghost] | None = None


@dataclass(frozen=True)
class TargetPlan:
    """A pathfinding target and optional restrictions for the route."""

    target: tuple[int, int]
    allowed_cells: frozenset[tuple[int, int]] | None = None
    pathfinding: bool = True


@dataclass(frozen=True)
class MovementResult:
    """Result from a strategy with specialized movement semantics."""

    handled: bool = False
    next_behaviour: Behaviour | None = None


class GhostBehaviour(ABC):
    """Strategy interface for ghost target and movement policies."""

    def on_enter(self) -> None:
        """Reset any behavior-local state when this strategy becomes active."""

    def on_exit(self) -> None:
        """Release behavior-local state when this strategy is left."""

    @abstractmethod
    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        """Choose a target and any path constraints for this behavior."""

    def update_movement(
            self, context: BehaviourContext, delta_time: float
    ) -> MovementResult:
        """Return unhandled unless this behavior owns movement directly."""
        return MovementResult()
