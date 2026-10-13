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
            self, largeur: int = 20, hauteur: int = 20,
            seed: int = random.randint(0, 10)):
        self.HAUT = 1
        self.DROITE = 2
        self.BAS = 4
        self.GAUCHE = 8
        gen = MazeGenerator(size=(largeur, hauteur), perfect=False, seed=seed)
        gen.generate(seed=seed)
        self.grid: list[list[Cell]] = self._symetriser(
            self._convertir(gen.maze))
        self.hauteur: int = len(self.grid)
        self.largeur: int = len(self.grid[0])

    def _convertir(self, maze: list[list[int]]) -> list[list[Cell]]:
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
                if not case & self.DROITE:
                    grid[gy][gx + 1].state = "corridor"
                if not case & self.BAS:
                    grid[gy + 1][gx].state = "corridor"
        return grid

    def _symetriser(
            self, grid: list[list[Cell]],
            ecart: int = 4) -> list[list[Cell]]:
        """Flip the map and place it next to the
          original to create symmetry."""
        centre = len(grid[0]) - 1
        new: list[list[Cell]] = []

        for y, ligne in enumerate(grid):
            etats = [cell.state for cell in ligne]
            etats = etats + etats[-2::-1]
            new.append([Cell((x, y), etat) for x, etat in enumerate(etats)])

        for y in range(1, len(new) - 1, 2):
            if y % ecart == 1 and new[y][centre - 1].state == "corridor":
                new[y][centre].state = "corridor"

        return new


if __name__ == "__main__":
    map = Map(5, 8)
    for line in map.grid:
        for cell in line:
            if cell.state == "wall":
                print("█", end="")
            elif cell.state == "corridor":
                print(" ", end="")
            elif cell.state == "ghost_house":
                print(" ", end="")
            elif cell.state == "door":
                print("‾", end="")
        print()
