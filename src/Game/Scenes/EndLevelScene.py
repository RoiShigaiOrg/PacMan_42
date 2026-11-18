from Engine.InputHandler.KeyCode import KEY_ENTER, KEY_ESC
from Engine import InputHandler
from Engine.Graphics import Rect, Line
from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Game.GameState import GameState
from Game.UI.XpmAlphabet import XpmAlphabet
from Engine.Graphics import TextBox

FILE_ALPHABET = "assets/alphabet"


class EndLevel(Scene):
    """
        EndLevel Scene Class Definition

        This Scene will appear when the player completed
            one level and will display and calculate the
            bonus point depending on the remaining time of
            the level and the remaining life of the player.
    """

    def __init__(
            self,
            engine: Engine,
            display: MlxDisplay,
            stats: GameState) -> None:
        """ Init Method of the EndLevel Class """
        self.__engine = engine
        self.__display = display
        self.stats = stats
        self.__title_font = XpmAlphabet(FILE_ALPHABET)
        self.__time_score: int = 0
        self.__life_score: int = 0
        self.__calculate_time: bool = False
        self.__calculate_lives: bool = False
        self.__cached_score: int = 0
        self.__bonus_score: int = 0
        self.__bonus_time_rect: Rect = Rect(
                display.relative_width(0.4),
                display.relative_height(0.1),
                display.relative_width(0.2),
                display.relative_height(0.1),
                0x000000
            )
        self.__div_bar: Line = Line(
                (display.relative_width(0.2),
                 display.relative_height(0.6)),
                (display.relative_width(0.6),
                 display.relative_height(0.6)),
                display.relative_width(0.6),
                display.relative_height(0.6),
                0xFFFFFFFF
                )
        self.__bonus_life_rect: Rect = Rect(
                display.relative_width(0.4),
                display.relative_height(0.1),
                display.relative_width(0.2),
                display.relative_height(0.1),
                0x000000
            )
        self.__score_rect: Rect = Rect(
                display.relative_width(0.8),
                display.relative_height(0.1),
                display.relative_width(0.2),
                display.relative_height(0.1),
                0x000000
            )
        self._iterator: int = 0

    def update(
            self,
            delta_time: float,
            input_handler: InputHandler) -> None:
        """ Update the screen with the user inputs """
        if input_handler.was_key_pressed(KEY_ENTER):
            self.__engine.scene_manager.change_scene("game_scene")
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.change_scene("main_scene")

    def render(self) -> None:
        """ Render the all elements of the scene """
        if not self.__calculate_time:
            self.__cached_time -= 1
            if self.__cached_time <= 0:
                self.__calculate_time = True
        self.__bonus_time_rect.add_text(
                    TextBox(f"Time  {self.__format_time(self.__cached_time)}\t{self.__time_score}", 0xFFFFFFFF)
                )
        self.__bonus_life_rect.draw(self.__display)
        if self.__calculate_time:
            self.__bonus_life_rect.add_text(
                    TextBox(f"Lives  {self.__cached_lives}\t{self.__life_score}", 0xFFFFFFFF)    
                )
            if self.__cached_lives - self._iterator > 0:
                self._iterator += 1
                self.__life_score += 200 * self._iterator
                self.__bonus_life_rect.draw(self.__display)
            else:
                self.__calculate_lives = True

        if self.__calculate_time and self.__calculate_lives:
            self.__div_bar.draw(self.__display)
            self.__score_rect.add_text(
                    TextBox(f"Score  {self.__cached_score + self.__bonus_score}", 0xFFFFFFFF)
                )
            self.__score_rect.draw(self.__display)
            if self.__cached_score + self.__bonus_score < self.stats.scores:
                self.__bonus_score += 1

    def render_on_change(self) -> None:
        """
        Render on Change method
        This method will render the statis frame of the scene to avoid
            constant high compute of rendering
        Calculate the bonus scores directly so the player can pass the
            score animation to the next level directly
        """
        self.__display.clear_window()
        self.__display.clear(0xFF000000)
        title = "Level Complete"
        width = self.__title_font.length_texte(title, spacing=4)
        self.__title_font.write(
                        self.__display, (self.__display.width - width) // 2,
                        self.__display.relative_height(0.05),
                        title,
                        spacing=4
                    )
        self.__display.render()
        self.__cached_score: int = self.stats.scores
        self.__cached_time: int = int(self.stats.level_time)
        self.__cached_lives: int = self.stats.lives
        self.stats.scores += self.__cached_lives * 200
        bonus_time: int = self.__engine.get_config_key("level_time")
        bonus_time = int(bonus_time - self.__cached_time)
        if bonus_time > 0:
            self.stats.scores += int(bonus_time * 10)

    def __format_time(self, time: float) -> str:
        """ Format the time in '00:00:00' model """
        hour: int = int(time // 3600)
        minutes: int = int(time // 60)
        seconds: int = int(time % 60)
        res: str = ""

        if hour < 10:
            res = f"{res}0{hour}:"
        else:
            res = f"{res}{hour}:"
        if minutes < 10:
            res = f"{res}0{minutes}:"
        else:
            res = f"{res}{minutes}:"
        if seconds < 10:
            res = f"{res}0{seconds}"
        else:
            res = f"{res}{seconds}"
        return res

    def __reset_values(self) -> None:
        """ Reset the computed values of the Scene """
        self.__time_score = 0
        self.__life_score = 0
        self.__calculate_time = False
        self.__calculate_lives = False
        self.__cached_score = 0
        self.__bonus_score = 0
