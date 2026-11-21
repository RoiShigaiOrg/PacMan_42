from Engine.Engine import Engine
from Engine.Application import Application
from Engine.InputHandler import InputHandler
from .Scenes.MainScene import MainScene
from .Scenes.MapScene import MapScene
from .Scenes.OptionScene import OptionScene
from .Scenes.EndLevelScene import EndLevel
from Engine.Graphics.MlxDisplay import MlxDisplay
from typing import Tuple
from pathlib import Path
from .Scenes.GameOverScene import GameOverScene
from .GameState import GameState
from .Scenes.ScoreScene import ScoreScene
from .Config import GameConfigLoader


class PacMan(Application):
    """
        Main Class of the Project.

        This PacMac Class will compose with all different features
            from Engine to run the Game.
    """

    def __init__(self, config_file: Path) -> None:
        """ Init Method of the PacMan """
        self.engine: Engine = Engine("Pac-Man", GameConfigLoader(config_file))
        self.stats: GameState = GameState()
        self.color: str
        self.dimension: Tuple[int, int] = self.engine.get_config_key(
            "dimension"
        )
        self.display: MlxDisplay
        self.engine.scene_manager.add_scene(
            {
                "main_scene": MainScene(
                    self.engine,
                    self.engine.create_display(self.dimension)
                ),
                "game_scene": MapScene(
                    self.engine,
                    self.engine.create_display(self.dimension),
                    self.stats
                ),
                "game_over_scene": GameOverScene(
                    self.engine,
                    self.engine.create_display(self.dimension),
                    self.stats
                ),
                "score_scene": ScoreScene(
                    self.engine,
                    self.engine.create_display(self.dimension),
                    self.stats,
                    False
                ),
                "leaderboard_scene": ScoreScene(
                    self.engine,
                    self.engine.create_display(self.dimension),
                    self.stats,
                    True
                ),
                "endlevel_scene": EndLevel(
                    self.engine,
                    self.engine.create_display(self.dimension),
                    self.stats
                ),
                "option_scene": OptionScene(
                    self.engine,
                    self.engine.create_display(self.dimension),
                )
            }
        )

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """ Update Method of the PacMan Class """
        self.engine.scene_manager.update(delta_time, input_handler)

    def render(self) -> None:
        """ Render the actual scene in the SceneManager """
        self.engine.scene_manager.render()

    def run(self) -> None:
        """ Main method that will contain the loop of the program """
        self.engine.scene_manager.change_scene("main_scene")
        self.engine.run(self)
