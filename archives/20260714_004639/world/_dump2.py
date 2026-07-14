import suite
import inspect

# Show _render_budget
if hasattr(suite, '_render_budget'):
    print("=== _render_budget ===")
    print(inspect.getsource(suite._render_budget))

# Show _render_projects
if hasattr(suite, '_render_projects'):
    print("=== _render_projects ===")
    print(inspect.getsource(suite._render_projects))

# Show main
if hasattr(suite, 'main'):
    print("=== main ===")
    print(inspect.getsource(suite.main))

# Check for time-related
for name in dir(suite):
    if 'time' in name.lower():
        print(f"Found: {name}")
