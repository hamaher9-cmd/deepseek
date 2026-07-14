# Read the rest of dashboard_engine.py after line 155
with open("dashboard_engine.py") as f:
    lines = f.readlines()
print("=== dashboard_engine.py (lines 155-end) ===")
for i, line in enumerate(lines[154:], start=155):
    print(f"{i}: {line}", end="")

print("\n\n=== suite.py (lines 148-end) ===")
with open("suite.py") as f:
    lines = f.readlines()
for i, line in enumerate(lines[147:], start=148):
    print(f"{i}: {line}", end="")

print("\n\n=== budget_engine.py (lines 155-end) ===")
with open("budget_engine.py") as f:
    lines = f.readlines()
for i, line in enumerate(lines[154:], start=155):
    print(f"{i}: {line}", end="")
