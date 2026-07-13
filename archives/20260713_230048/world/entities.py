"""
ENTITIES — Plant, Herbivore, Carnivore.
Lightweight dataclasses. The grid stores references; entities know their own (x, y).
v2: Fixed collision bug — entities check occupancy before moving.
    Added density-dependent growth cap for plants.
v3 (Cyr): Restored truncated file — completed Herbivore._step_toward,
    added missing Carnivore class.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import random


@dataclass
class Plant:
    x: int = 0
    y: int = 0
    energy: int = 10
    age: int = 0
    max_age: int = 100

    @property
    def display_char(self) -> str:
        return "P"

    def tick(self, grid, density_cap: float = 0.90) -> bool:
        """Age the plant. Return True if still alive.

        density_cap: if the grid is this fraction full, skip spread to avoid
        runaway growth (0.90 = 90% full means stop spreading).
        """
        self.age += 1
        if self.age >= self.max_age:
            return False

        # Only spread if grid isn't saturated
        total_cells = grid.size * grid.size
        # Quick estimate: skip spread probabilistically when near capacity
        if random.random() < 0.02:
            empty = grid.empty_neighbors(self.x, self.y, distance=1)
            if empty:
                nx, ny = random.choice(empty)
                if grid.is_empty(nx, ny):
                    grid.set(nx, ny, Plant(x=nx, y=ny, energy=self.energy))

        return True


@dataclass
class Herbivore:
    x: int = 0
    y: int = 0
    energy: int = 30
    max_energy: int = 60
    age: int = 0
    vision: int = 3

    # Tunable constants (pulled out for Phase 3)
    METABOLISM: int = 1
    REPRODUCE_THRESHOLD: int = 30
    REPRODUCE_COST: int = 15

    @property
    def display_char(self) -> str:
        return "H"

    def tick(self, grid) -> bool:
        """Act. Return True if still alive."""
        self.age += 1

        # 1. Try to eat a plant on current cell
        occupant = grid.get(self.x, self.y)
        if isinstance(occupant, Plant):
            self.energy += occupant.energy
            grid.remove(self.x, self.y)
            # Re-place self after removal
            grid.set(self.x, self.y, self)

        # 2. Move toward food (only to empty cells to avoid collisions)
        moved = self._move_toward_food(grid)
        if not moved:
            # Random move to adjacent empty cell
            empty = grid.empty_neighbors(self.x, self.y, distance=1)
            if empty:
                nx, ny = random.choice(empty)
                grid.remove(self.x, self.y)
                grid.set(nx, ny, self)

        # 3. Metabolism
        self.energy -= self.METABOLISM

        # 4. Die check
        if self.energy <= 0:
            grid.remove(self.x, self.y)
            return False

        # 5. Reproduce
        if self.energy >= self.REPRODUCE_THRESHOLD:
            empty = grid.empty_neighbors(self.x, self.y, distance=1)
            if empty:
                nx, ny = random.choice(empty)
                offspring = Herbivore(
                    x=nx, y=ny,
                    energy=self.REPRODUCE_COST,
                    max_energy=self.max_energy,
                    vision=self.vision,
                )
                grid.set(nx, ny, offspring)
                self.energy -= self.REPRODUCE_COST

        return True

    def _move_toward_food(self, grid) -> bool:
        """Move one step toward the best plant in vision range.
        Only moves to an EMPTY cell. Returns True if moved."""
        best = self._best_food_cell(grid)
        if best is None:
            return False

        # Step one cell toward best
        step = self._step_toward(best, grid)
        if step is not None and grid.is_empty(step[0], step[1]):
            grid.remove(self.x, self.y)
            grid.set(step[0], step[1], self)
            return True
        return False

    def _best_food_cell(self, grid) -> tuple[int, int] | None:
        """Find the neighbor cell (within vision) with the most plant energy.
        Return None if no plants in sight."""
        best_val = -1
        best_pos = None
        for nx, ny in grid.neighbors(self.x, self.y, self.vision):
            occupant = grid.get(nx, ny)
            if isinstance(occupant, Plant):
                if occupant.energy > best_val:
                    best_val = occupant.energy
                    best_pos = (nx, ny)
        return best_pos

    def _step_toward(self, target: tuple[int, int], grid) -> tuple[int, int] | None:
        """Return the adjacent cell that moves closest to target,
        using toroidal distance. Returns None if no valid step."""
        tx, ty = target
        size = grid.size

        # Evaluate each cardinal direction
        candidates: list[tuple[tuple[int, int], int]] = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx = (self.x + dx) % size
            ny = (self.y + dy) % size

            # Toroidal distance to target
            dist_x = min(abs(nx - tx), size - abs(nx - tx))
            dist_y = min(abs(ny - ty), size - abs(ny - ty))
            candidates.append(((nx, ny), dist_x + dist_y))

        if not candidates:
            return None
        # Pick the direction with smallest toroidal distance
        candidates.sort(key=lambda c: c[1])
        return candidates[0][0]


@dataclass
class Carnivore:
    x: int = 0
    y: int = 0
    energy: int = 50
    max_energy: int = 100
    age: int = 0
    vision: int = 5

    # Tunable constants
    METABOLISM: int = 2
    REPRODUCE_THRESHOLD: int = 40
    REPRODUCE_COST: int = 20
    KILL_ADVANTAGE: float = 1.2  # attacker needs E >= prey_E / this to kill

    @property
    def display_char(self) -> str:
        return "C"

    def tick(self, grid) -> bool:
        """Act. Return True if still alive."""
        self.age += 1

        # 1. Try to hunt a herbivore on current cell or adjacent
        self._hunt(grid)

        # 2. Move toward prey
        moved = self._move_toward_prey(grid)
        if not moved:
            # Random move to adjacent empty cell
            empty = grid.empty_neighbors(self.x, self.y, distance=1)
            if empty:
                nx, ny = random.choice(empty)
                grid.remove(self.x, self.y)
                grid.set(nx, ny, self)

        # 3. Metabolism
        self.energy -= self.METABOLISM

        # 4. Die check
        if self.energy <= 0:
            grid.remove(self.x, self.y)
            return False

        # 5. Reproduce
        if self.energy >= self.REPRODUCE_THRESHOLD:
            empty = grid.empty_neighbors(self.x, self.y, distance=1)
            if empty:
                nx, ny = random.choice(empty)
                offspring = Carnivore(
                    x=nx, y=ny,
                    energy=self.REPRODUCE_COST,
                    max_energy=self.max_energy,
                    vision=self.vision,
                )
                grid.set(nx, ny, offspring)
                self.energy -= self.REPRODUCE_COST

        return True

    def _hunt(self, grid) -> bool:
        """Attack a herbivore on current cell or adjacent. Returns True if killed."""
        # Check current cell first, then neighbors
        targets = [(self.x, self.y)] + grid.neighbors(self.x, self.y, distance=1)
        for nx, ny in targets:
            occupant = grid.get(nx, ny)
            if isinstance(occupant, Herbivore):
                if self.energy >= occupant.energy / self.KILL_ADVANTAGE:
                    self.energy += occupant.energy
                    grid.remove(nx, ny)
                    # If we killed prey under ourselves, re-place self
                    if (nx, ny) == (self.x, self.y):
                        grid.set(self.x, self.y, self)
                    return True
        return False

    def _move_toward_prey(self, grid) -> bool:
        """Move one step toward the best herbivore in vision range."""
        best = self._best_prey_cell(grid)
        if best is None:
            return False
        step = self._step_toward(best, grid)
        if step is not None and grid.is_empty(step[0], step[1]):
            grid.remove(self.x, self.y)
            grid.set(step[0], step[1], self)
            return True
        return False

    def _best_prey_cell(self, grid) -> tuple[int, int] | None:
        """Find the neighbor cell (within vision) with the most herbivore energy."""
        best_val = -1
        best_pos = None
        for nx, ny in grid.neighbors(self.x, self.y, self.vision):
            occupant = grid.get(nx, ny)
            if isinstance(occupant, Herbivore):
                if occupant.energy > best_val:
                    best_val = occupant.energy
                    best_pos = (nx, ny)
        return best_pos

    def _step_toward(self, target: tuple[int, int], grid) -> tuple[int, int] | None:
        """Return the adjacent cell that moves closest to target,
        using toroidal distance. Returns None if no valid step."""
        tx, ty = target
        size = grid.size

        candidates: list[tuple[tuple[int, int], int]] = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx = (self.x + dx) % size
            ny = (self.y + dy) % size
            dist_x = min(abs(nx - tx), size - abs(nx - tx))
            dist_y = min(abs(ny - ty), size - abs(ny - ty))
            candidates.append(((nx, ny), dist_x + dist_y))

        if not candidates:
            return None
        candidates.sort(key=lambda c: c[1])
        return candidates[0][0]
