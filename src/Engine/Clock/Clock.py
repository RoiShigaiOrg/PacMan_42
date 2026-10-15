import time


class Clock:
    """Track frame time and optionally limit the frame rate.

    Args:
        max_delta: Maximum value returned for a single frame delta.
        target_fps: Desired maximum frame rate. ``None`` disables limiting.
    """

    def __init__(
            self,
            max_delta: float = 0.1,
            target_fps: float | None = 60.0,
    ) -> None:
        """Initialize a clock.

        Raises:
            ValueError: If ``max_delta`` or ``target_fps`` is not positive.
        """
        if max_delta <= 0:
            raise ValueError("max_delta must be positive")
        if target_fps is not None and target_fps <= 0:
            raise ValueError("target_fps must be positive")

        self._previous_time = time.perf_counter()
        self._delta_time = 0.0
        self._elapsed_time = 0.0
        self._max_delta = max_delta
        self._frame_duration = (
            None if target_fps is None else 1.0 / target_fps
        )

    def tick(self) -> float:
        """Wait for the frame budget and return the elapsed frame time.

        The returned value includes time spent sleeping and is clamped by
        ``max_delta`` so long pauses do not cause a large simulation jump.

        Returns:
            The elapsed time since the previous tick, in seconds.
        """
        current_time = time.perf_counter()
        delta = current_time - self._previous_time

        if self._frame_duration is not None:
            remaining = self._frame_duration - delta
            if remaining > 0:
                time.sleep(remaining)
                current_time = time.perf_counter()
                delta = current_time - self._previous_time

        self._previous_time = current_time

        self._delta_time = min(delta, self._max_delta)
        self._elapsed_time += self._delta_time
        return self._delta_time

    @property
    def delta_time(self) -> float:
        """Return the most recently measured frame delta in seconds."""
        return self._delta_time

    @property
    def elapsed_time(self) -> float:
        """Return the accumulated, clamped elapsed time in seconds."""
        return self._elapsed_time
