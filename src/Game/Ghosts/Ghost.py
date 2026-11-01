from collections.abc import Sequence
from Engine.Graphics import MlxDisplay
from Engine.Entity.Entity import Entity
from Engine.Entity.PathFinding import HeuristicType, PathFinding
from Engine.Physics.Collider import Collider
from Engine.Physics.Physics import PhysicsEngine
from Engine.Physics.Vector2 import Vector2
from ..GameState import GameState, PacManState
from ..MapGeneration.MapNode import MapNode
from ..MapGeneration import Map
from abc import abstractmethod
from typing import Dict, Tuple, cast
from enum import Enum

COLLIDER_DEBUG_COLOR: int = 0xFFFFFFFF
COLLIDER_SIZE_RATIO: float = 0.8
DEFAULT_MOVEMENT_SPEED: float = 160.0
DEATH_MOVEMENT_SPEED: float = 140.0
RESPAWN_WAIT_DURATION: float = 3.0
GRID_CENTER_TOLERANCE: float = 1e-6
FLEE_DISTANCE_THRESHOLD: int = 5


class Behaviour(Enum):
    """ Behaviour Enum Class to indicate the Behaviour State of each Ghost """
    CHASE = 1
    FLEAT = 2
    DEAD = 3


class Ghost(Entity):
    """
    Ghost Class Definition

    Abstract Class to create the different Ghost with unified method
    """

    def __init__(self, movement_speed: float = DEFAULT_MOVEMENT_SPEED) -> None:
        if movement_speed <= 0:
            raise ValueError("movement_speed must be positive")
        self._movement_speed = movement_speed
        self._origin: Tuple[int, int] = (0, 0)
        self._path: list[MapNode] = []
        self._path_index = 0
        self._target: Tuple[int, int] | None = None
        self._behaviour = Behaviour.CHASE
        self._respawn_wait_remaining: float | None = None

    @property
    def behaviour(self) -> Behaviour:
        """ Return the actual Ghost behaviour """
        return self._behaviour

    def change_behaviour(self, behaviour: Behaviour) -> None:
        """ Change the behaviour of the ghost to the given Behaviour Enum. """
        if not isinstance(behaviour, Behaviour):
            raise TypeError("behaviour must be a Behaviour")
        if behaviour is self._behaviour:
            return
        self._behaviour = behaviour
        self._path = []
        self._path_index = 0
        self._target = None
        self._respawn_wait_remaining = None

    @property
    def origin(self) -> Tuple[int, int]:
        """Return this ghost's home cell in map coordinates."""
        return self._origin

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
        """Return the graphical dimensions used for dirty-region redraws."""
        return self._width, self._height

    def draw(self, display: MlxDisplay) -> None:
        """Draw the ghost and its debug collider."""
        self._graphical_shape.fill(display)
        self._collider.debug_draw(display, COLLIDER_DEBUG_COLOR)

    @abstractmethod
    def init_ghost(self, display: MlxDisplay, actual_map: Map) -> None:
        ...

    def set_path(self, path: Sequence[MapNode]) -> None:
        """Set the cell-by-cell route consumed by :meth:`update_movement`.

        Paths may include the ghost's current cell as their first node. Every
        subsequent node must be a cardinally adjacent map cell.
        """
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

    def update_movement(
            self,
            actual_map: Map,
            physics: PhysicsEngine,
            delta_time: float,
            game_state: GameState | None = None,
    ) -> None:
        """Move according to the current behaviour.

        CHASE and FLEAT consume the assigned grid path and obey wall
        collisions. DEAD ghosts return directly to their origin, ignore walls,
        wait there, then respawn according to the current Pac-Man state.
        """
        if delta_time <= 0:
            return

        if self.behaviour is Behaviour.DEAD:
            self._update_dead_movement(actual_map, delta_time, game_state)
            return

        if self._path_index >= len(self._path):
            return

        remaining_distance = self._movement_speed * delta_time
        cell_width, cell_height = actual_map.cell_size
        max_step = min(cell_width, cell_height) / 2
        grid_origin_x, grid_origin_y = actual_map.grid_origin
        wall_colliders = actual_map.wall_colliders()

        while (
            remaining_distance > GRID_CENTER_TOLERANCE
            and self._path_index < len(self._path)
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
                movement = Vector2(step if dx > 0 else -step, 0.0)
            else:
                movement = Vector2(0.0, step if dy > 0 else -step)

            if not self._can_move(movement, physics, wall_colliders):
                return

            self._move(movement)
            remaining_distance -= step
            if step >= distance:
                self._path_index += 1

    def _update_dead_movement(
            self,
            actual_map: Map,
            delta_time: float,
            game_state: GameState | None,
    ) -> None:
        """Return directly to the origin, wait, then respawn."""
        if self._respawn_wait_remaining is not None:
            self._respawn_wait_remaining -= delta_time
            if self._respawn_wait_remaining <= 0:
                behaviour = (
                    Behaviour.FLEAT
                    if (
                        game_state is not None
                        and game_state.state is PacManState.SUPER
                    )
                    else Behaviour.CHASE
                )
                self.change_behaviour(behaviour)
            return

        cell_width, cell_height = actual_map.cell_size
        grid_origin_x, grid_origin_y = actual_map.grid_origin
        target = Vector2(
            grid_origin_x + (self.origin[0] + 0.5) * cell_width,
            grid_origin_y + (self.origin[1] + 0.5) * cell_height,
        )
        displacement = target - self._collider.world_position
        distance = displacement.length()
        if distance <= GRID_CENTER_TOLERANCE:
            self._respawn_wait_remaining = RESPAWN_WAIT_DURATION
            return

        step = min(DEATH_MOVEMENT_SPEED * delta_time, distance)
        self._move(displacement.normalized() * step)
        if step >= distance:
            self._respawn_wait_remaining = RESPAWN_WAIT_DURATION

    def compute_path(
            self,
            position: Tuple[int, int],
            target: Tuple[int, int],
            graph: Dict[Tuple[int, int], MapNode],
    ) -> None:
        """Replan toward target while keeping the current movement leg."""
        if self.behaviour is Behaviour.DEAD:
            self.set_path(())
            return

        target_node = graph.get(target)

        start_node: MapNode | None
        if self._path_index < len(self._path):
            start_node = self._path[self._path_index]
        else:
            start_node = graph.get(position)
        if start_node is None or target_node is None:
            self.set_path(())
            return
        path = PathFinding.a_star(
            start_node,
            target_node,
            HeuristicType.MANHATTAN,
        )
        self.set_path(cast(list[MapNode], path))

    def select_target(
            self,
            ghost_cell: Tuple[int, int],
            player_cell: Tuple[int, int],
            actual_map: Map,
            game_state: GameState,
    ) -> Tuple[int, int]:
        """Select a pathfinding destination for a ghost's current mode."""
        if self.behaviour is Behaviour.DEAD:
            return self._dead(self.origin)
        if game_state.state != PacManState.SUPER:
            self.change_behaviour(Behaviour.CHASE)
            return self._chase(player_cell)

        self.change_behaviour(Behaviour.FLEAT)
        distance = (
            abs(ghost_cell[0] - player_cell[0])
            + abs(ghost_cell[1] - player_cell[1])
        )
        if distance > FLEE_DISTANCE_THRESHOLD:
            return self._fleat(self.origin)
        return self._fleat(
            self.__flee_target(ghost_cell, player_cell, actual_map)
        )

    def __flee_target(
            self,
            ghost_cell: Tuple[int, int],
            player_cell: Tuple[int, int],
            actual_map: Map
    ) -> Tuple[int, int]:
        """Choose a reachable walkable cell away from Pac-Man."""
        start = actual_map.graph.get(ghost_cell)
        if start is None:
            return ghost_cell

        reachable: list[Tuple[int, int]] = []
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
                cell: Tuple[int, int],
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

    @abstractmethod
    def _chase(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Chase Behaviour abstract method for Ghost Class """
        ...

    @abstractmethod
    def _fleat(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Fleat Behaviour abstract method for Ghost Class """
        ...

    @abstractmethod
    def _dead(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Dead Behaviour abstract method for Ghost Class """
        ...
