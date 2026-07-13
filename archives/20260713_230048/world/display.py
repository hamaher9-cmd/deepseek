"""
DISPLAY — ASCII terminal renderer for the ecosystem grid.
Clears and redraws each tick. Supports color and stats bar.
"""

from __future__ import annotations
import os
import sys
import time
from grid import Grid
from entities import Plant, Herbivore, Carnivore

# ANSI escape codes
CLEAR = "\033[2J\033[H"
RESET = "\033[0m"
COLORS = {
    "P": "\033[92m",  # green
    "H": "\033[93m",  # yellow
    "C": "\033[91m",  # red
    ".": "\033[90m",  # dim gray for empty
}
BOLD = "\033[1m"


def render(grid: Grid, stats: dict | None = None, use_color: bool = True) -> str:
    """Build the full display string: grid + stats bar.
    Returns the string; caller decides whether to print or save."""
    lines = []

    # Top border
    lines.append("+" + "-" * grid.size + "+")

    # Grid rows
    for y in range(grid.size):
        row = "|"
        for x in range(grid.size):
            entity = grid.get(x, y)
            if entity is None:
                char = "."
                code = COLORS["."]
            elif isinstance(entity, Plant):
                char = "P"
                code = COLORS["P"]
            elif isinstance(entity, Herbivore):
                char = "H"
                code = COLORS["H"]
            elif isinstance(entity, Carnivore):
                char = "C"
                code = COLORS["C"]
            else:
                char = "?"
                code = ""

            if use_color:
                row += code + char + RESET
            else:
                row += char
        row += "|"
        lines.append(row)

    # Bottom border
    lines.append("+" + "-" * grid.size + "+")

    # Stats bar
    if stats:
        tick = stats.get("tick", 0)
        plants = stats.get("plants", 0)
        herbivores = stats.get("herbivores", 0)
        carnivores = stats.get("carnivores", 0)
        total = plants + herbivores + carnivores

        stat_line = f"{BOLD}Tick {tick:>5}{RESET} | "
        if use_color:
            stat_line += f"{COLORS['P']}P: {plants:>4}{RESET}  "
            stat_line += f"{COLORS['H']}H: {herbivores:>4}{RESET}  "
            stat_line += f"{COLORS['C']}C: {carnivores:>4}{RESET}  "
        else:
            stat_line += f"P: {plants:>4}  H: {herbivores:>4}  C: {carnivores:>4}  "
        stat_line += f"total: {total:>4}"
        lines.append(stat_line)

    return "\n".join(lines)


def clear_screen():
    """Clear the terminal."""
    sys.stdout.write(CLEAR)
    sys.stdout.flush()


def interactive_mode(
    engine, delay: float = 0.1, max_ticks: int = 500, use_color: bool = True
):
    """Run the simulation with auto-refresh display.
    Press Ctrl+C to stop, or it runs to max_ticks."""
    try:
        clear_screen()
        stats = engine.stats
        print(render(engine.grid, stats, use_color=use_color))
        print("\nPress Enter to step, type 'auto' for auto-run, Ctrl+C to quit.")

        auto = False
        while engine.tick_count < max_ticks:
            if not auto:
                cmd = input().strip().lower()
                if cmd == "auto":
                    auto = True
                elif cmd == "q" or cmd == "quit":
                    break
                # else: any key (including empty Enter) steps one tick

            stats = engine.tick()
            clear_screen()
            print(render(engine.grid, stats, use_color=use_color))

            if auto:
                time.sleep(delay)

                # Pause if everything dies
                if stats["plants"] == 0 and stats["herbivores"] == 0 and stats["carnivores"] == 0:
                    print("\n[All populations extinct. Simulation halted.]")
                    break

    except KeyboardInterrupt:
        pass
    finally:
        print(f"\nSimulation ended at tick {engine.tick_count}.")


def headless_run(engine, max_ticks: int = 500) -> list[dict]:
    """Run without display, returning all stats. For logging/batch runs."""
    history = []
    while engine.tick_count < max_ticks:
        stats = engine.tick()
        history.append(dict(stats))
        total = stats["plants"] + stats["herbivores"] + stats["carnivores"]
        if total == 0:
            break
    return history
