from Engine.SceneManager.Scene.Scene import Scene
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import (
    KEY_ESC, KEY_ENTER
)
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Engine import Engine
from typing import List
from ..UI.TextPannel import TextPannel

PANNEL_POSITIONS: tuple[tuple[float, float], ...] = (
    (0.35, 0.4),
    (0.35, 0.45),
    (0.35, 0.5),
)


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
        self.__rebuild_layout()
        self.mark_full_screen_dirty(display)
        self.__pannel: List[TextPannel] = [
                TextPannel(
                    0.4, 0.05,
                    self._start_game).add_label("Start Game"),
                TextPannel(
                    0.4, 0.05,
                    self._leaderboard).add_label("LeaderBoard"),
                TextPannel(
                    0.4, 0.05,
                    self._settings).add_label("Settings"),
                TextPannel(
                    0.4, 0.05,
                    self._exit).add_label("Exit")
            ]

    def __rebuild_layout(self) -> None:
        """Recreate pixel-based menu geometry for the current display size."""
        self.__display.clear(0xFF000000)
        for i, pannel in enumerate(self.__pannel):
            print(f"enumerate i : {i}")
            pannel.render(
                    self.__display,
                    (0.3, 0.4 + (i * 0.1))
                )
        self.__static_layer = self.__display.snapshot()
        self.__select_iter: int = 0

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
        if self.__input.key_capture_active:
            if input_handler.was_key_pressed(KEY_ESC):
                self.__input.end_key_capture()
                self.__input_target = None
                self.__mark_input_dirty()
                return
            keycode = self.__input.capture_key(input_handler)
            if keycode is not None and self.__input_target is not None:
                self.__engine.set_config_key(self.__input_target, keycode)
                self.__input.end_key_capture()
                self.__input_target = None
                self.__mark_input_dirty()
            return

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
        self.__display.clear(0xFFFF0000)
        self.mark_full_screen_dirty(self.__display)

    def render(self) -> None:
        """ Render all the the current frame in the Window """
        if self.dirty_regions:
            self.restore_dirty_regions(self.__display, self.__static_layer)
            self.__display.render()
            self.clear_dirty_regions()

    def __update_selected(self, input_handler: InputHandler) -> None:
        """ Update the selected Component in the Option Scene."""
        component = self.__config_option[self.__select_iter]

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
