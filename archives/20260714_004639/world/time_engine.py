"""Time engine: block CRUD, day/week views, conflict detection.

All functions are pure: they take a list of block dicts plus arguments
and return (blocks, result). Never touches the filesystem directly.

Block dict format:
    {
        "id": 1,
        "day": "mon",
        "start": "09:00",
        "duration": 60,
        "label": "Deep Work",
        "task_id": null
    }

Days: mon, tue, wed, thu, fri, sat, sun
"""

import re

VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}

# Strict HH:MM — exactly "##:##" with leading zeros
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_id(blocks):
    """Return the next available block id (max + 1, or 1 if empty)."""
    if not blocks:
        return 1
    return max(b["id"] for b in blocks) + 1


def _to_minutes(time_str):
    """Convert 'HH:MM' to minutes since midnight."""
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


def _to_time_str(total_minutes):
    """Convert minutes since midnight back to 'HH:MM' string."""
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"


def _end_time(start, duration):
    """Return end time as 'HH:MM' given start and duration in minutes."""
    return _to_time_str(_to_minutes(start) + duration)


def _overlap(start_a, dur_a, start_b, dur_b):
    """Return True if block A and block B overlap in time."""
    a_start = _to_minutes(start_a)
    a_end = a_start + dur_a
    b_start = _to_minutes(start_b)
    b_end = b_start + dur_b
    return a_start < b_end and b_start < a_end


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def add_block(blocks, day, start, duration, label, task_id=None):
    """Add a new time block. Auto-assigns the next sequential ID.

    Returns (blocks, block_dict).

    Raises ValueError if *day* is not a valid day (mon-sun),
    if *start* is not strict 'HH:MM' format (e.g. '09:00'),
    or if *duration* is not a positive integer.
    """
    if day not in VALID_DAYS:
        raise ValueError(f"Invalid day '{day}'. Must be one of: {', '.join(sorted(VALID_DAYS))}.")

    # Validate start — must be exactly HH:MM with leading zeros
    if not isinstance(start, str) or not _TIME_RE.match(start):
        raise ValueError(f"Invalid start time '{start}'. Must be HH:MM format (00:00-23:59).")

    if not isinstance(duration, int) or duration <= 0:
        raise ValueError(f"Duration must be a positive integer, got {duration!r}.")

    block = {
        "id": _next_id(blocks),
        "day": day,
        "start": start,
        "duration": duration,
        "label": label,
        "task_id": task_id,
    }
    blocks.append(block)
    return blocks, block


def delete_block(blocks, block_id):
    """Remove a block by id. Idempotent — no error if not found.

    Returns (blocks, deleted_block_or_None).
    """
    for i, b in enumerate(blocks):
        if b["id"] == block_id:
            removed = blocks.pop(i)
            return blocks, removed
    return blocks, None


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def list_day(blocks, day):
    """Return blocks for *day* sorted by start time.

    Raises ValueError if *day* is not valid.
    """
    if day not in VALID_DAYS:
        raise ValueError(f"Invalid day '{day}'. Must be one of: {', '.join(sorted(VALID_DAYS))}.")

    result = [b for b in blocks if b["day"] == day]
    result.sort(key=lambda b: _to_minutes(b["start"]))
    return result


def list_week(blocks):
    """Return dict mapping each day to its sorted list of blocks.

    All seven days are always present as keys, even if empty.
    """
    result = {day: [] for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]}
    for b in blocks:
        if b["day"] in result:
            result[b["day"]].append(b)
    for day in result:
        result[day].sort(key=lambda b: _to_minutes(b["start"]))
    return result


# ---------------------------------------------------------------------------
# Conflicts
# ---------------------------------------------------------------------------

def find_conflicts(blocks, day, start, duration):
    """Return list of blocks on *day* that overlap with the proposed block.

    The proposed block runs from *start* for *duration* minutes.
    Blocks are returned in start-time order.

    Raises ValueError if *day* is not valid.
    """
    if day not in VALID_DAYS:
        raise ValueError(f"Invalid day '{day}'. Must be one of: {', '.join(sorted(VALID_DAYS))}.")

    day_blocks = [b for b in blocks if b["day"] == day]
    conflicts = [b for b in day_blocks if _overlap(start, duration, b["start"], b["duration"])]
    conflicts.sort(key=lambda b: _to_minutes(b["start"]))
    return conflicts
