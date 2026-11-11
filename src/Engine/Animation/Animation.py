from .Sprite.Sprite import Sprite
from .Graphics import MlxDisplay
from typing import List


class Animation:
    """
    Animation Class Definition

    Animation Class is a set of Sprite that will create an animation
        within a certain FrameRate.
    """

    def __init__(self, sprite_lst: List[Sprite], framerate: int) -> None:
        """ Init Method of the Animation Class """
        self.__sprites: List[Sprite] = sprite_lst
        self.__framerate: int = framerate
        self.__last_update: int = 0

    def draw(self, display: MlxDisplay, delta_time: int) -> None:
        """ Draw method of the Animation Class """
        pass
