from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from Game.UI.XpmAlphabet import XpmAlphabet
from Engine.InputHandler.KeyCode import KEY_ESC
from Game.UI.InputBar import InputBar
from Game.GameState import GameState
from Engine.FileManager.Loader import ScoreLoader

FILE_ALPHABET = "assets/alphabet"

BLACK: int = 0xFF000000
BLUE: int = 0xFF0000FF
WHITE: int = 0xFFFFFFFF
LOGIN_MAX_LEN: int = 18


class GameOverScene(Scene):
    """
        Game Over Scene Class Definition

        Displayed at the end of a game: show the score and let the
            player type a login to save it in the leaderboard.
    """

    def __init__(
            self, engine: Engine, display: MlxDisplay,
            stats: GameState) -> None:
        """ Init Method of the GameOverScene Class """
        self.__engine = engine
        self.__display = display
        self.__stats = stats
        self.__title_font = XpmAlphabet(FILE_ALPHABET)
        width = display.relative_width(0.3)
        self.__bar = InputBar(
            (display.width - width) // 2,
            display.relative_height(0.5),
            width,
            LOGIN_MAX_LEN
        )
        self.__file_manager = engine.file_manager

    def render_on_change(self) -> None:
        """ Draw the static part of the scene once """
        self.__bar.text = ""
        self.__display.clear_window()
        self.__display.clear(BLACK)
        title = "game  over"
        width = self.__title_font.length_texte(title, spacing=4)
        self.__title_font.write(self.__display,
                                (self.__display.width - width) // 2,
                                self.__display.relative_height(0.1),
                                title,
                                spacing=4)
        self.__bar.draw(self.__display, BLACK, BLUE)

    def update(
            self, delta_time: float, input_handler: InputHandler
            ) -> None:
        """ Save the score when the player validates a login """
        login = self.__bar.update(input_handler)
        if login == "None":
            return "error name can´t be 'None'"
        if login is not None:
            self.__file_manager.store(ScoreLoader(
                    self.__stats.SCORE_FILES[self.__stats.game_mode],
                    score={"login": login,
                           "score": self.__stats.scores,
                           "time": int(self.__stats.play_time)}))
            self.__leave("score_scene")
        elif input_handler.was_key_pressed(KEY_ESC):
            self.__leave("main_scene")

    def __leave(self, scene: str) -> None:
        """ Reset the statistics for the next game and go back to the menu """
        self.__stats.reset_stats()
        self.__engine.scene_manager.change_scene(scene)

    def render(self) -> None:
        """ Present the image, then write the texts over it """
        self.__display.render()
        self.__bar.draw_text(self.__display, WHITE)
        self.__display.write_text(self.__bar.x + 100, self.__bar.y - 70, WHITE,
                                  f"Your score : {self.__stats.scores}")
        self.__display.write_text(self.__bar.x + 100, self.__bar.y - 40, WHITE,
                                  f"Your time  : {self.__stats.play_time}")
