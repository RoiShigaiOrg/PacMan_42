import importlib

import pytest

from Engine.Clock import Clock


clock_module = importlib.import_module("Engine.Clock.Clock")


def test_tick_waits_for_target_frame_duration(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_time = 10.0
    sleeps: list[float] = []

    def perf_counter() -> float:
        return current_time

    def sleep(duration: float) -> None:
        nonlocal current_time
        sleeps.append(duration)
        current_time += duration

    monkeypatch.setattr(clock_module.time, "perf_counter", perf_counter)
    monkeypatch.setattr(clock_module.time, "sleep", sleep)

    clock = Clock(target_fps=60)
    clock.tick()

    assert sleeps == pytest.approx([1 / 60])
    assert clock.delta_time == pytest.approx(1 / 60)


def test_tick_does_not_sleep_when_frame_is_already_slow(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    times = iter((10.0, 10.1))
    sleeps: list[float] = []

    monkeypatch.setattr(clock_module.time, "perf_counter", lambda: next(times))
    monkeypatch.setattr(clock_module.time, "sleep", sleeps.append)

    clock = Clock(target_fps=60)

    assert clock.tick() == pytest.approx(0.1)
    assert sleeps == []


def test_uncapped_clock_does_not_sleep(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    times = iter((10.0, 10.25))
    sleeps: list[float] = []

    monkeypatch.setattr(clock_module.time, "perf_counter", lambda: next(times))
    monkeypatch.setattr(clock_module.time, "sleep", sleeps.append)

    clock = Clock(target_fps=None)

    assert clock.tick() == pytest.approx(0.1)
    assert sleeps == []


@pytest.mark.parametrize("kwargs", [
    {"max_delta": 0},
    {"max_delta": -1},
    {"target_fps": 0},
    {"target_fps": -1},
])
def test_clock_rejects_non_positive_values(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        Clock(**kwargs)
