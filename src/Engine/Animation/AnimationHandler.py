from ..Graphics import MlxDisplay
from .Animation import Animation
from ..Sprite import Sprite


class AnimationHandler:
    """
    Animation Handler Class definition

    Animation Handler is the system that will manage multiple Sprite
        and timing to create an animation.
    Every Entity/Game Object/ Scene containing animation must have
        their own AnimationHandler instance.
    """

    def __init__(self, animations: dict[str, Animation]) -> None:
        """ Init Method of AnimationHandler """
        if not animations:
            raise ValueError(
                "an animation handler needs at least one animation"
            )
        self.__animations = dict(animations)
        self.__actual_key = next(iter(self.__animations))
        self.__actual_animation = self.__animations[self.__actual_key]

    def set_animation(self, key: str) -> None:
        """ Set the current animation of the Animation Handler """
        try:
            animation = self.__animations[key]
        except KeyError as error:
            raise KeyError(f"unknown animation key: {key}") from error
        if key != self.__actual_key:
            animation.reset()
        self.__actual_key = key
        self.__actual_animation = animation

    def update(self, delta_time: float) -> None:
        """Advance the active animation independently of drawing."""
        self.__actual_animation.update(delta_time)

    @property
    def current_key(self) -> str:
        """Return the active animation's key."""
        return self.__actual_key

    @property
    def current_frame_index(self) -> int:
        """Return the active animation's current frame index."""
        return self.__actual_animation.current_index

    @property
    def current_sprite(self) -> Sprite:
        """Return the sprite for the active animation's current frame."""
        return self.__actual_animation.current_sprite

    def get_actual_frame(self) -> Sprite:
        """Return the active animation's current frame for rendering."""
        return self.current_sprite

    def draw(
            self,
            display: MlxDisplay,
            pos: tuple[int, int],
            size: tuple[int, int] | None = None,
    ) -> None:
        """
        Draw the actual animation on the given display
            at the given position
        """
        sprite: Sprite = self.current_sprite
        sprite.draw(display, pos, size)
