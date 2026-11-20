from .Graphics.MlxDisplay import MlxDisplay
from .FileManager import FileManager, ConfigLoader
from typing import Any, Tuple, cast
from .Graphics.MlxWindow import MlxWindow
from .Application.Application import Application
from .InputHandler import InputHandler
from .SceneManager.SceneManager import SceneManager
from .Clock import Clock
from .Physics import PhysicsEngine
from .ConfigHandler.ConfigHandler import ConfigHandler
from .FileManager.Loader.SpriteLoader import SpriteLoader
from .Sprite.SpriteSheet import SpriteSheet
from pathlib import Path
from pydantic import BaseModel
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

    def __init__(
            self,
            program_name: str,
            config_loader: ConfigLoader,
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
        self.__config: ConfigHandler[BaseModel] = ConfigHandler(
                self.__file_manager.load(
                    config_loader
                )
            )
        print(f"config: {self.__config}")
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
        self.__physics = PhysicsEngine()
        self._clock = Clock(target_fps=target_fps)

    @property
    def file_manager(self) -> FileManager:
        """Return the file service owned by this engine."""
        return self.__file_manager

    @property
    def input_handler(self) -> InputHandler:
        """Return the input service owned by this engine."""
        return self._input_handler

    @property
    def physics(self) -> PhysicsEngine:
        """Return the physics service owned by this engine."""
        return self.__physics

    def get_config_key(self, key: str) -> Any:
        """ Return the value stored in the given key from the config """
        return self.__config[key]

    def set_config_key(self, key: str, value: Any) -> Any:
        """ Set the value of a Config key """
        self.__config[key] = value

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

    def apply_resolution(self, size: tuple[int, int]) -> None:
        """Replace the window and refresh scenes for an allowed resolution."""
        available = self.get_config_key("available_dimension")
        if not isinstance(available, dict):
            raise ValueError("available resolutions must be a mapping")
        allowed_sizes = {
            tuple(dimension)
            for dimension in available.values()
            if isinstance(dimension, (list, tuple))
        }
        if size not in allowed_sizes:
            raise ValueError(f"unsupported resolution: {size}")
        if size == self._window.size():
            return

        self._window.recreate(size, self._input_handler.attach_window)
        self.set_config_key("dimension", list(size))
        self.scene_manager.resolution_changed()

    def load_sprite_sheet(
            self,
            image_path: Path,
            metadata_path: Path | None = None,
    ) -> SpriteSheet:
        """Load a sprite sheet using this engine's active MLX session."""
        loader = SpriteLoader(
            image_path,
            self._session,
            self._mlx_ptr,
            metadata_path,
        )
        return cast(SpriteSheet, self.__file_manager.load(loader))

    def run(self, application: Application) -> None:
        """Run the application until the MLX loop exits.

        Args:
            application: Application object to update and render.
        """
        fps_frames = 0
        fps_started = time.perf_counter()

        def frame(_param: object) -> None:
            nonlocal fps_frames, fps_started
            delta_time = self._clock.tick()
            application.update(delta_time, self._input_handler)
            application.render()
            fps_frames += 1
            now = time.perf_counter()
            elapsed = now - fps_started
            if elapsed >= 1.0:
                fps_frames = 0
                fps_started = now
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
