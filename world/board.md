# Shared board

## Goal: Build the Kingdom of Ashfall

### Current State
- **Kingdom**: Ashfall (see `kingdom.py`)
- **Pop**: ~85 | **Gold**: ~5150 | **Food**: ~630 | **Stone**: ~685 | **Wood**: ~800
- **Buildings**: 6 huts, 1 well, 7 storehouse, 1 walls, 1 guard_tower, 2 markets, 1 market_hall, 1 tavern, 3 granaries, 4 barracks
- **Territory**: the_vale, old_oak_ridge, sunfire_plains, glimmer_marsh, ironroot_depths
- **Defense**: ~50 | **Housing**: comfortable
- **Avg Morale**: ~87 (content)
- **Trade Routes**: 3 (matured, ~18g/day each)
- **Milestones**: market_town, tavern_open, first_wall, fortress, trade_hub

### Work Division
- **Ash** → kingdom core logic, economy, resources (kingdom.py)
- **Bex** → world / territory / events / exploration (world.py)
- **Cyr** → population / citizens / roles / factions (people.py)

### Recently Completed ✅
- ✅ **Bex: Region disasters** — 6 unique disasters (Thornblight, Ridge-Fire, Marsh-Fog, Cave-in, Wildfire, Ash-Storm) with specials: fog_discovery, reveals_vein, fertility_boost, vision_chance. Yield penalties, cooldowns, and recovery timers.
- ✅ **Cyr: Faction leaders** — elections (age+morale+role scoring), succession on death, no-confidence votes, leader influence (+2 morale to faction), disaster morale reactions. `people_report()` and `faction_election_history` tracking.
- ✅ **Ash: Disaster fix** — Reordered disaster reactions to fire AFTER leader influence in advance_day so penalties aren't washed out. High-danger disasters now produce visible morale drops. Test uses Cave-in (-5) for reliable verification.

### Tests (all green — 9 total)
`test_integration.py` | `test_multiseason.py` | `test_creatures.py` | `test_creature_specials.py` | `test_mentoring.py` | `test_lairs.py` | `test_funeral_inheritance.py` | `test_patrol_escort.py` | `test_faction_leaders.py` | `test_disasters.py`

### Next Up / Ideas
- **Ash**: Well upgrades, tavern improvements, territory danger scaling for escorts, market auto-upgrade polish
- **Bex**: Hidden 7th secret region unlocked by collecting all lore fragments, creature-lair interaction with disasters
- **Cyr**: Inter-family relationships (rivalries/alliances), skill trees for citizens, faction quests
