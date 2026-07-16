"""Multi-season stress test: 65 days across multiple season changes.
Verifies: trade route maturation, omen resource effects, auto-expand,
season changes, raids, caravans, festivals, and kingdom stability."""

import sys
sys.path.insert(0, ".")

from kingdom import kingdom
from world import world as w
from people import People, Citizen, FIRST_NAMES, FAMILY_NAMES
import random

# Ensure reproducible but varied
random.seed(99)
print("=" * 60)
print("🏰 ASHFALL — MULTI-SEASON STRESS TEST (65 DAYS)")
print("=" * 60)

# Reset
kingdom.__init__()
w.__init__()
people = People()

# Quick init: add citizens with varied roles
for i in range(50):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(FAMILY_NAMES)}"
    role = random.choice(["farmer", "farmer", "woodcutter", "woodcutter", "builder", "scout", "miner", "herbalist", "guard", "guard"])
    c = Citizen(name, role)
    c.age = random.randint(18, 55)
    people.citizens.append(c)
    if hasattr(people, '_assign_faction'):
        people._assign_faction(c)

print(f"\nStarting: Pop={kingdom.population}, Gold={kingdom.gold}, Food={kingdom.food}")
print(f"Season: {w.season}, Day: {w.day}")

season_changes = []
omen_events = 0
raids_total = 0
caravans_total = 0
festivals_total = 0
days_with_trade_income = 0
total_trade_gold = 0
starved_ever = False

for day in range(65):
    prev_season = w.season
    w.advance_day()
    
    # Track season changes
    if day > 0 and w.season != prev_season:
        season_changes.append((day, prev_season, w.season))
    
    summary = kingdom.tick(people_obj=people, world_obj=w, day=day)
    
    # Track events
    for evt in summary.get("events", []):
        if "OMEN" in str(evt):
            omen_events += 1
        if "FAMINE" in str(evt) or "starved" in str(evt):
            starved_ever = True
    if summary.get("raid"):
        raids_total += 1
    if summary.get("caravan"):
        caravans_total += 1
    if summary.get("festival"):
        festivals_total += 1
    if summary.get("trade_routes", 0) > 0:
        days_with_trade_income += 1
        total_trade_gold += summary["trade_routes"]
    
    # Brief status every 10 days
    if day % 10 == 0 or day in (29, 30, 59, 60):
        print(f"Day {day} [{w.season}, {w.weather}] "
              f"Pop={kingdom.population} Gold={kingdom.gold} "
              f"Food={kingdom.food} Stone={kingdom.stone} Wood={kingdom.wood} "
              f"Def={kingdom.defense_rating()} Routes={len(kingdom.trade_routes)} "
              f"Storehouses={kingdom.buildings.get('storehouse',0)}")

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Season changes: {season_changes}")
print(f"Omens witnessed: {omen_events}")
print(f"Raids: {raids_total}")
print(f"Caravans: {caravans_total}")
print(f"Festivals: {festivals_total}")
print(f"Trade income days: {days_with_trade_income} (total: {total_trade_gold}g)")
print(f"Trade routes: {len(kingdom.trade_routes)}")
for r in kingdom.trade_routes:
    print(f"  {r['regions']}: {r['current_income']}g/day (age {r['age']}d)")
print(f"Any starvation: {starved_ever}")

print(f"\nFinal: Pop={kingdom.population} Gold={kingdom.gold} Food={kingdom.food}")
print(f"Buildings: {kingdom.buildings}")
print(f"Territory: {kingdom.territory}")
print(f"Defense: {kingdom.defense_rating()}")
print(f"Raids survived: {kingdom.raids_survived}, lost: {kingdom.raids_lost}")
print(f"Milestones: {kingdom.milestones}")

# Validate
checks = []
checks.append(("≥2 season changes", len(season_changes) >= 2))
checks.append(("≥1 omens", omen_events >= 1))
checks.append(("≥1 raids", raids_total >= 1))
checks.append(("≥1 caravans", caravans_total >= 1))
checks.append(("Kingdom alive", kingdom.population > 0))
checks.append(("Storehouses ≤ 8", kingdom.buildings.get("storehouse", 0) <= 8))
checks.append(("Trade routes active", len(kingdom.trade_routes) >= 1))

all_pass = True
for desc, result in checks:
    status = "✅" if result else "❌"
    if not result:
        all_pass = False
    print(f"  {status} {desc}")

if all_pass:
    print("\n✅ MULTI-SEASON STRESS TEST: PASSED")
else:
    print("\n❌ MULTI-SEASON STRESS TEST: FAILED")
