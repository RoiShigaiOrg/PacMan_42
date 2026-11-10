from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from ..UI.XpmAlphabet import (
    XpmAlphabet,
    FILL,
    SHADOW)
from Engine.InputHandler.KeyCode import KEY_ESC
from Engine.FileManager.Loader import ScoreLoader

FILE_ALPHABET_SMALL = "assets/alphabet_small"
FILE_ALPHABET = "assets/alphabet"

ROW_COLORS: tuple[int, ...] = (
    0xFFFF0000,
    0xFFFFB8FF,
    0xFF00FFFF,
    0xFFFFB852,
)

NB_SCORES: int = 10
LINE_SPACING: int = 12

BLACK: int = 0xFF000000


class ScoreScene(Scene):
    def __init__(self, engine: Engine, display: MlxDisplay) -> None:
        """"""
        self.__engine = engine
        self.__display = display
        self.__title_font = XpmAlphabet(FILE_ALPHABET)
        self.__text_font = XpmAlphabet(FILE_ALPHABET_SMALL)

    def render_on_change(self) -> None:
        """ Load the scores and draw the whole leaderboard once """
        self.__display.clear_window()
        self.__display.clear(BLACK)

        title = "best scores"
        width = self.__title_font.length_texte(title)
        self.__title_font.write(self.__display,
                                (self.__display.width - width) // 2,
                                self.__display.relative_height(0.05), title)

        scores = self.__engine.file_manager.load(ScoreLoader())["scores"]
        scores.sort(key=lambda entry: int(entry.get("score", 0)),
                    reverse=True)
        x_rank = self.__display.relative_width(0.28)
        x_login = self.__display.relative_width(0.34)
        x_score = self.__display.relative_width(0.72)
        y = self.__display.relative_height(0.28)
        line_height = self.__text_font.height + LINE_SPACING

        if not scores:
            self.__write(x_login, y, "no score yet")
        for rank, entry in enumerate(scores[:NB_SCORES], start=1):
            color = ROW_COLORS[(rank - 1) % len(ROW_COLORS)]
            palette = {FILL: color, SHADOW: BLACK}
            score = str(int(entry.get("score", 0)))
            self.__write(x_rank, y, str(rank), palette)
            self.__write(x_login, y, str(entry.get("login", "?")), palette)
            self.__write(x_score - self.__text_font.length_texte(score,
                                                                 spacing=1),
                         y, score, palette)
            y += line_height

    def __write(self, x: int, y: int, text: str,
                colors: dict[int, int] | None = None) -> None:
        """ Draw a line of text with the small alphabet """
        self.__text_font.write(self.__display, x, y, text,
                               spacing=1, colors=colors)

    def update(
            self, delta_time: float,
            input_handler: InputHandler) -> None:
        """quit the scene when press ESC"""
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.change_scene("main_scene")

    def render(self) -> None:
        """it displays the image prepared in render_on_change"""
        self.__display.render()
