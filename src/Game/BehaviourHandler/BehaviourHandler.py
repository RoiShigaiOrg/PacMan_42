from __future__ import annotations

from collections.abc import Mapping

from ..GameState import PacManState
from ..Ghosts.Behaviours.Behaviour import (
    Behaviour,
    BehaviourContext,
    GhostBehaviour,
    MovementResult,
    TargetPlan,
)


class BehaviourHandler:
    """Select and delegate to an entity's current behavior strategy.

    Strategies are supplied by the owning entity, so each ghost can have its
    own chase strategy and independent state such as a selected roam target.
    Timed transitions use the game's frame delta, never wall-clock time.
    """

    def __init__(
            self,
            behaviours: Mapping[Behaviour, GhostBehaviour],
            initial_behaviour: Behaviour = Behaviour.CHASE,
    ) -> None:
        self._behaviours = dict(behaviours)
        missing = set(Behaviour) - self._behaviours.keys()
        if missing:
            names = ", ".join(behaviour.name for behaviour in missing)
            raise ValueError(f"Missing behavior strategies: {names}")
        self._behaviour = initial_behaviour
        self._behaviours[self._behaviour].on_enter()

    @property
    def behaviour(self) -> Behaviour:
        """Return the selected behavior state."""
        return self._behaviour

    @property
    def active_behaviour(self) -> GhostBehaviour:
        """Return the strategy currently handling this entity."""
        return self._behaviours[self._behaviour]

    def change_behaviour(self, behaviour: Behaviour) -> bool:
        """Switch strategies and report whether a transition occurred."""
        if not isinstance(behaviour, Behaviour):
            raise TypeError("behaviour must be a Behaviour")
        if behaviour is self._behaviour:
            return False
        self._behaviours[self._behaviour].on_exit()
        self._behaviour = behaviour
        self._behaviours[self._behaviour].on_enter()
        return True

    def synchronize(self, context: BehaviourContext) -> bool:
        """Select the living ghost mode implied by Pac-Man's current state.

        Eaten ghosts retain their independent return-and-wait lifecycle.
        """
        if self._behaviour is Behaviour.DEAD:
            return False
        if context.game_state is None:
            return False
        if context.game_state.state is PacManState.DEAD:
            desired = Behaviour.RECOVERY
        elif context.game_state.state is PacManState.SUPER:
            desired = Behaviour.FLEAT
        else:
            desired = Behaviour.CHASE
        return self.change_behaviour(desired)

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        """Delegate target selection to the active behavior strategy."""
        return self.active_behaviour.compute_target(context)

    def update_movement(
            self, context: BehaviourContext, delta_time: float
    ) -> MovementResult:
        """Let special strategies handle movement when required."""
        result = self.active_behaviour.update_movement(context, delta_time)
        if result.next_behaviour is not None:
            self.change_behaviour(result.next_behaviour)
        return result
