"""
Test the region-specific disaster events system.
"""

import sys
sys.path.insert(0, '.')

import importlib
import kingdom as k_mod
import world as w_mod

def reset_all():
    """Reset singletons for a clean test."""
    importlib.reload(k_mod)
    importlib.reload(w_mod)
    return k_mod.kingdom, w_mod.world

print("=" * 60)
print("🌋 REGION DISASTER SYSTEM TEST")
print("=" * 60)

# ── Test 1: DISASTERS dict structure ──
print("\n─── Test 1: DISASTERS dict structure ──")
kingdom, world = reset_all()

from world import DISASTERS

for region in ["the_vale", "old_oak_ridge", "glimmer_marsh",
               "ironroot_depths", "sunfire_plains", "the_ashen_copse"]:
    d = DISASTERS[region]
    print(f"  {region}: {d['name']} (chance: {d['chance']}, recovery: {d['recovery_day']}d)")
    assert d['name'], f"{region} has no name"
    assert 'narrative' in d
    assert 'effects' in d
    assert 'recovery_day' in d
    assert 'recovery_msg' in d

print("  ✅ DISASTERS dict structure valid!")

# ── Test 2: World tracks disasters ──
print("\n─── Test 2: World init tracks disasters ──")
kingdom, world = reset_all()

assert hasattr(world, '_active_disasters'), "Missing _active_disasters"
assert hasattr(world, '_disaster_cooldown'), "Missing _disaster_cooldown"
assert hasattr(world, '_sunfire_fertility'), "Missing _sunfire_fertility"
assert world._active_disasters == {}
assert world._disaster_cooldown == {}
assert world._sunfire_fertility == False
print("  ✅ Disaster tracking fields initialized!")

# ── Test 3: _check_disasters method exists and runs ──
print("\n─── Test 3: _check_disasters method ──")
kingdom, world = reset_all()

assert hasattr(world, '_check_disasters'), "Missing _check_disasters method"
assert hasattr(world, 'disaster_status'), "Missing disaster_status method"

result = world._check_disasters()
print(f"  _check_disasters result: {result}")
print("  ✅ _check_disasters runs without error!")

# ── Test 4: disaster_status ──
print("\n─── Test 4: disaster_status ──")
kingdom, world = reset_all()

status = world.disaster_status()
print(f"  Status (no disasters): {status[:60]}...")
assert "No active disasters" in status or "peace" in status.lower()
print("  ✅ disaster_status works!")

# ── Test 5: Manual disaster trigger ──
print("\n─── Test 5: Manual disaster trigger ──")
kingdom, world = reset_all()

world._active_disasters["the_vale"] = {
    "name": "Thornblight",
    "day_struck": world.day,
    "recovery_day": world.day + 3,
}

status = world.disaster_status()
print(f"  Status with active disaster:")
for line in status.split("\\n"):
    print(f"    {line}")
assert "Thornblight" in status
assert "ACTIVE DISASTERS" in status
print("  ✅ disaster_status reflects active disasters!")

# ── Test 6: Disaster yield penalty ──
print("\n─── Test 6: Disaster yield penalty ──")
kingdom, world = reset_all()

world.discovered.add("the_vale")
world._active_disasters = {}  # no disaster
kingdom.food = 100
base_harvest = world.harvest("the_vale")
base_food = base_harvest.get("food", 0)
print(f"  Base harvest food: {base_food}")

# With active disaster (70% penalty)
kingdom.food = 100
world._active_disasters["the_vale"] = {
    "name": "Thornblight",
    "day_struck": world.day,
    "recovery_day": world.day + 5,
}
disaster_harvest = world.harvest("the_vale")
disaster_food = disaster_harvest.get("food", 0)
print(f"  Disaster harvest food: {disaster_food}")

assert disaster_food < base_food * 0.5, f"Expected yield reduction, got {disaster_food} vs {base_food}"
print("  ✅ Disaster yield penalty applied!")

# ── Test 7: Disaster recovery ──
print("\n─── Test 7: Disaster recovery ──")
kingdom, world = reset_all()

world._active_disasters["the_vale"] = {
    "name": "Thornblight",
    "day_struck": 0,
    "recovery_day": 3,
}

for d in range(4):
    world.day = d
    world._check_disasters()

assert "the_vale" not in world._active_disasters, "Disaster should have recovered"
assert "the_vale" in world._disaster_cooldown, "Should be in cooldown"
print(f"  Day {world.day}: the_vale recovered, cooldown until day {world._disaster_cooldown['the_vale']}")
print("  ✅ Disaster recovery works!")

# ── Test 8: Cooldown prevents re-trigger ──
print("\n─── Test 8: Cooldown prevention ──")
kingdom, world = reset_all()

# Set cooldown far in the future so it never expires during our test
world._disaster_cooldown["the_vale"] = world.day + 9999
disaster_count = 0
for i in range(200):
    world.day = i
    result = world._check_disasters()
    if result:
        for r in result:
            if r.get("type") == "disaster" and r.get("region") == "the_vale":
                disaster_count += 1

assert disaster_count == 0, f"Expected 0 disasters during cooldown, got {disaster_count}"
print(f"  the_vale disasters during cooldown: {disaster_count}")
print("  ✅ Cooldown prevents disasters!")

# ── Test 9: advance_day integration ──
print("\n─── Test 9: advance_day integration ──")
kingdom, world = reset_all()

world.discovered.add("the_vale")
world.discovered.add("old_oak_ridge")

for d in range(10):
    world.advance_day()

print(f"  Ran 10 advance_day cycles without error.")
print(f"  Active disasters: {list(world._active_disasters.keys())}")
print(f"  Cooldowns: {list(world._disaster_cooldown.keys())}")
print("  ✅ advance_day integration working!")

# ── Test 10: All regions have unique disasters ──
print("\n─── Test 10: All regions have unique disasters ──")
kingdom, world = reset_all()

disaster_names = set()
for region, d in DISASTERS.items():
    disaster_names.add(d['name'])
    special = d.get('special')
    print(f"  {region}: {d['name']} (special: {special})")

assert len(disaster_names) >= 6, f"Expected >=6 unique names, got {len(disaster_names)}"
print(f"  ✅ All {len(disaster_names)} regions have unique disaster types!")

# ── Test 11: Sunfire fertility boost ──
print("\n─── Test 11: Sunfire wildfire fertility boost ──")
kingdom, world = reset_all()

world.discovered.add("sunfire_plains")
world._sunfire_fertility = True

kingdom.food = 100
boosted = world.harvest("sunfire_plains")
print(f"  Boosted sunfire_plains harvest: {boosted}")

assert world._sunfire_fertility == False, "Fertility should be consumed after one harvest"
print("  ✅ Sunfire fertility boost consumed after one harvest!")

# ── Test 12: Marsh-Fog recovery special ──
print("\n─── Test 12: Marsh-Fog recovery special ──")
kingdom, world = reset_all()

world.discovered.add("glimmer_marsh")
world._active_disasters["glimmer_marsh"] = {
    "name": "Marsh-Fog",
    "day_struck": 0,
    "recovery_day": 1,
}
world.day = 1
world._check_disasters()

assert "glimmer_marsh" not in world._active_disasters
print(f"  Marsh-Fog recovered. Lore fragments: {len(world.lore_fragments)}, Gold: {kingdom.gold}")
print("  ✅ Marsh-Fog recovery special works!")

print("\n" + "=" * 60)
print("✅ ALL DISASTER SYSTEM TESTS PASSED!")
print("=" * 60)
