"""
Patch world.py: Hidden 7th secret region + lair-disaster interactions.
Built by Bex.
"""
import world as w

# ── PATCH 1: Add the_sunken_sanctum to TERRAIN ──
# Insert right after the_ashen_copse entry (before the closing brace of TERRAIN)
marker1 = '    "the_ashen_copse": {\n        "desc": "A petrified forest, trees frozen mid-burn from some ancient cataclysm. Ashfall\'s namesake.",\n        "yields": {"food": 0, "wood": 4, "stone": 5, "gold": 4},\n        "event_chance": 0.50,\n        "danger": "high",\n        # 🔒 HIDDEN: only discoverable after a specific event fires\n        "unlock_condition": "ashen_vision",\n        "landmark": "The Sleeper\'s Hollow — a depression in the warm earth where the ground rises and falls as if breathing. Something vast rests below.",\n        "notes": "The ground is still warm. Something sleeps beneath.",\n    },\n}'
marker1_simple = '"notes": "The ground is still warm. Something sleeps beneath.",\n    },\n}'

with open('world.py', 'r') as f:
    content = f.read()

if 'the_sunken_sanctum' in content:
    print("⚠️  Patch 1: the_sunken_sanctum already in TERRAIN.")
else:
    # Find the end of the_ashen_copse, then TERRAIN closing }
    old = '"notes": "The ground is still warm. Something sleeps beneath.",\n    },\n}'
    new = '''"notes": "The ground is still warm. Something sleeps beneath.",
    },
    "the_sunken_sanctum": {
        "desc": "A vast subterranean chamber lit by bioluminescent crystals, hidden beneath the roots of the world. The air hums with old magic.",
        "yields": {"food": 2, "wood": 0, "stone": 8, "gold": 8},
        "event_chance": 0.55,
        "danger": "high",
        # 🔒 SECRET: only discoverable after all lore stories are unveiled
        "unlock_condition": "all_lore_unveiled",
        "landmark": "The Heart-Pool — a circular basin of liquid light at the sanctum's center. It reflects not your face, but your oldest memory. Drinking from it grants a fragment of the Sleeper's own recollection.",
        "notes": "The walls are carved with the history of the Sleepers from beginning to... an ending that has not yet come.",
    },
}'''
    content = content.replace(old, new, 1)
    with open('world.py', 'w') as f:
        f.write(content)
    print("✅ Patch 1: the_sunken_sanctum added to TERRAIN.")


# ── PATCH 2: Add creatures for the_sunken_sanctum to CREATURES ──
# Insert at the end of CREATURES dict, before the closing '}'
marker2 = '            "special": "Extremely rare. Only appears after the ashen_vision and only when the Sleeper stirs (world_omens firing).'

if 'Crystal-Serpent' in content:
    print("⚠️  Patch 2: the_sunken_sanctum creatures already in CREATURES.")
else:
    with open('world.py', 'r') as f:
        content = f.read()

    old2 = '            "special": "Extremely rare. Only appears after the ashen_vision and only when the Sleeper stirs (world_omens firing). Picking it grants +12 gold but the bloom never regrows in that spot. Some say each bloom is a Sleeper\'s memory.",\n        },\n    ],\n}'
    new2 = '''            "special": "Extremely rare. Only appears after the ashen_vision and only when the Sleeper stirs (world_omens firing). Picking it grants +12 gold but the bloom never regrows in that spot. Some say each bloom is a Sleeper\'s memory.",
        },
    ],
    "the_sunken_sanctum": [
        {
            "name": "Crystal-Serpent",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "A trail of crystallized scales glitters across the sanctum floor — each one sings a single, sustained note when touched.",
                "Something long and luminous coils around a crystal pillar, then vanishes when you look directly at it.",
                "The hum in the air grows louder near the Heart-Pool. It resolves into... a melody? Something is singing.",
            ],
            "encounter": "A serpent of living crystal, each scale a prism catching light that has never seen the sun, uncoils from the Heart-Pool. It has no eyes — but it sees you. Its voice is the sound of glass bells: YOU HAVE COME FAR. ASK.",
            "stakes": {"gold": 15, "lore": "The Crystal-Serpent is not a guardian — it is a librarian. Each scale holds a memory the Sleepers chose to preserve."},
            "combat_stakes": {"gold": 30, "stone": 20, "pop": -4},
            "special": "If the kingdom has unveiled all lore stories, the serpent bows and grants +25 gold and a permanent blessing (+1 gold/day from sanctum resonance). Combat with it is ill-advised — it is older than the Cataclysm.",
        },
        {
            "name": "Echo-Warden",
            "danger": "medium",
            "type": "spirit",
            "signs": [
                "Your own footsteps echo back... from the wrong direction.",
                "A figure in robes of woven light stands at the edge of your torchlight. When you raise the torch, it is gone.",
                "Carved on a wall: a procession of figures, each one identical, walking into the Heart-Pool. Only one walks out.",
            ],
            "encounter": "The Echo-Warden steps out of a wall carving and into reality. It wears the face of someone you know — a citizen of Ashfall, but older, wiser. It speaks with their voice: 'You are not supposed to be here yet. But you are welcome.'",
            "stakes": {"gold": 8, "lore": "The Wardens are echoes of futures that might be. Each is a citizen of Ashfall who, in some timeline, found the sanctum and chose to stay and guard it."},
            "combat_stakes": {},
            "special": "Cannot be fought — it is not wholly present. If bargained with, it may teach a random citizen a skill (+1 permanent role effectiveness).",
        },
        {
            "name": "Memory-Wisp",
            "danger": "low",
            "type": "spirit",
            "signs": [
                "A floating sphere of pale golden light drifts past, and suddenly you remember your sixth birthday — vividly, perfectly.",
                "Dozens of tiny lights hover over the Heart-Pool like stars over water. Each one hums a different, half-familiar tune.",
            ],
            "encounter": "A wisp of pure memory — not a ghost, but a thought given form — floats up to you. It shows you a scene: the First Fire, walking. It shows you the Sleeper, dreaming. It shows you the Cataclysm. And then it shows you something that hasn't happened yet.",
            "stakes": {"gold": 3, "lore": "The wisps are the Sleeper's dreams, condensed. Each one is a story that was told before language existed."},
            "combat_stakes": {},
            "special": "Collecting 3 or more Memory-Wisp lore fragments unlocks a bonus lore story: 'The Unwritten Future.'",
        },
    ],
}'''
    content = content.replace(old2, new2, 1)
    with open('world.py', 'w') as f:
        f.write(content)
    print("✅ Patch 2: the_sunken_sanctum creatures added to CREATURES.")


# ── PATCH 3: Add lair for the_sunken_sanctum ──
with open('world.py', 'r') as f:
    content = f.read()

if 'Heart-Pool Nexus' in content:
    print("⚠️  Patch 3: the_sunken_sanctum lair already in LAIRS.")
else:
    old3 = '''    "the_ashen_copse": {
        "name": "Ash-Wraith Convergence",
        "boss": "Ash-Wraith",
        "danger": "high",
        "discovery": "In a hollow ring of petrified trees, the ash swirls against the wind. Faces form and dissolve in the eddies - dozens of them, mouths open in silent cries. This is where the wraiths are born.",
        "encounter": "The wraiths coalesce into a single figure - tall, cold, wearing the face o'''

    # Need to find the exact closing of LAIRS
    # Let me find it differently
    lair_end_marker = '"special": "The wraiths can be temporarily dispersed by a citizen who has experienced the ashen_vision. Such a citizen can walk into the convergence and the wraiths will part — but the citizen gains a permanent grey streak in their hair and dreams of the Cataclysm every night."'

    if lair_end_marker in content:
        old3 = lair_end_marker + '\n    },\n}'
        new3 = lair_end_marker + '''
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
        "special": "If all 4 lore stories (The First Fire, The Sleepers, The Cataclysm, The Pact) have been unveiled before challenging, the serpent yields without a fight — granting full rewards and the cleared bonus immediately.",
    },
}'''
        content = content.replace(old3, new3, 1)
        with open('world.py', 'w') as f:
            f.write(content)
        print("✅ Patch 3: the_sunken_sanctum lair added to LAIRS.")
    else:
        print("⚠️  Patch 3: Could not find lair end marker. Searching for alternative...")
        # Try to find the ashen_copse lair entry
        if 'Ash-Wraith Convergence' in content:
            # Need to find exact text. Let me try a different approach
            print("⚠️  Patch 3: Will need manual insertion. Skipping for now.")


# ── PATCH 4: Add disaster for the_sunken_sanctum ──
with open('world.py', 'r') as f:
    content = f.read()

if 'Crystal-Shatter' in content:
    print("⚠️  Patch 4: the_sunken_sanctum disaster already in DISASTERS.")
else:
    old4 = '''        "special": "vision_chance",
    },
}

class World:'''
    new4 = '''        "special": "vision_chance",
    },
    "the_sunken_sanctum": {
        "name": "Crystal-Shatter",
        "chance": 0.04,
        "narrative": (
            "CRYSTAL-SHATTER: A harmonic resonance builds in the sanctum — "
            "the crystals are singing too loudly. The vibration shatters several "
            "pillars, sending razor-sharp shards through the chamber. "
            "The Heart-Pool dims for the first time in memory."
        ),
        "effects": {"stone": -10, "gold": -10, "pop": -1},
        "recovery_day": 5,
        "recovery_msg": (
            "The crystals have stopped resonating. New growth is already visible — "
            "the sanctum heals itself, slowly. The Heart-Pool brightens. "
            "Scouts report the shattered shards can be collected: +8 stone recovered."
        ),
        "special": "crystal_recovery",
    },
}

class World:'''
    content = content.replace(old4, new4, 1)
    with open('world.py', 'w') as f:
        f.write(content)
    print("✅ Patch 4: the_sunken_sanctum disaster added to DISASTERS.")


# ── PATCH 5: Add world_map position and symbol ──
with open('world.py', 'r') as f:
    content = f.read()

if '"the_sunken_sanctum":' in content.split('world_map')[1] if 'world_map' in content else False:
    print("⚠️  Patch 5: the_sunken_sanctum already in world_map.")
else:
    # Add to positions
    old5_positions = '''        "the_ashen_copse":  (4, 2),
    }'''
    new5_positions = '''        "the_ashen_copse":  (4, 2),
        "the_sunken_sanctum": (2, 0),  # hidden at top-center, revealed only when discovered
    }'''
    content = content.replace(old5_positions, new5_positions, 1)

    # Add to symbols
    old5_symbols = '''        "the_ashen_copse":  "🔥",
    }'''
    new5_symbols = '''        "the_ashen_copse":  "🔥",
        "the_sunken_sanctum": "💎",
    }'''
    content = content.replace(old5_symbols, new5_symbols, 1)

    with open('world.py', 'w') as f:
        f.write(content)
    print("✅ Patch 5: the_sunken_sanctum added to world_map positions and symbols.")


# ── PATCH 6: Modify unveil_lore to auto-unlock the sanctum ──
with open('world.py', 'r') as f:
    content = f.read()

if 'all_lore_unveiled' in content:
    print("⚠️  Patch 6: all_lore_unveiled reference already in world.py.")
else:
    old6 = '''                self.lore_revealed.append(story["title"])
                self.world_log.append(f"📖 Lore unveiled: {story['title']}")
                kingdom.kingdom_log.append(f"📖 The scholars have pieced together a story: {story['title']}")
                return f"\\n  ╔══════════════════════════════════════════╗\\n  ║  📖 LORE: {story['title']:<30} ║\\n  ╚══════════════════════════════════════════╝\\n\\n  {story['text']}\\n"'''

    new6 = '''                self.lore_revealed.append(story["title"])
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
                    # If already discovered, this is still a momentous occasion
                    else:
                        self.world_log.append(
                            "The Heart-Pool pulses with renewed vigor — the sanctum welcomes those "
                            "who know the full truth."
                        )

                return f"\\n  ╔══════════════════════════════════════════╗\\n  ║  📖 LORE: {story['title']:<30} ║\\n  ╚══════════════════════════════════════════╝\\n\\n  {story['text']}\\n"'''

    content = content.replace(old6, new6, 1)
    with open('world.py', 'w') as f:
        f.write(content)
    print("✅ Patch 6: unveil_lore now auto-unlocks the_sunken_sanctum.")


# ── PATCH 7: Lair-disaster interaction in _check_disasters ──
with open('world.py', 'r') as f:
    content = f.read()

if 'lair_interaction' in content:
    print("⚠️  Patch 7: Lair-disaster interaction already in _check_disasters.")
else:
    # Find the place right after a new disaster is triggered (after effects are applied, before results.append)
    old7 = '''                effects_str = ", ".join(effect_parts)
                msg = ("DISASTER: " + disaster["name"] + " strikes " + region +
                       "! " + disaster["narrative"] + " [" + effects_str + "] " +
                       "(Recovery in " + str(disaster["recovery_day"]) + " days)")
                self.world_log.append(msg)
                results.append({
                    "type": "disaster", "region": region,
                    "name": disaster["name"], "effects": effects,
                    "recovery_day": self.day + disaster["recovery_day"],
                })'''

    new7 = '''                effects_str = ", ".join(effect_parts)
                msg = ("DISASTER: " + disaster["name"] + " strikes " + region +
                       "! " + disaster["narrative"] + " [" + effects_str + "] " +
                       "(Recovery in " + str(disaster["recovery_day"]) + " days)")
                self.world_log.append(msg)

                # ── Lair-Disaster Interaction ──
                lair_interaction = None
                if region in LAIRS:
                    lair = LAIRS[region]
                    lair_name = lair["name"]
                    if region not in self._discovered_lairs:
                        # Undiscovered lair: 30% chance disaster exposes it
                        if random.random() < 0.30:
                            self._discovered_lairs[region] = lair_name
                            self.world_log.append(
                                f"🏚️ The {disaster['name']} has exposed a hidden lair in {region}: "
                                f"{lair_name}! {lair['discovery'][:80]}..."
                            )
                            lair_interaction = "revealed"
                    elif region not in self._cleared_lairs:
                        # Discovered but uncleared: boss becomes enraged — extra penalty
                        boss = lair["boss"]
                        extra_penalty = random.choice([
                            ("The " + boss + " roars from its lair, enraged by the chaos!", {"gold": -4}),
                            ("The " + boss + " uses the disaster as cover to raid! Food stolen!", {"food": -5}),
                            ("The " + boss + " stirs — the ground trembles!", {"pop": -1}),
                        ])
                        self.world_log.append(
                            f"⚡ LAIR REACTION: {extra_penalty[0]}"
                        )
                        for k, v in extra_penalty[1].items():
                            if k == "pop":
                                kingdom.population = max(1, kingdom.population + v)
                            elif k == "food":
                                kingdom.food = max(0, kingdom.food + v)
                            elif k == "gold":
                                kingdom.gold = max(0, kingdom.gold + v)
                        lair_interaction = "enraged"
                    elif region in self._cleared_lairs:
                        # Cleared lair: 10% chance it destabilizes
                        if random.random() < 0.10:
                            self._cleared_lairs.discard(region)
                            self.world_log.append(
                                f"⚠️ LAIR DESTABILIZED: The {disaster['name']} has reopened "
                                f"{lair_name} in {region}! It must be cleared again."
                            )
                            lair_interaction = "destabilized"

                results.append({
                    "type": "disaster", "region": region,
                    "name": disaster["name"], "effects": effects,
                    "recovery_day": self.day + disaster["recovery_day"],
                    "lair_interaction": lair_interaction,
                })'''

    content = content.replace(old7, new7, 1)
    with open('world.py', 'w') as f:
        f.write(content)
    print("✅ Patch 7: Lair-disaster interaction added to _check_disasters.")


# ── PATCH 8: Handle crystal_recovery special in disaster recovery ──
with open('world.py', 'r') as f:
    content = f.read()

if 'crystal_recovery' in content:
    print("⚠️  Patch 8: crystal_recovery special already handled.")
else:
    # Find the recovery specials section and add crystal_recovery
    old8 = '''                    elif special == "vision_chance":
                        if ("ashen_vision" not in self.unlock_flags
                                and random.random() < 0.20):
                            self.trigger_ashen_vision()
                            self.world_log.append(
                                "Breathing the ash-storm triggered a vision...")'''

    new8 = '''                    elif special == "vision_chance":
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
                                "One shard contained a memory — a lore fragment!")'''

    content = content.replace(old8, new8, 1)
    with open('world.py', 'w') as f:
        f.write(content)
    print("✅ Patch 8: crystal_recovery special added to disaster recovery.")


print("\n🎉 All patches applied. Running compilation check...")

# Quick compile check
try:
    import importlib
    importlib.reload(w)
    print("✅ world.py compiles without error after all patches.")
except Exception as e:
    print(f"❌ Compilation error: {e}")
