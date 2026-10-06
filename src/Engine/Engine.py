from .Graphics.MlxDisplay import MlxDisplay
from .FileManager import FileManager
from typing import Any, Dict
from .Graphics.MlxWindow import MlxWindow
from .Application.Application import Application
from .ScreenManager.ScreenManager import ScreenManager
from .ScreenManager.Screen.Screen import Screen
import mlx


class Engine:
    """
        Engine Class Definition

        The Engine is the backbone of the whole backend of the project.
        Handle the files operation for map creation,
            score storage and assets/sprites loading.
        Handle the coordonate of the whole Entity present in the project,
            Pathfinding algorithm and position updates

    """

    def __init__(self, program_name: str) -> None:
        """ Init method for the Engine """

        self._session = mlx.Mlx()
        self._mlx_ptr: Any = self._session.mlx_init()
        if not self._mlx_ptr:
            raise RuntimeError("failed to initialize MLX")
        self.__file_manager: FileManager = FileManager()
        self.__config = self.__file_manager.load_config()
        self._window = MlxWindow(
                self._session,
                self._mlx_ptr,
                tuple(self.get_config_key("dimension")),
                program_name
                )
        self._screen_manager: ScreenManager = ScreenManager(
                    {
                        "main_scene": MainScreen(
                        self.create_display(320, 240)
                        )
                    }
                )

    def get_config_key(self, key: str) -> Any:
        """ Return the value stored in the given key from the config """
        return self.__config[key]

    def update_config(self, data: dict) -> None:
        """ Update the config with the new value """
        self.__config.update(data)

    def get_window(self) -> MlxWindow:
        """ Return the MlxWindow Object Instance """
        return self._window

    def create_display(self, width: int, height: int) -> MlxDisplay:
        """ Create a Display from the actual window """
        return self._window.create_display(
                    (width, height)
                )

    def add_scene(self, scenes: Dict[str: Screen]) -> None:
        self._screen_manager.add_screen(scenes)

    def run(self, application: Application) -> None:
        """
            Core method of the Engine that will run
                the given Application object (Game or else)
                created with the Engine API.
        """
        self._session.mlx_loop_hook(self._mlx_ptr, )
