from Engine.SceneManager.Scene.Scene import Scene
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_S, KEY_Z, KEY_ESC, KEY_Q, KEY_D
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Graphics.Components.Rect import Rect
from Engine.Graphics.Components.Circle import Circle
from Engine.Graphics.Components.Line import Line
from Engine.Graphics.Components.TextBox import TextBox
from Engine.Graphics.Components.TextJustify import TEXT_CENTER
from typing import Tuple


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

    def __init__(self, display: MlxDisplay) -> None:
        """ Init Method of the MainScreen Class """
        self.__display = display
        self.__rect: Rect = Rect(480, 312, 50, 50, 0xFF0000FF)
        self.__circle: Circle = Circle(80, 80, 0xFF00FFFF)
        self.__line: Line = Line((220, 400), (930, 300), 0xFF00FF00)
        self.__rect.add_text(TextBox("TEST", 0xFFFFFFFF), TEXT_CENTER)
        self.__dirty_region: Region | None = (
            0, 0, display.width, display.height
        )

        self.__display.clear(0xFFFF0000)
        self.__circle.draw(self.__display, 1200, 240)
        self.__circle.fill(self.__display, 1200, 240)
        self.__line.draw(self.__display, 0, 0)
        self.__static_layer = self.__display.snapshot()

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """
            MainScene Update Method used to update the position of each object
                in the scene depending on the user input
                and Engine Calculation.
        """
        old_pos: Tuple[int, int] = self.__rect.pos

        if input_handler.is_key_down(KEY_S):
            self.__rect.update_pos(old_pos[0], old_pos[1] + 5)
        if input_handler.is_key_down(KEY_Z):
            self.__rect.update_pos(old_pos[0], old_pos[1] - 5)
        if input_handler.is_key_down(KEY_D):
            self.__rect.update_pos(old_pos[0] + 5, old_pos[1])
        if input_handler.is_key_down(KEY_Q):
            self.__rect.update_pos(old_pos[0] - 5, old_pos[1])
        if input_handler.is_key_down(KEY_ESC):
            self.__display.close()

        if old_pos != self.__rect.pos:
            self.__dirty_region = self.union_regions(
                self.__dirty_region,
                self.movement_region(self.__rect.size, old_pos),
                self.movement_region(self.__rect.size, self.__rect.pos),
            )

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
            self.__dirty_region = None

