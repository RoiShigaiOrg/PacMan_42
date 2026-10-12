from ..Graphics.Components import Components
from ..Graphics import Rect
from typing import List, Any


class PhysicsEngine:
    """
        Physic Engine Class Definition

        The PhysicsEngine is the part of the Engine that will
            compute all the mouvement velocity and checks for the
            Collision between multiple objects.
    """

    def handle_collision(self, player: Any, entities: List[Any]) -> None:
        """ Resolve the collision of all entities given by the list """
        for entity in entities:
            self.__check_collision(player, entity)

    def __check_collision(self, collision_1: Components, collision_2: Components) -> bool:
        """ Method to detect collision between 2 Components Object """
        if type(collision_1) is Rect and type(collision_2) is Rect:
            return self.__check_rect_shape_collision(collision_1, collision_2)

    def __check_rect_shape_collision(self, rect1: Rect, rect2: Rect) -> bool:
        """ Check the collision between 2 Rect Object """
        x1, y1 = rect1.pos
        x2, y2 = rect2.pos
        w1, h1 = rect1.size
        w2, h2 = rect2.size

        print(f"rect1: {x1} {y1} {w1} {h1}")
        print(f"rect2: {x2} {y2} {w2} {h2}")
        if (x1 > x2 + w2 or x1 + w1 < x2 or y1 > y2 + h2 or y1 + h1 < y2):
            return False
        else:
            return True

