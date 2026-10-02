from .Screen import Screen
from ..ScreenManager import ScreenManager


class MainScreen(Screen):

    def __init__(
            self,
            engine: Engine,
            scene_manager: SceneManager) -> None:
        """ Init Method for the MainScreen """
        self.__screen_manager: ScreenManager = scene_manager
        self.__engine = engine
        self.__name = "main_screen"
