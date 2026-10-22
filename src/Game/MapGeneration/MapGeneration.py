from Engine.Graphics import MlxDisplay
from mazegenerator import MazeGenerator
from .Cell import Cell
import random

TOP: int = 1
RIGHT: int = 2
DOWN: int = 4
LEFT: int = 8


class Map():
    """class builds the map from the mazegenerator modules"""

    def __init__(
            self, width: int = 5, height: int = 5,
            seed: int = random.randint(0, 10)):
        """ Init Method of Map Generation """

        gen = MazeGenerator(size=(width, height), perfect=False, seed=seed)
        gen.generate(seed=seed)
        self.grid: list[list[Cell]] = self._symmetrize_vertical(
                self._convert(gen.maze)
            )
        self.grid = self._symmetrize_horizontal(
                self.grid
            )
        self.height: int = len(self.grid)
        self.width: int = len(self.grid[0])

    def _convert(self, maze: list[list[int]]) -> list[list[Cell]]:
        """converts base-8 data into cells"""
        height, width = len(maze), len(maze[0])
        grid = [[Cell((x, y), False) for x in range(width * 2 + 1)]
                for y in range(height * 2 + 1)]
        for y in range(height):
            for x in range(width):
                case = maze[y][x]
                if case == 15:
                    continue
                gx, gy = x * 2 + 1, y * 2 + 1
                grid[gy][gx].walkable = True
                if not case & RIGHT:
                    grid[gy][gx + 1].walkable = True
                if not case & DOWN:
                    grid[gy + 1][gx].walkable = True
        return grid

    def _symmetrize_horizontal(
            self, grid: list[list[Cell]],
            gap: int = 4) -> list[list[Cell]]:
        """Flip the map and place it next to the
          original to create symmetry."""
        center = len(grid[0]) - 1
        new: list[list[Cell]] = []

        for y, ligne in enumerate(grid):
            states = [cell.walkable for cell in ligne]
            states = states + states[-2::-1]
            new.append([Cell((x, y), state) for x, state in enumerate(states)])

        for y in range(1, len(new) - 1, 2):
            if y % gap == 1 and new[y][center - 1].walkable:
                new[y][center].walkable = True

        return new

    def _symmetrize_vertical(
            self, grid: list[list[Cell]],
            gap: int = 4) -> list[list[Cell]]:
        """Mirror the map from top to bottom."""

        original_height = len(grid)
        new = [
            [Cell((x, y), cell.walkable) for x, cell in enumerate(row)]
            for y, row in enumerate(grid)
        ]

        for row in grid[-2::-1]:
            y = len(new)
            new.append([
                Cell((x, y), cell.walkable)
                for x, cell in enumerate(row)
            ])
        center = original_height - 1

        for x in range(1, len(new[0]) - 1, 2):
            if x % gap == 1 and new[center - 1][x].walkable:
                new[center][x].walkable = True

        return new

    def draw(
            self,
            display: MlxDisplay,
            pos_x: int, pos_y: int,
            width: int, height: int) -> None:
        """ Draw method of the Map Object """
        cell_height: int = int(height / self.height)
        cell_width: int = int(width / self.width)

        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].draw(
                        display,
                        pos_x + (cell_width * x), pos_y + (cell_height * y),
                        cell_width, cell_height
                    )
