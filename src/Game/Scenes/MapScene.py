from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from ..GameState import GameState, PacManState
from Engine.InputHandler.KeyCode import KEY_ESC, KEY_C, KEY_B
from ..MapGeneration.MapGeneration import Map
from ..MapGeneration import (
        RELATIVE_MAP_POS_X,
        RELATIVE_MAP_POS_Y,
        RELATIVE_MAP_WIDTH,
        RELATIVE_MAP_HEIGHT
        )
from ..Player.Player import Player
from ..Ghosts.Ghost import Behaviour, FLEE_DISTANCE_THRESHOLD, Ghost
from ..Ghosts.Blinky import Blinky
from typing import Tuple, List


Region = Tuple[int, int, int, int]


class MapScene(Scene):
    """A class for drawing the map based on the Map object:
      handling the size of corridors, walls, corners, colors, etc."""

    def __init__(
            self, engine: Engine,
            display: MlxDisplay,
            stats: GameState) -> None:
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
        initial_player_cell = self.map.cell_coordinates_at(
                self.__player.collider.world_position
            )
        self.__ghosts: List[Ghost] = [Blinky()]
        self.__ghost_targets: dict[Ghost, Tuple[int, int]] = {}
        for ghost in self.__ghosts:
            ghost.init_ghost(display, self.map)
            ghost_cell = self.map.cell_coordinates_at(
                ghost.collider.world_position
            )
            target = self.__target_for_ghost(
                ghost, ghost_cell, initial_player_cell
            )
            self.__ghost_targets[ghost] = target
            ghost.compute_path(
                ghost_cell, target, self.map.graph
            )
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
        if input_handler.was_key_pressed(KEY_B):
            if self.stats.state == PacManState.NORMAL:
                self.stats.state = PacManState.SUPER
            else:
                self.stats.state = PacManState.NORMAL
        if input_handler.was_key_pressed(KEY_ESC):
            self.display.close()
        self.__update_player(input_handler, delta_time)
        player_cell = self.map.cell_coordinates_at(
                self.__player.collider.world_position
            )
        self.__update_ghosts(player_cell, delta_time)

    def __update_player(
            self,
            input_handler: InputHandler,
            delta_time: float) -> None:
        """
        Updates the player position and direction depending on the InputHandler
        and the delta time.
        """
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

    def __update_ghosts(
            self, player_cell: Tuple[int, int], delta_time: float,
    ) -> None:
        """
        Updates the ghost within the scene depending on the player position
        and the GameState.
        """
        for ghost in self.__ghosts:
            ghost_cell = self.map.cell_coordinates_at(
                ghost.collider.world_position
            )
            target = self.__target_for_ghost(
                ghost, ghost_cell, player_cell
            )
            if self.__ghost_targets.get(ghost) != target:
                ghost.compute_path(
                    ghost_cell, target, self.map.graph
                )
                self.__ghost_targets[ghost] = target
            old_ghost_position = ghost.position
            old_ghost_center = ghost.collider.world_position
            ghost.update_movement(
                self.map, self.__physics, delta_time
            )
            if ghost.collider.world_position != old_ghost_center:
                self.__dirty_region = self.union_regions(
                    self.__dirty_region,
                    self.movement_region(ghost.size, old_ghost_position),
                    self.movement_region(
                        ghost.size, ghost.position
                    ),
                )

    def __target_for_ghost(
            self,
            ghost: Ghost,
            ghost_cell: Tuple[int, int],
            player_cell: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Select a pathfinding destination for a ghost's current mode."""
        if self.stats.state != PacManState.SUPER:
            ghost.change_behaviour(Behaviour.CHASE)
            return ghost._chase(player_cell)

        ghost.change_behaviour(Behaviour.FLEAT)
        distance = (
            abs(ghost_cell[0] - player_cell[0])
            + abs(ghost_cell[1] - player_cell[1])
        )
        if distance > FLEE_DISTANCE_THRESHOLD:
            return ghost._fleat(ghost.origin)
        return ghost._fleat(self.__flee_target(ghost_cell, player_cell))

    def __flee_target(
            self,
            ghost_cell: Tuple[int, int],
            player_cell: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Choose a reachable walkable cell away from Pac-Man."""
        start = self.map.graph.get(ghost_cell)
        if start is None:
            return ghost_cell

        reachable: list[Tuple[int, int]] = []
        visited = {start}
        pending = [start]
        while pending:
            node = pending.pop()
            reachable.append(node.coordinate)
            for neighbor, _cost in node.neighbors():
                if neighbor not in visited:
                    visited.add(neighbor)
                    pending.append(neighbor)

        direction_x = ghost_cell[0] - player_cell[0]
        direction_y = ghost_cell[1] - player_cell[1]
        if direction_x == 0 and direction_y == 0:
            return max(
                reachable,
                key=lambda cell: (
                    abs(cell[0] - player_cell[0])
                    + abs(cell[1] - player_cell[1]),
                    -cell[1],
                    -cell[0],
                ),
            )

        ideal_x = ghost_cell[0] + direction_x
        ideal_y = ghost_cell[1] + direction_y
        ideal_target = (ideal_x, ideal_y)
        if ideal_target in reachable:
            return ideal_target

        def away_score(
                cell: Tuple[int, int],
        ) -> tuple[int, int, int, int, int, int]:
            offset_x = cell[0] - player_cell[0]
            offset_y = cell[1] - player_cell[1]
            projection = offset_x * direction_x + offset_y * direction_y
            cross_product = abs(
                offset_x * direction_y - offset_y * direction_x
            )
            player_distance = abs(offset_x) + abs(offset_y)
            ideal_distance = (
                abs(cell[0] - ideal_x) + abs(cell[1] - ideal_y)
            )
            return (
                projection,
                -cross_product,
                player_distance,
                -ideal_distance,
                -cell[1],
                -cell[0],
            )

        return max(reachable, key=away_score)

    def render(self) -> None:
        """ Render Method for the MapScene Object"""
        if self.__dirty_region is not None:
            x, y, width, height = self.__dirty_region
            self.display.restore_region(
                self.__static_layer, x, y, width, height
            )
            self.__dirty_region = None
        self.__player.draw(self.display)
        for ghost in self.__ghosts:
            ghost.draw(self.display)
        self.display.render()

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.display.clear_window()
        self.display.clear(0xFFFF0000)
        self.__dirty_region = (
            0, 0, self.display.width, self.display.height
        )
