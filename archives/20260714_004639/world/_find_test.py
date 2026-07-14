with open("test_dashboard_engine.py") as f:
    lines = f.readlines()

# Find the failing test
for i, line in enumerate(lines):
    if "test_get_dashboard_all_empty" in line or "test_get_dashboard_mixed" in line or "test_get_dashboard_handles_missing" in line:
        end = min(len(lines), i+30)
        for j in range(i, end):
            print(f"{j+1}: {lines[j]}", end="")
        print("---")
