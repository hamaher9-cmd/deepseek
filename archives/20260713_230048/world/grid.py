"""
GRID — N×N toroidal world.
Data-oriented: a 2D list is the single source of truth.
Each cell is None (empty) or holds an entity reference.
"""

from __future__ import annotations
from typing import Optional, Any


class Grid:
    """Toroidal grid. Wrap-around edges on all sides."""

    def __init__(self, size: int = 50):
        if size < 2:
            raise ValueError("Grid size must be >= 2")
        self.size = size
        self._cells: list[list[Optional[Any]]] = [
            [None for _ in range(size)] for _ in range(size)
        ]

    # --- access ---

    def get(self, x: int, y: int) -> Optional[Any]:
        """Return whatever is at (x, y), or None."""
        x, y = self._wrap(x, y)
        return self._cells[y][x]

    def set(self, x: int, y: int, entity: Optional[Any]) -> None:
        """Place entity at (x, y). Overwrites whatever was there."""
        x, y = self._wrap(x, y)
        self._cells[y][x] = entity
        if entity is not None:
            entity.x, entity.y = x, y

    def remove(self, x: int, y: int) -> Optional[Any]:
        """Clear cell and return what was there."""
        entity = self.get(x, y)
        self.set(x, y, None)
        return entity

    def is_empty(self, x: int, y: int) -> bool:
        return self.get(x, y) is None

    # --- neighbors ---

    def neighbors(self, x: int, y: int, distance: int = 1) -> list[tuple[int, int]]:
        """Return list of (nx, ny) coordinates within given Chebyshev distance."""
        result = []
        for dy in range(-distance, distance + 1):
            for dx in range(-distance, distance + 1):
                if dx == 0 and dy == 0:
                    continue
                result.append((self._wrap_x(x + dx), self._wrap_y(y + dy)))
        return result

    def empty_neighbors(self, x: int, y: int, distance: int = 1) -> list[tuple[int, int]]:
        """Return neighbor coordinates that are empty."""
        return [
            (nx, ny) for nx, ny in self.neighbors(x, y, distance)
            if self.is_empty(nx, ny)
        ]

    def cells(self):
        """Iterate over (x, y, entity) for every cell."""
        for y in range(self.size):
            for x in range(self.size):
                yield x, y, self._cells[y][x]

    # --- internal ---

    def _wrap(self, x: int, y: int) -> tuple[int, int]:
        return self._wrap_x(x), self._wrap_y(y)

    def _wrap_x(self, x: int) -> int:
        return x % self.size

    def _wrap_y(self, y: int) -> int:
        return y % self.size
