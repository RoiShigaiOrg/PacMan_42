from .Graphics import MlxDisplay
from .Animation import Animation
from .Sprite import Sprite
from typing import Dict, Tuple


class AnimationHandler:
    """
    Animation Handler Class definition

    Animation Handler is the system that will manage multiple Sprite
        and timing to create an animation.
    Every Entity/Game Object/ Scene containing animation must have
        their own AnimationHandler instance.
    """

    def __init__(self, animations: Dict[str, Animation]) -> None:
        """ Init Method of AnimationHandler """
        self.__animations: Dict[str, Animation] = animations

    def set_animation(self, key: str) -> None:
        """ Set the current animation of the Animation Handler """
        try:
            self.__actual_animation = self.__animations[key]
        except (KeyError):
            raise RuntimeError(f"unkown animation key: {key}")

    def draw(
            self,
            display: MlxDisplay,
            pos: Tuple[int, int],
            delta_time: float) -> None:
        """
        Draw the actual animation on the given display
            at the given position
        """
        self.__actual_animation.update(delta_time)
        sprite: Sprite = self.__actual_animation.current_sprite
        sprite.draw(display, pos)
