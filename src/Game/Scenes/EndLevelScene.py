from enum import Enum, auto

from Engine import InputHandler, Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler.KeyCode import KEY_ENTER, KEY_ESC
from Game.GameState.GameStateFactory import GameStateFactory
from Game.UI.XpmAlphabet import XpmAlphabet

FILE_ALPHABET = "assets/alphabet"
BLACK: int = 0xFF000000
WHITE: int = 0xFFFFFFFF
TIME_POINTS_PER_SECOND: int = 10
LIFE_POINTS: int = 200
TIME_STEP_INTERVAL: float = 0.08
LIFE_STEP_INTERVAL: float = 0.35
SCORE_COUNT_RATE: float = 2000.0


class _AnimationPhase(Enum):
    TIME = auto()
    LIVES = auto()
    SCORE = auto()
    COMPLETE = auto()


class EndLevel(Scene):
    """Show the level results and animate the earned bonus points."""

    def __init__(
            self,
            engine: Engine,
            display: MlxDisplay,
            game: GameStateFactory) -> None:
        super().__init__()
        self.__engine = engine
        self.__display = display
        self.game = game
        self.__title_font = XpmAlphabet(FILE_ALPHABET)
        self.__base_layer: bytes | None = None

        self.__cached_level: int = 0
        self.__cached_score: int = 0
        self.__cached_lives: int = 0
        self.__elapsed_time: int = 0
        self.__time_limit: int = 0
        self.__time_bonus: int = 0
        self.__life_bonus: int = 0
        self.__final_score: int = 0
        self.__bonus_applied: bool = False

        self.__phase = _AnimationPhase.TIME
        self.__time_score: int = 0
        self.__lives_counted: int = 0
        self.__life_score: int = 0
        self.__display_score: int = 0
        self.__time_elapsed: float = 0.0
        self.__life_elapsed: float = 0.0
        self.__score_progress: float = 0.0

    def update(
            self,
            delta_time: float,
            input_handler: InputHandler) -> None:
        """Advance the animation or leave the results scene immediately."""
        if input_handler.was_key_pressed(KEY_ENTER):
            self.game.state.next_level()
            if self.game.state.has_won():
                self.__engine.scene_manager.change_scene("victory_scene")
            else:
                self.__engine.scene_manager.change_scene("game_scene")
            return
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.change_scene("main_scene")
            return
        if delta_time <= 0:
            return

        if self.__phase is _AnimationPhase.TIME:
            self.__update_time_bonus(delta_time)
        elif self.__phase is _AnimationPhase.LIVES:
            self.__update_life_bonus(delta_time)
        elif self.__phase is _AnimationPhase.SCORE:
            self.__update_final_score(delta_time)

    def render(self) -> None:
        """Redraw the static background and the currently animated values."""
        if self.__base_layer is None:
            return

        self.__display.restore_region(
            self.__base_layer,
            0,
            0,
            self.__display.width,
            self.__display.height,
        )
        self.__display.render()

        text_x = self.__display.relative_width(0.2)
        self.__display.write_text(
            text_x,
            self.__display.relative_height(0.35),
            WHITE,
            (
                f"Time  {self.__format_time(self.__elapsed_time)} / "
                f"{self.__format_time(self.__time_limit)}  "
                f"+{self.__time_score}"
            ),
        )

        if self.__phase is not _AnimationPhase.TIME:
            self.__display.write_text(
                text_x,
                self.__display.relative_height(0.45),
                WHITE,
                f"Lives  {self.__cached_lives}  +{self.__life_score}",
            )

        if self.__phase in (
                _AnimationPhase.SCORE,
                _AnimationPhase.COMPLETE):
            self.__display.write_text(
                text_x,
                self.__display.relative_height(0.65),
                WHITE,
                f"Score  {self.__display_score}",
            )

    def render_on_change(self) -> None:
        """Prepare the background and award the complete bonus exactly once."""
        self.__apply_bonus_once()
        self.__reset_animation()

        self.__display.clear_window()
        self.__display.clear(BLACK)
        title = "Level Complete"
        title_width = self.__title_font.length_texte(title, spacing=4)
        self.__title_font.write(
            self.__display,
            (self.__display.width - title_width) // 2,
            self.__display.relative_height(0.05),
            title,
            spacing=4,
        )
        self.__display.fill_rect(
            self.__display.relative_width(0.2),
            self.__display.relative_height(0.6),
            self.__display.relative_width(0.6),
            max(1, self.__display.relative_height(0.002)),
            WHITE,
        )
        self.__base_layer = self.__display.snapshot()
        self.__display.render()

    def __apply_bonus_once(self) -> None:
        """Calculate the earned bonuses and apply them to the game score."""
        if (
                self.__bonus_applied
                and self.game.state.level == self.__cached_level
                and self.game.state.scores >= self.__final_score):
            return

        self.__cached_level = self.game.state.level
        self.__cached_score = self.game.state.scores
        self.__cached_lives = max(0, self.game.state.lives)
        self.__time_limit = max(
            0, int(self.__engine.get_config_key("level_time"))
        )
        remaining_time = min(
            float(self.__time_limit), max(0.0, self.game.state.level_time)
        )
        remaining_seconds = min(
            self.__time_limit, max(0, int(remaining_time))
        )
        self.__elapsed_time = self.__time_limit - remaining_seconds
        self.__time_bonus = remaining_seconds * TIME_POINTS_PER_SECOND
        self.__life_bonus = self.__cached_lives * LIFE_POINTS
        self.__final_score = (
            self.__cached_score + self.__time_bonus + self.__life_bonus
        )
        self.game.state.scores = self.__final_score
        self.__bonus_applied = True

    def __reset_animation(self) -> None:
        """Reset only the display counters; the awarded score stays applied."""
        self.__phase = _AnimationPhase.TIME
        self.__time_score = 0
        self.__lives_counted = 0
        self.__life_score = 0
        self.__display_score = self.__cached_score
        self.__time_elapsed = 0.0
        self.__life_elapsed = 0.0
        self.__score_progress = 0.0

    def __update_time_bonus(self, delta_time: float) -> None:
        if self.__time_bonus == 0:
            self.__phase = _AnimationPhase.LIVES
            return

        self.__time_elapsed += delta_time
        while (
                self.__time_elapsed >= TIME_STEP_INTERVAL
                and self.__time_score < self.__time_bonus):
            self.__time_elapsed -= TIME_STEP_INTERVAL
            self.__time_score += TIME_POINTS_PER_SECOND

        if self.__time_score >= self.__time_bonus:
            self.__time_score = self.__time_bonus
            self.__phase = _AnimationPhase.LIVES

    def __update_life_bonus(self, delta_time: float) -> None:
        if self.__lives_counted >= self.__cached_lives:
            self.__phase = _AnimationPhase.SCORE
            return

        self.__life_elapsed += delta_time
        while (
                self.__life_elapsed >= LIFE_STEP_INTERVAL
                and self.__lives_counted < self.__cached_lives):
            self.__life_elapsed -= LIFE_STEP_INTERVAL
            self.__lives_counted += 1
            self.__life_score += LIFE_POINTS

        if self.__lives_counted >= self.__cached_lives:
            self.__life_score = self.__life_bonus
            self.__phase = _AnimationPhase.SCORE

    def __update_final_score(self, delta_time: float) -> None:
        if self.__display_score >= self.__final_score:
            self.__display_score = self.__final_score
            self.__phase = _AnimationPhase.COMPLETE
            return

        self.__score_progress += delta_time * SCORE_COUNT_RATE
        increment = int(self.__score_progress)
        if increment <= 0:
            return
        self.__score_progress -= increment
        self.__display_score = min(
            self.__final_score, self.__display_score + increment
        )
        if self.__display_score >= self.__final_score:
            self.__phase = _AnimationPhase.COMPLETE

    @staticmethod
    def __format_time(time: int) -> str:
        """Format a duration as ``HH:MM:SS``."""
        hours, remainder = divmod(max(0, time), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
