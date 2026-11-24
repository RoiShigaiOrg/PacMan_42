from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import ClassVar
from Engine.Engine import Engine


class PacManState(Enum):
    NORMAL = 1
    SUPER = 2
    DEAD = 3


class GameMode(Enum):
    """How the game is played."""

    NORMAL = "normal"
    INFINITE = "infinite"


class GameState(ABC):
    """
        GameState Abstract Class Definition

        Everything that is the same in every game mode:
            score, lives, level, timers, speed, power mode, death.
        What changes from one mode to the other is abstract and
            written in the child classes (ArcadeMode, InfinityMode).
    """

    SCORE_FILE: ClassVar[Path]

    def __init__(self,  engine: Engine) -> None:
        """init class variables"""
        self.engine = engine
        self.__start_lives = engine.get_config_key("lives")
        self.cheat: bool = False
        self.reset_stats()

    @property
    @abstractmethod
    def mode(self) -> GameMode:
        """ The game mode of this class """

    @abstractmethod
    def has_won(self) -> bool:
        """ True when the game is won (never in some modes) """

    @property
    def score_file(self) -> Path:
        """ The leaderboard file of this mode """
        return self.SCORE_FILE

    def reset_stats(self) -> None:
        """ initialize variables for the start of a game/level"""
        self.lives: int = self.__start_lives
        self._speed: float = 1.0
        self.level_time: float = self.engine.get_config_key("level_time")
        self.scores: int = 0
        self.level: int = 1
        self.ghost_combo: int = 0
        self.extra_life_given: bool = False
        self.state: PacManState = PacManState.NORMAL
        self._death_recovery_remaining: float = 0.0
        self.play_time: float = 0.0
        self._power_remaining: float = 0.0

    @property
    def speed(self) -> float:
        """Speed multiplier applied to every entity (player, ghosts...)."""
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"speed must be positive, not {value}")
        self._speed = min(value, self.engine.get_config_key("max_speed"))

    def cheat_mod(self, cheat: bool) -> None:
        """ select cheat/normal mode"""
        self.cheat = cheat

    def time_in_level(self, delta_time: float) -> None:
        """Call once per frame: the time left goes down to 0."""
        self.play_time += delta_time
        if self.level_time <= 0:
            return
        self.level_time = max(0.0, self.level_time - delta_time)

    def add_point(self, points: int) -> None:
        """ increases the score"""
        self.scores += points
        if (not self.extra_life_given
                and self.scores >= self.engine.get_config_key("extra_life")):
            self.lives += 1
            self.extra_life_given = True

    def eat_pac_dot(self) -> None:
        """add value point of pellet"""
        self.add_point(self.engine.get_config_key("pacgum_points"))

    def eat_fruit(self) -> None:
        """ add value point of power by pellet"""
        self.add_point(self.engine.get_config_key("power_pellet_points"))
        if self.state is not PacManState.DEAD:
            self.state = PacManState.SUPER
            self._power_remaining = self.engine.get_config_key(
                "power_duration")
        self.ghost_combo = 0

    def eat_ghost(self) -> int:
        """ add value of consumed ghost: doubled for each ghost in a row"""
        base = int(self.engine.get_config_key("ghost_points"))
        combo = min(self.ghost_combo, int(self.engine.get_config_key(
            "max_ghost_combo")))
        points = base * 2 ** combo
        self.ghost_combo += 1
        self.add_point(points)
        return int(points)

    def end_power_mode(self) -> None:
        """ state of end power mode"""
        if self.state is PacManState.SUPER:
            self.state = PacManState.NORMAL
        self.ghost_combo = 0

    @property
    def power_remaining(self) -> float:
        """Return the remaining power mode duration."""
        return self._power_remaining

    def update_power_remaining(self, delta_time: float) -> None:
        """Advance the power remaining time and restore normal mode."""
        if (
            self.state is not PacManState.SUPER
            or self._power_remaining <= 0
            or delta_time <= 0
        ):
            return
        self._power_remaining = max(
            0.0, self._power_remaining - delta_time
        )
        if self._power_remaining == 0:
            self.end_power_mode()

    def lose_life(self) -> None:
        """ managing the loss of a life and the death of Pac-Man"""
        if self.cheat:
            return
        self.lives = max(0, self.lives - 1)
        self.ghost_combo = 0
        self.state = PacManState.DEAD
        self._death_recovery_remaining = self.engine.get_config_key(
            "death_recovery_duration")

    @property
    def death_recovery_remaining(self) -> float:
        """Return the remaining shared Pac-Man/ghost recovery duration."""
        return self._death_recovery_remaining

    def update_death_recovery(self, delta_time: float) -> None:
        """Advance the shared post-death interval and restore normal mode."""
        if (
            self.state is not PacManState.DEAD
            or self._death_recovery_remaining <= 0
            or delta_time <= 0
        ):
            return
        self._death_recovery_remaining = max(
            0.0, self._death_recovery_remaining - delta_time
        )
        if self._death_recovery_remaining == 0:
            self.state = PacManState.NORMAL

    def next_level(self) -> None:
        """ init the next level"""
        step_level = self.engine.get_config_key("step_level")
        if (self.level - 1) % step_level == 0:
            self._speed = self._speed + self.engine.get_config_key(
                "speed_increase")
        self.level += 1
        self.ghost_combo = 0
        self.level_time = 0.0
        self.state = PacManState.NORMAL
        self._death_recovery_remaining = 0.0

    def is_over(self) -> bool:
        """ init the end of game"""
        return self.lives <= 0
