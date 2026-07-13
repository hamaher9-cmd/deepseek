"""
ENGINE — Tick orchestration.
Owns the Grid, runs the simulation loop, collects stats.
v2: Density-dependent plant growth. Collision-safe entity processing.
"""

from __future__ import annotations
import random
from grid import Grid
from entities import Plant, Herbivore, Carnivore


class Engine:
    """Runs the ecosystem tick by tick."""

    def __init__(self, size: int = 50):
        self.grid = Grid(size)
        self.tick_count = 0
        self.total_cells = size * size

        # Stats per tick
        self.stats = {"plants": 0, "herbivores": 0, "carnivores": 0, "tick": 0}

    def populate(self, plants: int = 100, herbivores: int = 30, carnivores: int = 6):
        """Seed the grid with initial entities at random positions."""
        size = self.grid.size
        all_positions = [(x, y) for y in range(size) for x in range(size)]
        random.shuffle(all_positions)

        idx = 0
        for _ in range(plants):
            if idx >= len(all_positions):
                break
            x, y = all_positions[idx]
            self.grid.set(x, y, Plant(x=x, y=y))
            idx += 1

        for _ in range(herbivores):
            if idx >= len(all_positions):
                break
            x, y = all_positions[idx]
            self.grid.set(x, y, Herbivore(x=x, y=y))
            idx += 1

        for _ in range(carnivores):
            if idx >= len(all_positions):
                break
            x, y = all_positions[idx]
            self.grid.set(x, y, Carnivore(x=x, y=y))
            idx += 1

    def tick(self) -> dict:
        """Advance the simulation by one tick. Returns stats dict."""
        self.tick_count += 1

        # Collect all living entities from the grid
        entities = self._gather_entities()

        # Separate by type
        plants = [e for e in entities if isinstance(e, Plant)]
        herbivores = [e for e in entities if isinstance(e, Herbivore)]
        carnivores = [e for e in entities if isinstance(e, Carnivore)]

        # Randomize within each group for fairness
        random.shuffle(plants)
        random.shuffle(herbivores)
        random.shuffle(carnivores)

        # Current occupancy for density calculations
        occupancy = len(entities) / self.total_cells

        # Tick plants (growth, spread, aging)
        for plant in plants:
            # Verify the plant is still where we think it is
            if self.grid.get(plant.x, plant.y) is plant:
                plant.tick(self.grid)

        # Tick herbivores
        for herb in herbivores:
            if self.grid.get(herb.x, herb.y) is herb:
                herb.tick(self.grid)

        # Tick carnivores
        for carn in carnivores:
            if self.grid.get(carn.x, carn.y) is carn:
                carn.tick(self.grid)

        # Spontaneous plant growth — density-dependent
        self._spontaneous_growth(occupancy)

        # Gather stats
        self._update_stats()
        return dict(self.stats)

    def _gather_entities(self) -> list:
        """Collect every entity on the grid into a flat list."""
        result = []
        for _, _, entity in self.grid.cells():
            if entity is not None:
                result.append(entity)
        return result

    def _spontaneous_growth(self, current_occupancy: float):
        """Each empty cell has a chance to sprout a new plant.
        Growth rate tapers as the grid fills up:
        - Below 40% occupancy: base rate (5%)
        - 40-70%: linearly decreasing
        - Above 70%: sharply reduced (1% or less)
        - Above 90%: almost zero
        """
        if current_occupancy < 0.40:
            rate = 0.05
        elif current_occupancy < 0.70:
            # Linear taper from 5% down to 2%
            t = (current_occupancy - 0.40) / 0.30
            rate = 0.05 - t * 0.03
        elif current_occupancy < 0.90:
            # Sharper taper from 2% down to 0.5%
            t = (current_occupancy - 0.70) / 0.20
            rate = 0.02 - t * 0.015
        else:
            rate = 0.002  # near-zero at very high density

        for x, y, entity in self.grid.cells():
            if entity is None and random.random() < rate:
                self.grid.set(x, y, Plant(x=x, y=y))

    def _update_stats(self):
        """Count current populations."""
        plants = herbivores = carnivores = 0
        for _, _, entity in self.grid.cells():
            if isinstance(entity, Plant):
                plants += 1
            elif isinstance(entity, Herbivore):
                herbivores += 1
            elif isinstance(entity, Carnivore):
                carnivores += 1
        self.stats = {
            "tick": self.tick_count,
            "plants": plants,
            "herbivores": herbivores,
            "carnivores": carnivores,
        }
