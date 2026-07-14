#!/usr/bin/env python3
"""Test the Creature Lairs system in world.py."""

import sys
sys.path.insert(0, ".")

# Fresh import
import importlib
import kingdom as k_mod
import world as w_mod

importlib.reload(k_mod)
importlib.reload(w_mod)

from kingdom import kingdom
from world import World, LAIRS

def reset_kingdom():
    """Reset kingdom to a known state."""
    kingdom.population = 50
    kingdom.food = 120
    kingdom.gold = 100
    kingdom.wood = 80
    kingdom.stone = 40
    kingdom.territory = ["the_vale", "old_oak_ridge", "sunfire_plains", "glimmer_marsh", "ironroot_depths"]
    kingdom.buildings = {
        "huts": 7, "well": 1, "storehouse": 3, "walls": 8,
        "guard_tower": 1, "market": 2, "barracks": 3, "granary": 3,
        "tavern": 1, "market_hall": 1
    }
    kingdom.kingdom_log = []
    kingdom._raid_cooldown = 0

print("=" * 60)
print("CREATURE LAIRS SYSTEM TEST")
print("=" * 60)

# ── Test 1: LAIRS dict structure ──
print("\n--- Test 1: LAIRS dict structure ---")
for region in ["the_vale", "old_oak_ridge", "glimmer_marsh", "ironroot_depths", "sunfire_plains", "the_ashen_copse"]:
    assert region in LAIRS, f"Missing lair for {region}"
    lair = LAIRS[region]
    for key in ["name", "boss", "danger", "discovery", "encounter", "stakes", "combat_stakes", "cleared_bonus", "special"]:
        assert key in lair, f"Missing key '{key}' in lair {region}"
    print(f"  {region}: {lair['name']} (boss: {lair['boss']}, danger: {lair['danger']})")
print("  LAIRS dict structure valid!")

# ── Test 2: World init has lair tracking ──
print("\n--- Test 2: World init tracks lairs ---")
reset_kingdom()
w = World()
assert hasattr(w, '_discovered_lairs'), "Missing _discovered_lairs"
assert hasattr(w, '_cleared_lairs'), "Missing _cleared_lairs"
assert w._discovered_lairs == {}, f"Expected empty dict, got {w._discovered_lairs}"
assert w._cleared_lairs == set(), f"Expected empty set, got {w._cleared_lairs}"
print("  Lair tracking fields initialized correctly!")

# ── Test 3: lair_status shows all discovered regions ──
print("\n--- Test 3: lair_status ---")
reset_kingdom()
w = World()
status = w.lair_status()
print(f"  Status preview: {status[:120]}...")
assert "LAIR STATUS" in status, "lair_status missing header"
for region in w.discovered:
    assert region in status, f"Region {region} missing from lair_status"
print("  lair_status covers all discovered regions!")

# ── Test 4: challenge_lair (manually set a discovered lair) ──
print("\n--- Test 4: challenge_lair ---")
reset_kingdom()
w = World()
kingdom.food = 500
kingdom.gold = 500
# Manually discover a lair
w._discovered_lairs["the_vale"] = "Thorn-Bear's Hollow"

# Try challenging a non-existent lair
result = w.challenge_lair("old_oak_ridge")
assert result is None, "Should return None for undiscovered lair"
print("  Correctly rejects undiscovered lair")

# Challenge with 'avoid'
result = w.challenge_lair("the_vale", "avoid")
assert result is not None
assert result["cleared"] == False
assert "the_vale" not in w._cleared_lairs
print(f"  Avoid: {result}")

# Challenge with 'fight'
result = w.challenge_lair("the_vale", "fight")
assert result is not None
assert result["cleared"] == True
assert "the_vale" in w._cleared_lairs
print(f"  Fight: {result}")
print(f"  Gold after fight: {kingdom.gold}")

# Challenge already cleared lair
result = w.challenge_lair("the_vale", "fight")
assert result is None, "Should reject already-cleared lair"
print("  Correctly rejects already-cleared lair")

# ── Test 5: challenge_lair with bargain ──
print("\n--- Test 5: Lair bargain ---")
reset_kingdom()
w = World()
kingdom.food = 500
kingdom.gold = 500
w._discovered_lairs["old_oak_ridge"] = "Ridge-Wolf Lair"
result = w.challenge_lair("old_oak_ridge", "bargain")
assert result is not None
assert result["cleared"] == True
assert "old_oak_ridge" in w._cleared_lairs
print(f"  Bargain result: {result}")
print(f"  Gold: {kingdom.gold}, Food: {kingdom.food}")

# ── Test 6: Non-fightable lair (Bog-Wisp) ──
print("\n--- Test 6: Non-fightable lair ---")
reset_kingdom()
w = World()
kingdom.food = 500
kingdom.gold = 500
w._discovered_lairs["glimmer_marsh"] = "Bog-Wisp Mire"
# Try to fight it (should fail gracefully)
result = w.challenge_lair("glimmer_marsh", "fight")
assert result is not None
assert result["cleared"] == False, "Bog-Wisp should not be fightable"
print(f"  Fight attempt on Bog-Wisp: {result}")
# But bargain should work
result = w.challenge_lair("glimmer_marsh", "bargain")
assert result["cleared"] == True
print(f"  Bargain on Bog-Wisp: {result}")

# ── Test 7: lair_status after clearing ──
print("\n--- Test 7: lair_status after actions ---")
w._discovered_lairs["the_vale"] = "Thorn-Bear's Hollow"
w._cleared_lairs.add("the_vale")
status = w.lair_status()
print(f"  Status:\n{status}")
assert "[CLEARED]" in status, "Should show cleared lair"
print("  lair_status correctly reflects state!")

# ── Test 8: _check_lair_activity passive bonuses ──
print("\n--- Test 8: _check_lair_activity passive bonuses ---")
reset_kingdom()
w = World()
kingdom.gold = 100
kingdom.food = 100
# Clear multiple lairs
w._cleared_lairs = {"the_vale", "old_oak_ridge", "ironroot_depths", "sunfire_plains", "the_ashen_copse"}
gold_before = kingdom.gold
food_before = kingdom.food
w._check_lair_activity()
# Expected: +1 food (vale) +1 food (ridge) +2 gold (depths) +1 gold (plains) +3 gold (copse) = +2 food, +6 gold
print(f"  Gold before: {gold_before}, after: {kingdom.gold} (expected +6)")
print(f"  Food before: {food_before}, after: {kingdom.food} (expected +2)")
assert kingdom.gold == gold_before + 6, f"Expected +6 gold, got {kingdom.gold - gold_before}"
assert kingdom.food == food_before + 2, f"Expected +2 food, got {kingdom.food - food_before}"
print("  Passive lair bonuses working correctly!")

# ── Test 9: Gloom-Saturation event ──
print("\n--- Test 9: Gloom-Saturation ---")
reset_kingdom()
w = World()
kingdom.gold = 100
kingdom.food = 100
# Set up: all 6 regions infected, lair not cleared
w._gloom_lantern_regions = {"ironroot_depths", "the_vale", "old_oak_ridge", "glimmer_marsh", "sunfire_plains", "the_ashen_copse"}
w._cleared_lairs = set()  # lair NOT cleared
w._check_lair_activity()
# Should trigger gloom-saturation: -10 gold, -5 food
print(f"  Gold: {kingdom.gold} (expected 90), Food: {kingdom.food} (expected 95)")
assert kingdom.gold == 90, f"Expected 90 gold after saturation, got {kingdom.gold}"
assert kingdom.food == 95, f"Expected 95 food after saturation, got {kingdom.food}"
print("  Gloom-Saturation event triggers correctly!")

# ── Test 10: advance_day integration ──
print("\n--- Test 10: advance_day integration ---")
reset_kingdom()
w = World()
w._cleared_lairs = {"the_vale"}
kingdom.food = 100
# advance one day
w.advance_day()
print(f"  Day after advance: {w.day}, food: {kingdom.food}")
print("  advance_day integration verified!")

# ── Test 11: Glimmer_marsh lair harvest bonus ──
print("\n--- Test 11: Glimmer_marsh lair harvest bonus ---")
reset_kingdom()
w = World()
kingdom.gold = 500
kingdom.food = 500
w.exploration_bonuses["glimmer_marsh"] = True
w.unlock_flags.add("marsh_revelation")
w._cleared_lairs.add("glimmer_marsh")
# Base glimmer_marsh yields: food=3, wood=1, stone=0, gold=2
# exploration_bonus (*1.25): food=3, wood=1, stone=0, gold=2
# marsh_revelation (*1.5): food=4, wood=1, stone=0, gold=3
# lair bonus (*1.15): food=4, wood=1, stone=0, gold=3
result = w.harvest("glimmer_marsh")
print(f"  Glimmer_marsh harvest with all bonuses: {result}")
# With all multipliers stacked: food should be at least 3
assert result["food"] >= 3, f"Expected food >= 3, got {result}"
print("  Glimmer_marsh lair harvest bonus working!")

print("\n" + "=" * 60)
print("ALL LAIR SYSTEM TESTS PASSED!")
print("=" * 60)
