from Engine.Engine import Engine
from Engine.Physics.Vector2 import Vector2
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Graphics.Components.Circle import Circle
from Engine.Animation import Animation, AnimationHandler
from Engine.Physics.Collider import Collider
from Engine.Physics.Shapes import AABB
from ..MapGeneration import Map
from typing import Tuple
from .Ghost import Ghost
from .Behaviours import BlinkyChaseBehaviour
from pathlib import Path

MOVEMENT_SPEED: float = 160.0
BLINKY_COLOR: int = 0xFFFF0000
COLLIDER_DEBUG_COLOR: int = 0xFFFFFFFF
COLLIDER_SIZE_RATIO: float = 0.8
HIGH_LEFT: int = 1
HIGH_RIGHT: int = 2
LOW_LEFT: int = 3
LOW_RIGHT: int = 4


class Blinky(Ghost):
    """
    Blinky Ghost Class Definition

    Blinky will be the red Ghost, he's behaviour is to chase PacMan
        and try to be in front of him at each moment.
    """

    def __init__(self, engine: Engine, movement_speed: float = MOVEMENT_SPEED) -> None:
        """ Init Method of Blinky """
        super().__init__(engine, movement_speed, BlinkyChaseBehaviour())
        sprite_sheet = engine.load_sprite_sheet(
            Path("assets/BlinkySprite/blinkysheet.png"),
            Path("assets/BlinkySprite/blinkysheet.json"),
        )
        player_animations = {
            direction: Animation(sprite_sheet.get_sprite(tag))
            for direction, tag in (
                ("right", "walk_right"),
                ("left", "walk_left"),
                ("up", "walk_up"),
                ("down", "walk_down"),
            )
        }
        animation_handler = AnimationHandler(player_animations)
        self.__animation_handler = animation_handler
        if self.__animation_handler is not None:
            self.__animation_handler.set_animation("left")

    def init_ghost(self, display: MlxDisplay, actual_map: Map) -> None:
        """ Init The Ghost position depending of the actual map """
        self._origin: Tuple[int, int] = actual_map.corner(HIGH_RIGHT)
        self._width, self._height = actual_map.cell_size
        map_pos_x, map_pos_y = actual_map.grid_origin
        pos_x: int = int(
                map_pos_x + self._origin[0] * self._width
            )
        pos_y: int = int(
                map_pos_y + self._origin[1] * self._height
            )
        self._graphical_shape: Circle = Circle(
                self._width,
                self._height,
                pos_x,
                pos_y,
                BLINKY_COLOR,
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
        self.set_path(())
