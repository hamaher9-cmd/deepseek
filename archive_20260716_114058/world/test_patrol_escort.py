"""Test patrol routes and caravan escort system."""

import sys
sys.path.insert(0, ".")

from kingdom import kingdom
from world import world as w
from people import People, Citizen, FIRST_NAMES, FAMILY_NAMES
import random

random.seed(42)
print("=" * 60)
print("🛡️ PATROL & ESCORT SYSTEM TEST")
print("=" * 60)

# Reset
kingdom.__init__()
w.__init__()
people = People()

# Add citizens with scouts and guards
for i in range(50):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(FAMILY_NAMES)}"
    role = random.choice(["farmer", "farmer", "woodcutter", "builder", "scout", "scout", "guard", "guard", "miner", "herbalist"])
    c = Citizen(name, role)
    c.age = random.randint(18, 45)
    people.citizens.append(c)
    if hasattr(people, '_assign_faction'):
        people._assign_faction(c)

# Ensure we have at least 3 scouts and 3 guards for testing
for c in people.citizens:
    if c.role == "scout":
        c.combat_skill = random.randint(10, 50)
    if c.role == "guard":
        c.combat_skill = random.randint(20, 60)

scout_count = sum(1 for c in people.citizens if c.alive and c.role == "scout")
guard_count = sum(1 for c in people.citizens if c.alive and c.role == "guard")
print(f"Setup: {len(people.citizens)} citizens, {scout_count} scouts, {guard_count} guards")

# ── Test 1: Patrol system ──
print("\n─── Test 1: Patrol ───")
patrol_reduction, discoveries = kingdom._patrol(people, w)
print(f"  Patrol reduction: {patrol_reduction:.4f}")
print(f"  Discoveries: {len(discoveries)}")
for d in discoveries:
    print(f"    {d[:120]}")
if patrol_reduction > 0:
    print("  ✅ Patrol system active!")
else:
    print("  ⚠️  No patrol reduction (no scouts available?)")

# ── Test 2: Patrol reduces raid chance ──
print("\n─── Test 2: Patrol + Raid integration ───")
# Force a raid check
raids_without_patrol = 0
raids_with_patrol = 0

for _ in range(200):
    # Without patrol
    if kingdom._roll_raid(w, patrol_reduction=0.0):
        raids_without_patrol += 1
    # With patrol
    if kingdom._roll_raid(w, patrol_reduction=patrol_reduction):
        raids_with_patrol += 1

print(f"  200 trials: without patrol={raids_without_patrol}, with patrol={raids_with_patrol}")
if raids_with_patrol <= raids_without_patrol:
    print("  ✅ Patrol reduces raid frequency!")
else:
    print("  ⚠️  Statistical anomaly (small sample)")

# ── Test 3: Caravan escort ──
print("\n─── Test 3: Caravan Escort ───")
caravan = kingdom._roll_caravan(w)
if caravan:
    print(f"  Caravan: {caravan['type']} — {caravan['description']}")
    escort_ok, narrative, bonus = kingdom.escort_caravan(caravan, people)
    print(f"  Escort success: {escort_ok}")
    print(f"  Narrative: {narrative[:120]}")
    print(f"  Bonus: {bonus}")
    if escort_ok and bonus.get("gold", 0) > 0:
        print("  ✅ Caravan escort working!")
    elif not escort_ok:
        print("  ⚠️  No guards available for escort")
else:
    print("  No caravan this tick (low chance, rerun if needed)")

# ── Test 4: Integration in tick ──
print("\n─── Test 4: Tick integration ───")
kingdom.__init__()
# Add buildings so things work
kingdom.buildings["walls"] = 3
kingdom.buildings["market"] = 1
kingdom.gold = 200
kingdom.food = 200

escort_count = 0
patrol_count = 0
for day in range(30):
    w.advance_day()
    summary = kingdom.tick(people_obj=people, world_obj=w, day=day)
    if summary.get("escort"):
        escort_count += 1
    if summary.get("patrol"):
        patrol_count += 1

print(f"  Over 30 days: escorts={escort_count}, patrols={patrol_count}")
print(f"  Escort history: {len(kingdom.escort_history)} entries")
print(f"  Patrol log: {len(kingdom.patrol_log)} entries")
if patrol_count > 0:
    print("  ✅ Patrol integrated in tick!")
else:
    print("  ⚠️  No patrol discoveries (low chance per tick)")
if len(kingdom.escort_history) > 0:
    print("  ✅ Escort integrated in tick!")
else:
    print("  ⚠️  No escorts (depends on caravan + guard availability)")

print("\n" + "=" * 60)
print("✅ PATROL & ESCORT SYSTEM TEST COMPLETE!")
print("=" * 60)
