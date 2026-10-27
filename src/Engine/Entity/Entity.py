from abc import ABC
from typing import Tuple
from ..Physics.Vector2 import Vector2
from ..Physics.Physics import PhysicsEngine
from ..Physics.Collider import Collider
from ..Graphics.MlxDisplay import MlxDisplay


class Entity(ABC):
    """
        Entity Abstract Class

        The Entity Class serve as a boase to represent any
            movable entity present in the project (Player, Ghost)
    """

    def draw(self, display: MlxDisplay) -> None:
        """ draw Method of the Entity Class """
        ...

    @property
    def coord(self) -> tuple[int, int]:
        """ Getter method for the Object position """
        return self._coord

    @coord.setter
    def coord(self, coord: tuple[int, int]) -> None:
        """ Setter method for the Object position """
        self._coord = coord

    @property
    def name(self) -> str:
        """ Getter method for the Object Name """
        return self._name

    @property
    def position(self) -> Tuple[int, int]:
        """Return the graphical top-left position derived from the collider."""
        center = self._collider.world_position
        return (
            round(center.x - self._width / 2),
            round(center.y - self._height / 2),
        )

    @position.setter
    def position(self, value: Tuple[int, int]) -> None:
        """Set the graphic position and move the authoritative collider."""
        world_center = Vector2(
            value[0] + self._width / 2,
            value[1] + self._height / 2,
        )
        self._collider.position = world_center - self._collider.offset
        self._sync_graphics_position()

    def _can_move(
            self,
            delta: Vector2,
            physics: PhysicsEngine,
            wall_colliders: tuple[Collider, ...],
    ) -> bool:
        can_move: bool = physics.can_move(
            self._collider, delta, *wall_colliders
        )
        return can_move

    def _move(self, delta: Vector2) -> None:
        """Apply an accepted displacement and keep the graphic in sync."""
        self._collider.position = self._collider.position + delta
        self._sync_graphics_position()

    def _sync_graphics_position(self) -> None:
        """Place the integer-pixel graphic around the collider's center."""
        center = self._collider.world_position
        self._graphical_shape.update_pos(
            round(center.x - self._width / 2),
            round(center.y - self._height / 2),
        )
