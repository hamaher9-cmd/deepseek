Turn 50 summary (Cyr):

Built five features — two bridges + three tier-4 expansions. All 11 tests green ✅.

## 1. Bridge: Regional Vision → Dream-Bond Echoes 🌊👁️
- `_check_dream_bond_regional_vision()` — checks `world._regional_vision_region` and `_regional_vision_day` match today
- Bonded pairs connected to the vision region: +3-5 morale each, 30% chance +5-10g
- Unconnected pairs: 15% chance of lesser bonus (+1-3 morale, +2-5g)
- 25% lore fragment chance. Three narrative variants.
- Wired at step 13.9875.

## 2. Bridge: Trifecta Wonder → Faction Epic Quest 🔗💎🌟
- `_check_trifecta_faction_quest()` — when `world._trifecta_fired` has new entries, spawns epic quest
- Region→faction affinity mapping (vale→Hearthkeepers, ridge→Wildwalkers, depths→Deepwardens, etc.)
- "Honor the Wonder of [region]" quest: 20×scale gold + 8×scale stone target, eternal_legacy bonus, 90-day deadline
- Tracked via `_trifecta_quests_spawned` to prevent duplicates
- Wired at step 13.997.

## 3. Dream-Bond Tier 4: Danger-Sense 🫂⚔️🛡️
- `_check_dream_bond_tier4()` — two effects:
  - **Protector-Civilian Asymmetry**: guard/scout bonded to civilian → civilian +2 morale, 20% chance protector +3 combat_skill, 10% intuition gold (2-6g)
  - **Disaster Resilience**: active disasters → 35% chance per pair of +2 morale each
- Three narrative variants per event type
- Wired at step 13.991.

## 4. Heirloom Tier 4: Faction Relic Ritual 🏺🕯️
- `_check_heirloom_relic_ritual()` — each relic spawns ceremony every 30-50 days
- Rewards: +5-15g (+3 per gen_scale), +3-8f (+gen_scale), +3-5 morale to all faction members
- 30-50% lore chance scaled by relic generation
- Tracked via `_last_ritual_day` per relic entry
- Three narrative variants. Wired at step 13.9895.
- Report shows ritual timer in Faction Relics section.

## 5. Council Tier 4: Alliance Joint Mega-Quest 🤝♾️⚔️
- `_check_alliance_joint_quest()` — permanent allies get shared mega-quest every 40-60 days (15%/day)
- Three templates: Build the Alliance Monument, Host the Grand Alliance Festival, Chart the Alliance Trade Road
- Both factions share one quest object (`_is_joint`, `_joint_factions`). 75-day deadline.
- Both factions get rewards on completion; both suffer on failure.
- Updated `_complete_faction_quest()` to clear both slots and apply morale to both factions' members.
- Wired at step 13.998.

## Updated wiring and report
- Steps reflowed: 13.9875 regional vision, 13.9895 relic ritual, 13.991 dream-bond tier 4, 13.997 trifecta quest, 13.998 joint quest
- Report: Faction Relics section shows ritual timer. Permanent Alliances shows joint quest status.
- Joint quest cleanup handles dual-slot clearing in `_complete_faction_quest()`.

## Files changed
- people.py: All five new methods + wiring in advance_day + report additions + joint quest cleanup in _complete_faction_quest

## Ideas for next time
- faction relic tier 5: relic awakens sentience
- dream-bond tier 5: bonded pair shares a dream-body
- council tier 5: council of all factions — kingdom-wide senate
- bridge: veteran caches + dream-bond -> bonded citizens can tap veteran cache knowledge
