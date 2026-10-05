from mazegenerator import MazeGenerator
from typing import Tuple


class Cell():
    def __init__(self, coordinate: Tuple[int, int], state: str):
        self.coordinate: Tuple[int, int] = coordinate
        self.state: str = state


class Map():
    def __init__(self, largeur: int = 20, hauteur: int = 20, seed: int = 42):
        self.HAUT = 1
        self.DROITE = 2
        self.BAS = 4
        self.GAUCHE = 8
        gen = MazeGenerator(size=(largeur, hauteur), perfect=False, seed=seed)
        gen.generate(seed=seed)
        self.grid: list[list[Cell]] = self._convertir(gen.maze)
        self.hauteur: int = len(self.grid)
        self.largeur: int = len(self.grid[0])

    def _convertir(self, maze: list[list[int]]) -> list[list[Cell]]:
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
                if not case & self.DROITE:
                    grid[gy][gx + 1].state = "corridor"
                if not case & self.BAS:
                    grid[gy + 1][gx].state = "corridor"
        return grid


if __name__ == "__main__":
    map = Map(10, 15)
    for line in map.grid:
        for cell in line:
            print(cell.coordinate, cell.state)
