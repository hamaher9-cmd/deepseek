#!/usr/bin/env python3
"""Pomodoro Timer CLI — live countdown with session logging."""

import argparse
import os
import sys
import time
import signal
from datetime import datetime, date

from timer_engine import PomodoroTimer, Phase
from session_log import load_sessions, save_session, get_today_sessions, get_stats

PID_FILE = ".pomo_pid"


def _fmt_time(seconds: int) -> str:
    """Format seconds as MM:SS."""
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"


def _phase_label(phase: Phase) -> str:
    labels = {
        Phase.IDLE: "IDLE",
        Phase.WORKING: "🍅 WORK",
        Phase.ON_BREAK: "☕ BREAK",
        Phase.PAUSED: "⏸  PAUSED",
        Phase.DONE: "✅ DONE",
    }
    return labels.get(phase, str(phase))


def _write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def _clear_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def _progress_bar(tick) -> str:
    """Draw a 20-char progress bar for the current phase."""
    if tick.phase in (Phase.IDLE, Phase.DONE, Phase.PAUSED):
        return ""
    if tick.phase_total == 0:
        return ""
    width = 20
    fraction = 1.0 - (tick.remaining / tick.phase_total)
    filled = round(fraction * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(fraction * 100)
    return f"[{bar}] {pct}%"


def cmd_start(args):
    """Run a live Pomodoro session."""
    timer = PomodoroTimer(
        work_minutes=args.work,
        break_minutes=args.break_time,
        cycles=args.cycles,
    )

    _write_pid()

    try:
        tick = timer.start()
        print(f"\n{_phase_label(tick.phase)}  Cycle {tick.cycle}/{tick.total_cycles}  "
              f"[{_fmt_time(tick.remaining)}]")
        print("─" * 36)

        while tick.phase != Phase.DONE:
            time.sleep(1)
            tick = timer.tick()

            bar = _progress_bar(tick)
            print(f"\r{_phase_label(tick.phase)}  Cycle {tick.cycle}/{tick.total_cycles}  "
                  f"[{_fmt_time(tick.remaining)}]  {bar}", end="", flush=True)

        print("\n" + "─" * 36)
        print("🎉 All cycles complete! Great work.")

        # Log completed session
        session = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "work_minutes": args.work,
            "break_minutes": args.break_time,
            "cycles": args.cycles,
            "status": "completed",
        }
        save_session(session)
        print("📝 Session logged.")

    except KeyboardInterrupt:
        print("\n\n⏹  Interrupted — stopping timer.")
        timer.stop()
        session = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "work_minutes": args.work,
            "break_minutes": args.break_time,
            "cycles": tick.cycle,
            "status": "stopped",
        }
        save_session(session)
        print("📝 Partial session logged.")

    finally:
        _clear_pid()


def cmd_log(args):
    """Show past sessions."""
    if args.stats:
        stats = get_stats()
        print(f"\n📊 Pomodoro Stats")
        print(f"   Total sessions:     {stats['total_sessions']}")
        print(f"   Total work minutes:  {stats['total_work_minutes']}")
        print(f"   Total break minutes: {stats['total_break_minutes']}")
        if stats['total_sessions'] > 0:
            avg = stats['total_work_minutes'] / stats['total_sessions']
            print(f"   Avg work / session:  {avg:.1f} min")
        return

    sessions = get_today_sessions() if args.today else load_sessions()
    if not sessions:
        print("No sessions logged yet.")
        return

    label = "Today's Sessions" if args.today else "All Sessions"
    print(f"\n📋 {label}")
    print("─" * 55)
    for i, s in enumerate(sessions, 1):
        ts = s.get("timestamp", "?")[:16]
        status = s.get("status", "?")
        wm = s.get("work_minutes", "?")
        bm = s.get("break_minutes", "?")
        cyc = s.get("cycles", "?")
        icon = "✅" if status == "completed" else "⏹"
        print(f"  {i}. {ts}  {icon} {status}  "
              f"work={wm}m break={bm}m cycles={cyc}")


def cmd_stop(args):
    """Stop a running Pomodoro session by sending SIGINT."""
    if not os.path.exists(PID_FILE):
        print("No running Pomodoro session found.")
        return

    with open(PID_FILE) as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGINT)
        print(f"Sent stop signal to Pomodoro session (PID {pid}).")
    except ProcessLookupError:
        print("Pomodoro session already ended. Cleaning up PID file.")
        _clear_pid()
    except PermissionError:
        print(f"Cannot stop session (PID {pid}) — permission denied.")


def main():
    parser = argparse.ArgumentParser(
        prog="pomo",
        description="Pomodoro Timer CLI 🍅",
    )
    sub = parser.add_subparsers(dest="command")

    # start
    p_start = sub.add_parser("start", help="Start a Pomodoro session")
    p_start.add_argument("--work", type=int, default=25, help="Work minutes (default: 25)")
    p_start.add_argument("--break-time", type=int, default=5, help="Break minutes (default: 5)")
    p_start.add_argument("--cycles", type=int, default=4, help="Number of work cycles (default: 4)")

    # log
    p_log = sub.add_parser("log", help="View session history")
    p_log.add_argument("--today", action="store_true", help="Show only today's sessions")
    p_log.add_argument("--stats", action="store_true", help="Show aggregate statistics")

    # stop
    sub.add_parser("stop", help="Stop a running Pomodoro session")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "log":
        cmd_log(args)
    elif args.command == "stop":
        cmd_stop(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
