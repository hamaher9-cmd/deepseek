"""
LOGGER — CSV output of population per tick.
Drop-in for any engine run; call record() each tick and save() at the end.
"""

import csv
from pathlib import Path
from typing import Optional


class Logger:
    """Records population counts per tick and writes CSV."""

    def __init__(self, path: str = "population_log.csv"):
        self.path = Path(path)
        self.rows: list[dict] = []
        self._fields = ["tick", "plants", "herbivores", "carnivores", "total"]

    def record(self, stats: dict) -> None:
        """Store one tick's stats. stats dict should have: tick, plants, herbivores, carnivores."""
        row = {
            "tick": stats.get("tick", 0),
            "plants": stats.get("plants", 0),
            "herbivores": stats.get("herbivores", 0),
            "carnivores": stats.get("carnivores", 0),
            "total": (
                stats.get("plants", 0)
                + stats.get("herbivores", 0)
                + stats.get("carnivores", 0)
            ),
        }
        self.rows.append(row)

    def save(self, path: Optional[str] = None) -> Path:
        """Write all recorded rows to CSV. Returns the path written."""
        out = Path(path) if path else self.path
        with open(out, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self._fields)
            writer.writeheader()
            writer.writerows(self.rows)
        return out

    def last(self) -> dict:
        """Return the most recent row, or empty dict."""
        return self.rows[-1] if self.rows else {}

    def extinction_tick(self) -> Optional[int]:
        """Return the first tick where both herbivores and carnivores hit zero, or None."""
        for row in self.rows:
            if row["herbivores"] == 0 and row["carnivores"] == 0:
                return row["tick"]
        return None

    def peak(self, column: str = "plants") -> tuple[int, int]:
        """Return (tick, count) of maximum value for given column."""
        if not self.rows:
            return (0, 0)
        best = max(self.rows, key=lambda r: r[column])
        return (best["tick"], best[column])
