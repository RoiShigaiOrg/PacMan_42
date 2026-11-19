from collections import deque
from Engine.Engine import Engine
from Engine.Graphics import MlxDisplay
from Engine.Animation import Animation, AnimationHandler
from Engine.Sprite import Sprite
from mazegenerator import MazeGenerator
from typing import Dict, Mapping, Tuple, List, Sequence
from Engine.Physics.Collider import Collider
from Engine.Physics.Vector2 import Vector2
from pathlib import Path
from .Cell import Cell
from .MapNode import MapNode
import random
import math

TOP: int = 1
RIGHT: int = 2
DOWN: int = 4
LEFT: int = 8

HIGH_LEFT: int = 1
HIGH_RIGHT: int = 2
LOW_LEFT: int = 3
LOW_RIGHT: int = 4

WALL_MASK_TO_TAG: dict[int, str] = {
    0: "solo",
    TOP: "bottom",
    RIGHT: "left",
    DOWN: "top",
    LEFT: "right",
    TOP | DOWN: "vertical",
    RIGHT | LEFT: "horizontal",
    TOP | RIGHT: "corner_bot_left",
    TOP | LEFT: "corner_bot_right",
    DOWN | RIGHT: "corner_top_left",
    DOWN | LEFT: "corner_top_right",
    TOP | RIGHT | LEFT: "horizontal_top",
    DOWN | RIGHT | LEFT: "horizontal_bot",
    TOP | DOWN | RIGHT: "vertical_right",
    TOP | DOWN | LEFT: "vertical_left",
    TOP | RIGHT | DOWN | LEFT: "center",
}

Region = Tuple[int, int, int, int]


def wall_neighbor_mask(
        grid: list[list[Cell]], column: int, row: int
) -> int:
    """Return the cardinal wall-neighbor mask for one cell.

    Out-of-bounds neighbors are treated as open space. The direction bits
    reuse the maze's TOP, RIGHT, DOWN, and LEFT flags.
    """
    height = len(grid)
    width = len(grid[0])
    mask = 0

    if row > 0 and not grid[row - 1][column].walkable:
        mask |= TOP
    if column + 1 < width and not grid[row][column + 1].walkable:
        mask |= RIGHT
    if row + 1 < height and not grid[row + 1][column].walkable:
        mask |= DOWN
    if column > 0 and not grid[row][column - 1].walkable:
        mask |= LEFT

    return mask


class Map():
    """class builds the map from the mazegenerator modules"""

    def __init__(
            self, engine: Engine, width: int = 5, height: int = 5):
        """ Init Method of Map Generation """
        seed: int = random.randint(0, 100)
        gen = MazeGenerator(size=(width, height), perfect=False, seed=seed)
        gen.generate(seed=seed)
        self.grid: List[List[Cell]] = self._symmetrize_vertical(
                self._convert(gen.maze)
            )
        self.grid = self._symmetrize_horizontal(
                self.grid
            )
        self.height: int = len(self.grid)
        self.width: int = len(self.grid[0])
        self._open_center()
        wall_sheet = engine.load_sprite_sheet(
            Path("assets/Map/mapspritesheet.png"),
            Path("assets/Map/Mapspritesheet.json"),
        )
        self.__wall_sprites: dict[int, Sprite] = {
            mask: wall_sheet.get_sprite(tag)[0].sprite
            for mask, tag in WALL_MASK_TO_TAG.items()
        }
        self.__corner_coordinates = self._find_corner_coordinates()
        self.__corner_cells = frozenset(
            self.__corner_coordinates.values()
        )
        self.__pellet: List[Cell] = [
            cell
            for row in self.grid
            for cell in row
            if cell.walkable
        ]
        self.__pellet_coordinates = {
            pellet.coordinate for pellet in self.__pellet
        }
        self.__pacgum_sprite: Sprite = engine.load_sprite_sheet(
                Path("assets/Pellet/pacgum.png")
            ).extract_sprite((0, 0), (32, 32))
        pellet_frames = engine.load_sprite_sheet(
            Path("assets/Pellet/pelletspritesheet.png"),
            Path("assets/Pellet/pelletspritesheet.json"),
        ).get_sprite("animation")
        self.__animation_handler = AnimationHandler({
            "pellet": Animation(pellet_frames),
        })
        self.__grid_origin: Tuple[int, int] | None = None
        self.__cell_size: Tuple[int, int] | None = None
        self.graph: Dict[Tuple[int, int], MapNode] = self.build_graph()
        print("map generated")

    def contain_pellet(self) -> bool:
        """
        Return a boolean indicating if there is pellet or
            not in the map.
        """
        return True if self.__pellet else False

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

    def corner(self, corner: int = HIGH_LEFT) -> Tuple[int, int]:
        """Return the cached nearest walkable cell for a map corner."""
        if corner not in (HIGH_LEFT, HIGH_RIGHT, LOW_LEFT, LOW_RIGHT):
            raise ValueError(f"Unknown map corner: {corner}")
        try:
            return self.__corner_coordinates[corner]
        except (AttributeError, KeyError) as error:
            raise ValueError("Map has no walkable cells") from error

    def _find_corner_coordinates(self) -> dict[int, Tuple[int, int]]:
        """Find nearest walkable cells in stable corner-relative order.

        Cells are checked in increasing Manhattan-distance layers. Within a
        layer, the scan proceeds along the corner's outer edge before moving
        inward, giving ties a stable, corner-relative order.
        """
        corners: dict[int, tuple[Tuple[int, int], int, int]] = {
            HIGH_LEFT: ((0, 0), 1, 1),
            HIGH_RIGHT: ((self.width - 1, 0), -1, 1),
            LOW_LEFT: ((0, self.height - 1), 1, -1),
            LOW_RIGHT: ((self.width - 1, self.height - 1), -1, -1),
        }
        coordinates: dict[int, Tuple[int, int]] = {}
        max_distance = self.width + self.height - 2
        for corner, (
                (start_column, start_row), column_step, row_step
        ) in corners.items():
            for distance in range(max_distance + 1):
                for row_distance in range(distance + 1):
                    column_distance = distance - row_distance
                    column = start_column + column_step * column_distance
                    row = start_row + row_step * row_distance
                    if (
                        0 <= column < self.width
                        and 0 <= row < self.height
                        and self.grid[row][column].walkable
                    ):
                        coordinates[corner] = (column, row)
                        break
                if corner in coordinates:
                    break
            else:
                raise ValueError("Map has no walkable cells")

        return coordinates

    def is_corner(self, pos: Tuple[int, int]) -> bool:
        """ Return a boolean if the given position is a map corner """
        coordinate = self.cell_coordinates_at(pos)
        return (coordinate in self.__corner_cells)

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

    @property
    def pellet_cells(self) -> tuple[Tuple[int, int], ...]:
        """Return coordinates for cells that still contain a pellet."""
        return tuple(cell.coordinate for cell in self.__pellet)

    @property
    def pellet_bounds(self) -> Tuple[int, int, int, int]:
        """Return the pixel bounds of the map's pellet grid."""
        origin_x, origin_y = self.grid_origin
        cell_width, cell_height = self.cell_size
        return (
            origin_x,
            origin_y,
            self.width * cell_width,
            self.height * cell_height,
        )

    @property
    def animated_pellet_regions(self) -> tuple[Region, ...]:
        """Return dirty regions for corner pellets that remain on the map."""
        return tuple(
            self.cell_region(coordinate)
            for coordinate in sorted(self.__corner_cells)
            if coordinate in self.__remaining_pellet_coordinates()
        )

    def cell_region(
            self, coordinate: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        """Return the pixel rectangle for a cell coordinate."""
        column, row = coordinate
        origin_x, origin_y = self.grid_origin
        cell_width, cell_height = self.cell_size
        return (
            origin_x + column * cell_width,
            origin_y + row * cell_height,
            cell_width,
            cell_height,
        )

    def consume_pellet_at(self, position: Vector2) -> Cell | None:
        """Remove and return the pellet in the cell containing a position."""
        coordinate = self.cell_coordinates_at(position)
        remaining = self.__remaining_pellet_coordinates()
        if coordinate not in remaining:
            return None

        for index, pellet in enumerate(self.__pellet):
            if pellet.coordinate == coordinate:
                remaining.remove(coordinate)
                return self.__pellet.pop(index)
        return None

    def __remaining_pellet_coordinates(self) -> set[Tuple[int, int]]:
        """Return the coordinate index, building it if not initialized."""
        if not hasattr(self, "_Map__pellet_coordinates"):
            self.__pellet_coordinates = {
                pellet.coordinate for pellet in self.__pellet
            }
        return self.__pellet_coordinates

    def update_pellet_animation(self, delta_time: float) -> bool:
        """Advance the shared pellet animation and report frame changes."""
        previous_frame = self.__animation_handler.current_frame_index
        self.__animation_handler.update(delta_time)
        return bool(
            self.__animation_handler.current_frame_index != previous_frame
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

    def build_graph(self) -> Dict[Tuple[int, int], MapNode]:
        """ Return a Graph representation of the map """
        graph: Dict[Tuple[int, int], MapNode] = {
                    cell.coordinate: MapNode(cell.coordinate)
                    for row in self.grid
                    for cell in row
                    if cell.walkable
                }
        for (column, row), node in graph.items():
            for neighbor_coordinate in (
                    (column + 1,
                     row), (column, row + 1)):
                neighbor = graph.get(neighbor_coordinate)
                if neighbor is not None:
                    node.connect(neighbor, 1.0)
                    neighbor.connect(node, 1.0)
        return graph

    def graph_territories(
            self,
            origins: Mapping[str, Tuple[int, int]],
            max_distance: int,
    ) -> Dict[str, set[Tuple[int, int]]]:
        """Partition nearby graph cells between the supplied origins.

        A multi-source breadth-first search gives each reachable cell to its
        nearest origin, stopping expansion at ``max_distance`` graph edges.
        Equal-distance ties are resolved by the order of ``origins``.
        Cells outside every origin's radius, and disconnected components, are
        left unassigned.
        """
        if max_distance < 0:
            raise ValueError("max_distance must not be negative")

        territories: Dict[str, set[Tuple[int, int]]] = {
            name: set() for name in origins
        }
        distances: Dict[Tuple[int, int], int] = {}
        owners: Dict[Tuple[int, int], str] = {}
        pending: deque[Tuple[int, int]] = deque()

        for name, origin in origins.items():
            if origin not in self.graph:
                raise ValueError(f"Territory origin is not walkable: {origin}")
            if origin in owners:
                raise ValueError("Territory origins must be distinct")
            owners[origin] = name
            distances[origin] = 0
            territories[name].add(origin)
            pending.append(origin)

        while pending:
            coordinate = pending.popleft()
            distance = distances[coordinate]
            if distance == max_distance:
                continue

            owner = owners[coordinate]
            for neighbor, _cost in self.graph[coordinate].neighbors():
                next_coordinate = neighbor.coordinate
                if next_coordinate in owners:
                    continue
                owners[next_coordinate] = owner
                distances[next_coordinate] = distance + 1
                territories[owner].add(next_coordinate)
                pending.append(next_coordinate)

        return territories

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
        """Fit a centered, square-cell grid inside the requested bounds."""
        if width <= 0 or height <= 0:
            raise ValueError("map bounds must have positive dimensions")

        cell_size = min(width // self.width, height // self.height)
        if cell_size <= 0:
            raise ValueError("map bounds are too small for square cells")

        grid_width = cell_size * self.width
        grid_height = cell_size * self.height
        grid_origin_x = pos_x + (width - grid_width) // 2
        grid_origin_y = pos_y + (height - grid_height) // 2
        self.__grid_origin = (grid_origin_x, grid_origin_y)
        self.__cell_size = (cell_size, cell_size)

        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].set_collider(
                        grid_origin_x + cell_size * x,
                        grid_origin_y + cell_size * y,
                        cell_size,
                        cell_size,
                    )

    def render_pellets(
            self,
            display: MlxDisplay,
            regions: Sequence[Region] | None = None,
    ) -> None:
        """Draw pellets in the supplied dirty regions, or all if omitted."""
        cell_width, cell_height = self.cell_size
        origin_x, origin_y = self.grid_origin
        if regions is None:
            coordinates = tuple(
                pellet.coordinate for pellet in self.__pellet
            )
        else:
            if not regions:
                return
            coordinates = tuple(sorted(
                self.__pellets_in_regions(regions)
            ))

        sprite: Sprite = self.__animation_handler.current_sprite
        for column, row in coordinates:
            coordinate = (column, row)
            x = origin_x + column * cell_width
            y = origin_y + row * cell_height

            if coordinate in self.__corner_cells:
                sprite.draw(
                    display,
                    (x, y),
                    (cell_width, cell_height)
                )
            else:
                self.__pacgum_sprite.draw(
                    display,
                    (x, y),
                    (cell_width, cell_height),
                )

    def __pellets_in_regions(
            self, regions: Sequence[Region]
    ) -> set[Tuple[int, int]]:
        """Find remaining pellets by visiting cells covered by dirty areas."""
        origin_x, origin_y = self.grid_origin
        cell_width, cell_height = self.cell_size
        map_right = origin_x + self.width * cell_width
        map_bottom = origin_y + self.height * cell_height
        remaining = self.__remaining_pellet_coordinates()
        coordinates: set[Tuple[int, int]] = set()

        for x, y, width, height in regions:
            left = max(x, origin_x)
            top = max(y, origin_y)
            right = min(x + width, map_right)
            bottom = min(y + height, map_bottom)
            if left >= right or top >= bottom:
                continue

            first_column = (left - origin_x) // cell_width
            first_row = (top - origin_y) // cell_height
            column_stop = min(
                self.width,
                (right - origin_x + cell_width - 1) // cell_width,
            )
            row_stop = min(
                self.height,
                (bottom - origin_y + cell_height - 1) // cell_height,
            )
            for row in range(first_row, row_stop):
                for column in range(first_column, column_stop):
                    coordinate = (column, row)
                    if coordinate in remaining:
                        coordinates.add(coordinate)

        return coordinates

    def draw(self, display: MlxDisplay) -> None:
        """Draw the previously configured grid using its collider layout."""
        grid_origin_x, grid_origin_y = self.grid_origin
        cell_width, cell_height = self.cell_size

        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                wall_sprite = None
                if not cell.walkable:
                    wall_sprite = self.__wall_sprites[
                        wall_neighbor_mask(self.grid, x, y)
                    ]
                self.grid[y][x].draw(
                        display,
                        grid_origin_x + cell_width * x,
                        grid_origin_y + cell_height * y,
                        cell_width, cell_height,
                        wall_sprite,
                    )
