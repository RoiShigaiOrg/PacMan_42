from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from src.Engine.Graphics import MlxWindow
else:
    try:
        from ..Engine.Graphics import MlxWindow
    except ImportError:
        from Engine.Graphics import MlxWindow

from .Screen import Screen


class ScreenManager:
    """
        ScreenManager Object Class Definition

        The ScreenManger is one of the main component for Graphical
            Engine. It will manage the different screen/menu and give it
            to the mlx_screen object.
    """

    def __init__(
            self,
            screen_dict: Dict[str, Screen] | None = None) -> None:
        """ Init Method of the ScreenManager Object """
        self.__screens: Dict[str, Screen] = dict(screen_dict or {})
        self.__actual_screen: Screen | None = None

        if self.__screens:
            self.__actual_screen = next(iter(self.__screens.values()))

    @property
    def actual_screen(self) -> Screen | None:
        """Return the currently selected screen, if one is registered."""
        return self.__actual_screen

    def change_screen(self, screen_id: str) -> None:
        """ Change to the given screen_id to render in the mlx window """
        if screen_id in self.__screens:
            self.__actual_screen = self.__screens[screen_id]
        else:
            raise ValueError(f"ScreenManager Error: {screen_id} do not exist")

    def add_screen(self, screen_id: str, screen: Screen) -> None:
        """Register a screen under ``screen_id``."""
        self.__screens[screen_id] = screen
        if self.__actual_screen is None:
            self.__actual_screen = screen

    def render(self) -> None:
        """Render and present the currently selected screen."""
        if self.__actual_screen is None:
            raise RuntimeError("ScreenManager has no active screen")

        self.__actual_screen.render()
