from maze import Map
import math
from src.Engine import Engine, Scene, SceneManager
from src.Engine.Graphics.MlxDisplay import MlxDisplay
from typing import Tuple
from src.Engine.InputHandler import InputHandler


class GameScene(Scene):
    """A class for drawing the map based on the Map object:
      handling the size of corridors, walls, corners, colors, etc."""
    def __init__(
            self, display: MlxDisplay, la_map: Map,
            color: Tuple[int, int]) -> None:
        self.display = display
        self.map = la_map
        self.ZOOM = 1.4
        self.TAILLE = round(12 * self.ZOOM)
        self.FOND, self.WALL = color
        self.MARGE = round(3 * self.ZOOM)
        self.EPAISSEUR = round(1 * self.ZOOM)
        self.RAYON = self.MARGE

    def is_wall(self, x: int, y: int) -> bool:
        """ Check the neighboring cells to see if it's a wall or a corridor."""
        if 0 <= y < len(self.map.grid) and 0 <= x < len(self.map.grid[0]):
            return self.map.grid[y][x].state == "wall"
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
        T, M, E, R = self.TAILLE, self.MARGE, self.EPAISSEUR, self.RAYON
        px, py = x * T, y * T
        haut, bas = self.is_wall(x, y - 1), self.is_wall(x, y + 1)
        gauche, droite = self.is_wall(x - 1, y), self.is_wall(x + 1, y)

        debut_x = px if gauche else px + M + R
        fin_x = px + T if droite else px + T - M - R
        debut_y = py if haut else py + M + R
        fin_y = py + T if bas else py + T - M - R
        if not haut:
            self.display.fill_rect(
                debut_x, py + M,
                fin_x - debut_x, E, self.WALL)
        if not bas:
            self.display.fill_rect(
                debut_x, py + T - M - E,
                fin_x - debut_x, E, self.WALL)
        if not gauche:
            self.display.fill_rect(
                px + M, debut_y,
                E, fin_y - debut_y, self.WALL)
        if not droite:
            self.display.fill_rect(
                px + T - M - E, debut_y,
                E, fin_y - debut_y, self.WALL)

        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            mur_x, mur_y = self.is_wall(x + dx, y), self.is_wall(x, y + dy)
            bord_x = px + M if dx < 0 else px + T - M
            bord_y = py + M if dy < 0 else py + T - M

            if not mur_x and not mur_y:
                self.arc(bord_x - dx * R, bord_y - dy * R, dx, dy, R - E, R)

            elif mur_x and mur_y and not self.is_wall(x + dx, y + dy):
                self.arc(bord_x + dx * R, bord_y + dy * R, -dx, -dy, R, R + E)
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
        T, M = self.TAILLE, self.MARGE
        cx = x * T + T / 2
        cy = y * T + T / 2
        rayon = T / 2 - M
        for py in range(y * T + M, y * T + T - M):
            for px in range(x * T + M, x * T + T - M):
                if math.hypot(px + 0.5 - cx, py + 0.5 - cy) <= rayon:
                    self.display.draw_pixel(px, py, self.WALL)

    def render_on_change(self) -> None:
        """manage the drawing of map"""
        self.display.clear(self.FOND)
        for ligne in self.map.grid:
            for cell in ligne:
                if cell.state == "wall":
                    x, y = cell.coordinate
                    if self.is_isole(x, y):
                        self.fill_bloc(x, y)
                    else:
                        self.draw_wall(x, y)
        self.display.render()

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        """unused func"""
        pass

    def render(self) -> None:
        """ display map"""
        self.display.render()


class Game:
    """Class to manage the map display"""
    def __init__(self, engine: Engine) -> None:
        self.NOIR = 0xFF000000
        self.BLEU = 0xFF2121DE
        self.GRIS = 0xFF2A2F31
        self.YELLOW = 0xFFEDE31B
        la_map = Map(7, 15)
        display = engine.create_display(engine.get_window().size())
        self.scenes = SceneManager({"game": GameScene(
            display, la_map,
            (self.NOIR, self.BLEU))})
        self.scenes.change_screen("game")

    def update(self, delta_time: float, input_handler: InputHandler) -> None:
        """unused func"""
        pass

    def render(self) -> None:
        """display"""
        self.scenes.render()


if __name__ == "__main__":
    engine = Engine("Pac-Man")
    engine.run(Game(engine))
