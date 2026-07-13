"""
MICRO-ECOSYSTEM :: main.py
Entry point. All modules are live — drop a scenario name to run.
"""

import sys
from engine import Engine
from display import render, clear_screen, interactive_mode, headless_run
from params import SCENARIOS
from logger import Logger


def run(scenario_name: str = "balanced", mode: str = "headless"):
    """Run the ecosystem simulation.

    Args:
        scenario_name: key from params.SCENARIOS (default "balanced")
        mode: "headless" for CSV output, "interactive" for terminal display,
              "step" for manual tick-by-tick
    """
    scenario = SCENARIOS.get(scenario_name, SCENARIOS["balanced"])
    print(f"Scenario: {scenario_name}")
    print(f"Grid: {scenario.grid_size}x{scenario.grid_size}, "
          f"Ticks: {scenario.max_ticks}, "
          f"P0={scenario.initial_plants} "
          f"H0={scenario.initial_herbivores} "
          f"C0={scenario.initial_carnivores}")

    engine = Engine(size=scenario.grid_size)
    engine.populate(
        plants=scenario.initial_plants,
        herbivores=scenario.initial_herbivores,
        carnivores=scenario.initial_carnivores,
    )
    logger = Logger()

    if mode == "interactive":
        interactive_mode(engine, delay=scenario.tick_delay, max_ticks=scenario.max_ticks)

    elif mode == "headless":
        print("Running headless...")
        history = headless_run(engine, max_ticks=scenario.max_ticks)
        for stats in history:
            logger.record(stats)
        out_path = logger.save()
        print(f"Log saved to {out_path}")
        print(f"Final: {logger.last()}")
        ext = logger.extinction_tick()
        if ext:
            print(f"Animal extinction at tick {ext}")
        peak_tick, peak_count = logger.peak("plants")
        print(f"Peak plants: {peak_count} at tick {peak_tick}")

    else:
        print(f"Unknown mode: {mode}. Use 'headless' or 'interactive'.")


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "balanced"
    mode = sys.argv[2] if len(sys.argv) > 2 else "headless"
    run(scenario, mode)
