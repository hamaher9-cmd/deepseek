"""Unit tests for habit_engine.py — plain asserts, run directly."""
from datetime import date
from habit_engine import (
    add_habit,
    checkin,
    list_habits,
    get_stats,
    delete_habit,
    calc_streak,
)

# -----------------------------------------------------------------------
# add_habit
# -----------------------------------------------------------------------

def test_add_habit_creates_daily():
    habits = []
    habits, h = add_habit(habits, "Read", "daily")
    assert h["name"] == "Read"
    assert h["frequency"] == "daily"
    assert h["checkins"] == []
    assert h["created_at"] == str(date.today())


def test_add_habit_creates_weekly():
    habits = []
    habits, h = add_habit(habits, "Gym", "weekly")
    assert h["frequency"] == "weekly"


def test_add_habit_defaults_to_daily():
    habits = []
    habits, h = add_habit(habits, "Meditate")
    assert h["frequency"] == "daily"


def test_add_habit_rejects_duplicate():
    habits = []
    add_habit(habits, "Run")
    try:
        add_habit(habits, "Run")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "already exists" in str(e)


def test_add_habit_rejects_bad_frequency():
    habits = []
    try:
        add_habit(habits, "Run", "monthly")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "daily" in str(e) or "weekly" in str(e)


# -----------------------------------------------------------------------
# checkin
# -----------------------------------------------------------------------

def test_checkin_adds_date():
    habits = []
    add_habit(habits, "Run")
    habits, res = checkin(habits, "Run", "2025-07-14")
    assert res["date"] == "2025-07-14"
    assert res["already"] is False
    assert "2025-07-14" in habits[0]["checkins"]


def test_checkin_defaults_to_today():
    habits = []
    add_habit(habits, "Run")
    habits, res = checkin(habits, "Run")
    assert res["date"] == str(date.today())


def test_checkin_already_checked_in():
    habits = []
    add_habit(habits, "Run")
    checkin(habits, "Run", "2025-07-14")
    habits, res = checkin(habits, "Run", "2025-07-14")
    assert res["already"] is True


def test_checkin_keeps_sorted_order():
    habits = []
    add_habit(habits, "Run")
    checkin(habits, "Run", "2025-07-16")
    checkin(habits, "Run", "2025-07-14")
    checkin(habits, "Run", "2025-07-15")
    assert habits[0]["checkins"] == ["2025-07-14", "2025-07-15", "2025-07-16"]


def test_checkin_habit_not_found():
    habits = []
    try:
        checkin(habits, "Ghost")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)


# -----------------------------------------------------------------------
# list_habits
# -----------------------------------------------------------------------

def test_list_habits_empty():
    assert list_habits([]) == []


def test_list_habits_basic():
    habits = []
    add_habit(habits, "Run", "daily")
    add_habit(habits, "Gym", "weekly")
    checkin(habits, "Run", "2025-07-14")
    result = list_habits(habits)
    assert len(result) == 2
    assert result[0]["name"] == "Run"
    assert result[0]["total_checkins"] == 1
    assert "current" not in result[0]


def test_list_habits_with_streaks():
    habits = []
    add_habit(habits, "Run", "daily")
    checkin(habits, "Run", "2025-07-14")
    checkin(habits, "Run", "2025-07-15")
    result = list_habits(habits, with_streaks=True, today_str="2025-07-15")
    assert result[0]["current"] == 2
    assert result[0]["best"] == 2


# -----------------------------------------------------------------------
# get_stats
# -----------------------------------------------------------------------

def test_get_stats_full():
    habits = []
    add_habit(habits, "Run", "daily")
    checkin(habits, "Run", "2025-07-14")
    checkin(habits, "Run", "2025-07-15")
    s = get_stats(habits, "Run", today_str="2025-07-15")
    assert s["name"] == "Run"
    assert s["frequency"] == "daily"
    assert s["total_checkins"] == 2
    assert s["current_streak"] == 2
    assert s["best_streak"] == 2
    assert s["checkins"] == ["2025-07-14", "2025-07-15"]


def test_get_stats_not_found():
    try:
        get_stats([], "Nope")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)


# -----------------------------------------------------------------------
# delete_habit
# -----------------------------------------------------------------------

def test_delete_habit():
    habits = []
    add_habit(habits, "Run")
    add_habit(habits, "Gym")
    habits, removed = delete_habit(habits, "Run")
    assert removed["name"] == "Run"
    assert len(habits) == 1
    assert habits[0]["name"] == "Gym"


def test_delete_habit_not_found():
    try:
        delete_habit([], "Ghost")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)


# -----------------------------------------------------------------------
# calc_streak — daily
# -----------------------------------------------------------------------

def test_streak_daily_no_checkins():
    s = calc_streak([], "daily")
    assert s["current"] == 0
    assert s["best"] == 0


def test_streak_daily_current_from_today():
    s = calc_streak(
        ["2025-07-14", "2025-07-15", "2025-07-16"],
        "daily",
        today=date(2025, 7, 16),
    )
    assert s["current"] == 3
    assert s["best"] == 3


def test_streak_daily_current_zero_when_today_missing():
    s = calc_streak(
        ["2025-07-14", "2025-07-15"],
        "daily",
        today=date(2025, 7, 17),
    )
    assert s["current"] == 0


def test_streak_daily_best_larger_than_current():
    # current = 1 (only today), but best = 5 from an earlier run
    checkins = [
        "2025-07-10", "2025-07-11", "2025-07-12", "2025-07-13", "2025-07-14",
        "2025-07-20",
    ]
    s = calc_streak(checkins, "daily", today=date(2025, 7, 20))
    assert s["current"] == 1
    assert s["best"] == 5


def test_streak_daily_single_checkin():
    s = calc_streak(["2025-07-14"], "daily", today=date(2025, 7, 14))
    assert s["current"] == 1
    assert s["best"] == 1


def test_streak_daily_non_consecutive():
    s = calc_streak(
        ["2025-07-14", "2025-07-16", "2025-07-18"],
        "daily",
        today=date(2025, 7, 18),
    )
    assert s["current"] == 1
    assert s["best"] == 1


# -----------------------------------------------------------------------
# calc_streak — weekly
# -----------------------------------------------------------------------

def test_streak_weekly_no_checkins():
    s = calc_streak([], "weekly")
    assert s["current"] == 0
    assert s["best"] == 0


def test_streak_weekly_current_from_this_week():
    # 2025-07-14 (Mon) = ISO week 29
    s = calc_streak(
        ["2025-07-14"],
        "weekly",
        today=date(2025, 7, 16),  # also week 29
    )
    assert s["current"] == 1
    assert s["best"] == 1


def test_streak_weekly_current_zero_when_this_week_missing():
    s = calc_streak(
        ["2025-07-07"],  # week 28
        "weekly",
        today=date(2025, 7, 14),  # week 29
    )
    assert s["current"] == 0


def test_streak_weekly_multiple_checkins_same_week_count_as_one():
    # All in week 29, current should be 1 not 3
    s = calc_streak(
        ["2025-07-14", "2025-07-15", "2025-07-16"],
        "weekly",
        today=date(2025, 7, 16),
    )
    assert s["current"] == 1
    assert s["best"] == 1


def test_streak_weekly_best_larger_than_current():
    # weeks 27 (one checkin), then gap, then today in week 29
    checkins = ["2025-06-30", "2025-07-01", "2025-07-02"]  # all week 27
    s = calc_streak(checkins, "weekly", today=date(2025, 7, 14))  # week 29
    assert s["current"] == 0
    assert s["best"] == 1


def test_streak_weekly_consecutive_weeks():
    # week 27 + week 28
    checkins = [
        "2025-06-30",             # week 27 (Mon)
        "2025-07-07",             # week 28 (Mon)
    ]
    s = calc_streak(checkins, "weekly", today=date(2025, 7, 7))
    assert s["current"] == 2
    assert s["best"] == 2


def test_streak_weekly_across_year_boundary():
    # 2024-12-30 (Mon) = week 1 of 2025 (ISO!)
    # Actually let's use a cleaner example
    # 2024-12-30 is ISO 2025-W01, and 2025-01-06 is ISO 2025-W02
    checkins = [
        "2024-12-30",  # ISO 2025-W01
        "2025-01-06",  # ISO 2025-W02
    ]
    s = calc_streak(checkins, "weekly", today=date(2025, 1, 6))
    assert s["current"] == 2
    assert s["best"] == 2


# -----------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        # add_habit
        ("add_habit creates daily", test_add_habit_creates_daily),
        ("add_habit creates weekly", test_add_habit_creates_weekly),
        ("add_habit defaults to daily", test_add_habit_defaults_to_daily),
        ("add_habit rejects duplicate", test_add_habit_rejects_duplicate),
        ("add_habit rejects bad frequency", test_add_habit_rejects_bad_frequency),
        # checkin
        ("checkin adds date", test_checkin_adds_date),
        ("checkin defaults to today", test_checkin_defaults_to_today),
        ("checkin already checked in", test_checkin_already_checked_in),
        ("checkin keeps sorted order", test_checkin_keeps_sorted_order),
        ("checkin habit not found", test_checkin_habit_not_found),
        # list_habits
        ("list_habits empty", test_list_habits_empty),
        ("list_habits basic", test_list_habits_basic),
        ("list_habits with streaks", test_list_habits_with_streaks),
        # get_stats
        ("get_stats full", test_get_stats_full),
        ("get_stats not found", test_get_stats_not_found),
        # delete_habit
        ("delete_habit", test_delete_habit),
        ("delete_habit not found", test_delete_habit_not_found),
        # calc_streak daily
        ("streak daily no checkins", test_streak_daily_no_checkins),
        ("streak daily current from today", test_streak_daily_current_from_today),
        ("streak daily current zero when today missing", test_streak_daily_current_zero_when_today_missing),
        ("streak daily best larger than current", test_streak_daily_best_larger_than_current),
        ("streak daily single checkin", test_streak_daily_single_checkin),
        ("streak daily non-consecutive", test_streak_daily_non_consecutive),
        # calc_streak weekly
        ("streak weekly no checkins", test_streak_weekly_no_checkins),
        ("streak weekly current from this week", test_streak_weekly_current_from_this_week),
        ("streak weekly current zero when this week missing", test_streak_weekly_current_zero_when_this_week_missing),
        ("streak weekly multiple checkins same week count as one", test_streak_weekly_multiple_checkins_same_week_count_as_one),
        ("streak weekly best larger than current", test_streak_weekly_best_larger_than_current),
        ("streak weekly consecutive weeks", test_streak_weekly_consecutive_weeks),
        ("streak weekly across year boundary", test_streak_weekly_across_year_boundary),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed, {len(tests)} total")
