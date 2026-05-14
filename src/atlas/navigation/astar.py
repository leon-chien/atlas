from __future__ import annotations

from collections.abc import Iterable
from heapq import heappop, heappush

import numpy as np

GridPoint = tuple[int, int]


def _neighbors(point: GridPoint, shape: tuple[int, int]) -> Iterable[GridPoint]:
    row, col = point
    for next_row, next_col in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
        if 0 <= next_row < shape[0] and 0 <= next_col < shape[1]:
            yield next_row, next_col


def _manhattan(a: GridPoint, b: GridPoint) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def plan_grid_path(occupancy: np.ndarray, start: GridPoint, goal: GridPoint) -> list[GridPoint]:
    """Plan a 4-connected A* path through a 2D occupancy grid where nonzero cells are blocked."""
    if occupancy.ndim != 2:
        raise ValueError("occupancy must be a 2D grid")
    if occupancy[start] != 0 or occupancy[goal] != 0:
        raise ValueError("start and goal must be in free space")

    frontier: list[tuple[int, GridPoint]] = []
    heappush(frontier, (0, start))
    came_from: dict[GridPoint, GridPoint | None] = {start: None}
    cost_so_far: dict[GridPoint, int] = {start: 0}

    while frontier:
        _, current = heappop(frontier)
        if current == goal:
            break
        for neighbor in _neighbors(current, occupancy.shape):
            if occupancy[neighbor] != 0:
                continue
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + _manhattan(neighbor, goal)
                heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    if goal not in came_from:
        return []

    path = [goal]
    current = goal
    while came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    return list(reversed(path))
