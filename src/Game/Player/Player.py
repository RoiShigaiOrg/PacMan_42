from Engine.Graphics import MlxDisplay
from Engine.Entity.Entity import Entity
from Engine.Graphics import Circle
from typing import Tuple
from ..MapGeneration import Map
from ..MapGeneration import (
        RELATIVE_MAP_POS_X,
        RELATIVE_MAP_POS_Y,
        RELATIVE_MAP_WIDTH,
        RELATIVE_MAP_HEIGHT
    )


class Player:

    def InitPlayer(self, display: MlxDisplay, actual_map: Map) -> None:
        """
        Init Methode for the Player

        This method is meant to be called at each start of the Levels
            to setup the Player at the right position of the map.
        """
        map_center: Tuple[int, int] = actual_map.center()
        print(f"map_center: {map_center} map size: {actual_map.size()}")
        self.__width: int = int(
                display.relative_width(RELATIVE_MAP_WIDTH) / actual_map.width
            )
        self.__height: int = int(
                display.relative_height(RELATIVE_MAP_HEIGHT) / actual_map.height
            )
        pos_x: int = int(
                display.relative_width(RELATIVE_MAP_POS_X) + map_center[0] * self.__width
            )
        pos_y: int = int(
                display.relative_height(RELATIVE_MAP_POS_Y) + map_center[1] * self.__height
            )
        print(f"width: {self.__width} height: {self. __height} x: {pos_x} y: {pos_y}")
        self.__graphical_shape: Circle = Circle(
                self.__width,
                self.__height,
                pos_x,
                pos_y,
                0xFFFFFF00
            )

    def draw(self, display: MlxDisplay) -> None:
        """ draw Method of the Player Class """
        self.__graphical_shape.fill(display)
