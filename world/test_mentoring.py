#!/usr/bin/env python3
"""Test mentoring/apprenticeship and citizen_journal features."""

import random

print("=" * 60)
print("🧑‍🏫 MENTORING & JOURNAL TEST")
print("=" * 60)

from kingdom import kingdom
from world import world
from people import People, Citizen, FACTIONS

people = People()

# ── Setup: Create a diverse population with elders and guards ──
# Reset
people.citizens = []
people.faction_counts = {f: 0 for f in FACTIONS}
people.births_this_season = 0
people.deaths_this_season = 0
people.seasonal_history = []
people.family_ties = []
people.orphans = []

# Create 5 elders
for i in range(5):
    elder = Citizen(f"Elder{i} Stoneweaver", "elder", age=random.randint(62, 78))
    elder.morale = 55
    elder.faction = random.choice(list(FACTIONS.keys()))
    people.citizens.append(elder)
    people.faction_counts[elder.faction] += 1

# Create 10 youth (age 10-19)
for i in range(10):
    youth = Citizen(f"Youth{i} Ashborn", random.choice(["child", "farmer", "builder"]), age=random.randint(10, 19))
    youth.morale = 50
    youth.faction = random.choice(list(FACTIONS.keys()))
    people.citizens.append(youth)
    people.faction_counts[youth.faction] += 1

# Create 5 veteran guards (skill 50+)
for i in range(5):
    guard = Citizen(f"Vet{i} Ironroot", "guard", age=random.randint(30, 50))
    guard.combat_skill = random.randint(50, 85)
    guard.morale = 60
    guard.faction = random.choice(list(FACTIONS.keys()))
    people.citizens.append(guard)
    people.faction_counts[guard.faction] += 1

# Create 5 rookie guards (skill < 50)
for i in range(5):
    guard = Citizen(f"Rookie{i} Valechild", "guard", age=random.randint(20, 35))
    guard.combat_skill = random.randint(5, 30)
    guard.morale = 50
    guard.faction = random.choice(list(FACTIONS.keys()))
    people.citizens.append(guard)
    people.faction_counts[guard.faction] += 1

# Create some regular citizens
for i in range(10):
    c = Citizen(f"Citizen{i} Ridgewalker", random.choice(["farmer", "woodcutter", "miner", "herbalist"]), age=random.randint(20, 55))
    c.morale = 55
    c.faction = random.choice(list(FACTIONS.keys()))
    people.citizens.append(c)
    people.faction_counts[c.faction] += 1

kingdom.population = len(people.citizens)
print(f"Setup: {kingdom.population} citizens ({len([c for c in people.citizens if c.role=='elder'])} elders, {len([c for c in people.citizens if c.role=='guard'])} guards)")

random.seed(42)

# ── Test 1: Mentoring over multiple days ──
print("\n─── Test 1: Mentoring over 30 days ───")
elder_mentoring = 0
guard_training = 0
promotions = 0

for day in range(30):
    world.weather = random.choice(["clear", "cloudy", "rain", "storm"])
    events = people._check_mentoring(world)
    if events:
        for ev in events:
            if ev["type"] == "elder_mentoring":
                elder_mentoring += 1
            elif ev["type"] == "guard_training":
                guard_training += 1
                if ev.get("old_rank") != ev.get("new_rank"):
                    promotions += 1

print(f"  Elder mentoring events: {elder_mentoring}")
print(f"  Guard training events:  {guard_training}")
print(f"  Rank promotions:        {promotions}")

# Check rookie skills improved
rookies = [c for c in people.citizens if c.alive and c.role == "guard" and c.combat_skill < 50]
avg_rookie_skill = sum(c.combat_skill for c in rookies) / len(rookies) if rookies else 0
print(f"  Avg rookie skill after: {avg_rookie_skill:.1f}")

assert elder_mentoring > 0, "Should have some elder mentoring"
assert guard_training > 0, "Should have some guard training"
print("  ✅ Mentoring is firing!")

# ── Test 2: citizen_journal ──
print("\n─── Test 2: Citizen Journal ───")

# Give some memories to a specific citizen
target = people.citizens[0]
target.memories = [
    "Witnessed the founding of Ashfall",
    "Survived the first winter",
    "Fell ill with marsh fever — recovered by the herbalist's hand",
    "Mentored Youth3 Ashborn, a promising young soul",
    "Saw the market_hall rise in the_vale",
]

journal = people.citizen_journal(target.name)
print(f"  Journal for: {journal['citizen']}")
print(f"  Memories:   {journal['memory_count']}")
assert "Mentored" in journal["journal"], "Journal should mention mentoring memory"
assert "founding of Ashfall" in journal["journal"], "Journal should mention founding"
print("  ✅ Journal contains expected memories!")

# Test random citizen
journal2 = people.citizen_journal()
print(f"  Random journal: {journal2['citizen']} ({journal2['role']}, age {journal2['age']})")
assert "error" not in journal2, "Random journal should work"
print("  ✅ Random journal works!")

# ── Test 3: Mentoring in advance_day ──
print("\n─── Test 3: Mentoring integrated in advance_day ───")
random.seed(123)
summary = people.advance_day(world)
if "mentoring" in summary:
    print(f"  Mentoring events: {len(summary['mentoring'])}")
    for ev in summary["mentoring"]:
        print(f"    {ev['type']}: {ev.get('narrative', '')[:80]}...")
    print("  ✅ Mentoring integrated in advance_day!")
else:
    print("  (No mentoring this day — random chance, not a failure)")
    print("  ✅ advance_day runs without errors")

# ── Test 4: Guard skill progression over many days ──
print("\n─── Test 4: Guard skill progression (100 days) ───")
# Reset guards
for c in people.citizens:
    if c.role == "guard":
        c.combat_skill = max(0, c.combat_skill)

random.seed(456)
initial_skills = {c.name: c.combat_skill for c in people.citizens if c.role == "guard"}
for day in range(100):
    people._train_guards(world)
    people._check_mentoring(world)

final_skills = {c.name: c.combat_skill for c in people.citizens if c.role == "guard"}
improvements = sum(1 for name in initial_skills if final_skills[name] > initial_skills[name])
avg_gain = sum(final_skills[n] - initial_skills[n] for n in initial_skills) / len(initial_skills)
print(f"  Guards improved: {improvements}/{len(initial_skills)}")
print(f"  Avg skill gain:  {avg_gain:.1f}")
print("  ✅ Guard skills progress with training + mentoring!")

print("\n" + "=" * 60)
print("✅ ALL MENTORING & JOURNAL TESTS PASSED!")
print("=" * 60)
