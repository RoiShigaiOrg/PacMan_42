from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from typing import Dict, Tuple, cast

from Engine.Graphics import MlxDisplay
from Engine.Entity.Entity import Entity
from Engine.Entity.PathFinding import HeuristicType, PathFinding
from Engine.Physics.Collider import Collider
from Engine.Physics.Physics import PhysicsEngine
from Engine.Physics.Vector2 import Vector2
from ..BehaviourHandler.BehaviourHandler import BehaviourHandler
from ..GameState import GameState
from ..MapGeneration.MapNode import MapNode
from ..MapGeneration import Map
from ..Player import Player
from .Behaviours import (
    Behaviour,
    BehaviourContext,
    EatenBehaviour,
    FleatBehaviour,
    GhostBehaviour,
    MovementResult,
    PlayerChaseBehaviour,
    RecoveryBehaviour,
    TargetPlan,
)

COLLIDER_DEBUG_COLOR: int = 0xFFFFFFFF
COLLIDER_SIZE_RATIO: float = 0.8
DEFAULT_MOVEMENT_SPEED: float = 160.0
GRID_CENTER_TOLERANCE: float = 1e-6
FLEA_ROAM_RADIUS: int = 5


class Ghost(Entity):
    """Shared movement and path mechanics for the game's ghosts."""

    def __init__(
            self,
            movement_speed: float = DEFAULT_MOVEMENT_SPEED,
            chase_behaviour: GhostBehaviour | None = None,
    ) -> None:
        if movement_speed <= 0:
            raise ValueError("movement_speed must be positive")
        self._movement_speed = movement_speed
        self._origin: Tuple[int, int] = (0, 0)
        self._path: list[MapNode] = []
        self._path_index = 0
        self._target: Tuple[int, int] | None = None
        self._roam_territory: tuple[Tuple[int, int], ...] = ()
        strategies = {
            Behaviour.CHASE: chase_behaviour or PlayerChaseBehaviour(),
            Behaviour.FLEAT: FleatBehaviour(),
            Behaviour.DEAD: EatenBehaviour(),
            Behaviour.RECOVERY: RecoveryBehaviour(),
        }
        self._behaviour_handler = BehaviourHandler(strategies)

    @property
    def behaviour(self) -> Behaviour:
        """Return the current ghost behavior state."""
        return self._behaviour_handler.behaviour

    @property
    def behaviour_handler(self) -> BehaviourHandler:
        """Return this ghost's strategy dispatcher."""
        return self._behaviour_handler

    def change_behaviour(self, behaviour: Behaviour) -> None:
        """Change behavior and discard a path planned for the previous mode."""
        if self._behaviour_handler.change_behaviour(behaviour):
            self._clear_path()

    def synchronize_behaviour(self, context: BehaviourContext) -> None:
        """Align a living ghost's mode with Pac-Man's game state."""
        if self._behaviour_handler.synchronize(context):
            self._clear_path()

    def compute_target(self, context: BehaviourContext) -> TargetPlan:
        """Ask the active behavior strategy for a target and path policy."""
        self.synchronize_behaviour(context)
        return self._behaviour_handler.compute_target(context)

    def behaviour_context(
            self,
            player: Player | None,
            actual_map: Map,
            game_state: GameState | None = None,
            ghosts: Mapping[str, Ghost] | None = None,
    ) -> BehaviourContext:
        """Build the typed world context consumed by behavior strategies."""
        return BehaviourContext(
            self, actual_map, player, game_state, ghosts
        )

    def select_target(
            self,
            player: Player,
            actual_map: Map,
            game_state: GameState,
            ghosts: Mapping[str, Ghost] | None = None,
    ) -> Tuple[int, int]:
        """Convenience wrapper around strategy target selection."""
        context = self.behaviour_context(
            player, actual_map, game_state, ghosts
        )
        return self.compute_target(context).target

    @property
    def origin(self) -> Tuple[int, int]:
        """Return this ghost's home cell in map coordinates."""
        return self._origin

    @property
    def path_complete(self) -> bool:
        """Whether the current route has no remaining waypoints."""
        return self._path_index >= len(self._path)

    @property
    def roam_territory(self) -> tuple[Tuple[int, int], ...]:
        """Return the walkable cells assigned to this ghost for roaming."""
        return self._roam_territory

    def set_roam_territory(
            self, territory: Iterable[Tuple[int, int]]
    ) -> None:
        """Set the cells this ghost may roam while fleeing or recovering."""
        cells = tuple(sorted(set(territory)))
        if not cells:
            raise ValueError("A ghost's roam territory cannot be empty")
        if self.origin not in cells:
            raise ValueError(
                "A ghost's roam territory must include its origin"
            )
        self._roam_territory = cells

    @property
    def movement_speed(self) -> float:
        """Return movement speed in pixels per second."""
        return self._movement_speed

    @property
    def collider(self) -> Collider:
        """Return the collider that owns this ghost's world position."""
        return self._collider

    @property
    def size(self) -> Tuple[int, int]:
        """Return graphical dimensions used for dirty-region redraws."""
        return self._width, self._height

    def draw(self, display: MlxDisplay) -> None:
        """Draw the ghost and its debug collider."""
        self._graphical_shape.fill(display)
        self._collider.debug_draw(display, COLLIDER_DEBUG_COLOR)

    @abstractmethod
    def init_ghost(self, display: MlxDisplay, actual_map: Map) -> None:
        """Initialize this ghost's map position, shape, and collider."""
        ...

    def set_path(self, path: Sequence[MapNode]) -> None:
        """Set the cell-by-cell route consumed by :meth:`update_movement`."""
        nodes = list(path)
        for first, second in zip(nodes, nodes[1:]):
            column_distance = abs(
                first.coordinate[0] - second.coordinate[0]
            )
            row_distance = abs(first.coordinate[1] - second.coordinate[1])
            if column_distance + row_distance != 1:
                raise ValueError(
                    "Ghost paths must contain cardinally adjacent cells"
                )
        self._path = nodes
        self._path_index = 0

    def _clear_path(self) -> None:
        self._path = []
        self._path_index = 0
        self._target = None

    def update_movement(
            self,
            actual_map: Map,
            physics: PhysicsEngine,
            delta_time: float,
            game_state: GameState | None = None,
    ) -> None:
        """Update special behavior movement or follow the planned path."""
        if delta_time <= 0:
            return

        context = BehaviourContext(self, actual_map, game_state=game_state)
        previous_behaviour = self.behaviour
        if game_state is not None:
            self.synchronize_behaviour(context)
        movement: MovementResult = self._behaviour_handler.update_movement(
            context, delta_time
        )
        if self.behaviour is not previous_behaviour:
            self._clear_path()
        if movement.handled:
            return

        if self.path_complete:
            return

        remaining_distance = self._movement_speed * delta_time
        cell_width, cell_height = actual_map.cell_size
        max_step = min(cell_width, cell_height) / 2
        grid_origin_x, grid_origin_y = actual_map.grid_origin
        wall_colliders = actual_map.wall_colliders()

        while (
            remaining_distance > GRID_CENTER_TOLERANCE
            and not self.path_complete
        ):
            center = self._collider.world_position
            waypoint = self._path[self._path_index].coordinate
            target_column, target_row = waypoint
            if not actual_map.is_walkable_cell(target_column, target_row):
                return

            target = Vector2(
                grid_origin_x + (target_column + 0.5) * cell_width,
                grid_origin_y + (target_row + 0.5) * cell_height,
            )
            dx = target.x - center.x
            dy = target.y - center.y
            if (
                abs(dx) > GRID_CENTER_TOLERANCE
                and abs(dy) > GRID_CENTER_TOLERANCE
            ):
                raise ValueError(
                    "Ghost path changes direction away from a cell center"
                )

            distance = abs(dx) + abs(dy)
            if distance <= GRID_CENTER_TOLERANCE:
                self._path_index += 1
                continue

            step = min(remaining_distance, max_step, distance)
            if abs(dx) > GRID_CENTER_TOLERANCE:
                movement_vector = Vector2(step if dx > 0 else -step, 0.0)
            else:
                movement_vector = Vector2(0.0, step if dy > 0 else -step)

            if not self._can_move(movement_vector, physics, wall_colliders):
                return

            self._move(movement_vector)
            remaining_distance -= step
            if step >= distance:
                self._path_index += 1

    def compute_path(
            self,
            position: Tuple[int, int],
            target: Tuple[int, int],
            graph: Dict[Tuple[int, int], MapNode],
            allowed_cells: frozenset[Tuple[int, int]] | None = None,
            pathfinding: bool = True,
    ) -> None:
        """Plan a route, optionally restricted by the active strategy."""
        if not pathfinding:
            self.set_path(())
            self._target = target
            return

        target_node = graph.get(target)
        start_node: MapNode | None
        if self._path_index < len(self._path):
            start_node = self._path[self._path_index]
        else:
            start_node = graph.get(position)
        if start_node is None or target_node is None:
            self.set_path(())
            self._target = target
            return

        allowed_nodes = None
        if allowed_cells is not None:
            allowed_nodes = {
                graph[coordinate]
                for coordinate in allowed_cells
                if coordinate in graph
            }
        path = PathFinding.a_star(
            start_node,
            target_node,
            HeuristicType.MANHATTAN,
            allowed_nodes=allowed_nodes,
        )
        self.set_path(cast(list[MapNode], path))
        self._target = target
