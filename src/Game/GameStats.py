

PELLET_POINTS: int = 10
POWER_PELLET_POINTS: int = 50
GHOST_POINTS: tuple[int, ...] = (200, 400, 800, 1600)
EXTRA_LIFE_SCORE: int = 10000

NORMAL = "normal"
SUPER = "super"
DEAD = "dead"


class GameStats:
    def __init__(self, lives: int = 3) -> None:
        """init class variables"""
        self.__start_lives = lives
        self.game_infinit: bool = False
        self.cheat: bool = False
        self.reset_stats()

    def reset_stats(self) -> None:
        """ initialize variables for the start of a game/level"""
        self.lives: int = self.__start_lives
        self.scores: int = 0
        self.level: int = 1
        self.ghost_combo: int = 0
        self.extra_life_given: bool = False
        self.state: str = NORMAL
        self.level_time: float = 0.0

    def game_mod(self, mode: bool) -> None:
        """ select Infinite/Normal mode"""
        self.game_infinit = mode

    def cheat_mod(self, cheat: bool) -> None:
        """ select cheat/normal mode"""
        self.cheat = cheat

    def time_in_level(self, delta_time: float) -> None:
        """Call once per frame from the scene's update()."""
        self.level_time += delta_time

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
        if not self.game_infinit:
            self.lives = max(0, self.lives - 1)
        self.ghost_combo = 0
        self.state = DEAD

    def next_level(self) -> None:
        """ init the next level"""
        self.level += 1
        self.ghost_combo = 0
        self.level_time = 0.0
        self.state = NORMAL

    def is_over(self) -> bool:
        """ init the end of game"""
        return self.lives <= 0
