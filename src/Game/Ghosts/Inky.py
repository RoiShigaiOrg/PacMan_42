from Engine.Physics.Vector2 import Vector2
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Graphics.Components.Circle import Circle
from Engine.Physics.Collider import Collider
from Engine.Physics.Shapes import AABB
from ..MapGeneration import Map
from ..Player.Player import Player
from typing import Tuple
from .Ghost import Ghost

MOVEMENT_SPEED: float = 160.0
INKY_COLOR: int = 0xFF0000FF
COLLIDER_DEBUG_COLOR: int = 0xFFFFFFFF
COLLIDER_SIZE_RATIO: float = 0.8
HIGH_LEFT: int = 1
HIGH_RIGHT: int = 2
LOW_LEFT: int = 3
LOW_RIGHT: int = 4


class Inky(Ghost):
    """
    Inky Ghost Class Definition

    Inky will be the Blue Ghost, he's behaviour is to chase PacMan
        and try to be in front of him at each moment.
    """

    def __init__(self, movement_speed: float = MOVEMENT_SPEED) -> None:
        """ Init Method of Inky """
        super().__init__(movement_speed)

    def init_ghost(self, display: MlxDisplay, actual_map: Map) -> None:
        """ Init The Ghost position depending of the actual map """
        self._origin: Tuple[int, int] = actual_map.corner(HIGH_LEFT)
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
                INKY_COLOR,
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

    def _chase(
            self,
            player: Player,
            actual_map: Map,
            ghost_cell: Tuple[int, int]) -> Tuple[int, int]:
        """ Chase Behaviour abstract method for Ghost Class """
        return actual_map.cell_coordinates_at(
                player.collider.world_position
            )

    def _fleat(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Fleat Behaviour abstract method for Ghost Class """
        return target

    def _dead(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """ Dead Behaviour abstract method for Ghost Class """
        return self.origin
