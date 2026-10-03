from .Screen import Screen
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.Engine.Graphics import MlxScreen
else:
    try:
        from ...Engine.Graphics import MlxScreen
    except ImportError:
        from Engine.Graphics import MlxScreen


class MainScreen(Screen):
    """Small example screen that draws a centered Pac-Man-like marker."""

    def render(self, screen: MlxScreen) -> None:
        center_x = screen.width // 2
        center_y = screen.height // 2
        screen.pixel(center_x, center_y, 0xFFFFFF00)
