"""Unit tests for journal_engine.py — plain asserts, run directly."""
from journal_engine import (
    add_entry,
    get_entry,
    delete_entry,
    search_entries,
    list_entries,
    list_tags,
)


# -----------------------------------------------------------------------
# add_entry
# -----------------------------------------------------------------------

def test_add_entry_creates_new():
    entries = []
    entries, e = add_entry(entries, "2025-07-14", "Great day.", ["happy"])
    assert e["date"] == "2025-07-14"
    assert e["body"] == "Great day."
    assert e["tags"] == ["happy"]
    assert len(entries) == 1


def test_add_entry_overwrites_existing():
    entries = []
    add_entry(entries, "2025-07-14", "First version.")
    entries, e = add_entry(entries, "2025-07-14", "Revised version.")
    assert len(entries) == 1
    assert entries[0]["body"] == "Revised version."
    assert e["body"] == "Revised version."


def test_add_entry_defaults_tags_to_empty():
    entries = []
    entries, e = add_entry(entries, "2025-07-14", "No tags.")
    assert e["tags"] == []


def test_add_entry_tags_keeps_given_list():
    entries = []
    entries, e = add_entry(entries, "2025-07-14", "Tagged.", ["a", "b"])
    assert e["tags"] == ["a", "b"]


def test_add_entry_multiple_dates():
    entries = []
    add_entry(entries, "2025-07-14", "Monday.")
    add_entry(entries, "2025-07-15", "Tuesday.")
    assert len(entries) == 2


# -----------------------------------------------------------------------
# get_entry
# -----------------------------------------------------------------------

def test_get_entry_returns_entry():
    entries = []
    add_entry(entries, "2025-07-14", "Found it.")
    e = get_entry(entries, "2025-07-14")
    assert e is not None
    assert e["body"] == "Found it."


def test_get_entry_returns_none_for_missing():
    entries = []
    e = get_entry(entries, "2025-07-14")
    assert e is None


def test_get_entry_returns_none_for_wrong_date():
    entries = []
    add_entry(entries, "2025-07-14", "Here.")
    e = get_entry(entries, "2025-07-15")
    assert e is None


# -----------------------------------------------------------------------
# delete_entry
# -----------------------------------------------------------------------

def test_delete_entry_removes_and_returns():
    entries = []
    add_entry(entries, "2025-07-14", "Delete me.")
    entries, removed = delete_entry(entries, "2025-07-14")
    assert removed["body"] == "Delete me."
    assert len(entries) == 0


def test_delete_entry_raises_for_missing():
    entries = []
    try:
        delete_entry(entries, "2025-07-14")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "2025-07-14" in str(e)


def test_delete_entry_keeps_other_entries():
    entries = []
    add_entry(entries, "2025-07-14", "Keep.")
    add_entry(entries, "2025-07-15", "Remove.")
    entries, _ = delete_entry(entries, "2025-07-15")
    assert len(entries) == 1
    assert entries[0]["date"] == "2025-07-14"


# -----------------------------------------------------------------------
# search_entries
# -----------------------------------------------------------------------

def test_search_finds_matching_body():
    entries = []
    add_entry(entries, "2025-07-14", "A wonderful day.")
    add_entry(entries, "2025-07-15", "A terrible day.")
    results = search_entries(entries, "wonderful")
    assert len(results) == 1
    assert results[0]["date"] == "2025-07-14"


def test_search_is_case_insensitive():
    entries = []
    add_entry(entries, "2025-07-14", "Hello World.")
    results = search_entries(entries, "hello")
    assert len(results) == 1


def test_search_returns_empty_when_no_match():
    entries = []
    add_entry(entries, "2025-07-14", "Hello.")
    results = search_entries(entries, "xyzzy")
    assert results == []


def test_search_returns_multiple_matches():
    entries = []
    add_entry(entries, "2025-07-14", "I love Python.")
    add_entry(entries, "2025-07-15", "Python is great.")
    add_entry(entries, "2025-07-16", "Just Java.")
    results = search_entries(entries, "python")
    assert len(results) == 2


def test_search_with_tag_filter():
    entries = []
    add_entry(entries, "2025-07-14", "Good day.", ["happy"])
    add_entry(entries, "2025-07-15", "Good evening.", ["sad"])
    results = search_entries(entries, "good", tag="happy")
    assert len(results) == 1
    assert results[0]["date"] == "2025-07-14"


def test_search_with_tag_and_no_body_match():
    entries = []
    add_entry(entries, "2025-07-14", "Hello.", ["happy"])
    results = search_entries(entries, "xyzzy", tag="happy")
    assert results == []


def test_search_results_newest_first():
    entries = []
    add_entry(entries, "2025-07-14", "Python day.")
    add_entry(entries, "2025-07-16", "Python rocks.")
    add_entry(entries, "2025-07-15", "Python again.")
    results = search_entries(entries, "python")
    assert results[0]["date"] == "2025-07-16"
    assert results[1]["date"] == "2025-07-15"
    assert results[2]["date"] == "2025-07-14"


# -----------------------------------------------------------------------
# list_entries
# -----------------------------------------------------------------------

def test_list_entries_returns_all_sorted():
    entries = []
    add_entry(entries, "2025-07-15", "Tuesday.")
    add_entry(entries, "2025-07-14", "Monday.")
    add_entry(entries, "2025-07-16", "Wednesday.")
    result = list_entries(entries)
    assert len(result) == 3
    assert result[0]["date"] == "2025-07-14"
    assert result[1]["date"] == "2025-07-15"
    assert result[2]["date"] == "2025-07-16"


def test_list_entries_empty():
    assert list_entries([]) == []


def test_list_entries_filtered_by_tag():
    entries = []
    add_entry(entries, "2025-07-14", "A.", ["work"])
    add_entry(entries, "2025-07-15", "B.", ["personal"])
    add_entry(entries, "2025-07-16", "C.", ["work"])
    result = list_entries(entries, tag="work")
    assert len(result) == 2
    assert result[0]["date"] == "2025-07-14"
    assert result[1]["date"] == "2025-07-16"


def test_list_entries_filtered_by_tag_no_match():
    entries = []
    add_entry(entries, "2025-07-14", "A.", ["work"])
    result = list_entries(entries, tag="personal")
    assert result == []


# -----------------------------------------------------------------------
# list_tags
# -----------------------------------------------------------------------

def test_list_tags_returns_tags_with_counts():
    entries = []
    add_entry(entries, "2025-07-14", "A.", ["happy", "work"])
    add_entry(entries, "2025-07-15", "B.", ["happy"])
    add_entry(entries, "2025-07-16", "C.", ["work"])
    result = list_tags(entries)
    assert len(result) == 2
    # Most frequent first
    assert result[0]["tag"] == "happy"
    assert result[0]["count"] == 2
    assert result[1]["tag"] == "work"
    assert result[1]["count"] == 2


def test_list_tags_empty_when_no_entries():
    assert list_tags([]) == []


def test_list_tags_empty_when_no_tags_on_entries():
    entries = []
    add_entry(entries, "2025-07-14", "No tags.", [])
    add_entry(entries, "2025-07-15", "Also none.")
    assert list_tags(entries) == []


def test_list_tags_sorted_by_count_desc():
    entries = []
    add_entry(entries, "2025-07-14", "A.", ["common"])
    add_entry(entries, "2025-07-15", "B.", ["common"])
    add_entry(entries, "2025-07-16", "C.", ["common", "rare"])
    add_entry(entries, "2025-07-17", "D.", ["rare"])
    result = list_tags(entries)
    assert result[0]["tag"] == "common"
    assert result[0]["count"] == 3
    assert result[1]["tag"] == "rare"
    assert result[1]["count"] == 2


def test_list_tags_alphabetical_for_ties():
    entries = []
    add_entry(entries, "2025-07-14", "A.", ["beta"])
    add_entry(entries, "2025-07-15", "B.", ["alpha"])
    result = list_tags(entries)
    # Both count=1, so alphabetical: alpha before beta
    assert result[0]["tag"] == "alpha"
    assert result[1]["tag"] == "beta"


def test_list_tags_handles_missing_tags_key():
    """Entries without a 'tags' key should be treated as having no tags."""
    entries = [{"date": "2025-07-14", "body": "No tags key."}]
    result = list_tags(entries)
    assert result == []


if __name__ == "__main__":
    tests = [
        test_add_entry_creates_new,
        test_add_entry_overwrites_existing,
        test_add_entry_defaults_tags_to_empty,
        test_add_entry_tags_keeps_given_list,
        test_add_entry_multiple_dates,
        test_get_entry_returns_entry,
        test_get_entry_returns_none_for_missing,
        test_get_entry_returns_none_for_wrong_date,
        test_delete_entry_removes_and_returns,
        test_delete_entry_raises_for_missing,
        test_delete_entry_keeps_other_entries,
        test_search_finds_matching_body,
        test_search_is_case_insensitive,
        test_search_returns_empty_when_no_match,
        test_search_returns_multiple_matches,
        test_search_with_tag_filter,
        test_search_with_tag_and_no_body_match,
        test_search_results_newest_first,
        test_list_entries_returns_all_sorted,
        test_list_entries_empty,
        test_list_entries_filtered_by_tag,
        test_list_entries_filtered_by_tag_no_match,
        test_list_tags_returns_tags_with_counts,
        test_list_tags_empty_when_no_entries,
        test_list_tags_empty_when_no_tags_on_entries,
        test_list_tags_sorted_by_count_desc,
        test_list_tags_alphabetical_for_ties,
        test_list_tags_handles_missing_tags_key,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
