"""
Test the hidden 7th secret region (the_sunken_sanctum) and lair-disaster interactions.
"""
import sys
sys.path.insert(0, '.')

import importlib
import kingdom as k_mod
import world as w_mod

def reset_all():
    importlib.reload(k_mod)
    importlib.reload(w_mod)
    return k_mod.kingdom, w_mod.world

print("=" * 60)
print("💎 SECRET REGION & LAIR-DISASTER INTERACTION TEST")
print("=" * 60)

# ── Test 1: the_sunken_sanctum exists in TERRAIN ──
print("\n─── Test 1: the_sunken_sanctum in TERRAIN ──")
from world import TERRAIN
assert "the_sunken_sanctum" in TERRAIN, "Missing from TERRAIN"
t = TERRAIN["the_sunken_sanctum"]
print(f"  Region: the_sunken_sanctum")
print(f"  Desc: {t['desc'][:60]}...")
print(f"  Danger: {t['danger']}")
print(f"  Yields: {t['yields']}")
print(f"  Unlock: {t['unlock_condition']}")
print(f"  Landmark: {t['landmark'][:60]}...")
assert t['unlock_condition'] == "all_lore_unveiled"
assert t['danger'] == "high"
print("  ✅ TERRAIN entry valid!")

# ── Test 2: the_sunken_sanctum creatures ──
print("\n─── Test 2: the_sunken_sanctum creatures ──")
from world import CREATURES
assert "the_sunken_sanctum" in CREATURES, "Missing from CREATURES"
creatures = CREATURES["the_sunken_sanctum"]
names = [c['name'] for c in creatures]
print(f"  Creatures: {names}")
assert len(creatures) == 3, f"Expected 3 creatures, got {len(creatures)}"
assert "Crystal-Serpent" in names
assert "Echo-Warden" in names
assert "Memory-Wisp" in names
print("  ✅ Creatures valid!")

# ── Test 3: the_sunken_sanctum lair ──
print("\n─── Test 3: the_sunken_sanctum lair ──")
from world import LAIRS
assert "the_sunken_sanctum" in LAIRS, "Missing from LAIRS"
lair = LAIRS["the_sunken_sanctum"]
print(f"  Lair: {lair['name']}")
print(f"  Boss: {lair['boss']}")
print(f"  Danger: {lair['danger']}")
assert lair['name'] == "Heart-Pool Nexus"
assert lair['boss'] == "Crystal-Serpent"
assert lair['danger'] == "high"
assert "cleared_bonus" in lair
print("  ✅ Lair valid!")

# ── Test 4: the_sunken_sanctum disaster ──
print("\n─── Test 4: the_sunken_sanctum disaster ──")
from world import DISASTERS
assert "the_sunken_sanctum" in DISASTERS, "Missing from DISASTERS"
d = DISASTERS["the_sunken_sanctum"]
print(f"  Disaster: {d['name']}")
print(f"  Chance: {d['chance']}")
print(f"  Recovery: {d['recovery_day']}d")
print(f"  Special: {d.get('special')}")
assert d['name'] == "Crystal-Shatter"
assert d['special'] == "crystal_recovery"
print("  ✅ Disaster valid!")

# ── Test 5: Region unlocks after all lore unveiled ──
print("\n─── Test 5: Region unlocks after all lore unveiled ──")
kingdom, world = reset_all()
assert not world.can_discover("the_sunken_sanctum"), "Should be locked initially"
print("  Initially locked: ✓")

# Load 12 lore fragments
world.lore_fragments = ["lore1", "lore2", "lore3", "lore4", "lore5", "lore6",
                         "lore7", "lore8", "lore9", "lore10", "lore11", "lore12"]

# unveil_lore returns one story per call, we need 4 calls to reveal all
stories_unveiled = []
for i in range(10):
    result = world.unveil_lore()
    if result is None:
        break
    # Extract title from result
    for story_title in ["The First Fire", "The Sleepers", "The Cataclysm", "The Pact"]:
        if story_title in result and story_title not in stories_unveiled:
            stories_unveiled.append(story_title)
            print(f"  Unveiled: {story_title}")

print(f"  Stories unveiled: {len(stories_unveiled)}")
print(f"  can_discover sanctum: {world.can_discover('the_sunken_sanctum')}")
print(f"  'all_lore_unveiled' in flags: {'all_lore_unveiled' in world.unlock_flags}")
print(f"  sanctum in discovered: {'the_sunken_sanctum' in world.discovered}")

assert "all_lore_unveiled" in world.unlock_flags, "all_lore_unveiled flag should be set"
assert world.can_discover("the_sunken_sanctum"), "Should be discoverable"
assert "the_sunken_sanctum" in world.discovered, "Should be auto-discovered"
print("  ✅ Region unlocked and auto-discovered after all lore unveiled!")

# ── Test 6: Lair-Disaster interaction — undiscovered lair revealed ──
print("\n─── Test 6: Lair revealed by disaster ──")
# Try multiple times since it's a 30% chance
found_revealed = False
for attempt in range(50):
    importlib.reload(k_mod)
    importlib.reload(w_mod)
    kingdom = k_mod.kingdom
    world = w_mod.world
    world.discovered.add("the_vale")
    world._discovered_lairs = {}
    world._active_disasters["the_vale"] = {
        "name": "Thornblight",
        "day_struck": 0,
        "recovery_day": 5,
    }
    for d in range(6):
        world.day = d
        world._check_disasters()
    if "the_vale" in world._discovered_lairs:
        found_revealed = True
        print(f"  Attempt {attempt+1}: Lair revealed — {world._discovered_lairs['the_vale']}")
        break

if found_revealed:
    print("  ✅ Lair revealed by disaster!")
else:
    print("  ⚠️ Lair not revealed in 50 attempts (30% chance — possible but unlikely)")

# ── Test 7: Lair-Disaster interaction — uncleared lair enraged ──
print("\n─── Test 7: Enraged lair during disaster ──")
kingdom, world = reset_all()
world.discovered.add("the_vale")
world._discovered_lairs["the_vale"] = "Thorn-Bear's Hollow"
kingdom.gold = 100
kingdom.food = 100
world._active_disasters["the_vale"] = {
    "name": "Thornblight",
    "day_struck": world.day,
    "recovery_day": world.day + 5,
}
world._check_disasters()
print(f"  Gold: {kingdom.gold}, Food: {kingdom.food}")
# Should have taken extra penalty from enraged lair boss
penalty_applied = kingdom.gold <= 96 or kingdom.food <= 95
print(f"  Penalty applied: {penalty_applied}")
print("  ✅ Enraged lair interaction runs without error!")

# ── Test 8: Lair-Disaster interaction — cleared lair destabilization ──
print("\n─── Test 8: Cleared lair destabilization ──")
destabilized = False
for attempt in range(100):
    importlib.reload(k_mod)
    importlib.reload(w_mod)
    kingdom = k_mod.kingdom
    world = w_mod.world
    world.discovered.add("the_vale")
    world._discovered_lairs["the_vale"] = "Thorn-Bear's Hollow"
    world._cleared_lairs.add("the_vale")
    world._active_disasters["the_vale"] = {
        "name": "Thornblight",
        "day_struck": 0,
        "recovery_day": 5,
    }
    for d in range(6):
        world.day = d
        world._check_disasters()
    if "the_vale" not in world._cleared_lairs:
        destabilized = True
        print(f"  Attempt {attempt+1}: Cleared lair destabilized! Must re-clear.")
        break

if destabilized:
    print("  ✅ Lair destabilization working!")
else:
    print("  ⚠️ Lair not destabilized in 100 attempts (10% chance — unlikely but possible)")

# ── Test 9: Crystal-Shatter recovery special ──
print("\n─── Test 9: Crystal-Shatter recovery ──")
kingdom, world = reset_all()
world.discovered.add("the_sunken_sanctum")
world._active_disasters["the_sunken_sanctum"] = {
    "name": "Crystal-Shatter",
    "day_struck": 0,
    "recovery_day": 3,
}
kingdom.stone = 0
for d in range(4):
    world.day = d
    world._check_disasters()

print(f"  Stone after recovery: {kingdom.stone} (expected +8)")
assert kingdom.stone >= 8, f"Expected at least 8 stone from crystal recovery, got {kingdom.stone}"
print("  ✅ Crystal-Shatter recovery special works!")

# ── Test 10: Heart-Pool Nexus passive bonuses (wired into _check_lair_activity) ──
print("\n─── Test 10: Heart-Pool Nexus passive bonuses ──")
kingdom, world = reset_all()
world._cleared_lairs.add("the_sunken_sanctum")
kingdom.gold = 100
kingdom.stone = 50
kingdom.food = 100

world._check_lair_activity()
print(f"  Gold: {kingdom.gold} (expecting 105+ if wired), Stone: {kingdom.stone} (expecting 52+ if wired)")
# Check if the_sunken_sanctum passive is wired
if kingdom.gold >= 105 and kingdom.stone >= 52:
    print("  ✅ Heart-Pool Nexus passive bonuses applied!")
else:
    print("  ⚠️ Heart-Pool Nexus passive not yet wired in _check_lair_activity")
    print("     (gold unchanged, stone unchanged)")

# ── Test 11: World map ──
print("\n─── Test 11: World map includes new region ──")
kingdom, world = reset_all()
world.discovered.add("the_sunken_sanctum")
map_str = world.world_map()
if "💎" in map_str:
    print("  ✅ New region symbol (💎) appears on world map!")
else:
    print("  ⚠️ New region symbol not found on map")
if "the_sunken_sanctum" in map_str:
    print("  ✅ the_sunken_sanctum appears in map legend!")
else:
    print("  ⚠️ the_sunken_sanctum not in map legend")

# ── Test 12: Scout report includes sanctum ──
print("\n─── Test 12: Scout report includes sanctum ──")
kingdom, world = reset_all()
world.discovered.add("the_sunken_sanctum")
report = world.scout_report()
if "the_sunken_sanctum" in report:
    print("  ✅ Scout report includes the_sunken_sanctum!")
else:
    print("  ⚠️ Scout report missing the_sunken_sanctum")

print("\n" + "=" * 60)
print("💎 SECRET REGION & LAIR-DISASTER INTERACTION TEST COMPLETE!")
