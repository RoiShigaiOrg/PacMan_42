from Engine.Graphics import MlxDisplay
from Engine.Entity.Entity import Entity
from Engine.Graphics import Circle
from typing import Tuple
from ..MapGeneration import Map


class Player(Entity):

    def InitPlayer(self, display: MlxDisplay, actual_map: Map) -> None:
        """
        Init Methode for the Player

        This method is meant to be called at each start of the Levels
            to setup the Player at the right position of the map.
        """
        map_center: Tuple[int, int] = actual_map.center()
        self.__graphical_shape: Circle = Circle(
                display.relative_width(),
                display.relative_height(),
                map_center[0],
                map_center[1],
                0xFF00FFFF
            )
