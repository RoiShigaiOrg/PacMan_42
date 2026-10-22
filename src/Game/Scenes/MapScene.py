from Engine import Scene
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_ESC, KEY_C
from ..MapGeneration.MapGeneration import Map
from Engine.Engine import Engine


Region = tuple[int, int, int, int]


class MapScene(Scene):
    """A class for drawing the map based on the Map object:
      handling the size of corridors, walls, corners, colors, etc."""

    def __init__(self, engine: Engine, display: MlxDisplay) -> None:
        self.__engine = engine
        self.display = display
        self.map = Map()
        self.display.clear(0xFFFF0000)
        self.map.draw(
                display,
                self.display.relative_width(0.1),
                self.display.relative_height(0.1),
                self.display.relative_width(0.8),
                self.display.relative_height(0.8),
                )
        self.__dirty_region: Region | None = (
            0, 0, display.width, display.height
        )
        self.__static_layer = self.display.snapshot()

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        """ Update method for the MapScene Object """
        if input_handler.was_key_pressed(KEY_C):
            self.__engine.scene_manager.change_scene("main_scene")
        if input_handler.was_key_pressed(KEY_ESC):
            self.display.close()

    def render(self) -> None:
        """ Render Method for the MapScene Object"""
        if self.__dirty_region is not None:
            x, y, width, height = self.__dirty_region
            self.display.restore_region(
                self.__static_layer, x, y, width, height
            )
            self.__dirty_region = None
        self.display.render()

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.display.clear_window()
        self.display.clear(0xFFFF0000)
        self.__dirty_region = (
            0, 0, self.display.width, self.display.height
        )
