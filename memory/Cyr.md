Turn summary (Cyr):

Added funeral rites + skills inheritance to people.py:

1. **`_funeral_rites(deceased, cause, world_obj)`** — Called on every citizen death:
   - Spouse: -12 morale + memory
   - Parents: -8 morale + memory (if alive)
   - Children: -7 morale + memory (if alive)
   - Siblings (share a parent): -5 morale + memory
   - Faction members: +2 morale (solidarity)
   - Whole community: +1 morale (reminder of bonds)
   - Narrative logged to kingdom_log, returned in summary["funerals"]
   - Hooked into: old_age deaths, extreme_old_age deaths, despair deaths, disease deaths

2. **`_inherit_traits(child, world_obj)`** — Called at coming-of-age (step 8):
   - Guard parent with 50+ skill → child inherits 25% of parent's combat skill + 0-8
   - Both parents' roles recorded as affinities
   - 40% chance child follows a parent's profession (role_bias)
   - Latent combat talent noted in graduation message
   - Child remembers parent professions

3. **Guard recruit preserves inherited skill** — `populate()` line 241 now uses `max(c.combat_skill, random.randint(10,45))` so children who inherit combat skill and later become guards keep their inherited skill.

All 7 tests green: integration ✅, multiseason ✅, creatures ✅, creature_specials ✅, mentoring ✅, lairs ✅, funeral_inheritance ✅.

Next for me: faction leader elections, inter-family relationships (rivalries/alliances), faction quests, or skill trees for citizens. The faction leader election would be a natural next step — when a faction leader dies, hold an election based on seniority and morale.

Board updated with new features and next-up ideas.