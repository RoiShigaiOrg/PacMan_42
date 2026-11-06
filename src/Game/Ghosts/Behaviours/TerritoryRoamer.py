from __future__ import annotations

import random

from .Behaviour import BehaviourContext


class TerritoryRoamer:
    """Keep one roam destination until the ghost reaches it."""

    def __init__(self) -> None:
        self._target: tuple[int, int] | None = None

    def reset(self) -> None:
        self._target = None

    def target_plan(
            self,
            context: BehaviourContext,
            ghost_cell: tuple[int, int],
    ) -> tuple[tuple[int, int], frozenset[tuple[int, int]] | None]:
        territory = context.ghost.roam_territory
        if not territory:
            return context.ghost.origin, None

        if ghost_cell not in territory:
            self._target = context.ghost.origin
            return self._target, None

        if self._target is None or context.ghost.path_complete:
            candidates = tuple(
                cell for cell in territory if cell != ghost_cell
            )
            self._target = random.choice(candidates or territory)
        return self._target, frozenset(territory)
