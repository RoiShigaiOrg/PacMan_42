from Engine import Scene
from Engine.Engine import Engine
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from ..GameState import GameState, PacManState
from Engine.InputHandler.KeyCode import (
        KEY_ESC, KEY_C, KEY_B, KEY_X, KEY_H, KEY_R
    )
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
from Game.UI.Lives import Lives
from Game.UI.Score import Score
from Game.UI.PowerTime import PowerTimer


class MapScene(Scene):
    """A class for drawing the map based on the Map object:
      handling the size of corridors, walls, corners, colors, etc."""

    def __init__(
            self, engine: Engine,
            display: MlxDisplay,
            stats: GameState) -> None:
        super().__init__()
        self.__engine = engine
        self.stats = stats
        self.display = display
        self.map = Map(engine)
        self.display.clear(0xFF000000)
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
        self.mark_full_screen_dirty(display)
        self.__consume_player_pellet()
        self.__static_layer = self.display.snapshot()
        self.lives = Lives(10, 10, max_lives=4, scale=2)
        self.score = Score(self.display.relative_width(0.6), 10, 0xFFFFFFFF)
        self.power_timer = PowerTimer(self.display.relative_width(0.35), 10)

    def __reset_map(self) -> None:
        """ Generate a New map and Reset the entity position """
        self.map = Map(self.__engine)
        self.display.clear(0xFF000000)
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
        self.map.draw(self.display)
        self.__player = Player(self.__engine)
        self.__player.InitPlayer(self.display, self.map)
        for ghost in self.__ghosts.values():
            ghost.init_ghost(self.display, self.map)

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
        self.mark_full_screen_dirty(self.display)
        self.__consume_player_pellet()
        self.__static_layer = self.display.snapshot()

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        """ Update method for the MapScene Object """
        self.stats.time_in_level(delta_time)
        self.stats.update_death_recovery(delta_time)
        self.stats.update_power_remaining(delta_time)
        if self.stats.is_over():
            self.__reset_map()
            self.__engine.scene_manager.change_scene("game_over_scene")
            return
        if not self.map.contain_pellet():
            self.__reset_map()
            self.__engine.scene_manager.change_scene("endlevel_scene")
        if self.map.update_pellet_animation(delta_time):
            self.mark_dirty(*self.map.animated_pellet_regions)
        if input_handler.was_key_pressed(KEY_C):
            self.__engine.scene_manager.change_scene("main_scene")
        if input_handler.was_key_pressed(KEY_R):
            self.__reset_map()
        if input_handler.was_key_pressed(KEY_X):
            for ghost in self.__ghosts.values():
                ghost.change_behaviour(Behaviour.DEAD)
        if input_handler.was_key_pressed(KEY_B):
            if self.stats.state == PacManState.NORMAL:
                self.stats.state = PacManState.SUPER
            elif self.stats.state == PacManState.SUPER:
                self.stats.state = PacManState.NORMAL
        if input_handler.was_key_pressed(KEY_H):
            self.__engine.scene_manager.change_scene("endlevel_scene")
        if input_handler.was_key_pressed(KEY_ESC):
            self.display.close()
        self.__update_player(input_handler, delta_time)
        self.__update_ghosts(delta_time)
        self.__check_player_ghost_collision()
        self.lives.set_lives(self.stats.lives)
        self.score.set_score(self.stats.scores)
        self.power_timer.set_time(self.stats.power_remaining)

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
        self.__consume_player_pellet()
        new_position = self.__player.position
        position_changed = self.__player.collider.world_position != old_center
        visual_changed = self.__player.visual_state != old_visual_state
        if position_changed or visual_changed:
            regions = [self.movement_region(self.__player.size, new_position)]
            if position_changed:
                regions.append(
                    self.movement_region(self.__player.size, old_position)
                )
            self.mark_dirty(*regions)

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
                self.mark_dirty(*regions)

    def __consume_player_pellet(self) -> None:
        """Consume and score the pellet in Pac-Man's current map cell."""
        pellet = self.map.consume_pellet_at(
            self.__player.collider.world_position
        )
        if pellet is None:
            return
        if self.map.is_corner(self.__player.collider.world_position):
            self.stats.eat_fruit()
        else:
            self.stats.eat_pac_dot()
        self.mark_dirty(self.map.cell_region(pellet.coordinate))

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
        """Restore and redraw only the changed areas of the backbuffer."""
        dirty_regions = self.restore_dirty_regions(
            self.display, self.__static_layer
        )
        self.map.render_pellets(self.display, dirty_regions)
        self.__player.draw(self.display)
        for ghost in self.__ghosts.values():
            ghost.draw(self.display)
        self.display.render()
        self.clear_dirty_regions()
        self.power_timer.draw(self.display)
        self.lives.draw(self.display, 0xFF000000)
        self.score.draw(self.display)

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.display.clear_window()
        self.display.clear(0xFFFF0000)
        self.mark_full_screen_dirty(self.display)
        self.lives.redraw()
        self.__dirty_region = (
            0, 0, self.display.width, self.display.height
        )
