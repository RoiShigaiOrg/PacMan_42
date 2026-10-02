from .Graphics import MlxScreen
from Screen import Screen
from typing import Dict


class ScreenManager:
    """
        ScreenManager Object Class Definition

        The ScreenManger is one of the main component for Graphical
            Engine. It will manage the different screen/menu and give it
            to the mlx_screen object.
    """

    def __init__(
            self,
            mlx_screen: MlxScreen,
            screen_dict: Dict[str, Screen]) -> None:
        """ Init Method of the ScreenManager Object """
        self.__main_window: MlxScreen = mlx_screen
        self.__screens: Dict[str, Screen] = screen_dict
        self.actual_screen: Screen

    def change_screen(self, screen_id: str) -> None:
        """ Change to the given screen_id to render in the mlx window """
        if screen_id in self.screens:
            self.actual_screen = self.__screens[screen_id]
        else:
            raise ValueError(f"ScreenManager Error: {screen_id} do not exist")

    def add_screen(self, screen: Dict[str, Screen]) -> None:
        """ Add a screen into the screens dict of the ScreenManager """
        self.__screens.update(screen)
