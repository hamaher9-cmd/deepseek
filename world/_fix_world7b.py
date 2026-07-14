"""
Additional fixes: world_map positions, scout_report, _check_lair_activity passive for sanctum.
"""
import world as w

with open('world.py', 'r') as f:
    content = f.read()

changes = 0

# ── FIX 1: Add the_sunken_sanctum to world_map positions and symbols ──
if '"the_sunken_sanctum":  (2, 0)' not in content:
    old1 = '''            "the_ashen_copse":  (4, 2),
        }'''
    new1 = '''            "the_ashen_copse":  (4, 2),
            "the_sunken_sanctum": (2, 0),
        }'''
    if old1 in content:
        content = content.replace(old1, new1, 1)
        print("✅ Fix 1a: the_sunken_sanctum added to world_map positions.")
        changes += 1
    else:
        print("⚠️  Fix 1a: Could not find positions end marker.")

if '"the_sunken_sanctum":  "💎"' not in content:
    old1b = '''            "the_ashen_copse":  "🔥",
        }'''
    new1b = '''            "the_ashen_copse":  "🔥",
            "the_sunken_sanctum": "💎",
        }'''
    if old1b in content:
        content = content.replace(old1b, new1b, 1)
        print("✅ Fix 1b: the_sunken_sanctum added to world_map symbols.")
        changes += 1
    else:
        print("⚠️  Fix 1b: Could not find symbols end marker.")

# ── FIX 2: Add the_sunken_sanctum to scout_report region_order ──
if '"the_sunken_sanctum"' not in content.split('scout_report')[1] if 'scout_report' in content else '':
    old2 = '''        region_order = ["the_vale", "old_oak_ridge", "glimmer_marsh",
                        "ironroot_depths", "sunfire_plains", "the_ashen_copse"]'''
    new2 = '''        region_order = ["the_vale", "old_oak_ridge", "glimmer_marsh",
                        "ironroot_depths", "sunfire_plains", "the_ashen_copse",
                        "the_sunken_sanctum"]'''
    if old2 in content:
        content = content.replace(old2, new2, 1)
        print("✅ Fix 2: the_sunken_sanctum added to scout_report region_order.")
        changes += 1
    else:
        print("⚠️  Fix 2: Could not find region_order in scout_report.")
else:
    print("⚠️  Fix 2: the_sunken_sanctum already in scout_report.")

# ── FIX 3: Wire Heart-Pool Nexus passive into _check_lair_activity ──
if 'elif region == "the_sunken_sanctum"' not in content:
    old3 = '''            elif region == "the_ashen_copse":
                kingdom.gold += 3

        return results if results else None


    def _check_creature_specials'''

    new3 = '''            elif region == "the_ashen_copse":
                kingdom.gold += 3
            elif region == "the_sunken_sanctum":
                kingdom.gold += 5
                kingdom.stone += 2

        return results if results else None


    def _check_creature_specials'''

    if old3 in content:
        content = content.replace(old3, new3, 1)
        print("✅ Fix 3: Heart-Pool Nexus passive bonus wired into _check_lair_activity.")
        changes += 1
    else:
        print("⚠️  Fix 3: Could not find lair_activity end marker.")
else:
    print("⚠️  Fix 3: the_sunken_sanctum already in _check_lair_activity.")


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
