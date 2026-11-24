
from Engine.SceneManager import Scene
from Engine.Engine import Engine
from Engine.Graphics import MlxDisplay
from Engine.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_ENTER, KEY_ESC
from ..GameState.GameState import GameMode
from ..GameState.GameStateFactory import GameStateFactory
from ..UI.TextPannel import TextPannel
from ..UI.XpmAlphabet import XpmAlphabet

BLACK: int = 0xFF000000
FILE_ALPHABET: str = "assets/alphabet"
TITLE: str = "select   mode"
TITLE_POSITION: float = 0.1
OPTION_SIZE: tuple[float, float] = (0.4, 0.05)
OPTION_POSITIONS: tuple[tuple[float, float], ...] = (
    (0.3, 0.4),
    (0.3, 0.47),
)

OPTION_MODES: tuple[tuple[GameMode, str], ...] = (
    (GameMode.NORMAL, "ARCADE"),
    (GameMode.INFINITE, "INFINITY"),
)


class ModeScene(Scene):
    """
    Mode Scene Class Definition

    The Mode Scene lets the User choose the game mode before playing.
        UP / DOWN : select ARCADE or INFINITY
        ENTER     : create the game of this mode and start playing
        ESC       : back to the previous scene
    """

    def __init__(
            self,
            engine: Engine,
            display: MlxDisplay,
            game: GameStateFactory) -> None:
        """ Init Method of the ModeScene. """
        super().__init__()
        self.__engine: Engine = engine
        self.__display: MlxDisplay = display
        self.__game: GameStateFactory = game
        self.__title_font: XpmAlphabet = XpmAlphabet(FILE_ALPHABET)
        self.__static_layer: bytes | None = None
        self.__options: list[TextPannel] = [
            TextPannel(*OPTION_SIZE, self._start_arcade),
            TextPannel(*OPTION_SIZE, self._start_infinity),
            ]
        for option, label in zip(self.__options, ("Arcade", "Infinity")):
            option.add_label(label)
        self.__select_iter: int = 0
        self.__options[self.__select_iter].select()
        self.__enter_ready: bool = False

    def update(self,
               delta_time: float,
               input_handler: InputHandler) -> None:
        """ Update the Screen using the current frame's input state. """
        if not input_handler.is_key_down(KEY_ENTER):
            self.__enter_ready = True
        if input_handler.was_key_pressed(
                self.__engine.get_config_key("UP")):
            self.__process_move(-1)
            return
        if input_handler.was_key_pressed(
                self.__engine.get_config_key("DOWN")):
            self.__process_move(1)
            return
        if self.__enter_ready and input_handler.was_key_pressed(KEY_ENTER):
            self.__process_enter()
            return
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.last_scene()

    def render(self) -> None:
        """Restore and redraw only options whose state has changed."""
        if not self.dirty_regions or self.__static_layer is None:
            return

        dirty_regions = self.restore_dirty_regions(
            self.__display, self.__static_layer
        )
        for index, (option, pos) in enumerate(zip(
                self.__options, self.__option_positions())):
            if self.intersects_regions(
                    self.__option_region(index), dirty_regions):
                option.render(self.__display, pos)

        self.__display.render()
        for option, pos in zip(self.__options, self.__option_positions()):
            option.render_label(self.__display, pos)
        self.clear_dirty_regions()

    def render_on_change(self) -> None:
        """Build and snapshot the clean layer on scene entry."""
        self.__enter_ready = False
        self.__display.clear_window()
        self.__display.clear(BLACK)
        self.__render_title()
        self.__static_layer = self.__display.snapshot()
        self.mark_full_screen_dirty(self.__display)

    def on_resolution_changed(self) -> None:
        """Discard size-dependent cached content before the menu is redrawn."""
        self.__static_layer = None
        self.clear_dirty_regions()

    def __process_move(self, step: int) -> None:
        """ Select the previous (-1) or the next (+1) mode. """
        previous = self.__select_iter
        self.__options[self.__select_iter].unselect()
        self.__select_iter = (self.__select_iter + step) % len(self.__options)
        self.__options[self.__select_iter].select()
        self.__mark_option_dirty(previous, self.__select_iter)

    def __process_enter(self) -> None:
        """ Run the callback of the selected pannel. """
        self.__options[self.__select_iter].callback()

    def _start_arcade(self) -> None:
        """ Callback of the Arcade pannel: start a NORMAL game. """
        self.__start(GameMode.NORMAL)

    def _start_infinity(self) -> None:
        """ Callback of the Infinity pannel: start an INFINITE game. """
        self.__start(GameMode.INFINITE)

    def __start(self, mode: GameMode) -> None:
        """ Create the game of this mode and go to the game scene. """
        self.__game.start(mode)
        self.__engine.scene_manager.change_scene("game_scene")

    def __render_title(self) -> None:
        """ Draw the XPM title, centered, in the static layer. """
        width = self.__title_font.length_texte(TITLE)
        self.__title_font.write(
            self.__display,
            (self.__display.width - width) // 2,
            self.__display.relative_height(TITLE_POSITION),
            TITLE,
        )

    def __option_positions(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (
                self.__display.relative_width(x),
                self.__display.relative_height(y),
            )
            for x, y in OPTION_POSITIONS
        )

    def __option_region(self, index: int) -> tuple[int, int, int, int]:
        x, y = self.__option_positions()[index]
        return (
            x,
            y,
            max(1, self.__display.relative_width(OPTION_SIZE[0])),
            max(1, self.__display.relative_height(OPTION_SIZE[1])),
        )

    def __mark_option_dirty(self, *indices: int) -> None:
        self.mark_dirty(*(self.__option_region(index) for index in indices))
