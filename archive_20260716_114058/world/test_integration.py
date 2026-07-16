"""
Integration test: kingdom + world + people working together.
"""
import sys
sys.path.insert(0, ".")

# Force fresh imports
import importlib
import kingdom as k_mod
import world as w_mod
import people as p_mod

# Reload to get fresh state
importlib.reload(k_mod)
importlib.reload(w_mod)
importlib.reload(p_mod)

from kingdom import kingdom
from world import world
from people import People

people = People()

print("=" * 60)
print("🏰 ASHFALL — FULL INTEGRATION TEST")
print("=" * 60)

# Reset kingdom for clean test
kingdom.population = 50
kingdom.gold = 100
kingdom.food = 120
kingdom.stone = 30
kingdom.wood = 60

print(f"\nDay {world.day} [{world.season}, {world.weather}]")
print(f"Pop: {kingdom.population} | Gold: {kingdom.gold} | Food: {kingdom.food}")
print(f"Defense: {kingdom.defense_rating()} | Housing: {kingdom.housing_capacity()}")

# ── Population Pyramid (initial) ──
pyramid = people.population_pyramid()
print(f"\n{pyramid['pyramid']}")
print(f"Dependency ratio: {kingdom.dependency_ratio(people):.2f}")

# Run 7 integrated days (enough to see aging, possible migration)
for i in range(7):
    print(f"\n--- Day {world.day} [{world.season}, {world.weather}] ---")

    # World advances (season, weather, events)
    day_info = world.advance_day()

    # People work and update
    if hasattr(people, 'advance_day'):
        people.advance_day()
    elif hasattr(people, 'daily_update'):
        people.daily_update()

    # Kingdom tick with full integration
    summary = kingdom.tick(people_obj=people, world_obj=world, day=world.day)

    print(f"  Weather: {day_info['weather']} | Season: {day_info['season']}")
    if summary['produced']:
        print(f"  Produced: {summary['produced']}")
    if not summary['fed']:
        print(f"  ⚠️ {summary['events']}")
    if summary.get('immigration'):
        print(f"  {summary['immigration']['message']}")
    if summary.get('raid'):
        print(f"  ⚔️ {summary['raid']['narrative']}")
    print(f"  Pop: {kingdom.population} | Food: {kingdom.food} | Gold: {kingdom.gold}")
    print(f"  Defense: {kingdom.defense_rating()}")

    # Try building something
    if kingdom.stone >= 8 and kingdom.wood >= 4:
        ok, msg = kingdom.build("walls")
        if ok:
            print(f"  🔨 {msg}")

print(f"\n{'=' * 60}")
print("FINAL STATUS")
for k, v in kingdom.status().items():
    print(f"  {k}: {v}")
print(f"  defense_rating: {kingdom.defense_rating()}")
print(f"  housing: {kingdom.housing_capacity()}/{kingdom.population}")
print(f"  avg morale: {sum(c.morale for c in people.citizens)/len(people.citizens):.1f}")

# ── Population Pyramid (final) ──
pyramid2 = people.population_pyramid()
print(f"\n{pyramid2['pyramid']}")
print(f"Dependency ratio: {kingdom.dependency_ratio(people):.2f}")
print(f"Youngest: {pyramid2['youngest']:.1f}y  Oldest: {pyramid2['oldest']:.1f}y")

# ── Census ──
c = people.census()
print(f"\nCensus — Roles: {c['roles']}")
print(f"Census — Factions: {c['factions']}")
print(f"Births this season: {c['births_this_season']} | Deaths: {c['deaths_this_season']}")
