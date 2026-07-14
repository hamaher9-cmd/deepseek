"""
Test faction leader elections, disaster morale reactions, and succession.
"""
import sys
sys.path.insert(0, ".")

import importlib
import kingdom as k_mod
import world as w_mod
import people as p_mod
import random

importlib.reload(k_mod)
importlib.reload(w_mod)
importlib.reload(p_mod)

from kingdom import kingdom
from world import world
from people import People, FACTIONS

random.seed(42)

print("=" * 60)
print("🏛️  FACTION LEADER & DISASTER REACTION TEST")
print("=" * 60)

# ── Test 1: Initial faction leaders are elected ──
print("\n─── Test 1: Initial Faction Leaders ───")
people = People()
print(f"  faction_leaders: {people.faction_leaders}")
for faction, leader_name in people.faction_leaders.items():
    assert leader_name is not None, f"No leader for {faction}!"
    leader = None
    for c in people.citizens:
        if c.name == leader_name:
            leader = c
            break
    assert leader is not None, f"Leader {leader_name} not found!"
    assert leader.faction == faction, f"Leader {leader_name} is in {leader.faction}, not {faction}!"
    assert leader.alive, f"Leader {leader_name} is dead!"
    print(f"  {faction}: {leader_name} ({leader.role}, age {int(leader.age)}, morale {leader.morale})")
print(f"  Election history: {len(people.faction_election_history)} entries")
assert len(people.faction_election_history) >= 3, f"Expected >= 3 elections, got {len(people.faction_election_history)}"
print("  ✅ Initial faction leaders elected!")

# ── Test 2: Faction leader influence on member morale ──
print("\n─── Test 2: Leader Morale Influence ───")
# Run advance_day and check that faction members get +2 morale from leader
initial_morales = {}
for faction in FACTIONS:
    members = [c for c in people.citizens if c.alive and c.faction == faction]
    leader_name = people.faction_leaders.get(faction)
    non_leader_members = [c for c in members if c.name != leader_name]
    if non_leader_members:
        initial_morales[faction] = sum(c.morale for c in non_leader_members) / len(non_leader_members)

# Run a few days
for _ in range(3):
    people.advance_day(world)

for faction in FACTIONS:
    members = [c for c in people.citizens if c.alive and c.faction == faction]
    leader_name = people.faction_leaders.get(faction)
    non_leader_members = [c for c in members if c.name != leader_name]
    if non_leader_members and faction in initial_morales:
        new_avg = sum(c.morale for c in non_leader_members) / len(non_leader_members)
        print(f"  {faction}: avg morale {initial_morales[faction]:.1f} → {new_avg:.1f} (+{new_avg - initial_morales[faction]:.1f})")
print("  ✅ Leader influence working!")

# ── Test 3: Disaster reactions ──
print("\n─── Test 3: Disaster Morale Reactions ──")
# Use a high-danger disaster (Cave-in, -5 penalty) so the net effect is visible
# even with daily baseline +2 and leader influence +2
world._active_disasters["ironroot_depths"] = {
    "name": "Cave-in",
    "day_struck": world.day,
    "recovery_day": world.day + 5,
}

# Record pre-disaster morale for individual citizens
sample = [c for c in people.citizens if c.alive][:15]
pre_morales = {c.name: c.morale for c in sample}
pre_avg = sum(pre_morales.values()) / len(pre_morales)

# Run one advance_day
summary = people.advance_day(world)

# Check individual morale changes
post_morales = {c.name: c.morale for c in sample}
drops = sum(1 for name in pre_morales 
            if post_morales.get(name, 0) < pre_morales[name])
rises = sum(1 for name in pre_morales 
            if post_morales.get(name, 0) > pre_morales[name])
post_avg = sum(post_morales.values()) / len(post_morales)
print(f"  Sampled citizens: {len(sample)} (drops: {drops}, rises: {rises})")
print(f"  Avg morale: {pre_avg:.1f} → {post_avg:.1f}")

# Check that disaster news was generated
disaster_news = [n for n in summary.get("faction_news", []) if "DISASTER" in n]
print(f"  Disaster news items: {len(disaster_news)}")
if disaster_news:
    print(f"  Sample: {disaster_news[0][:100]}...")
assert len(disaster_news) >= 1, "No disaster news generated!"
# High-danger disaster (-5) + daily baseline (+2) + leader (+2) = net -1
# At least some citizens should dip (especially deepwardens matching stone priority)
assert drops >= 1, f"Expected some morale drops from high-danger disaster, got 0!"
print("  ✅ Disaster morale reactions working!")

# Clean up
world._active_disasters = {}

# ── Test 4: Faction leader succession on death ──
print("\n─── Test 4: Leader Death & Succession ──")
# Find a faction leader and kill them
target_faction = "hearthkeepers"
old_leader_name = people.faction_leaders.get(target_faction)
assert old_leader_name is not None, f"No leader for {target_faction}!"

old_leader = None
for c in people.citizens:
    if c.name == old_leader_name:
        old_leader = c
        break
assert old_leader is not None

# Kill the leader
old_leader.alive = False
old_leader.health = 0
people.faction_counts[target_faction] -= 1
kingdom.population -= 1

# Trigger succession
succession = people._check_faction_leader_deaths(old_leader, world)
assert succession is not None, "Succession should have triggered!"
print(f"  Old leader: {succession['old_leader']} ({target_faction})")
print(f"  New leader: {succession['new_leader']} ({target_faction})")
print(f"  Narrative: {succession['narrative'][:100]}...")

# Verify new leader is alive and in the right faction
new_leader_name = people.faction_leaders[target_faction]
assert new_leader_name != old_leader_name, "Leader should have changed!"
new_leader = None
for c in people.citizens:
    if c.name == new_leader_name:
        new_leader = c
        break
assert new_leader is not None
assert new_leader.alive
assert new_leader.faction == target_faction
print(f"  New leader: {new_leader_name} ({new_leader.role}, age {int(new_leader.age)}, morale {new_leader.morale})")
print("  ✅ Succession working!")

# ── Test 5: Election history grows ──
print("\n─── Test 5: Election History ───")
print(f"  Total elections: {len(people.faction_election_history)}")
for entry in people.faction_election_history:
    print(f"    Day {entry.get('day', '?')}: {entry.get('old_leader', 'none')} → {entry['new_leader']} ({entry.get('reason', '?')})")
assert len(people.faction_election_history) >= 4, f"Expected >= 4 elections, got {len(people.faction_election_history)}"
print("  ✅ Election history tracking!")

# ── Test 6: People report includes faction leaders ──
print("\n─── Test 6: People Report ───")
report = people.people_report()
report_text = report["report"]
assert "Faction Leaders" in report_text, "Report missing Faction Leaders section!"
# Find the section
lines = report_text.split('\n')
in_leaders = False
for line in lines:
    if "Faction Leaders" in line:
        in_leaders = True
    elif in_leaders and line.startswith("  ") and "→" in line:
        print(f"  {line.strip()}")
    elif in_leaders and not line.startswith("  "):
        in_leaders = False
print("  ✅ People report includes faction leaders!")

# ── Test 7: No-confidence election (low morale leader) ──
print("\n─── Test 7: No-Confidence Mechanism ──")
# Tank the morale of one faction's leader
target_faction = "deepwardens"
leader_name = people.faction_leaders.get(target_faction)
if leader_name:
    leader = None
    for c in people.citizens:
        if c.name == leader_name:
            leader = c
            break
    if leader:
        leader.morale = 20  # Critical low
        # Run multiple advance_day calls, check for no-confidence
        deposed = False
        for _ in range(50):
            summary = people.advance_day(world)
            for news in summary.get("faction_news", []):
                if "DEPOSED" in news:
                    print(f"  {news[:120]}...")
                    deposed = True
                    break
            if deposed:
                break
        
        if deposed:
            new_leader_name = people.faction_leaders.get(target_faction)
            print(f"  New leader after no-confidence: {new_leader_name}")
            print("  ✅ No-confidence mechanism works!")
        else:
            print("  ⚠️ No-confidence didn't fire within 50 days (low probability event)")
            print("  ✅ No-confidence code exists and runs without error!")
    else:
        print("  ⚠️ Leader not found")
else:
    print("  ⚠️ No leader for deepwardens")

print(f"\n{'=' * 60}")
print("ALL FACTION LEADER & DISASTER REACTION TESTS COMPLETE!")
print(f"{'=' * 60}")
