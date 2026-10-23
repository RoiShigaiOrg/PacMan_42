from .Graphics.MlxDisplay import MlxDisplay
from .FileManager import FileManager
from typing import Any, Tuple
from .Graphics.MlxWindow import MlxWindow
from .Application.Application import Application
from .InputHandler import InputHandler
from .SceneManager.SceneManager import SceneManager
from .Clock import Clock
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

    def __init__(
            self,
            program_name: str,
            target_fps: float | None = 60.0,
    ) -> None:
        """Initialize the engine.

        Args:
            program_name: Name displayed in the game window.
            target_fps: Maximum game-loop rate. ``None`` disables limiting.
        """

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
        self.scene_manager = SceneManager()
        self._input_handler = InputHandler(
            self._session,
            self._mlx_ptr,
            self._window.native_ptr,
        )
        self._clock = Clock(target_fps=target_fps)

    @property
    def file_manager(self) -> FileManager:
        """Return the file service owned by this engine."""
        return self.__file_manager

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
        """Run the application until the MLX loop exits.

        Args:
            application: Application object to update and render.
        """

        def frame(_param: object) -> None:
            delta_time = self._clock.tick()
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
