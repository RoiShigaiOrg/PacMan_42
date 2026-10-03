from typing import Any

import mlx

from .Engine.Graphics import MlxScreen
from .Engine import Engine
from .ScreenManager import ScreenManager
from .ScreenManager.Screen import Screen


class DemoScreen(Screen):
    """Draw a small static scene into the shared screen buffer."""

    def render(self, screen: MlxScreen) -> None:
        for y in range(20, screen.height - 20):
            for x in range(20, screen.width - 20):
                if x in (20, screen.width - 21) or y in (
                    20, screen.height - 21
                ):
                    screen.pixel(x, y, 0xFF2121DE)

        center_x = screen.width // 2
        center_y = screen.height // 2
        for y in range(center_y - 12, center_y + 13):
            for x in range(center_x - 12, center_x + 13):
                if (x - center_x) ** 2 + (y - center_y) ** 2 <= 12 ** 2:
                    screen.pixel(x, y, 0xFFFFFF00)


def main() -> None:
    """
        Test function for the mlx implementation
        DO NOT WRITE ANYTHING INTO IT !!!!

        This function will be deleted when the PacMan class is working
    """

    session = mlx.Mlx()
    mlx_ptr: Any = session.mlx_init()
    if not mlx_ptr:
        raise RuntimeError("failed to initialize MLX")
    screen = MlxScreen(session, mlx_ptr, (320, 240), "Pac-Man")
    manager = ScreenManager(screen)
    manager.add_screen("demo", DemoScreen())

    try:
        manager.render()
        session.mlx_loop_hook(mlx_ptr, lambda _param: manager.render(), None)
        session.mlx_loop(mlx_ptr)
    finally:
        screen.close()
        session.mlx_release(mlx_ptr)


class PacMan:

    def __init__(self) -> None:
        """ Init Method of the PacMan """
        self._session = mlx.Mlx()
        self._mlx_ptr: Any = self._session.mlx_init()
        if not self._mlx_ptr:
            raise RuntimeError("failed to initialize MLX")
        self._engine = Engine()
        self._screen = MlxScreen(
                self._session,
                self._mlx_ptr,
                tuple(self._engine.get_config_key("dimension")),
                "Pac-Man"
                )


if __name__ == "__main__":
    main()
