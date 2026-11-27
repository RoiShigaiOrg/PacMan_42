from functools import partial
from Engine.SceneManager import Scene
from Engine.Engine import Engine
from Engine.Graphics import MlxDisplay
from Engine.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_ENTER, KEY_ESC
from ..GameState.GameState import GameMode
from ..GameState.GameStateFactory import GAME_STATES, GameStateFactory
from ..UI.TextPannel import TextPannel
from ..UI.XpmAlphabet import XpmAlphabet

BLACK: int = 0xFF000000
WHITE: int = 0xFFFFFFFF
GREY: int = 0xFF9A9A9A
FILE_ALPHABET: str = "assets/alphabet"
TITLE: str = "select   mode"
TITLE_POSITION: float = 0.1
OPTION_SIZE: tuple[float, float] = (0.4, 0.05)
OPTION_X: float = 0.3
OPTION_FIRST_Y: float = 0.4
OPTION_STEP_Y: float = 0.07
DESCRIPTION_Y: float = 0.65
HINT: str = "ESC : main menu"
HINT_Y: float = 0.9
CHAR_WIDTH: int = 10
TEXT_HEIGHT: int = 20


MODE_TEXTS: dict[GameMode, tuple[str, str]] = {
    GameMode.ARCADE: ("Arcade", "Clear every level to win"),
    GameMode.INFINITE: ("Infinity", "Endless levels, survive"),
}


class ModeScene(Scene):
    """
    Mode Scene Class Definition

    The Mode Scene lets the User choose the game mode before playing.
        The menu lists every mode of GAME_STATES, with a short
        description of the selected one.
        UP / DOWN : select a mode (keys read from the engine config)
        ENTER     : create the game of this mode and open its map
        ESC       : back to the MainScene

    The MLX writes at most 64 characters per frame: the labels, the
        description and the hint must stay short.
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
        self.__modes: tuple[GameMode, ...] = tuple(GAME_STATES)
        self.__options: list[TextPannel] = []
        for mode in self.__modes:
            option = TextPannel(*OPTION_SIZE, partial(self.__start, mode))
            option.add_label(MODE_TEXTS[mode][0])
            self.__options.append(option)
        self.__select_iter: int = 0
        self.__options[self.__select_iter].select()
        self.__enter_ready: bool = False

    def update(self,
               delta_time: float,
               input_handler: InputHandler) -> None:
        """ Update the Screen using the current frame's input state. """
        # The ENTER that opened this scene must be released first
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
            self.__options[self.__select_iter].callback()
            return
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.change_scene("main_scene")

    def render(self) -> None:
        """Restore and redraw only what changed, then write the texts."""
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
        self.__write_centered(self.__description(), DESCRIPTION_Y, WHITE)
        self.__write_centered(HINT, HINT_Y, GREY)
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
        self.mark_dirty(self.__text_region(DESCRIPTION_Y))

    def __start(self, mode: GameMode) -> None:
        """ Create the game of this mode and open its map. """
        self.__game.start(mode)
        self.__engine.scene_manager.change_scene("game_scene")

    def __description(self) -> str:
        """ The explanation of the selected mode. """
        return MODE_TEXTS[self.__modes[self.__select_iter]][1]

    def __render_title(self) -> None:
        """ Draw the XPM title, centered, in the static layer. """
        width = self.__title_font.length_texte(TITLE)
        self.__title_font.write(
            self.__display,
            (self.__display.width - width) // 2,
            self.__display.relative_height(TITLE_POSITION),
            TITLE,
        )

    def __write_centered(self, text: str, y: float, color: int) -> None:
        """ Write one line of text, centered in the window. """
        x = (self.__display.width - len(text) * CHAR_WIDTH) // 2
        self.__display.write_text(
            x, self.__display.relative_height(y), color, text)

    def __text_region(self, y: float) -> tuple[int, int, int, int]:
        """ The full-width strip where a centered line is written. """
        return (0, self.__display.relative_height(y),
                self.__display.width, TEXT_HEIGHT)

    def __option_positions(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (
                self.__display.relative_width(OPTION_X),
                self.__display.relative_height(
                    OPTION_FIRST_Y + index * OPTION_STEP_Y),
            )
            for index in range(len(self.__options))
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
