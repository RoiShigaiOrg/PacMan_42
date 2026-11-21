from Engine.SceneManager.Scene.Scene import Scene
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_ENTER
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Engine import Engine
from typing import List
from ..UI.TextPannel import TextPannel

PANNEL_POSITIONS: tuple[tuple[float, float], ...] = (
    (0.3, 0.5),
    (0.3, 0.55),
    (0.3, 0.6),
    (0.3, 0.65),
)
PANNEL_SIZE: tuple[float, float] = (0.4, 0.05)


class MainScene(Scene):
    """
        Main Screen Class Definition

        The Main screen is the hub Scene where we get when starting the Game.
        It contain all path to:
            - Start: Start a new game
            - LeaderBoard: Link to the actual LeaderBoard Scene
            - Option: Link to the Option Scene
            - Quit: Exit the program normally
    """

    def __init__(self, engine: Engine, display: MlxDisplay) -> None:
        """ Init Method of the MainScreen Class """
        super().__init__()
        self.__engine = engine
        self.__display = display
        self.__static_layer: bytes | None = None
        self.__pannel: List[TextPannel] = [
                TextPannel(*PANNEL_SIZE, self._start_game),
                TextPannel(*PANNEL_SIZE, self._leaderboard),
                TextPannel(*PANNEL_SIZE, self._settings),
                TextPannel(*PANNEL_SIZE, self._exit),
            ]
        for pannel, label in zip(
                self.__pannel,
                ("Start Game", "LeaderBoard", "Settings", "Exit"),
        ):
            pannel.add_label(label)
        self.__select_iter = 0
        self.__pannel[self.__select_iter].select()
        self.__rebuild_layout()
        self.mark_full_screen_dirty(display)

    def __rebuild_layout(self) -> None:
        """Cache the clean background for the current display size."""
        self.__display.clear(0xFF000000)
        self.__static_layer = self.__display.snapshot()

    def on_resolution_changed(self) -> None:
        """Refresh menu shapes and their cached background image."""
        self.__rebuild_layout()
        self.clear_dirty_regions()
        self.mark_full_screen_dirty(self.__display)

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """
            MainScene Update Method used to update the position of each object
                in the scene depending on the user input
                and Engine Calculation.
        """
        if input_handler.was_key_pressed(
                self.__engine.get_config_key("UP")):
            self.__process_up()
            return
        if input_handler.was_key_pressed(
                self.__engine.get_config_key("DOWN")):
            self.__process_down()
            return
        if input_handler.was_key_pressed(KEY_ENTER):
            self.__process_enter()
            return

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.__display.clear_window()
        self.__rebuild_layout()
        self.mark_full_screen_dirty(self.__display)

    def render(self) -> None:
        """ Render all the the current frame in the Window """
        if not self.dirty_regions or self.__static_layer is None:
            return

        dirty_regions = self.restore_dirty_regions(
            self.__display, self.__static_layer
        )
        for index, (pannel, pos) in enumerate(zip(
                self.__pannel, self.__pannel_positions()
        )):
            if self.intersects_regions(
                    self.__pannel_region(index), dirty_regions
            ):
                pannel.render(self.__display, pos)

        self.__display.render()
        for pannel, pos in zip(self.__pannel, self.__pannel_positions()):
            pannel.render_label(self.__display, pos)
        self.clear_dirty_regions()

    def __process_up(self) -> None:
        """ Process the Up key for the Option Scene. """
        previous = self.__select_iter
        self.__pannel[self.__select_iter].unselect()
        self.__select_iter = self.__select_iter - 1
        if self.__select_iter < 0:
            self.__select_iter = len(self.__pannel) - 1
        self.__pannel[self.__select_iter].select()
        self.__mark_pannel_dirty(previous, self.__select_iter)

    def __process_down(self) -> None:
        """ Process the Down key for the Option Scene. """
        previous = self.__select_iter
        self.__pannel[self.__select_iter].unselect()
        self.__select_iter = (self.__select_iter + 1) % len(
                self.__pannel
            )
        self.__pannel[self.__select_iter].select()
        self.__mark_pannel_dirty(previous, self.__select_iter)

    def __process_enter(self) -> None:
        """ Process the Enter Key for the Option Scene """
        self.__pannel[self.__select_iter].callback()

    def _start_game(self) -> None:
        """ Go the Game Selection Scene. """
        self.__engine.scene_manager.change_scene("game_scene")

    def _leaderboard(self) -> None:
        """ Go to the LeaderBoard Scene """
        self.__engine.scene_manager.change_scene("leaderboard_scene")

    def _settings(self) -> None:
        """ Go to the Settings Scene """
        self.__engine.scene_manager.change_scene("option_scene")

    def _exit(self) -> None:
        """ Exit the Game """
        self.__display.close()

    def __mark_pannel_dirty(self, *indices: int) -> None:
        self.mark_dirty(*(self.__pannel_region(index) for index in indices))

    def __pannel_positions(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (
                self.__display.relative_width(x),
                self.__display.relative_height(y),
            )
            for x, y in PANNEL_POSITIONS
        )

    def __pannel_region(self, index: int) -> tuple[int, int, int, int]:
        x, y = self.__pannel_positions()[index]
        return (
            x,
            y,
            max(1, self.__display.relative_width(PANNEL_SIZE[0])),
            max(1, self.__display.relative_height(PANNEL_SIZE[1])),
        )
