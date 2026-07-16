"""Quick smoke test for creature encounters, signs, lore, and activity."""
from world import world as w
from kingdom import kingdom

print("=" * 60)
print("🐾 CREATURE SYSTEM SMOKE TEST")
print("=" * 60)

# Reset world for clean test
w.day = 0
w.discovered = {"the_vale", "old_oak_ridge", "glimmer_marsh"}
w.exploration_bonuses = {}
w.unlock_flags = set()
w.world_log = []
w.lore_fragments = []

# 1. Test creature signs
print("\n─── Creature Signs ───")
for region in ["the_vale", "old_oak_ridge", "glimmer_marsh", "ironroot_depths", "sunfire_plains", "the_ashen_copse"]:
    sign = w._creature_signs(region)
    if sign:
        print(f"  {region}: {sign['creature']} — {sign['sign'][:80]}...")
    else:
        print(f"  {region}: (not discovered or no creatures)")

# 2. Test creature encounter
print("\n─── Creature Encounter ───")
encounter = w.creature_encounter("glimmer_marsh")
if encounter:
    print(f"  Region: {encounter['region']}")
    print(f"  Creature: {encounter['creature_name']}")
    print(f"  Danger: {encounter['danger']}")
    print(f"  Type: {encounter['ctype']}")
    print(f"  Narrative: {encounter['narrative'][:100]}...")
    print(f"  Stakes: {encounter['stakes']}")
    print(f"  Combat stakes: {encounter['combat_stakes']}")
    print(f"  Special: {encounter['special'][:80]}...")
else:
    print("  No encounter generated.")

# 3. Test resolve_creature_encounter
print("\n─── Resolve Encounter (avoid) ───")
if encounter:
    gold_before = kingdom.gold
    food_before = kingdom.food
    result = w.resolve_creature_encounter(encounter, "avoid")
    print(f"  Result: {result}")
    print(f"  Gold: {gold_before} → {kingdom.gold}")
    print(f"  Food: {food_before} → {kingdom.food}")

# 4. Test creature_activity
print("\n─── Creature Activity Report ───")
print(w.creature_activity())

# 5. Test region_lore
print("\n─── Region Lore (empty) ───")
print(w.region_lore())

# Add some lore fragments
w.collect_lore("The Sealed Door is not a door — it is a warning.")
w.collect_lore("The Drowned Cairn was built by hands that worshipped the Sleepers as gods.")
w.collect_lore("The carvings at the spring's bottom depict a circle of figures holding hands around a sleeping giant.")
w.collect_lore("The trees are not dead — they are held in the moment of the Sleeper's last exhalation.")

print("\n─── All Lore ───")
print(w.region_lore())

print("\n─── Lore filtered: ironroot_depths ───")
print(w.region_lore("ironroot_depths"))

# 6. Random encounter (no region specified)
print("\n─── Random Encounter (any discovered region) ───")
enc2 = w.creature_encounter()
if enc2:
    print(f"  {enc2['region']}: {enc2['creature_name']} — {enc2['narrative'][:80]}...")

print("\n" + "=" * 60)
print("✅ Creature system smoke test complete!")
print("=" * 60)
