from collections.abc import Sequence
import math
from typing import cast

from ..Sprite import Sprite, SpriteFrame


class Animation:
    """Advance through sprites using seconds-based frame durations."""

    def __init__(
            self,
            frames: Sequence[SpriteFrame] | Sequence[Sprite],
            framerate: float | None = None,
            loop: bool = True,
    ) -> None:
        """Create an animation from timed frames or sprites at a fixed FPS.

        Pass the duration-bearing frames returned by ``SpriteSheet.get_sprite``
        to preserve Aseprite timing. For manually created sprites, provide a
        positive ``framerate`` in frames per second.
        """
        frame_tuple = tuple(frames)
        if not frame_tuple:
            raise ValueError("an animation must contain at least one frame")

        if all(isinstance(frame, SpriteFrame) for frame in frame_tuple):
            if framerate is not None:
                raise ValueError(
                    "framerate cannot be combined with timed sprite frames"
                )
            self.__frames = cast(tuple[SpriteFrame, ...], frame_tuple)
        elif all(isinstance(frame, Sprite) for frame in frame_tuple):
            if (
                framerate is None
                or not math.isfinite(framerate)
                or framerate <= 0
            ):
                raise ValueError(
                    "a positive framerate is required for plain sprites"
                )
            frame_duration_ms = 1000.0 / framerate
            self.__frames = tuple(
                SpriteFrame(cast(Sprite, frame), frame_duration_ms)
                for frame in frame_tuple
            )
        else:
            raise TypeError(
                "animation frames must all be Sprite or SpriteFrame objects"
            )

        self.__loop = loop
        self.__index = 0
        self.__elapsed_time = 0.0
        self.__finished = False

    @property
    def current_sprite(self) -> Sprite:
        """Return the sprite displayed by the current animation frame."""
        return self.__frames[self.__index].sprite

    @property
    def current_index(self) -> int:
        """Return the index of the current frame."""
        return self.__index

    @property
    def finished(self) -> bool:
        """Whether a non-looping animation has reached its last frame."""
        return self.__finished

    @property
    def framerate(self) -> float | None:
        """Return FPS for uniform-duration animations, otherwise ``None``."""
        first_duration = self.__frames[0].duration_seconds
        if any(
            frame.duration_seconds != first_duration
            for frame in self.__frames[1:]
        ):
            return None
        return 1.0 / first_duration

    def update(self, delta_time: float) -> None:
        """Advance the animation by ``delta_time`` seconds."""
        if not math.isfinite(delta_time):
            raise ValueError("delta_time must be finite")
        if self.__finished or delta_time <= 0:
            return

        self.__elapsed_time += delta_time
        while self.__elapsed_time >= self.__frames[
                self.__index].duration_seconds:
            self.__elapsed_time -= self.__frames[
                self.__index
            ].duration_seconds
            if self.__index + 1 < len(self.__frames):
                self.__index += 1
            elif self.__loop:
                self.__index = 0
            else:
                self.__index = len(self.__frames) - 1
                self.__elapsed_time = 0.0
                self.__finished = True
                break

    def reset(self) -> None:
        """Restart the animation at its first frame."""
        self.__index = 0
        self.__elapsed_time = 0.0
        self.__finished = False
