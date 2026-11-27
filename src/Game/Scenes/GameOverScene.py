from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from Game.UI.XpmAlphabet import XpmAlphabet
from Engine.InputHandler.KeyCode import KEY_ESC
from Game.UI.InputBar import InputBar
from Game.GameState.GameStateFactory import GameStateFactory
from Engine.FileManager.Loader import ScoreLoader
from Game.GameState import GameState

FILE_ALPHABET = "assets/alphabet"

BLACK: int = 0xFF000000
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
            game: GameStateFactory, title: str) -> None:
        """ Init Method of the GameOverScene Class """
        super().__init__()
        self.__engine = engine
        self.__display = display
        self.__game = game
        self.__title_font = XpmAlphabet(FILE_ALPHABET)
        self.__title = title
        self.__bar = InputBar(
            0.3, 0.1, max_len=LOGIN_MAX_LEN
        )
        self.__file_manager = engine.file_manager

    @property
    def __stats(self) -> GameState:
        """ The game in progress """
        return self.__game.state

    def render_on_change(self) -> None:
        """ Draw the static part of the scene once """
        self.__bar.reset()
        self.__display.clear_window()
        self.__display.clear(BLACK)
        width = self.__title_font.length_texte(self.__title, spacing=4)
        self.__title_font.write(self.__display,
                                (self.__display.width - width) // 2,
                                self.__display.relative_height(0.1),
                                self.__title,
                                spacing=4)

    def update(
            self, delta_time: float, input_handler: InputHandler
            ) -> None:
        """ Save the score when the player validates a login """
        login = self.__bar.update(input_handler)
        if login is not None:
            self.__file_manager.store(ScoreLoader(
                    self.__stats.score_file,
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

    def __format_time(self) -> str:
        """ Format the time in '00:00:00' model """
        hour: int = int(self.__stats.play_time // 3600)
        minutes: int = int(self.__stats.play_time // 60)
        seconds: int = int(self.__stats.play_time % 60)
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

    def render(self) -> None:
        """ Present the image, then write the texts over it """
        bar_pos = (
            self.__display.relative_width(0.35),
            self.__display.relative_height(0.6),
        )
        self.__bar.render(self.__display, bar_pos)
        self.__display.render()
        self.__bar.render_text(self.__display, bar_pos)
        self.__display.write_text(bar_pos[0] + 100, bar_pos[1] - 70, WHITE,
                                  f"Your score : {self.__stats.scores}")
        self.__display.write_text(bar_pos[0] + 100, bar_pos[1] - 40, WHITE,
                                  f"Your time  : {self.__format_time()}")
