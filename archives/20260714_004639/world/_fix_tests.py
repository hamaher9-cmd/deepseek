with open("test_dashboard_engine.py", "r") as f:
    content = f.read()

# Fix 1: test_get_dashboard_all_empty — add budget to expected keys
old1 = 'assert set(dash.keys()) == {"tasks", "pomodoro", "habits", "journal", "projects"}'
new1 = 'assert set(dash.keys()) == {"tasks", "pomodoro", "habits", "journal", "projects", "budget"}'
content = content.replace(old1, new1)

# Fix 2: Add budget assertion in test_get_dashboard_all_empty
old2 = "        assert dash[\"projects\"][\"total\"] == 0\n\n\ndef test_get_dashboard_mixed"
new2 = """        assert dash["projects"]["total"] == 0
        assert dash["budget"]["total"] == 0
        assert dash["budget"]["balance"] == 0.0


def test_get_dashboard_mixed"""
content = content.replace(old2, new2)

# Fix 3: test_get_dashboard_mixed — add budget.json to fake_load
old3 = '''        elif path.endswith("projects.json"):
            return [{"name": "P1", "status": "active", "tasks": []}]
        return []'''
new3 = '''        elif path.endswith("projects.json"):
            return [{"name": "P1", "status": "active", "tasks": []}]
        elif path.endswith("budget.json"):
            return [{"id": 1, "type": "income", "amount": 100.0, "category": "salary", "date": today}]
        return []'''
content = content.replace(old3, new3)

# Fix 4: Add budget assertion in test_get_dashboard_mixed
old4 = "        assert dash[\"projects\"][\"active\"] == 1\n\n\ndef test_get_dashboard_handles_missing_files"
new4 = """        assert dash["projects"]["active"] == 1
        assert dash["budget"]["total"] == 1
        assert dash["budget"]["balance"] == 100.0


def test_get_dashboard_handles_missing_files"""
content = content.replace(old4, new4)

with open("test_dashboard_engine.py", "w") as f:
    f.write(content)

print("Fixed 4 locations in test_dashboard_engine.py")
