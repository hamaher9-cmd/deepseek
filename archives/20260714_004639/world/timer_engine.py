"""Pomodoro timer engine — tick-based state machine."""

from enum import Enum, auto
from dataclasses import dataclass


class Phase(Enum):
    IDLE = auto()
    WORKING = auto()
    ON_BREAK = auto()
    PAUSED = auto()
    DONE = auto()


@dataclass
class Tick:
    phase: Phase
    remaining: int       # seconds left in current phase
    phase_total: int     # total seconds for the current phase
    cycle: int           # 1-indexed, which work cycle we're on
    total_cycles: int


class PomodoroTimer:
    """Tick-based Pomodoro engine. Call tick() each second."""

    def __init__(self, work_minutes: int = 25, break_minutes: int = 5,
                 cycles: int = 4):
        if work_minutes < 1:
            raise ValueError("work_minutes must be >= 1")
        if break_minutes < 1:
            raise ValueError("break_minutes must be >= 1")
        if cycles < 1:
            raise ValueError("cycles must be >= 1")

        self._work_secs = work_minutes * 60
        self._break_secs = break_minutes * 60
        self._total_cycles = cycles

        self._phase = Phase.IDLE
        self._remaining = 0
        self._phase_total = 0
        self._cycle = 0
        self._pre_pause_phase: Phase | None = None

    # -- public properties ------------------------------------------------

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def remaining(self) -> int:
        return self._remaining

    @property
    def cycle(self) -> int:
        return self._cycle

    @property
    def total_cycles(self) -> int:
        return self._total_cycles

    @property
    def work_seconds(self) -> int:
        return self._work_secs

    @property
    def break_seconds(self) -> int:
        return self._break_secs

    # -- commands ----------------------------------------------------------

    def start(self) -> Tick:
        """Begin the first work session. Raises RuntimeError if already
        running or finished."""
        if self._phase not in (Phase.IDLE, Phase.DONE):
            raise RuntimeError(f"Cannot start: timer is {self._phase.name}")
        self._phase = Phase.WORKING
        self._remaining = self._work_secs
        self._phase_total = self._work_secs
        self._cycle = 1
        return self._make_tick()

    def tick(self) -> Tick:
        """Advance one second. Returns the new state."""
        if self._phase in (Phase.IDLE, Phase.PAUSED, Phase.DONE):
            raise RuntimeError(f"Cannot tick: timer is {self._phase.name}")

        self._remaining -= 1
        if self._remaining > 0:
            return self._make_tick()

        # current phase ended — transition
        return self._advance_phase()

    def pause(self) -> Tick:
        """Pause the timer. Only valid while WORKING or ON_BREAK."""
        if self._phase not in (Phase.WORKING, Phase.ON_BREAK):
            raise RuntimeError(f"Cannot pause: timer is {self._phase.name}")
        self._pre_pause_phase = self._phase
        self._phase = Phase.PAUSED
        return self._make_tick()

    def resume(self) -> Tick:
        """Resume from pause."""
        if self._phase != Phase.PAUSED:
            raise RuntimeError(f"Cannot resume: timer is {self._phase.name}")
        if self._pre_pause_phase is None:
            raise RuntimeError("Cannot resume: no pre-pause phase recorded")
        self._phase = self._pre_pause_phase
        self._pre_pause_phase = None
        return self._make_tick()

    def stop(self) -> Tick:
        """Stop the timer prematurely."""
        if self._phase in (Phase.IDLE, Phase.DONE):
            raise RuntimeError(f"Cannot stop: timer is {self._phase.name}")
        self._phase = Phase.DONE
        self._remaining = 0
        return self._make_tick()

    # -- internals ---------------------------------------------------------

    def _advance_phase(self) -> Tick:
        """Handle phase transition when a countdown reaches zero."""
        if self._phase == Phase.WORKING:
            if self._cycle >= self._total_cycles:
                self._phase = Phase.DONE
                self._remaining = 0
                self._phase_total = 0
            else:
                self._phase = Phase.ON_BREAK
                self._remaining = self._break_secs
                self._phase_total = self._break_secs
        elif self._phase == Phase.ON_BREAK:
            self._cycle += 1
            self._phase = Phase.WORKING
            self._remaining = self._work_secs
            self._phase_total = self._work_secs
        return self._make_tick()

    def _make_tick(self) -> Tick:
        return Tick(
            phase=self._phase,
            remaining=self._remaining,
            phase_total=self._phase_total,
            cycle=self._cycle,
            total_cycles=self._total_cycles,
        )
