from collections.abc import Sequence
from Engine.Graphics import MlxDisplay
from Engine.Entity.Entity import Entity
from Engine.Entity.PathFinding import HeuristicType, PathFinding
from Engine.Physics.Collider import Collider
from Engine.Physics.Physics import PhysicsEngine
from Engine.Physics.Vector2 import Vector2
from ..MapGeneration.MapNode import MapNode
from ..MapGeneration import Map
from abc import abstractmethod
from typing import Dict, Tuple, cast
from enum import Enum

COLLIDER_DEBUG_COLOR: int = 0xFFFF0000
COLLIDER_SIZE_RATIO: float = 0.8
DEFAULT_MOVEMENT_SPEED: float = 175.0
GRID_CENTER_TOLERANCE: float = 1e-6


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
    ) -> None:
        """Move along the assigned path using grid centers and wall checks.

        Path selection and ghost behavior are deliberately external. This
        method only consumes the route most recently passed to ``set_path``.
        """
        if delta_time <= 0 or self._path_index >= len(self._path):
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

    def compute_path(
            self,
            position: Tuple[int, int],
            target: Tuple[int, int],
            graph: Dict[Tuple[int, int], MapNode]) -> None:
        """Build a route between supplied map cells, without choosing target.

        Target selection and behavior remain the caller's responsibility.
        """
        start_node = graph.get(position)
        target_node = graph.get(target)
        if start_node is None or target_node is None:
            self.set_path(())
            return
        path = PathFinding.a_star(
            start_node, target_node, HeuristicType.MANHATTAN
        )
        self.set_path(cast(list[MapNode], path))

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
