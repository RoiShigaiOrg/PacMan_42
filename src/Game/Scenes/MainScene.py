from Engine.SceneManager.Scene.Scene import Scene
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Graphics.Components.Rect import Rect
from Engine.Graphics.Components.Circle import Circle
from Engine.Graphics.Components.Line import Line


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
        self.__rect: Rect = Rect(480, 312, 0xFF0000FF)
        self.__circle: Circle = Circle(80, 80, 0xFF00FFFF)
        self.__line: Line = Line((220, 400), (930, 300), 0xFF00FF00)

    def render(self) -> None:
        self.__display.clear()
        self.__display.fill(0xFFFF0000)
        self.__rect.draw(self.__display, 50, 50)
        self.__circle.draw(self.__display, 1200, 240)
        self.__circle.fill(self.__display, 1200, 240)
        self.__line.draw(self.__display, 0, 0)
        self.__display.render()
