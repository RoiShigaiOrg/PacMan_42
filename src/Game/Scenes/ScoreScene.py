from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from Game.UI.XpmAlphabet import XpmAlphabet
from Engine.InputHandler.KeyCode import KEY_ESC, KEY_LEFT, KEY_RIGHT
from Engine.FileManager.Loader import ScoreLoader
from Game.GameState import GameState, GameMode

FILE_ALPHABET = "assets/alphabet"

WHITE: int = 0xFFFFFFFF
NB_SCORES: int = 10
LINE_HEIGHT: int = 25
CHAR_WIDTH: int = 10
FRAMES_BETWEEN_LINES: int = 4

BLACK: int = 0xFF000000

ROW_COLORS: tuple[int, ...] = (
    0xFFFF0000,
    0xFFFFB8FF,
    0xFF00FFFF,
    0xFFFFB852,
)

Row = tuple[str, str, str, str]


class ScoreScene(Scene):
    """
        Score Scene Class Definition

        Show the best scores saved in the leaderboard file.
    """
    def __init__(self, engine: Engine, display: MlxDisplay,
                 stats: GameState, can_switch: bool = False) -> None:
        """"""
        self.__engine = engine
        self.__display = display
        self.__title_font = XpmAlphabet(FILE_ALPHABET)
        self.__rows: list[Row] = []
        self.__next_row: int = 0
        self.__wait: int = 0
        self.stats = stats
        self.__ready: bool = False
        self.__can_switch = can_switch

    def render_on_change(self) -> None:
        """ Load the scores and draw the whole leaderboard once """
        self.__ready = False
        self.__mode = self.stats.game_mode
        self.__show()

    def update(
            self, delta_time: float,
            input_handler: InputHandler) -> None:
        """quit the scene when press ESC"""
        if not input_handler.is_key_down(KEY_ESC):
            self.__ready = True
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.change_scene("main_scene")
        if self.__can_switch and (
                input_handler.was_key_pressed(KEY_LEFT)
                or input_handler.was_key_pressed(KEY_RIGHT)):
            self.__mode = self.__other_mode()
            self.__show()

    def render(self) -> None:
        """it displays the image prepared in render_on_change"""
        if self.__wait > 0:
            self.__wait -= 1
            return
        if self.__next_row == -1:
            self.__write_mode()
        elif self.__next_row < len(self.__rows):
            self.__write_row(self.__next_row)
        else:
            return
        self.__next_row += 1
        self.__wait = FRAMES_BETWEEN_LINES

    def __other_mode(self) -> GameMode:
        """ The mode after the current one (and back to the first) """
        modes = list(GameMode)
        return modes[(modes.index(self.__mode) + 1) % len(modes)]

    def __show(self) -> None:
        """ Draw the title, load the scores of self.__mode """
        self.__display.clear_window()
        self.__display.clear(BLACK)
        title = "high scores"
        width = self.__title_font.length_texte(title, spacing=4)
        self.__title_font.write(self.__display,
                                (self.__display.width - width) // 2,
                                self.__display.relative_height(0.05),
                                title,
                                spacing=4)
        self.__display.render()
        scores = self.__engine.file_manager.load(
            ScoreLoader(self.stats.SCORE_FILES[self.__mode]))["scores"]
        scores.sort(key=lambda entry: int(entry.get("score", 0)),
                    reverse=True)
        self.__rows = []
        for rank, entry in enumerate(scores[:NB_SCORES], start=1):
            minutes, seconds = divmod(int(entry.get("time", 0)), 60)
            self.__rows.append((
                str(rank),
                str(entry.get("login") or "---"),
                f"{minutes}:{seconds:02d}",
                str(int(entry.get("score", 0))),
            ))
        while len(self.__rows) < NB_SCORES:
            rank = len(self.__rows) + 1
            self.__rows.append((str(rank), "---", "0:00", "0"))
        self.__next_row = -1
        self.__wait = FRAMES_BETWEEN_LINES

    def __write_mode(self) -> None:
        """ The name of the mode, with arrows if it can be switched """
        name = self.__mode.name
        text = f"<- {name} ->" if self.__can_switch else name
        x = (self.__display.width - len(text) * CHAR_WIDTH) // 2
        y = self.__display.height // 2 - 70
        self.__display.write_text(x, y, WHITE, text)

    def __write_row(self, index: int) -> None:
        """ Write the 4 columns of one row, in the color of the row """
        rank, login, time, score = self.__rows[index]
        color = ROW_COLORS[index % len(ROW_COLORS)]
        y = self.__display.relative_height(0.5) + index * LINE_HEIGHT
        columns = (
            (self.__display.relative_width(0.28), rank),
            (self.__display.relative_width(0.34), login),
            (self.__display.relative_width(0.58), time),
            (self.__display.relative_width(0.75) - len(score) * CHAR_WIDTH,
             score),
        )
        for x, text in columns:
            self.__display.write_text(x, y, color, text)
