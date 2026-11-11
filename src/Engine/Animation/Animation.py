from .Sprite.Sprite import Sprite
from typing import List, Tuple


class Animation:
    """
    Animation Class Definition

    Animation Class is a set of Sprite that will create an animation
        within a certain FrameRate.
    """

    def __init__(self, sprite_lst: List[Sprite], framerate: int, loop=True) -> None:
        """ Init Method of the Animation Class """
        self.__sprites: Tuple[Sprite] = tuple(sprite_lst)
        self.__framerate: int = framerate
        self.__loop: bool = loop
        self.__index: int = 0
        self.__elapsed_time: float = 0.0
        self.__finished: bool = False

    def update(self, delta_time):
        """
        Update method to set the right sprite depending on the framerate
            and the time
        """
        if self.__finished or delta_time <= 0:
            return

        self.__elapsed_time += delta_time
        while self.__elapsed_time >= self.__framerate:
            self.__elapsed_time -= self.__framerate
            if self.__index + 1 < len(self.__sprites):
                self.__index += 1
            elif self.__loop:
                self.__index = 0
            else:
                self.__index = len(self.__sprites) - 1
                self.__finished = True
                break

    @property
    def current_sprite(self):
        return self.frame[self.index]
