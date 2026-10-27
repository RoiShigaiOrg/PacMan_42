from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from ..GameStats import GameStats
from Engine.InputHandler.KeyCode import KEY_ESC, KEY_C
from ..MapGeneration.MapGeneration import Map
from ..MapGeneration import (
        RELATIVE_MAP_POS_X,
        RELATIVE_MAP_POS_Y,
        RELATIVE_MAP_WIDTH,
        RELATIVE_MAP_HEIGHT
        )
from ..Player.Player import Player


Region = tuple[int, int, int, int]


class MapScene(Scene):
    """A class for drawing the map based on the Map object:
      handling the size of corridors, walls, corners, colors, etc."""

    def __init__(
            self, engine: Engine,
            display: MlxDisplay, stats: GameStats) -> None:
        self.__engine = engine
        self.stats = stats
        self.display = display
        self.map = Map()
        self.display.clear(0xFFFF0000)
        self.map.set_colliders(
                self.display.relative_width(RELATIVE_MAP_POS_X),
                self.display.relative_height(RELATIVE_MAP_POS_Y),
                self.display.relative_width(RELATIVE_MAP_WIDTH),
                self.display.relative_height(RELATIVE_MAP_HEIGHT),
            )
        self.map.draw(
                display,
                self.display.relative_width(RELATIVE_MAP_POS_X),
                self.display.relative_height(RELATIVE_MAP_POS_Y),
                self.display.relative_width(RELATIVE_MAP_WIDTH),
                self.display.relative_height(RELATIVE_MAP_HEIGHT),
                )
        self.__player: Player = Player()
        self.__player.InitPlayer(display, self.map)
        self.__physics = engine.physics
        self.__dirty_region: Region | None = (
            0, 0, display.width, display.height
        )
        self.__static_layer = self.display.snapshot()

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        """ Update method for the MapScene Object """
        self.stats.time_in_level(delta_time)
        if self.stats.is_over():
            self.__engine.scene_manager.change_scene("game_over_scene")
            return
        if input_handler.was_key_pressed(KEY_C):
            self.__engine.scene_manager.change_scene("main_scene")
        if input_handler.was_key_pressed(KEY_ESC):
            self.display.close()
        old_position = self.__player.position
        old_center = self.__player.collider.world_position
        self.__player.update_direction(
            input_handler, self.map, self.__physics, delta_time
        )
        if self.__player.collider.world_position != old_center:
            self.__dirty_region = self.union_regions(
                self.__dirty_region,
                self.movement_region(self.__player.size, old_position),
                self.movement_region(
                    self.__player.size, self.__player.position
                ),
            )

    def render(self) -> None:
        """ Render Method for the MapScene Object"""
        if self.__dirty_region is not None:
            x, y, width, height = self.__dirty_region
            self.display.restore_region(
                self.__static_layer, x, y, width, height
            )
            self.__dirty_region = None
        self.__player.draw(self.display)
        self.display.render()

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.display.clear_window()
        self.display.clear(0xFFFF0000)
        self.__dirty_region = (
            0, 0, self.display.width, self.display.height
        )
