from .Graphics.MlxDisplay import MlxDisplay
from .FileManager import FileManager
from typing import Any, Tuple
from .Graphics.MlxWindow import MlxWindow
from .Application.Application import Application
from .InputHandler import InputHandler
import mlx
import time


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
        self._input_handler = InputHandler(
            self._session,
            self._mlx_ptr,
            self._window.native_ptr,
        )

    @property
    def input_handler(self) -> InputHandler:
        """Return the input service owned by this engine."""
        return self._input_handler

    def get_config_key(self, key: str) -> Any:
        """ Return the value stored in the given key from the config """
        return self.__config[key]

    def update_config(self, data: dict[str, Any]) -> None:
        """ Update the config with the new value """
        self.__config.update(data)

    def get_window(self) -> MlxWindow:
        """ Return the MlxWindow Object Instance """
        return self._window

    def create_display(self, size: Tuple[int, int]) -> MlxDisplay:
        """ Create a Display from the actual window """
        return self._window.create_display(
                    size
                )

    def run(self, application: Application) -> None:
        """
            Core method of the Engine that will run
                the given Application object (Game or else)
                created with the Engine API.
        """
        previous_time = time.perf_counter()
        def frame(_param: object) -> None:
            nonlocal previous_time

            current_time = time.perf_counter()
            delta_time = current_time - previous_time
            previous_time = current_time

            application.update(delta_time, self._input_handler)
            application.render()
            self._input_handler.end_frame()

        self._input_handler.register_hooks()
        self._session.mlx_loop_hook(
                self._mlx_ptr,
                frame,
                None
                )
        try:
            self._session.mlx_loop(self._mlx_ptr)
        finally:
            self._window.close()
            self._session.mlx_release(self._mlx_ptr)
