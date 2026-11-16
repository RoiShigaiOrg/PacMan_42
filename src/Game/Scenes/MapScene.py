from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from ..GameState import GameState, PacManState
from Engine.InputHandler.KeyCode import KEY_ESC, KEY_C, KEY_B, KEY_X
from ..MapGeneration.MapGeneration import Map
from ..MapGeneration import (
        RELATIVE_MAP_POS_X,
        RELATIVE_MAP_POS_Y,
        RELATIVE_MAP_WIDTH,
        RELATIVE_MAP_HEIGHT
        )
from ..Player.Player import Player
from ..Ghosts.Ghost import Behaviour, FLEA_ROAM_RADIUS, Ghost
from ..Ghosts.Behaviours import TargetPlan
from ..Ghosts.Blinky import Blinky
from ..Ghosts.Clyde import Clyde
from ..Ghosts.Inky import Inky
from ..Ghosts.Pinky import Pinky
from typing import Tuple, Dict


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
        map_x = self.display.relative_width(RELATIVE_MAP_POS_X)
        map_y = self.display.relative_height(RELATIVE_MAP_POS_Y)
        map_width = self.display.relative_width(RELATIVE_MAP_WIDTH)
        map_height = self.display.relative_height(RELATIVE_MAP_HEIGHT)
        self.map.set_colliders(
                map_x,
                map_y,
                map_width,
                map_height,
            )
        self.map.draw(display)
        self.__player: Player = Player(engine)
        self.__player.InitPlayer(display, self.map)
        self.__ghosts: Dict[str, Ghost] = {
                "blinky": Blinky(engine),
                "inky": Inky(engine=engine),
                "clyde": Clyde(engine=engine),
                "pinky": Pinky(engine=engine)
            }
        self.__ghost_targets: dict[
            Ghost, tuple[Behaviour, TargetPlan]
        ] = {}
        for ghost in self.__ghosts.values():
            ghost.init_ghost(display, self.map)

        territories = self.map.graph_territories(
            {
                name: ghost.origin
                for name, ghost in self.__ghosts.items()
            },
            FLEA_ROAM_RADIUS,
        )
        for name, ghost in self.__ghosts.items():
            ghost.set_roam_territory(territories[name])

        for ghost in self.__ghosts.values():
            ghost_cell = self.map.cell_coordinates_at(
                ghost.collider.world_position
            )
            target_plan = ghost.compute_target(
                ghost.behaviour_context(
                    self.__player, self.map, self.stats, self.__ghosts
                )
            )
            self.__ghost_targets[ghost] = (
                ghost.behaviour, target_plan
            )
            ghost.compute_path(
                ghost_cell,
                target_plan.target,
                self.map.graph,
                target_plan.allowed_cells,
                target_plan.pathfinding,
            )
        self.__physics = engine.physics
        self.__dirty_region: Region | None = (
            0, 0, display.width, display.height
        )
        self.__static_layer = self.display.snapshot()

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        """ Update method for the MapScene Object """
        self.stats.time_in_level(delta_time)
        self.stats.update_death_recovery(delta_time)
        if self.stats.is_over():
            self.__engine.scene_manager.change_scene("game_over_scene")
            return
        if input_handler.was_key_pressed(KEY_C):
            self.__engine.scene_manager.change_scene("main_scene")
        if input_handler.was_key_pressed(KEY_X):
            for ghost in self.__ghosts.values():
                ghost.change_behaviour(Behaviour.DEAD)
        if input_handler.was_key_pressed(KEY_B):
            if self.stats.state == PacManState.NORMAL:
                self.stats.state = PacManState.SUPER
            elif self.stats.state == PacManState.SUPER:
                self.stats.state = PacManState.NORMAL
        if input_handler.was_key_pressed(KEY_ESC):
            self.display.close()
        self.__update_player(input_handler, delta_time)
        self.__update_ghosts(delta_time)
        self.__check_player_ghost_collision()

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
        old_visual_state = self.__player.visual_state
        self.__player.update_direction(
            input_handler, self.map, self.__physics, delta_time
        )
        new_position = self.__player.position
        position_changed = self.__player.collider.world_position != old_center
        visual_changed = self.__player.visual_state != old_visual_state
        if position_changed or visual_changed:
            regions = [self.movement_region(self.__player.size, new_position)]
            if position_changed:
                regions.append(
                    self.movement_region(self.__player.size, old_position)
                )
            self.__dirty_region = self.union_regions(
                self.__dirty_region,
                *regions,
            )

    def __update_ghosts(
            self, delta_time: float,
    ) -> None:
        """
        Updates the ghost within the scene depending on the player position
        and the GameState.
        """
        for ghost in self.__ghosts.values():
            ghost_cell = self.map.cell_coordinates_at(
                ghost.collider.world_position
            )
            target_plan = ghost.compute_target(
                ghost.behaviour_context(
                    self.__player, self.map, self.stats, self.__ghosts
                )
            )
            behaviour_target = (ghost.behaviour, target_plan)
            if self.__ghost_targets.get(ghost) != behaviour_target:
                ghost.compute_path(
                    ghost_cell,
                    target_plan.target,
                    self.map.graph,
                    target_plan.allowed_cells,
                    target_plan.pathfinding,
                )
                self.__ghost_targets[ghost] = behaviour_target
            old_ghost_position = ghost.position
            old_ghost_center = ghost.collider.world_position
            old_visual_state = ghost.visual_state
            ghost.update_movement(
                self.map, self.__physics, delta_time, self.stats
            )
            position_changed = (
                ghost.collider.world_position != old_ghost_center
            )
            visual_changed = ghost.visual_state != old_visual_state
            if position_changed or visual_changed:
                regions = [
                    self.movement_region(ghost.size, ghost.position)
                ]
                if position_changed:
                    regions.append(
                        self.movement_region(ghost.size, old_ghost_position)
                    )
                self.__dirty_region = self.union_regions(
                    self.__dirty_region,
                    *regions,
                )

    def __check_player_ghost_collision(self) -> None:
        """
        Check if the ghost and the player are overlapping and
            change the PacManState or Ghost State in the GameState
            accordingly of the rules.
        """
        for ghost in self.__ghosts.values():
            if ghost.behaviour is Behaviour.DEAD:
                continue
            if self.stats.state is PacManState.DEAD:
                continue

            collision = self.__physics.handle_collision(
                    self.__player.collider, ghost.collider
                )
            if collision is None:
                continue
            if ghost.behaviour is Behaviour.FLEAT:
                self.stats.eat_ghost()
                ghost.change_behaviour(Behaviour.DEAD)
            elif ghost.behaviour is Behaviour.CHASE:
                print("Player lost a life")
                self.stats.lose_life()
                self.__player.set_to_origin()
                break

    def render(self) -> None:
        """ Render Method for the MapScene Object"""
        if self.__dirty_region is not None:
            x, y, width, height = self.__dirty_region
            self.display.restore_region(
                self.__static_layer, x, y, width, height
            )
            self.__dirty_region = None
        self.__player.draw(self.display)
        for ghost in self.__ghosts.values():
            ghost.draw(self.display)
        self.display.render()

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.display.clear_window()
        self.display.clear(0xFFFF0000)
        self.__dirty_region = (
            0, 0, self.display.width, self.display.height
        )
