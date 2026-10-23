from Engine.SceneManager.Scene.Scene import Scene
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import (
    KEY_V, KEY_ESC, KEY_C, KEY_N
)
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Graphics.Components.Rect import Rect
from Engine.Graphics.Components.TextBox import TextBox
from Engine.Graphics.Components.TextJustify import TEXT_CENTER
from Engine.Engine import Engine


Region = tuple[int, int, int, int]


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
        self.__engine = engine
        self.__display = display
        self.__rect: Rect = Rect(
                self.__display.relative_width(0.3),
                self.__display.relative_height(0.05),
                self.__display.relative_width(0.3),
                self.__display.relative_height(0.4),
                0xFF0000FF
            )
        self.__rect2: Rect = Rect(
                self.__display.relative_width(0.3),
                self.__display.relative_height(0.05),
                self.__display.relative_width(0.3),
                self.__display.relative_height(0.6),
                0xFF0000FF
            )
        self.__rect3: Rect = Rect(
                self.__display.relative_width(0.3),
                self.__display.relative_height(0.05),
                self.__display.relative_width(0.3),
                self.__display.relative_height(0.8),
                0xFF0000FF
            )
        self.__rect.add_text(
                TextBox("Press C to MapScene", 0xFFFFFFFF),
                TEXT_CENTER
            )
        self.__rect2.add_text(
                TextBox("Press V to TestScene", 0xFFFFFFFF),
                TEXT_CENTER
            )
        self.__rect3.add_text(
                TextBox("Press ESC to TestScene", 0xFFFFFFFF),
                TEXT_CENTER
            )
        self.__display.clear(0xFFFF0000)
        self.__rect.draw(self.__display)
        self.__rect2.draw(self.__display)
        self.__rect3.draw(self.__display)
        self.__display.render()

        self.__rect.draw_text(self.__display)
        self.__rect2.draw_text(self.__display)
        self.__rect3.draw_text(self.__display)
        self.__display.render()
        self.__dirty_region: Region | None = (
            0, 0, display.width, display.height
        )

        self.__static_layer = self.__display.snapshot()

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """
            MainScene Update Method used to update the position of each object
                in the scene depending on the user input
                and Engine Calculation.
        """
        if input_handler.was_key_pressed(KEY_C):
            self.__engine.scene_manager.change_scene("game_scene")
        if input_handler.was_key_pressed(KEY_V):
            self.__engine.scene_manager.change_scene("test_scene")
        if input_handler.was_key_pressed(KEY_N):
            self.__engine.scene_manager.change_scene("game_over_scene")
        if input_handler.was_key_pressed(KEY_ESC):
            self.__display.close()

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.__dirty_region = (
            0, 0, self.__display.width, self.__display.height
        )

    def render(self) -> None:
        """ Render all the the current frame in the Window """
        if self.__dirty_region is not None:
            x, y, width, height = self.__dirty_region
            self.__display.restore_region(
                self.__static_layer, x, y, width, height
            )
            self.__rect.draw(self.__display)
            self.__display.render()
            self.__rect.draw_text(self.__display)
            self.__rect2.draw(self.__display)
            self.__rect2.draw_text(self.__display)
            self.__rect3.draw(self.__display)
            self.__rect3.draw_text(self.__display)
            self.__dirty_region = None
