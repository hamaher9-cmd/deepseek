"""
PARAMS — All tunable knobs for the ecosystem simulation.
Import this from anywhere; tweak values here and everything responds.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WorldParams:
    """Grid and simulation-level settings."""
    grid_size: int = 50
    max_ticks: int = 500

    # Initial populations
    initial_plants: int = 100
    initial_herbivores: int = 30
    initial_carnivores: int = 6

    # Spontaneous plant growth (per empty cell, per tick)
    plant_spawn_rate: float = 0.05

    # Display
    tick_delay: float = 0.1  # seconds between ticks in auto mode


@dataclass
class PlantParams:
    """Plant-specific tuning."""
    energy: int = 10
    max_age: int = 100
    spread_chance: float = 0.02  # per tick, per plant


@dataclass
class HerbivoreParams:
    """Herbivore-specific tuning."""
    start_energy: int = 30
    max_energy: int = 60
    vision: int = 3
    metabolism: int = 1
    reproduce_threshold: int = 30
    reproduce_cost: int = 15


@dataclass
class CarnivoreParams:
    """Carnivore-specific tuning."""
    start_energy: int = 50
    max_energy: int = 100
    vision: int = 5
    metabolism: int = 2
    reproduce_threshold: int = 40
    reproduce_cost: int = 20
    kill_advantage: float = 1.2  # attacker must have E >= prey_E / this


# ---- Preset Scenarios ----
# Import these and pass to Engine.populate() / entity constructors.

SCENARIO_BALANCED = WorldParams(
    grid_size=50,
    max_ticks=500,
    initial_plants=100,
    initial_herbivores=30,
    initial_carnivores=6,
)

SCENARIO_RABBIT_PLAGUE = WorldParams(
    grid_size=40,
    max_ticks=500,
    initial_plants=200,
    initial_herbivores=80,
    initial_carnivores=2,
    plant_spawn_rate=0.08,
)

SCENARIO_LONE_WOLF = WorldParams(
    grid_size=30,
    max_ticks=500,
    initial_plants=50,
    initial_herbivores=20,
    initial_carnivores=1,
)

SCENARIO_GARDEN_OF_EDEN = WorldParams(
    grid_size=60,
    max_ticks=500,
    initial_plants=300,
    initial_herbivores=5,
    initial_carnivores=0,
    plant_spawn_rate=0.10,
)

SCENARIO_STRUGGLE = WorldParams(
    grid_size=30,
    max_ticks=300,
    initial_plants=10,
    initial_herbivores=10,
    initial_carnivores=5,
    plant_spawn_rate=0.02,
)

# Map of scenario names for easy lookup
SCENARIOS = {
    "balanced": SCENARIO_BALANCED,
    "rabbit_plague": SCENARIO_RABBIT_PLAGUE,
    "lone_wolf": SCENARIO_LONE_WOLF,
    "garden_of_eden": SCENARIO_GARDEN_OF_EDEN,
    "struggle": SCENARIO_STRUGGLE,
}
