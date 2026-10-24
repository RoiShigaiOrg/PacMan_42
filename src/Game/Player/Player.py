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
from ..MapGeneration import (
    RELATIVE_MAP_HEIGHT,
    RELATIVE_MAP_POS_X,
    RELATIVE_MAP_POS_Y,
    RELATIVE_MAP_WIDTH,
    Map,
)


MOVEMENT_SPEED: float = 180.0
PLAYER_COLOR: int = 0xFFFFFF00
COLLIDER_DEBUG_COLOR: int = 0xFFFF0000

_DIRECTION_KEYS: tuple[tuple[int, Vector2], ...] = (
    (KEY_Z, Vector2(0.0, -1.0)),
    (KEY_Q, Vector2(-1.0, 0.0)),
    (KEY_S, Vector2(0.0, 1.0)),
    (KEY_D, Vector2(1.0, 0.0)),
)


class Player:
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
        self.__movement_speed = movement_speed
        self.__direction = Vector2(0.0, 0.0)
        self.__requested_direction: Vector2 | None = None

    def InitPlayer(self, display: MlxDisplay, actual_map: Map) -> None:
        """
        Init Methode for the Player

        This method is meant to be called at each start of the Levels
            to setup the Player at the right position of the map,
        with the right size.
        """
        map_center: Tuple[int, int] = actual_map.center()
        print(f"map_center: {map_center} map size: {actual_map.size()}")
        self.__width: int = int(
                display.relative_width(RELATIVE_MAP_WIDTH)
                / actual_map.width
            )
        self.__height: int = int(
                display.relative_height(RELATIVE_MAP_HEIGHT)
                / actual_map.height
            )
        pos_x: int = int(
                display.relative_width(RELATIVE_MAP_POS_X)
                + map_center[0] * self.__width
            )
        pos_y: int = int(
                display.relative_height(RELATIVE_MAP_POS_Y)
                + map_center[1] * self.__height
            )
        print(
            f"width: {self.__width} height: {self.__height} "
            f"x: {pos_x} y: {pos_y}"
        )
        self.__graphical_shape: Circle = Circle(
                self.__width,
                self.__height,
                pos_x,
                pos_y,
                PLAYER_COLOR,
            )
        self.__collider: Collider = Collider(
                AABB(Vector2(
                    self.__width / 2, self.__height / 2)),
                Vector2(
                    pos_x + self.__width / 2,
                    pos_y + self.__height / 2,
                    )
                )
        self.__sync_graphics_position()

    @property
    def position(self) -> Tuple[int, int]:
        """Return the graphical top-left position derived from the collider."""
        center = self.__collider.world_position
        return (
            round(center.x - self.__width / 2),
            round(center.y - self.__height / 2),
        )

    @position.setter
    def position(self, value: Tuple[int, int]) -> None:
        """Set the graphic position and move the authoritative collider."""
        world_center = Vector2(
            value[0] + self.__width / 2,
            value[1] + self.__height / 2,
        )
        self.__collider.position = world_center - self.__collider.offset
        self.__sync_graphics_position()

    @property
    def collider(self) -> Collider:
        """Return the collider that owns the Player's world-space position."""
        return self.__collider

    @property
    def direction(self) -> Vector2:
        """Return the direction the Player is currently travelling."""
        return self.__direction

    @property
    def size(self) -> Tuple[int, int]:
        """Return the graphical and collider dimensions of the Player."""
        return self.__width, self.__height

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

        distance = self.__movement_speed * delta_time
        max_step = min(self.__width, self.__height) / 2
        step_count = max(1, math.ceil(distance / max_step))
        step = distance / step_count
        wall_colliders = actual_map.wall_colliders()

        for _ in range(step_count):
            requested = self.__requested_direction
            if requested is not None and self.__can_move(
                    requested * step, physics, wall_colliders):
                self.__direction = requested
                self.__requested_direction = None
                self.__move(requested * step)
                continue

            if self.__direction.length_squared() == 0:
                break
            current_delta = self.__direction * step
            if not self.__can_move(current_delta, physics, wall_colliders):
                break
            self.__move(current_delta)

    def __capture_requested_direction(self, inputs: InputHandler) -> None:
        """Remember the newest pressed or held direction until it can turn."""
        pressed = next(
            (direction for key, direction in _DIRECTION_KEYS
             if inputs.was_key_pressed(key)),
            None,
        )
        if pressed is not None:
            self.__requested_direction = pressed
            return

        held = next(
            (direction for key, direction in _DIRECTION_KEYS
             if inputs.is_key_down(key)),
            None,
        )
        if held is not None:
            self.__requested_direction = held

    def __can_move(
            self,
            delta: Vector2,
            physics: PhysicsEngine,
            wall_colliders: tuple[Collider, ...],
    ) -> bool:
        can_move: bool = physics.can_move(
            self.__collider, delta, *wall_colliders
        )
        return can_move

    def __move(self, delta: Vector2) -> None:
        """Apply an accepted displacement and keep the graphic in sync."""
        self.__collider.position = self.__collider.position + delta
        self.__sync_graphics_position()

    def __sync_graphics_position(self) -> None:
        """Place the integer-pixel graphic around the collider's center."""
        center = self.__collider.world_position
        self.__graphical_shape.update_pos(
            round(center.x - self.__width / 2),
            round(center.y - self.__height / 2),
        )

    def draw(self, display: MlxDisplay) -> None:
        """ draw Method of the Player Class """
        self.__graphical_shape.fill(display)
        self.__collider.debug_draw(display, COLLIDER_DEBUG_COLOR)
