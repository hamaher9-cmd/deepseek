"""Unit tests for PomodoroTimer engine."""

from timer_engine import PomodoroTimer, Phase


def test_start_idle():
    t = PomodoroTimer(work_minutes=25, break_minutes=5, cycles=4)
    tick = t.start()
    assert tick.phase == Phase.WORKING
    assert tick.remaining == 25 * 60
    assert tick.cycle == 1
    assert tick.total_cycles == 4


def test_tick_decrements():
    t = PomodoroTimer(work_minutes=25, break_minutes=5, cycles=4)
    t.start()
    tick = t.tick()
    assert tick.remaining == 25 * 60 - 1
    assert tick.phase == Phase.WORKING


def test_full_work_then_break():
    """Tick through an entire work session — should transition to break."""
    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=2)
    t.start()
    # Tick 59 times (1 min = 60 sec, so after 59 ticks, 1 remains)
    for _ in range(59):
        tick = t.tick()
    assert tick.remaining == 1
    assert tick.phase == Phase.WORKING

    # The 60th tick hits zero and transitions to break
    tick = t.tick()
    assert tick.phase == Phase.ON_BREAK
    assert tick.remaining == 60  # 1 min break
    assert tick.cycle == 1       # still first cycle


def test_break_to_next_work():
    """Break ends → next work cycle starts."""
    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=2)
    t.start()
    # exhaust work
    for _ in range(60):
        t.tick()
    # exhaust break
    for _ in range(59):
        tick = t.tick()
    assert tick.remaining == 1
    assert tick.phase == Phase.ON_BREAK

    tick = t.tick()  # last break second
    assert tick.phase == Phase.WORKING
    assert tick.cycle == 2
    assert tick.remaining == 60


def test_done_after_last_cycle():
    """After final work session, phase becomes DONE."""
    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=1)
    t.start()
    for _ in range(60):
        tick = t.tick()
    assert tick.phase == Phase.DONE
    assert tick.remaining == 0


def test_pause_resume():
    t = PomodoroTimer(work_minutes=25, break_minutes=5, cycles=4)
    t.start()
    t.tick()  # 1499 remaining
    t.tick()  # 1498 remaining
    tick = t.pause()
    assert tick.phase == Phase.PAUSED
    assert tick.remaining == 25 * 60 - 2

    # resume and verify we pick up where we left off
    tick = t.resume()
    assert tick.phase == Phase.WORKING
    assert tick.remaining == 25 * 60 - 2

    # ticking continues normally
    tick = t.tick()
    assert tick.remaining == 25 * 60 - 3


def test_pause_while_on_break():
    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=2)
    t.start()
    for _ in range(60):
        t.tick()  # now on break
    for _ in range(10):
        t.tick()  # 50 remaining on break
    tick = t.pause()
    assert tick.phase == Phase.PAUSED
    tick = t.resume()
    assert tick.phase == Phase.ON_BREAK
    assert tick.remaining == 50


def test_stop():
    t = PomodoroTimer(work_minutes=25, break_minutes=5, cycles=4)
    t.start()
    t.tick()
    tick = t.stop()
    assert tick.phase == Phase.DONE
    assert tick.remaining == 0


def test_cannot_start_twice():
    t = PomodoroTimer()
    t.start()
    try:
        t.start()
        assert False, "should have raised"
    except RuntimeError:
        pass


def test_cannot_tick_when_idle():
    t = PomodoroTimer()
    try:
        t.tick()
        assert False, "should have raised"
    except RuntimeError:
        pass


def test_cannot_tick_when_paused():
    t = PomodoroTimer()
    t.start()
    t.pause()
    try:
        t.tick()
        assert False, "should have raised"
    except RuntimeError:
        pass


def test_cannot_tick_when_done():
    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=1)
    t.start()
    for _ in range(60):
        t.tick()
    try:
        t.tick()
        assert False, "should have raised"
    except RuntimeError:
        pass


def test_cannot_pause_when_idle():
    t = PomodoroTimer()
    try:
        t.pause()
        assert False, "should have raised"
    except RuntimeError:
        pass


def test_cannot_resume_when_not_paused():
    t = PomodoroTimer()
    t.start()
    try:
        t.resume()
        assert False, "should have raised"
    except RuntimeError:
        pass


def test_cannot_stop_when_idle():
    t = PomodoroTimer()
    try:
        t.stop()
        assert False, "should have raised"
    except RuntimeError:
        pass


def test_validation():
    try:
        PomodoroTimer(work_minutes=0)
        assert False
    except ValueError:
        pass
    try:
        PomodoroTimer(break_minutes=0)
        assert False
    except ValueError:
        pass
    try:
        PomodoroTimer(cycles=0)
        assert False
    except ValueError:
        pass


def test_custom_durations():
    t = PomodoroTimer(work_minutes=10, break_minutes=3, cycles=3)
    assert t.work_seconds == 600
    assert t.break_seconds == 180
    assert t.total_cycles == 3
    t.start()
    assert t.remaining == 600


def test_multi_cycle_full_run():
    """3 cycles: work→break→work→break→work→DONE."""
    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=3)
    t.start()
    # cycle 1 work
    for _ in range(60):
        t.tick()
    assert t.phase == Phase.ON_BREAK
    # cycle 1 break
    for _ in range(60):
        t.tick()
    assert t.phase == Phase.WORKING
    assert t.cycle == 2
    # cycle 2 work
    for _ in range(60):
        t.tick()
    assert t.phase == Phase.ON_BREAK
    # cycle 2 break
    for _ in range(60):
        t.tick()
    assert t.phase == Phase.WORKING
    assert t.cycle == 3
    # cycle 3 work (last)
    for _ in range(60):
        t.tick()
    assert t.phase == Phase.DONE


if __name__ == "__main__":
    tests = [
        test_start_idle, test_tick_decrements, test_full_work_then_break,
        test_break_to_next_work, test_done_after_last_cycle,
        test_pause_resume, test_pause_while_on_break, test_stop,
        test_cannot_start_twice, test_cannot_tick_when_idle,
        test_cannot_tick_when_paused, test_cannot_tick_when_done,
        test_cannot_pause_when_idle, test_cannot_resume_when_not_paused,
        test_cannot_stop_when_idle, test_validation, test_custom_durations,
        test_multi_cycle_full_run,
    ]
    for test in tests:
        test()
        print(f"✅ {test.__name__}")
    print(f"\nAll {len(tests)} tests passed!")
