from Engine.Engine import Engine
from Engine.Application import Application
from Engine.InputHandler import InputHandler
from .Scenes.MainScene import MainScene
from .Scenes.MapScene import MapScene
from Engine.Graphics.MlxDisplay import MlxDisplay
from typing import Tuple


class PacMan(Application):
    """
        Main Class of the Project.

        This PacMac Class will compose with all different features
            from Engine to run the Game.
    """

    def __init__(self) -> None:
        """ Init Method of the PacMan """
        self.engine: Engine = Engine("Pac-Man")
        self.color: str
        self.dimension: Tuple[int, int]
        self.display: MlxDisplay
        self.engine.scene_manager.add_scene(
            {
                "main_scene": MainScene(
                    self.engine,
                    self.engine.create_display((1280, 720))
                ),
                "game_scene": MapScene(
                    self.engine,
                    self.engine.create_display((1280, 720))
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
