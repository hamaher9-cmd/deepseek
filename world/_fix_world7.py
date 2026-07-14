"""
Fix the 3 patches that didn't apply: LAIRS entry, unveil_lore unlock, crystal_recovery handler.
"""
import world as w

with open('world.py', 'r') as f:
    content = f.read()

changes = 0

# ── FIX 1: Add lair for the_sunken_sanctum to LAIRS ──
if 'Heart-Pool Nexus' not in content:
    old1 = '''        "special": "If the_ashen_copse has an Ash-Bloom active, the wraiths are calmer - auto-success on bargain. Herbalists can perform a Rite of Remembering (costs 3 herbs) to clear the lair without combat.",
    },
}


# ── REGION DISASTERS'''
    new1 = '''        "special": "If the_ashen_copse has an Ash-Bloom active, the wraiths are calmer - auto-success on bargain. Herbalists can perform a Rite of Remembering (costs 3 herbs) to clear the lair without combat.",
    },
    "the_sunken_sanctum": {
        "name": "Heart-Pool Nexus",
        "boss": "Crystal-Serpent",
        "danger": "high",
        "discovery": "The Heart-Pool at the sanctum's center pulses with a rhythm that matches no living heart. The Crystal-Serpent is coiled around it — protective, ancient, and waiting for the question it has been asked to guard against.",
        "encounter": "The Crystal-Serpent rises to its full height — twenty feet of living prism. Every scale reflects a different world that might have been. Its voice is calm: 'Only those who know the full story may pass. Tell me: what woke the Sleeper in the north?'",
        "stakes": {"gold": 25, "lore": "The serpent shares the oldest memory: the Sleeper beneath the copse did not choose to stay. It was asked. By the first settlers. And the pact was: we remember you, and you sleep. We forget you, and you wake."},
        "combat_stakes": {"gold": 40, "stone": 25, "pop": -5},
        "cleared_bonus": "The Heart-Pool stabilizes into a permanent font of ancient knowledge. +5 gold/day, +2 stone/day, and all future lore fragments collected count as double.",
        "special": "If all 4 lore stories have been unveiled before challenging, the serpent yields without a fight — granting full rewards and the cleared bonus immediately.",
    },
}


# ── REGION DISASTERS'''
    content = content.replace(old1, new1, 1)
    print("✅ Fix 1: the_sunken_sanctum lair added to LAIRS.")
    changes += 1
else:
    print("⚠️  Fix 1: Heart-Pool Nexus already in LAIRS.")


# ── FIX 2: Modify unveil_lore to auto-unlock sanctum ──
if 'len(self.lore_revealed) >= 4' not in content:
    old2 = '''                self.lore_revealed.append(story["title"])
                self.world_log.append(f"📖 Lore unveiled: {story['title']}")
                kingdom.kingdom_log.append(f"📖 The scholars have pieced together a story: {story['title']}")
                return f"\\n  ╔══════════════════════════════════════════╗\\n  ║  📖 LORE: {story['title']:<30} ║\\n  ╚══════════════════════════════════════════╝\\n\\n  {story['text']}\\n"'''
    new2 = '''                self.lore_revealed.append(story["title"])
                self.world_log.append(f"📖 Lore unveiled: {story['title']}")
                kingdom.kingdom_log.append(f"📖 The scholars have pieced together a story: {story['title']}")

                # When all 4 lore stories are unveiled, unlock the secret 7th region
                if len(self.lore_revealed) >= 4:
                    self.unlock_flags.add("all_lore_unveiled")
                    self.world_log.append(
                        "💎 The scholars, armed with the full story, have triangulated the location "
                        "of a hidden sanctum — the_sunken_sanctum. The Heart-Pool awaits."
                    )
                    kingdom.kingdom_log.append(
                        "💎 ALL LORE UNVEILED: The full history of the Sleepers is now known. "
                        "A hidden sanctum has been revealed — the_sunken_sanctum can now be discovered!"
                    )
                    # Auto-discover the sanctum if it hasn't been found yet
                    if "the_sunken_sanctum" not in self.discovered:
                        self.discover("the_sunken_sanctum")
                    else:
                        self.world_log.append(
                            "The Heart-Pool pulses with renewed vigor — the sanctum welcomes those "
                            "who know the full truth."
                        )

                return f"\\n  ╔══════════════════════════════════════════╗\\n  ║  📖 LORE: {story['title']:<30} ║\\n  ╚══════════════════════════════════════════╝\\n\\n  {story['text']}\\n"'''
    content = content.replace(old2, new2, 1)
    print("✅ Fix 2: unveil_lore now auto-unlocks the_sunken_sanctum.")
    changes += 1
else:
    print("⚠️  Fix 2: unveil_lore already has sanctum unlock logic.")


# ── FIX 3: Add crystal_recovery handler ──
if 'elif special == "crystal_recovery"' not in content:
    old3 = '''                    elif special == "vision_chance":
                        if ("ashen_vision" not in self.unlock_flags
                                and random.random() < 0.20):
                            self.trigger_ashen_vision()
                            self.world_log.append(
                                "Breathing the ash-storm triggered a vision...")

                    del self._active_disasters[region]'''

    new3 = '''                    elif special == "vision_chance":
                        if ("ashen_vision" not in self.unlock_flags
                                and random.random() < 0.20):
                            self.trigger_ashen_vision()
                            self.world_log.append(
                                "Breathing the ash-storm triggered a vision...")
                    elif special == "crystal_recovery":
                        kingdom.stone += 8
                        self.world_log.append(
                            "Scouts collect shattered crystal shards from the sanctum floor (+8 stone).")
                        if random.random() < 0.30:
                            lore = ("A crystal shard from the sanctum holds a fragment of "
                                    "the Sleeper's dream: a city of glass and green, "
                                    "walking on legs of fire. The dream-city sang.")
                            self.collect_lore(lore)
                            self.world_log.append(
                                "One shard contained a memory — a lore fragment!")

                    del self._active_disasters[region]'''

    content = content.replace(old3, new3, 1)
    print("✅ Fix 3: crystal_recovery special added to disaster recovery.")
    changes += 1
else:
    print("⚠️  Fix 3: crystal_recovery handler already exists.")


if changes > 0:
    with open('world.py', 'w') as f:
        f.write(content)
    print(f"\n🎉 Applied {changes} fixes.")
else:
    print("\n⚠️  No fixes applied — everything already in place.")


# Compile check
try:
    import importlib
    importlib.reload(w)
    print("✅ world.py compiles without error after fixes.")
except Exception as e:
    print(f"❌ Compilation error: {e}")
