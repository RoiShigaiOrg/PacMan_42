from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from ..UI.XpmAlphabet import XpmAlphabet
from Engine.InputHandler.KeyCode import KEY_ESC
from ..UI.InputBar import InputBar

FILE_ALPHABET_SMALL = "assets/alphabet_small"
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

    def __init__(self, engine: Engine, display: MlxDisplay) -> None:
        """ Init Method of the GameOverScene Class """
        self.__engine = engine
        self.__display = display
        self.score: int = 0
        self.__title_font = XpmAlphabet(FILE_ALPHABET)
        width = display.relative_width(0.3)
        self.__bar = InputBar(
            (display.width - width) // 2,
            display.relative_height(0.5),
            width,
            XpmAlphabet(FILE_ALPHABET_SMALL),
            LOGIN_MAX_LEN
        )

    def render_on_change(self) -> None:
        """ Draw the static part of the scene once """
        self.__bar.text = ""
        self.__display.clear(BLACK)
        title = "game  over"
        width = self.__title_font.length_texte(title)
        self.__title_font.write(self.__display,
                                (self.__display.width - width) // 2,
                                self.__display.relative_height(0.1), title)
        self.__bar.draw(self.__display, BLACK, BLUE)

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """ Save the score when the player validates a login """
        login = self.__bar.update(input_handler)
        if login is not None:
            self.__engine.file_manager.store_score(login, self.score)
            self.__engine.scene_manager.change_scene("main_scene")
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.change_scene("main_scene")

    def render(self) -> None:
        """ Present the image, then write the texts over it """
        self.__bar.draw_text(self.__display, BLACK, WHITE)
        self.__display.render()
        self.__display.write_text(self.__bar.x, self.__bar.y - 20, WHITE,
                                  f"Your score : {self.score}")
