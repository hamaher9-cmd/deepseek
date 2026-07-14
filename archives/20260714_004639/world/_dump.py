import dashboard_engine as de
import inspect

# Show PATHS
print("=== PATHS ===")
print(de.PATHS)

# Show get_dashboard source
print("\n=== get_dashboard ===")
print(inspect.getsource(de.get_dashboard))

# Show _budget_stats if it exists
if hasattr(de, '_budget_stats'):
    print("=== _budget_stats ===")
    print(inspect.getsource(de._budget_stats))

# Show _project_stats
if hasattr(de, '_project_stats'):
    print("=== _project_stats ===")
    print(inspect.getsource(de._project_stats))

# Check for time-related functions
for name in dir(de):
    if 'time' in name.lower():
        print(f"Found: {name}")
