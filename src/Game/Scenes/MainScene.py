from Engine.SceneManager.Scene.Scene import Scene
from Engine.Graphics.MlxDisplay import MlxDisplay


class MainScene(Scene):
    """
        Main Screen Class Definition

        The Main screen is the hub Scene where we get when starting the Game.
        It contain all path to:
            - Start: Start a new game
            - LeaderBoard: Link to the actual LeaderBoard Scene
            - Option: Link to the Option Scene
            - Quit: Exit the program normally
    """

    def __init__(self, display: MlxDisplay) -> None:
        """ Init Method of the MainScreen Class """
        self.__display = display

    def render(self) -> None:
        self.__display.clear()
        self.__display.fill(0xFFFF0000)
        self.__display.render()
