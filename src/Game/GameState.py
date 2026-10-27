from enum import Enum

PELLET_POINTS: int = 10
POWER_PELLET_POINTS: int = 50
GHOST_POINTS: tuple[int, ...] = (200, 400, 800, 1600)
EXTRA_LIFE_SCORE: int = 10000

NORMAL = "normal"
SUPER = "super"
DEAD = "dead"
LEVEL_TIME: float = 120.0
MAX_LEVEL = 10
SPEED_STEP_LEVELS: int = 3
SPEED_INCREASE: float = 0.1
MAX_SPEED = 3.0


class GameMode(Enum):
    """How the game is played."""

    NORMAL = "normal"
    INFINITE = "infinite"


class GameState:
    def __init__(self, lives: int = 3) -> None:
        """init class variables"""
        self.__start_lives = lives
        self.__game_mode: GameMode = GameMode.NORMAL
        self.cheat: bool = False
        self.reset_stats()

    def reset_stats(self) -> None:
        """ initialize variables for the start of a game/level"""
        self.lives: int = self.__start_lives
        self._speed: float = 1.0
        self.level_time: float = LEVEL_TIME
        self.scores: int = 0
        self.level: int = 1
        self.ghost_combo: int = 0
        self.extra_life_given: bool = False
        self.state: str = NORMAL

    @property
    def game_mode(self) -> GameMode:
        """ return Infinite/Normal mode"""
        return self.__game_mode

    @game_mode.setter
    def game_mode(self, mode: GameMode) -> None:
        """Change the mode of the game."""
        if not isinstance(mode, GameMode):
            raise TypeError(f"game_mode must be a GameMode, not {mode!r}")
        self.__game_mode = mode

    @property
    def speed(self) -> float:
        """Speed multiplier applied to every entity (player, ghosts...)."""
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"speed must be positive, not {value}")
        self._speed = min(value, MAX_SPEED)

    def cheat_mod(self, cheat: bool) -> None:
        """ select cheat/normal mode"""
        self.cheat = cheat

    def time_in_level(self, delta_time: float) -> None:
        """Call once per frame: the time left goes down to 0."""
        if self.level_time <= 0:
            return
        self.level_time = max(0.0, self.level_time - delta_time)

    def add_point(self, points: int) -> None:
        """ increases the score"""
        self.scores += points
        if not self.extra_life_given and self.scores >= EXTRA_LIFE_SCORE:
            self.lives += 1
            self.extra_life_given = True

    def eat_pac_dot(self) -> None:
        """add value point of pellet"""
        self.add_point(PELLET_POINTS)

    def eat_Fruit(self) -> None:
        """ add value point of power by pellet"""
        self.add_point(POWER_PELLET_POINTS)
        self.state = SUPER
        self.ghost_combo = 0

    def eat_ghost(self) -> int:
        """ add value of consumed ghost"""
        index = min(self.ghost_combo, len(GHOST_POINTS) - 1)
        points = GHOST_POINTS[index]
        self.ghost_combo += 1
        self.add_point(points)
        return points

    def end_power_mode(self) -> None:
        """ state of end power mode"""
        self.state = NORMAL
        self.ghost_combo = 0

    def lose_life(self) -> None:
        """ managing the loss of a life and the death of Pac-Man"""
        if self.cheat:
            return
        self.lives = max(0, self.lives - 1)
        self.ghost_combo = 0
        self.state = DEAD

    def has_won(self) -> bool:
        """In NORMAL mode, the player wins after the last level."""
        return self.game_mode is GameMode.NORMAL and self.level > MAX_LEVEL

    def next_level(self) -> None:
        """ init the next level"""
        if (self.level - 1) % SPEED_STEP_LEVELS == 0:
            self._speed = self._speed + SPEED_INCREASE
        self.level += 1
        self.ghost_combo = 0
        self.level_time = 0.0
        self.state = NORMAL

    def is_over(self) -> bool:
        """ init the end of game"""
        return self.lives <= 0
