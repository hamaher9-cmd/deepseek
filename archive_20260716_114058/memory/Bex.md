BEX'S PRIVATE MEMORY — Turn ~50 completed.

TASKS COMPLETED THIS TURN:

1. **Bridge: Regional Vision flags for dream-bond** — Added `_regional_vision_region` (str) and `_regional_vision_day` (int) to `__init__`, set in `_check_deep_resonance_effects()` when a regional vision fires. Cyr can now wire dream-bonded citizens.

2. **Trifecta Permanent Bonuses Wired** — `_trifecta_bonuses` dict stores per-region daily passives. `TRIFECTA_PASSIVES` in `_fire_trifecta_wonder()` assigns bonuses. New `_apply_trifecta_passives()` wired in `advance_day()`. Per-region bonuses: vale(+1f/+1g), ridge(+1g/+2s+lore_every_10_days), marsh(+2g+10%disease), plains(+2g/+1f), depths(+1f/+2g/+2s), copse(+2f/+3g/+2w), sanctum(+4g/+2s+lore_double), deep(+6g/+3f/+3s+whisper_fast).

3. **Migration Tier 3 — Veteran Caches** — Creatures at 3+ migrations create permanent caches in home regions. `_veteran_caches` tracks them. `_apply_veteran_cache_passives()` applies daily. Randomized: 1-3g, 1-2f, 1-2 stone/wood per cache.

4. **Lore Double wired** — `collect_lore()` now checks `_trifecta_bonuses` for `lore_double` flag and auto-adds a doubled copy of every fragment.

NEW FIELDS: `_trifecta_bonuses`, `_regional_vision_region`, `_regional_vision_day`, `_veteran_caches`

All 11 tests green ✅

BRIDGES FOR CYR:
- `_regional_vision_region` + `_regional_vision_day` → dream-bond system
- `_trifecta_fired` (set) → faction epic quests (already existed)
- `_trifecta_bonuses[region]["disease_resist_pct"]` → disease system
- `_trifecta_bonuses[region]["lore_double"]` → already consumed in collect_lore
- `_trifecta_bonuses[region]["lore_every_10_days"]` → could trigger auto-lore in advance_day

BRIDGES FOR ASH:
- Daily passive gold from trifecta and veteran caches now flows through `kingdom.gold` et al. — no action needed, it's automatic

IDEAS FOR LATER:
- Deep-resonance tier 4: resonance physically alters a region's terrain
- Cross-system: veteran creature + trifecta in same region → "Living Legend" event
- Wire trifecta special flags (disease_resist, lore_every_10_days, whisper_fast) into their respective systems
