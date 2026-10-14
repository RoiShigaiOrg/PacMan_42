from mazegenerator import MazeGenerator
from typing import Tuple
import random


class Cell():
    """Class composing the map: coordinates and state"""

    def __init__(self, coordinate: Tuple[int, int], state: str):
        self.coordinate: Tuple[int, int] = coordinate
        self.state: str = state


class Map():
    """class builds the map from the mazegenerator modules"""

    def __init__(
            self, largeur: int = 10, hauteur: int = 10,
            seed: int = random.randint(0, 10)):
        self.TOP = 1
        self.RIGHT = 2
        self.DOWN = 4
        self.LEFT = 8
        gen = MazeGenerator(size=(largeur, hauteur), perfect=False, seed=seed)
        gen.generate(seed=seed)
        self.grid: list[list[Cell]] = self._symmetrize(
            self._convert(gen.maze))
        self.hauteur: int = len(self.grid)
        self.largeur: int = len(self.grid[0])

    def _convert(self, maze: list[list[int]]) -> list[list[Cell]]:
        """converts base-8 data into cells"""
        hauteur, largeur = len(maze), len(maze[0])
        grid = [[Cell((x, y), "wall") for x in range(largeur * 2 + 1)]
                for y in range(hauteur * 2 + 1)]
        for y in range(hauteur):
            for x in range(largeur):
                case = maze[y][x]
                if case == 15:
                    continue
                gx, gy = x * 2 + 1, y * 2 + 1
                grid[gy][gx].state = "corridor"
                if not case & self.RIGHT:
                    grid[gy][gx + 1].state = "corridor"
                if not case & self.DOWN:
                    grid[gy + 1][gx].state = "corridor"
        return grid

    def _symmetrize(
            self, grid: list[list[Cell]],
            gap: int = 4) -> list[list[Cell]]:
        """Flip the map and place it next to the
          original to create symmetry."""
        center = len(grid[0]) - 1
        new: list[list[Cell]] = []

        for y, ligne in enumerate(grid):
            states = [cell.state for cell in ligne]
            states = states + states[-2::-1]
            new.append([Cell((x, y), state) for x, state in enumerate(states)])

        for y in range(1, len(new) - 1, 2):
            if y % gap == 1 and new[y][center - 1].state == "corridor":
                new[y][center].state = "corridor"

        return new
