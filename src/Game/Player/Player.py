from __future__ import annotations

import math
from typing import Tuple

from Engine.Graphics import Circle, MlxDisplay
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_D, KEY_Q, KEY_S, KEY_Z
from Engine.Physics.Collider import Collider
from Engine.Physics.Physics import PhysicsEngine
from Engine.Physics.Shapes import AABB
from Engine.Physics.Vector2 import Vector2
from Engine.Entity.Entity import Entity
from ..MapGeneration import Map


MOVEMENT_SPEED: float = 180.0
PLAYER_COLOR: int = 0xFFFFFF00
COLLIDER_DEBUG_COLOR: int = 0xFFFF0000
COLLIDER_SIZE_RATIO: float = 0.8
GRID_CENTER_TOLERANCE: float = 1e-6

_DIRECTION_KEYS: tuple[tuple[int, Vector2], ...] = (
    (KEY_Z, Vector2(0.0, -1.0)),
    (KEY_Q, Vector2(-1.0, 0.0)),
    (KEY_S, Vector2(0.0, 1.0)),
    (KEY_D, Vector2(1.0, 0.0)),
)


class Player(Entity):
    """
    Player Class Definition

    Define the player whithin the game. Containing:
        - Physical Shape for collision handling with walls
        - Graphical Shape | Sprite for visual representation
        - Position Data for movements
        - Behaviours Data to indicate to the Gamestate how others will
            behave depending of the Game rules.
        - InputHandling from the user to update character position
    """

    def __init__(self, movement_speed: float = MOVEMENT_SPEED) -> None:
        if movement_speed <= 0:
            raise ValueError("movement_speed must be positive")
        self._movement_speed = movement_speed
        self._direction = Vector2(0.0, 0.0)
        self._requested_direction: Vector2 | None = None

    def InitPlayer(self, display: MlxDisplay, actual_map: Map) -> None:
        """
        Init Methode for the Player

        This method is meant to be called at each start of the Levels
            to setup the Player at the right position of the map,
        with the right size.
        """
        map_center: Tuple[int, int] = actual_map.center()
        print(f"map_center: {map_center} map size: {actual_map.size()}")
        self._width, self._height = actual_map.cell_size
        map_pos_x, map_pos_y = actual_map.grid_origin
        pos_x: int = int(
                map_pos_x + map_center[0] * self._width
            )
        pos_y: int = int(
                map_pos_y + map_center[1] * self._height
            )
        print(
            f"width: {self._width} height: {self._height} "
            f"x: {pos_x} y: {pos_y}"
        )
        self._graphical_shape: Circle = Circle(
                self._width,
                self._height,
                pos_x,
                pos_y,
                PLAYER_COLOR,
            )
        self._collider: Collider = Collider(
                AABB(Vector2(
                    self._width * COLLIDER_SIZE_RATIO / 2,
                    self._height * COLLIDER_SIZE_RATIO / 2,
                    )),
                Vector2(
                    pos_x + self._width / 2,
                    pos_y + self._height / 2,
                    )
                )
        self._sync_graphics_position()

    @property
    def collider(self) -> Collider:
        """Return the collider that owns the Player's world-space position."""
        return self._collider

    @property
    def direction(self) -> Vector2:
        """Return the direction the Player is currently travelling."""
        return self._direction

    @property
    def size(self) -> Tuple[int, int]:
        """Return the graphical and collider dimensions of the Player."""
        return self._width, self._height

    def update_direction(
            self,
            inputs: InputHandler,
            actual_map: Map,
            physics: PhysicsEngine,
            delta_time: float,
    ) -> None:
        """
        Buffer directional input and move when the physics query permits it.

        Movement is measured in pixels per second. Each frame is split into
        small collision-checked steps so a large frame delta cannot skip over
        a wall collider.
        """
        self.__capture_requested_direction(inputs)
        if delta_time <= 0:
            return

        remaining_distance = self._movement_speed * delta_time
        max_step = min(self._width, self._height) / 2
        wall_colliders = actual_map.wall_colliders()
        grid_origin = actual_map.grid_origin
        cell_size = actual_map.cell_size

        while remaining_distance > GRID_CENTER_TOLERANCE:
            requested = self._requested_direction
            center = self._collider.world_position
            at_cell_center = actual_map.is_cell_centered(
                center, GRID_CENTER_TOLERANCE
            )

            if at_cell_center and requested is not None:
                if actual_map.next_cell_is_walkable(center, requested):
                    self._direction = requested
                    self._requested_direction = None

            if self._direction.length_squared() == 0:
                break

            if at_cell_center and not actual_map.next_cell_is_walkable(
                    center, self._direction):
                self._direction = Vector2(0.0, 0.0)
                break

            step = min(
                remaining_distance,
                max_step,
                abs(self._distance_to_next_grid_center(
                    self._direction, grid_origin, cell_size
                )),
            )
            if step <= GRID_CENTER_TOLERANCE:
                break

            current_delta = self._direction * step
            if not self._can_move(current_delta, physics, wall_colliders):
                self._direction = Vector2(0.0, 0.0)
                break
            self._move(current_delta)
            remaining_distance -= step

    def _distance_to_next_grid_center(
            self,
            direction: Vector2,
            grid_origin: Tuple[int, int],
            cell_size: Tuple[int, int],
    ) -> float:
        """Return signed distance to the next cell center along travel."""
        center = self._collider.world_position
        if direction.x != 0:
            coordinate = center.x
            origin = grid_origin[0]
            size = cell_size[0]
            travel_sign = direction.x
        else:
            coordinate = center.y
            origin = grid_origin[1]
            size = cell_size[1]
            travel_sign = direction.y

        first_center = origin + size / 2
        center_index = (coordinate - first_center) / size
        if travel_sign > 0:
            target_index = math.floor(center_index + 1e-9) + 1
        else:
            target_index = math.ceil(center_index - 1e-9) - 1
        target: float = first_center + target_index * size
        return float(target - coordinate)

    def __capture_requested_direction(self, inputs: InputHandler) -> None:
        """Remember the newest pressed or held direction until it can turn."""
        pressed = next(
            (direction for key, direction in _DIRECTION_KEYS
             if inputs.was_key_pressed(key)),
            None,
        )
        if pressed is not None:
            self._requested_direction = pressed
            return

        held = next(
            (direction for key, direction in _DIRECTION_KEYS
             if inputs.is_key_down(key)),
            None,
        )
        if held is not None:
            self._requested_direction = held

    def draw(self, display: MlxDisplay) -> None:
        """ draw Method of the Player Class """
        self._graphical_shape.fill(display)
        self._collider.debug_draw(display, COLLIDER_DEBUG_COLOR)
