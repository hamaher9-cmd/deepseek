"""Habit engine: CRUD, check-in, streak calculation, stats.

All functions are pure: they take a list of habit dicts plus arguments
and return (habits, result). Never touches the filesystem directly.
"""

from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find(habits, name):
    """Return index of habit with given name, or raise ValueError."""
    for i, h in enumerate(habits):
        if h["name"] == name:
            return i
    raise ValueError(f"Habit '{name}' not found.")


def _parse_date(s):
    """Return a date object from 'YYYY-MM-DD' or None for today."""
    if s is None:
        return date.today()
    return date.fromisoformat(s)


def _week_key(d):
    """Return (year, week_number) for a date — ISO calendar."""
    iso = d.isocalendar()
    return (iso[0], iso[1])


def _weeks_in_year(year):
    """Return number of ISO weeks in a year."""
    last_day = date(year, 12, 28)
    return last_day.isocalendar()[1]


def _prev_week(wk):
    """Return the ISO week before (year, week_number)."""
    y, w = wk
    if w == 1:
        return (y - 1, _weeks_in_year(y - 1))
    return (y, w - 1)


def _weeks_apart(w_newer, w_older):
    """Number of weeks between two (year, week) tuples (w_newer is the
    later week).  Returns the positive difference if they are exactly
    that many weeks apart, otherwise 999 (sentinel for non-consecutive)."""
    y1, wk1 = w_newer
    y2, wk2 = w_older
    if y1 == y2:
        return wk1 - wk2
    if y1 == y2 + 1:
        return (wk1 + _weeks_in_year(y2)) - wk2
    return 999  # gap too big


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def add_habit(habits, name, frequency="daily"):
    """Add a new habit.  Returns (habits, new_habit).

    Raises ValueError if a habit with the same name already exists, or
    if frequency is not 'daily' or 'weekly'.
    """
    if frequency not in ("daily", "weekly"):
        raise ValueError("Frequency must be 'daily' or 'weekly'.")

    # duplicate check
    for h in habits:
        if h["name"] == name:
            raise ValueError(f"Habit '{name}' already exists.")

    new_habit = {
        "name": name,
        "frequency": frequency,
        "created_at": str(date.today()),
        "checkins": [],
    }
    habits.append(new_habit)
    return habits, new_habit


def checkin(habits, name, date_str=None):
    """Mark a habit as done for *date_str* (default: today).

    Returns (habits, result) where
    result = {"habit": ..., "date": ..., "already": bool}.

    Raises ValueError if habit not found.
    """
    idx = _find(habits, name)
    d = _parse_date(date_str)
    ds = str(d)

    checkins = habits[idx]["checkins"]
    if ds in checkins:
        return habits, {"habit": habits[idx], "date": ds, "already": True}

    # insert keeping sorted order
    checkins.append(ds)
    checkins.sort()
    return habits, {"habit": habits[idx], "date": ds, "already": False}


def list_habits(habits, with_streaks=False, today_str=None):
    """Return a list of habit summary dicts.

    If *with_streaks* is True, each summary includes current and best streak.
    """
    today = _parse_date(today_str)
    result = []
    for h in habits:
        summary = {
            "name": h["name"],
            "frequency": h["frequency"],
            "total_checkins": len(h["checkins"]),
        }
        if with_streaks:
            summary.update(calc_streak(h["checkins"], h["frequency"], today))
        result.append(summary)
    return result


def get_stats(habits, name, today_str=None):
    """Return detailed stats for one habit.

    Result keys: name, frequency, created_at, total_checkins,
    current_streak, best_streak, checkins (the raw list).
    """
    idx = _find(habits, name)
    h = habits[idx]
    today = _parse_date(today_str)
    streaks = calc_streak(h["checkins"], h["frequency"], today)
    return {
        "name": h["name"],
        "frequency": h["frequency"],
        "created_at": h["created_at"],
        "total_checkins": len(h["checkins"]),
        "current_streak": streaks["current"],
        "best_streak": streaks["best"],
        "checkins": h["checkins"][:],  # shallow copy
    }


def delete_habit(habits, name):
    """Remove a habit by name.  Returns (habits, deleted_habit).

    Raises ValueError if not found.
    """
    idx = _find(habits, name)
    removed = habits.pop(idx)
    return habits, removed


def calc_streak(checkins, frequency, today=None):
    """Calculate current and best streak from a list of date strings.

    *today* should be a datetime.date or None (uses actual today).

    Returns {"current": int, "best": int}.

    - *daily*:  consecutive calendar days.
    - *weekly*: consecutive ISO weeks (multiple checkins in the
                same week count as one).
    """
    if today is None:
        today = date.today()

    if not checkins:
        return {"current": 0, "best": 0}

    if frequency == "daily":
        return _streak_daily(checkins, today)
    else:
        return _streak_weekly(checkins, today)


# ---------------------------------------------------------------------------
# Streak internals
# ---------------------------------------------------------------------------

def _streak_daily(checkins, today):
    """Compute daily current & best streak."""
    checkin_set = set(checkins)

    # Current streak: count backwards from today
    current = 0
    d = today
    while str(d) in checkin_set:
        current += 1
        d = d - timedelta(days=1)

    # Best streak: longest consecutive run ever
    dates = sorted(date.fromisoformat(c) for c in checkins)
    best = 0
    run = 0
    for i, dt in enumerate(dates):
        if i == 0:
            run = 1
        else:
            if (dt - dates[i - 1]).days == 1:
                run += 1
            else:
                run = 1
        best = max(best, run)

    return {"current": current, "best": best}


def _streak_weekly(checkins, today):
    """Compute weekly current & best streak.

    Multiple checkins in the same ISO week count as a single checkin
    for that week.
    """
    # Unique weeks present in checkins
    week_set = set()
    for c in checkins:
        week_set.add(_week_key(date.fromisoformat(c)))
    weeks = sorted(week_set)

    # Current streak: count backwards from this week
    this_week = _week_key(today)
    current = 0
    w = this_week
    while w in week_set:
        current += 1
        w = _prev_week(w)

    # Best streak: longest consecutive run of weeks
    best = 0
    run = 0
    for i, wk in enumerate(weeks):
        if i == 0:
            run = 1
        else:
            if _weeks_apart(wk, weeks[i - 1]) == 1:
                run += 1
            else:
                run = 1
        best = max(best, run)

    return {"current": current, "best": best}
