"""
MICRO-ECOSYSTEM :: Design Sketch
Bex's brain-dump. Tear it apart, improve it, build it.

CONCEPT:
A tiny 2D grid-world where plants grow, herbivores graze, and carnivores hunt.
Each tick, every entity acts. Energy flows, populations rise and crash.
Emergent behavior is the goal — nobody scripts the drama.

---- GRID ----
- NxN toroidal grid (wrap-around edges, like a little planet)
- Each cell can hold: empty, plant, or one creature at a time
- Tick-based: each tick = one full pass over all entities

---- ENTITIES ----

PLANT [P]
- Grows on empty cells with some probability per tick (e.g. 5%)
- Has an energy value when eaten (e.g. 10)
- Spreads to adjacent empty cells (low probability, like 2%)
- Dies of old age or overcrowding

HERBIVORE [H]  
- Moves to adjacent cell with most plant food (or random if none)
- Eats plant if on same cell, gains its energy
- Loses 1 energy per tick (metabolism)
- Reproduces if energy > threshold (spawns offspring on adjacent empty cell)
- Dies if energy <= 0
- Simple "vision" radius: can sense food in N adjacent cells

CARNIVORE [C]
- Moves toward nearest herbivore within vision radius
- Attacks if adjacent; kill chance based on relative energy
- Gains energy from kill
- Loses 2 energy per tick (higher metabolism)
- Same reproduce/die logic as herbivores
- Hunts herbivores preferentially; may scavenge if starving

---- PARAMETERS (tunable!) ----
GRID_SIZE = 50
INITIAL_PLANTS = 100
INITIAL_HERBIVORES = 30
INITIAL_CARNIVORES = 6
PLANT_ENERGY = 10
HERBIVORE_METABOLISM = 1
CARNIVORE_METABOLISM = 2
REPRODUCE_THRESHOLD = 30
REPRODUCE_COST = 15  # energy given to offspring

---- DISPLAY ----
- ASCII grid in terminal, cleared each tick
- P = plant, H = herbivore, C = carnivore, . = empty
- Or use pygame/curses if we're feeling fancy

---- STRETCH GOALS ----
- Mutation: offspring have slightly different parameters
- Seasons: plant growth rate varies cyclically
- Scavengers: a third creature type that eats corpses
- Data logging: population graphs over time
- Genetic lineage tracking

---- QUESTIONS FOR ASH & CYR ----
- Turn-based or real-time display?
- How complex is too complex for a first pass?
- Should entities be objects or should we go data-oriented (arrays/dicts)?
- Do we want a web view (Flask/sockets) or keep it terminal-first?

-- Bex (the one with the sketches)
"""

# Just a tiny seed to prove the concept — not runnable yet,
# but here's what a plant might look like:

from dataclasses import dataclass
from random import random

@dataclass
class Plant:
    energy: int = 10
    age: int = 0
    max_age: int = 100

    def tick(self) -> bool:
        """Return True if still alive."""
        self.age += 1
        return self.age < self.max_age

# Cyr: I bet you'd make this beautiful. Ash: I bet you'd make it fast.
# Let's build something alive.
