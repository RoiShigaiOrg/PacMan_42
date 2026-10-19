import math
from Engine import Scene
from Engine.Graphics.MlxDisplay import MlxDisplay
from Engine.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_ESC, KEY_C
from ..MapGeneration.MapGeneration import Map
from Engine.Engine import Engine


class MapScene(Scene):
    """A class for drawing the map based on the Map object:
      handling the size of corridors, walls, corners, colors, etc."""

    def __init__(self, engine: Engine, display: MlxDisplay) -> None:
        self.__engine = engine
        self.display = display
        self.map = Map()
        self.ZOOM = 1.5
        self.SIZE = round(12 * self.ZOOM)
        self.FOND, self.WALL = 0xFF0000FF, 0xFFFFFFFF
        self.MARGIN = round(3 * self.ZOOM)
        self.THICKNESS = round(1 * self.ZOOM)
        self.RADIUS = self.MARGIN

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        """unused func"""
        if input_handler.was_key_pressed(KEY_C):
            self.__engine.scene_manager.change_scene("main_scene")
        if input_handler.was_key_pressed(KEY_ESC):
            self.display.close()

    def render(self) -> None:
        """ display map"""
        self.display.render()

    def is_wall(self, x: int, y: int) -> bool:
        """ Check the neighboring cells to see if it's a wall or a corridor."""
        if 0 <= y < len(self.map.grid) and 0 <= x < len(self.map.grid[0]):
            return not self.map.grid[y][x].walkable
        return True

    def arc(
            self, cx: int, cy: int, sx: int,
            sy: int, r_min: int, r_max: int) -> None:
        """Draw the arcs."""
        for py in range(int(cy - r_max) - 1, int(cy + r_max) + 2):
            for px in range(int(cx - r_max) - 1, int(cx + r_max) + 2):
                ex, ey = px + 0.5 - cx, py + 0.5 - cy
                if (ex * sx >= 0 and ey * sy >= 0
                        and r_min <= math.hypot(ex, ey) < r_max):
                    self.display.draw_pixel(px, py, self.WALL)

    def draw_wall(self, x: int, y: int) -> None:
        """ Draw the straight wall"""
        T, M, E, R = self.SIZE, self.MARGIN, self.THICKNESS, self.RADIUS
        px, py = x * T, y * T
        top, down = self.is_wall(x, y - 1), self.is_wall(x, y + 1)
        left, right = self.is_wall(x - 1, y), self.is_wall(x + 1, y)

        start_x = px if left else px + M + R
        end_x = px + T if right else px + T - M - R
        start_y = py if top else py + M + R
        end_y = py + T if down else py + T - M - R
        if not top:
            self.display.fill_rect(
                start_x, py + M,
                end_x - start_x, E, self.WALL)
        if not down:
            self.display.fill_rect(
                start_x, py + T - M - E,
                end_x - start_x, E, self.WALL)
        if not left:
            self.display.fill_rect(
                px + M, start_y,
                E, end_y - start_y, self.WALL)
        if not right:
            self.display.fill_rect(
                px + T - M - E, start_y,
                E, end_y - start_y, self.WALL)

        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            wall_x, wall_y = self.is_wall(x + dx, y), self.is_wall(x, y + dy)
            bold_x = px + M if dx < 0 else px + T - M
            bold_y = py + M if dy < 0 else py + T - M

            if not wall_x and not wall_y:
                self.arc(bold_x - dx * R, bold_y - dy * R, dx, dy, R - E, R)

            elif wall_x and wall_y and not self.is_wall(x + dx, y + dy):
                self.arc(bold_x + dx * R, bold_y + dy * R, -dx, -dy, R, R + E)
                lx = px + M if dx < 0 else px + T - M - E
                ly = py + M if dy < 0 else py + T - M - E
                if dy < 0:
                    self.display.fill_rect(lx, py, E, M - R, self.WALL)
                else:
                    self.display.fill_rect(
                        lx, py + T - M + R,
                        E, M - R, self.WALL)
                if dx < 0:
                    self.display.fill_rect(
                        px, ly, M - R,
                        E, self.WALL)
                else:
                    self.display.fill_rect(
                        px + T - M + R, ly,
                        M - R, E, self.WALL)

    def is_isole(self, x: int, y: int) -> bool:
        """Check if the square is surrounded by corridors."""
        return not (self.is_wall(x, y - 1) or self.is_wall(x, y + 1)
                    or self.is_wall(x - 1, y) or self.is_wall(x + 1, y))

    def fill_bloc(self, x: int, y: int) -> None:
        """fill the case 1/1"""
        T, M = self.SIZE, self.MARGIN
        cx = x * T + T / 2
        cy = y * T + T / 2
        radius = T / 2 - M
        for py in range(y * T + M, y * T + T - M):
            for px in range(x * T + M, x * T + T - M):
                if math.hypot(px + 0.5 - cx, py + 0.5 - cy) <= radius:
                    self.display.draw_pixel(px, py, self.WALL)

    def render_on_change(self) -> None:
        """manage the drawing of map"""
        self.display.clear(self.FOND)
        for line in self.map.grid:
            for cell in line:
                if not cell.walkable:
                    x, y = cell.coordinate
                    if self.is_isole(x, y):
                        self.fill_bloc(x, y)
                    else:
                        self.draw_wall(x, y)
        self.display.render()
