from Engine.SceneManager import Scene
from Engine.Engine import Engine
from Engine.Graphics import MlxDisplay
from Engine.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import (
    KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESC
)

from .UI.Component import Component
from .UI.Selector import Selector
from typing import List


class OptionScene(Scene):
    """
    Option Scene Class Definition

    The Option will be interface for the User to setup some
        configuration within the Game. Like screen resolution and
        keyBindings.
    """

    def __init__(
            self,
            engine: Engine,
            display: MlxDisplay) -> None:
        """ Init Method of the OptionScene. """
        self.__engine: Engine = engine
        self.__display: MlxDisplay = display
        self.__config_option: List[Component] = [
            Selector(
                engine,
                0.9, 0.1,
                self.__engine.get_config_key("available_dimension"),
                "720",
            ),
            Selector(
                engine,
                ["UP", "DOWN", "LEFT", "RIGHT"]
            ),
            Clickable()
        ]
        self.__select_iter: int = 0

    def update(self,
               delta_time: float,
               input_handler: InputHandler) -> None:
        """ Update the Screen using the current frame's input state. """
        if input_handler.was_key_pressed(KEY_UP):
            self.__select_iter = self.__select_iter + 1 % len(
                    self.__config_option
                )
            return
        if input_handler.was_key_pressed(KEY_DOWN):
            self.__select_iter = self.__select_iter - 1
            if self.__select_iter < 0:
                self.__select_iter = len(self.__config_option)
            return
        if input_handler.was_key_pressed(KEY_ENTER):
            self.__config_option[self.__select_iter].callback()
            return
        if input_handler.was_key_pressed(KEY_ESC):
            self.__engine.scene_manager.last_scene()
            return
