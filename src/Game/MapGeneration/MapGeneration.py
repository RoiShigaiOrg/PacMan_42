from Engine.Graphics import MlxDisplay
from mazegenerator import MazeGenerator
from typing import Tuple, List
from Engine.Physics.Collider import Collider
from Engine.Physics.Vector2 import Vector2
from .Cell import Cell
import random
import math

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
        self._open_center()
        self.__grid_origin: Tuple[int, int] | None = None
        self.__cell_size: Tuple[int, int] | None = None

    def center(self) -> Tuple[int, int]:
        """ Return the center coordonates of the map """
        return (int(self.width / 2), int(self.height / 2))

    def size(self) -> Tuple[int, int]:
        """ Return the size of the Map object """
        return (self.width, self.height)

    def wall_colliders(self) -> tuple[Collider, ...]:
        """Return the colliders for every non-walkable cell."""
        return tuple(
            collider
            for row in self.grid
            for cell in row
            if (collider := cell.collider) is not None
        )

    @property
    def grid_origin(self) -> Tuple[int, int]:
        """Return the pixel position of the map's top-left cell."""
        if self.__grid_origin is None:
            raise RuntimeError("Map colliders must be configured first")
        return self.__grid_origin

    @property
    def cell_size(self) -> Tuple[int, int]:
        """Return the pixel dimensions of each map cell."""
        if self.__cell_size is None:
            raise RuntimeError("Map colliders must be configured first")
        return self.__cell_size

    def cell_coordinates_at(self, position: Vector2) -> Tuple[int, int]:
        """Return the column and row containing a world-space position."""
        pos_x, pos_y = self.grid_origin
        cell_width, cell_height = self.cell_size
        return (
            math.floor((position.x - pos_x) / cell_width),
            math.floor((position.y - pos_y) / cell_height),
        )

    def is_walkable_cell(self, column: int, row: int) -> bool:
        """Return whether a cell is in bounds and walkable."""
        return (
            0 <= column < self.width
            and 0 <= row < self.height
            and self.grid[row][column].walkable
        )

    def next_cell_is_walkable(
            self, position: Vector2, direction: Vector2
    ) -> bool:
        """Return whether the adjacent cell in a direction can be entered."""
        column, row = self.cell_coordinates_at(position)
        return self.is_walkable_cell(
            column + int(direction.x), row + int(direction.y)
        )

    def is_cell_centered(
            self, position: Vector2, tolerance: float = 1e-6
    ) -> bool:
        """Return whether a world-space position is at a cell center."""
        column, row = self.cell_coordinates_at(position)
        if not self.is_walkable_cell(column, row):
            return False
        pos_x, pos_y = self.grid_origin
        cell_width, cell_height = self.cell_size
        center_x = pos_x + (column + 0.5) * cell_width
        center_y = pos_y + (row + 0.5) * cell_height
        return bool(
            abs(position.x - center_x) <= tolerance
            and abs(position.y - center_y) <= tolerance
        )

    def build_graph(self) -> List[Tuple[int, ...]]:
        """ Return a Graph representation of the map """
        graph: List[Tuple[int, ...]] = [()] * (self.width * self.height)
        direction: Tuple[Tuple[int, int]] = (
                (0, -1),
                (1, 0),
                (0, 1),
                (-1, 0)
            )
        for row in range(self.height):
            for column in range(self.width):
                if not self.grid[row][column].walkable:
                    continue
                cell_id = row * self.width + column
                neighbor = []

                for dx, dy in direction:
                    next_column = column + dx
                    next_row = row + dy
                    if ( 0 <= next_column < self.width
                        and 0 <= next_row < self.height
                        and self.grid[next_row][next_column].walkable):
                        neighbor.append(next_row * self.width + next_column)
                graph[cell_id] = tuple(neighbor)
        return graph

    def _open_center(self) -> None:
        """ Free the center of the map so the Player is not blocked """
        center: Tuple[int, int] = self.center()
        start: Tuple[int, int] = (center[0] - 1, center[1] - 1)

        for y in range(start[1], start[1] + 3):
            for x in range(start[0], start[0] + 3):
                self.grid[x][y].walkable = True

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

    def set_colliders(
            self,
            pos_x: int, pos_y: int,
            width: int, height: int) -> None:
        """ The colliders for every cells in the map """
        cell_height: int = int(height / self.height)
        cell_width: int = int(width / self.width)
        self.__grid_origin = (pos_x, pos_y)
        self.__cell_size = (cell_width, cell_height)

        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].set_collider(
                        pos_x + (cell_width * x), pos_y + (cell_height * y),
                        cell_width, cell_height
                    )

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
