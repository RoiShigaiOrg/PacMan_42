from ..Engine.Engine import Engine
from ..Engine.ScreenManager.ScreenManager import ScreenManager


class PacMan:
    """
        Main Class of the Project.

        This PacMac Class will compose with all different objects needed
            to run the Game.
    """

    def __init__(self) -> None:
        """ Init Method of the PacMan """
        self.engine: Engine = Engine("Pac-Man")
        self.scenes: ScreenManager = ScreenManager()
        self.scenes.add_scene({
                        "main_scene": MainScene(
                        self.engine.create_display(
                            320, 240
                            )
                        )
                    }
                )

    def update(self, delta_time: float) -> None:
        self.scenes.update(delta_time)

    def render(self) -> None:
        """ Render the actual scene in the SceneManager """
        self.scenes.render()

    def run(self) -> None:
        """ Main method that will contain the loop of the proram """
        self.engine.run(self)

