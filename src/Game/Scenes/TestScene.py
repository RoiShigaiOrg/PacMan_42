from Engine.SceneManager.Scene.Scene import Scene
from Engine.InputHandler.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import (
    KEY_S, KEY_ESC, KEY_D, KEY_Q, KEY_Z,
)
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.Graphics.Components.Rect import Rect
from Engine.Graphics.Components.Circle import Circle
from Engine.Graphics.Components.Line import Line
from Engine.Graphics.Components.TextBox import TextBox
from Engine.Graphics.Components.TextJustify import TEXT_CENTER
from Engine.Physics import AABB, Collider, PhysicsEngine, Vector2
from typing import Tuple


Region = tuple[int, int, int, int]


class TestScene(Scene):
    """
        Main Screen Class Definition

        The Main screen is the hub Scene where we get when starting the Game.
        It contain all path to:
            - Start: Start a new game
            - LeaderBoard: Link to the actual LeaderBoard Scene
            - Option: Link to the Option Scene
            - Quit: Exit the program normally
    """

    def __init__(self, display: MlxDisplay) -> None:
        """ Init Method of the MainScreen Class """
        self.__display = display
        self.__rect: Rect = Rect(480, 312, 50, 50, 0xFF0000FF)
        self.__rect2: Rect = Rect(120, 120, 620, 300, 0xFFFF00FF)
        self.__circle: Circle = Circle(160, 160, 1120, 160, 0xFF00FFFF)
        self.__line: Line = Line((0, 100), (710, 0), 220, 300, 0xFF00FF00)
        self.__rect.add_text(TextBox("TEST", 0xFFFFFFFF), TEXT_CENTER)
        self.__physics = PhysicsEngine()
        self.__rect_collider = self.__make_rect_collider(self.__rect)
        self.__rect2_collider = self.__make_rect_collider(self.__rect2)
        self.__dirty_region: Region | None = (
            0, 0, display.width, display.height
        )
        self.__colliding: bool = False

        self.__display.clear(0xFFFF0000)
        self.__circle.draw(self.__display)
        self.__circle.fill(self.__display)
        self.__line.draw(self.__display)
        self.__rect2.fill(self.__display)
        self.__static_layer = self.__display.snapshot()

    def update(
            self, delta_time: float, input_handler: InputHandler
    ) -> None:
        """
            MainScene Update Method used to update the position of each object
                in the scene depending on the user input
                and Engine Calculation.
        """
        old_pos: Tuple[int, int] = self.__rect.pos
        x: int = old_pos[0]
        y: int = old_pos[1]
        self.__rect_collider.position = self.__center_at(
                x, y, self.__rect.size
            )

        dx: int = 0
        dy: int = 0
        if input_handler.is_key_down(KEY_D):
            dx += 5
        if input_handler.is_key_down(KEY_Q):
            dx -= 5
        if input_handler.is_key_down(KEY_S):
            dy += 5
        if input_handler.is_key_down(KEY_Z):
            dy -= 5

        collided = False
        if dx != 0:
            if self.__physics.can_move(
                    self.__rect_collider, Vector2(float(dx), 0.0),
                    self.__rect2_collider,
            ):
                x += dx
            else:
                collided = True
            self.__rect_collider.position = self.__center_at(
                    x, y, self.__rect.size
                )
        if dy != 0:
            if self.__physics.can_move(
                    self.__rect_collider, Vector2(0.0, float(dy)),
                    self.__rect2_collider,
            ):
                y += dy
            else:
                collided = True
            self.__rect_collider.position = self.__center_at(
                    x, y, self.__rect.size
                )

        if (x, y) != old_pos:
            self.__rect.update_pos(x, y)
        if input_handler.is_key_down(KEY_ESC):
            self.__display.close()

        if old_pos != self.__rect.pos:
            self.__dirty_region = self.union_regions(
                self.__dirty_region,
                self.movement_region(self.__rect.size, old_pos),
                self.movement_region(self.__rect.size, self.__rect.pos),
            )
        if collided != self.__colliding:
            self.__dirty_region = self.union_regions(
                self.__dirty_region,
                self.movement_region(self.__rect.size, self.__rect.pos)
            )
            self.__colliding = collided
            self.__rect.update_color(
                    0xFF0000FF if collided else 0xFF00FF00
                )

    @staticmethod
    def __center_at(x: int, y: int, size: Tuple[int, int]) -> Vector2:
        """Return the world-space center of a rectangle at a position."""
        width, height = size
        return Vector2(x + width / 2, y + height / 2)

    @classmethod
    def __make_rect_collider(cls, rect: Rect) -> Collider:
        """Create an AABB collider matching a graphics rectangle."""
        width, height = rect.size
        x, y = rect.pos
        return Collider(
            AABB(Vector2(width / 2, height / 2)),
            cls.__center_at(x, y, rect.size),
        )

    def render_on_change(self) -> None:
        """ Render on change method of MainScreen """
        self.__dirty_region = (
            0, 0, self.__display.width, self.__display.height
        )

    def render(self) -> None:
        """ Render all the the current frame in the Window """
        if self.__dirty_region is not None:
            x, y, width, height = self.__dirty_region
            self.__display.restore_region(
                self.__static_layer, x, y, width, height
            )
            self.__rect.draw(self.__display)
            self.__display.render()
            self.__rect.draw_text(self.__display)
            self.__dirty_region = None
