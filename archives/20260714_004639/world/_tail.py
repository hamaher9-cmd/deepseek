import sys
with open('test_project_engine.py') as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
for line in lines[-10:]:
    print(line.rstrip())
