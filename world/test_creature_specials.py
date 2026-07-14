#!/usr/bin/env python3
"""Test the new creature special systems: Gloom-Lantern spread, Shadow-Fox gift, Ash-Bloom."""

import sys
sys.path.insert(0, '.')

from world import world as w
from kingdom import kingdom

print("=" * 60)
print("🧪 CREATURE SPECIALS TEST")
print("=" * 60)

# Reset world
w.day = 0
w.season = "spring"
w.weather = "clear"
w.discovered = {"the_vale", "old_oak_ridge", "glimmer_marsh", "ironroot_depths", "sunfire_plains"}
w.exploration_bonuses = {}
w.unlock_flags = set()
w.world_log = []
w.lore_fragments = []
w._gloom_lantern_day = 0
w._gloom_lantern_regions = set()
w._shadow_fox_fed_day = 0
w._shadow_fox_gift_pending = False
w._shadow_fox_return_day = 5

# Sync kingdom territory
kingdom.territory = list(w.discovered)
kingdom.food = 500
kingdom.gold = 500
kingdom.population = 50

all_passed = True

# ── Test 1: Gloom-Lantern spread ──
print("\n─── Test 1: Gloom-Lantern spread ───")
w._gloom_lantern_day = 0
w._gloom_lantern_regions = {"ironroot_depths"}
for i in range(7):
    w.advance_day()
print(f"  After 7 days: day={w.day}, gloom_lantern_regions={w._gloom_lantern_regions}")
spread_msgs = [entry for entry in w.world_log if "GLOOM-LANTERN SPREAD" in entry]
print(f"  Spread events: {len(spread_msgs)}")
for msg in spread_msgs:
    print(f"    {msg[:130]}")

for i in range(7):
    w.advance_day()
print(f"  After 14 days: day={w.day}, gloom_lantern_regions={w._gloom_lantern_regions}")
spread_msgs2 = [entry for entry in w.world_log if "GLOOM-LANTERN SPREAD" in entry]
print(f"  Total spread events: {len(spread_msgs2)}")
if len(spread_msgs2) >= 2:
    print("  ✅ Spread mechanic working!")
else:
    print(f"  ❌ Expected at least 2 spreads, got {len(spread_msgs2)}")
    all_passed = False

# ── Test 2: Shadow-Fox gift ──
print("\n─── Test 2: Shadow-Fox gift ───")
kingdom.food = 500
w._shadow_fox_fed_day = w.day
w._shadow_fox_gift_pending = True
w._shadow_fox_return_day = 4
print(f"  Fed day: {w._shadow_fox_fed_day}, return in {w._shadow_fox_return_day} days")

gift_received = False
for i in range(10):
    w.advance_day()
    gift_msgs = [entry for entry in w.world_log if "SHADOW-FOX RETURNS" in entry]
    if gift_msgs:
        gift_received = True
        print(f"  ✅ Gift received on day {w.day}!")
        for msg in gift_msgs:
            print(f"    {msg[:120]}")
        break

if not gift_received:
    print("  ❌ Gift not received!")
    all_passed = False

# ── Test 3: Ash-Bloom during omens ──
print("\n─── Test 3: Ash-Bloom during omens ──")
w.discovered.add("the_ashen_copse")
if "the_ashen_copse" not in kingdom.territory:
    kingdom.territory.append("the_ashen_copse")
w._omen_cache_day = -1
w._omen_cache = None

ash_bloom_count = 0
for i in range(80):
    w.advance_day()
    omen = w.world_omens()
    if omen and omen.get("ash_bloom"):
        ash_bloom_count += 1

print(f"  Ash-Bloom events in 80 days: {ash_bloom_count}")
if ash_bloom_count > 0:
    print("  ✅ Ash-Bloom omen integration working!")
else:
    print("  ❌ No Ash-Bloom events — very unlikely, may indicate a bug")
    all_passed = False

# ── Test 4: resolve tracking ──
print("\n─── Test 4: resolve_creature_encounter tracking ──")
w._gloom_lantern_regions.clear()
w._gloom_lantern_day = 0

encounter = None
for _ in range(50):
    enc = w.creature_encounter("ironroot_depths")
    if enc and enc["creature_name"] == "Gloom-Lantern":
        encounter = enc
        break

if encounter:
    print(f"  Found Gloom-Lantern encounter")
    result = w.resolve_creature_encounter(encounter, "avoid")
    print(f"  After avoid: gloom_lantern_regions={w._gloom_lantern_regions}")
    if "ironroot_depths" in w._gloom_lantern_regions:
        print("  ✅ Gloom-Lantern avoid tracking works!")
    else:
        print("  ❌ Expected ironroot_depths in gloom regions")
        all_passed = False
else:
    print("  ⚠️ Couldn't roll Gloom-Lantern (low probability), skipping assertion")

print("\n" + "=" * 60)
if all_passed:
    print("✅ ALL CREATURE SPECIALS TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED!")
print("=" * 60)
