from .Screen import Screen
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.Engine.Graphics import MlxWindow
else:
    try:
        from ...Engine.Graphics import MlxWindow
    except ImportError:
        from Engine.Graphics import MlxWindow


class MainScreen(Screen):
    """Small example screen that draws a centered Pac-Man-like marker."""

    def render(self, screen: MlxWindow) -> None:
        center_x = screen.width // 2
        center_y = screen.height // 2
        screen.pixel(center_x, center_y, 0xFFFFFF00)
