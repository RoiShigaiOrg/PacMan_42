from Engine.Engine import Engine
from Engine.Application import Application
from Engine.SceneManager import SceneManager
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
        self.scenes: SceneManager = SceneManager()
        self.color: str
        self.dimension: Tuple[int, int]
        self.display: MlxDisplay
        self.scenes.add_scene(
            {
                "main_scene": MainScene(
                    self.engine.create_display((1280, 720))
                ),
                "game_scene": MapScene(
                    self.engine.create_display((1280, 720))
                )
            }
        )

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """ Update Method of the PacMan Class """
        self.scenes.update(delta_time, input_handler)

    def render(self) -> None:
        """ Render the actual scene in the SceneManager """
        print("application render")
        self.scenes.render()

    def run(self) -> None:
        """ Main method that will contain the loop of the program """
        self.scenes.change_screen("game_scene")
        print("scene has changed")
        self.engine.run(self)
