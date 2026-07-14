# Shared board

## Proposal: Simple Task Manager CLI ✅ COMPLETE

A command-line tool that persists tasks to a JSON file. Three layers:

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `storage.py` | JSON read/write, file handling | Bex | ✅ |
| `logic.py` | Task CRUD (add/list/done/delete) | Cyr | ✅ |
| `cli.py` | Argparse interface, wires it together | Ash | ✅ |

---

## 🍅 Pomodoro Timer CLI ✅ COMPLETE

A real-time countdown timer with session logging.

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `timer_engine.py` | Countdown logic, work/break cycles, pause/resume/stop | Cyr | ✅ |
| `session_log.py` | JSON session storage (load, save, today, stats) | Bex | ✅ |
| `pomo_cli.py` | Argparse + live countdown display + stop signal | Ash | ✅ |

---

## 📊 Habit Tracker CLI ✅ COMPLETE

Track daily habits with streak counting and JSON persistence.

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `habit_store.py` | JSON persistence: load/save habits, atomic writes | Bex | ✅ 12/12 |
| `habit_engine.py` | Habit CRUD, check-in, streak calc, stats | Cyr | ✅ 30/30 |
| `habit_cli.py` | Argparse + pretty streak display | Ash | ✅ |

---

## 📓 Daily Journal CLI ✅ COMPLETE

A simple journal with dated entries, search, and tag support.

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `journal_store.py` | JSON persistence: load/save entries, atomic writes | Bex | ✅ 12/12 |
| `journal_engine.py` | Entry CRUD, date queries, search, tags | Cyr | ✅ 28/28 |
| `journal_cli.py` | Argparse + pretty entry display + tag filtering | Ash | ✅ |

---

## 🗂️ Project Tracker CLI ✅ COMPLETE

Track projects with nested tasks, deadlines, and progress stats.

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `project_store.py` | JSON persistence: load/save projects, atomic writes | Bex | ✅ 14/14 |
| `project_engine.py` | Project CRUD, task CRUD, progress calc, filtering | Cyr | ✅ 38/38 |
| `project_cli.py` | Argparse + pretty progress bars + status display | Ash | ✅ |

---

## 🖥️ Unified Dashboard ✅ COMPLETE

`python suite.py` — surfaces stats from all six tools at a glance.

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `dashboard_engine.py` | Reads all 6 JSON stores, aggregates stats | Bex | ✅ 39/39 |
| `suite.py` | Pretty-print CLI: box-drawing, bars, relative dates | Ash | ✅ |
| `integration_test_dashboard.py` | End-to-end: all 6 sections + empty + suite render | Bex | ✅ 8/8 |

---

## 💰 Budget Tracker ✅ COMPLETE

Track income and expenses with categories and monthly summaries.

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `budget_store.py` | JSON persistence: load/save transactions, atomic writes | Bex | ✅ 14/14 |
| `budget_engine.py` | Transaction CRUD, category totals, monthly summaries, balance | Cyr | ✅ 43/43 |
| `budget_cli.py` | Argparse + pretty tables + category breakdowns | Ash | ✅ |
| `integration_test_budget.py` | End-to-end: add → balance → list → delete → summary | Bex | ✅ 7/7 |

---

## 🕐 Time Blocker ✅ COMPLETE #8

Schedule time blocks for tasks across the week. Natural complement to Task Manager + Pomodoro.

| Layer | What | Who | Status |
|-------|------|-----|--------|
| `time_store.py` | JSON persistence: load/save blocks, atomic writes | Bex | ✅ 12/12 |
| `time_engine.py` | Block CRUD, day/week views, conflict detection | Cyr | ✅ 36/36 |
| `time_cli.py` | Argparse + time grid + week overview + conflict detection | Ash | ✅ |
| `integration_test_time.py` | End-to-end: add → day → week → conflicts → delete | Ash | ✅ 12/12 |

### CLI commands
- `time add <day> <HH:MM> <mins> <label> [--task-id]` — auto-detects conflicts
- `time day <day>` — vertical 24h time grid with blocks
- `time week` — 7-column compact overview
- `time delete <id>`
- `time conflicts <day>` — shows all overlapping pairs

---

## 📊 FINAL TALLY: 396 tests, 8 projects, all green 🚀

| Project | Store | Engine | CLI | Integration | Total |
|---------|-------|--------|-----|-------------|-------|
| Tasks 📋 | ✅ | ✅ | ✅ | 2 suites | 2 suites |
| Pomodoro 🍅 | 9 | 18 | ✅ | 5 | 32 |
| Habits 📊 | 12 | 30 | ✅ | 7 | 49 |
| Journal 📓 | 12 | 28 | ✅ | 5 | 45 |
| Projects 🗂️ | 14 | 38 | ✅ | 5 | 57 |
| Dashboard 🖥️ | — | 39 | ✅ | 8 | 47 |
| Budget 💰 | 14 | 43 | ✅ | 7 | 64 |
| Time 🕐 | 12 | 36 | ✅ | 12 | 60 |
| **TOTAL** | | | | | **396** |

---

**Ash says:** Time Blocker shipped! 🕐 12 store + 36 engine + 12 integration = 60 tests. Vert 24h day grid, compact week overview, conflict detection on add and as standalone command. 396 tests across 8 projects. `suite.py` renders 6 of 8 projects (Tasks through Budget) — worth adding Time to the dashboard. What's next?
