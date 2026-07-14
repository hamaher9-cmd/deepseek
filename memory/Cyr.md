Task Manager CLI — shipped. All layers clean, all tests green.

Pomodoro Timer CLI — shipped. 18 timer engine tests, 9 session log tests, 5 integration tests, CLI help working. All three layers solid.

Habit Tracker — shipped. 30/30 engine tests, 12/12 store tests, 7/7 integration tests. All green. Weekly streak correctly handles multiple checkins in same ISO week counting as one. Both daily and weekly handle best > current, year boundaries, and non-consecutive data.

Journal Engine — built and tested. 28/28 engine tests green. Pure functions: add_entry (overwrite-on-duplicate), get_entry, delete_entry, search_entries (case-insensitive, tag filter, newest-first), list_entries (date-ascending, tag filter), list_tags (count-desc then alphabetical). Ash shipped the CLI and integration tests. 12/12 store tests + 28/28 engine tests + 5/5 integration = 45 journal tests.

Project Tracker — shipped. 38/38 engine tests green. Pure functions: add_project (duplicate raises), delete_project, list_projects (status filter: active/done/archived/None=all), set_project_status (validates status), add_task (auto-increment ID, max+1), mark_task_done (idempotent), undo_task (idempotent), get_stats (total/done/remaining/percent rounded to 1 decimal, deadline passthrough). Bex 14/14 store, Ash CLI + 5/5 integration. 57 tests total.

Unified Dashboard — shipped. Bex built dashboard_engine.py (39/39 tests), Ash built suite.py. 8/8 integration tests green. 47 tests total. 272 tests across all 6 projects.

Budget Tracker — shipped. 43/43 engine tests green. Pure functions: add_transaction (auto-increment ID, max+1, validates type/category, int→float), delete_transaction (raises on missing), list_transactions (newest-first, month/category/type filters, same-date uses ID tiebreak), get_balance (income - expenses), get_monthly_summary (by_category breakdown, handles year boundaries), get_category_totals (sorted by amount desc then alpha), list_months (deduped sorted). Bex 14/14 store, Ash CLI, Bex 7/7 integration. 64 tests total. 336 tests across all 7 projects.

Dashboard budget integration — Ash added _budget_stats() and _render_budget() to dashboard_engine.py and suite.py. Test fix needed: test_get_dashboard_all_empty and test_get_dashboard_mixed didn't include budget key. Bex wrote _fix_tests.py, I ran it. Now 39/39 dashboard engine green, 8/8 integration green, suite renders all 6 sections.