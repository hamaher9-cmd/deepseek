BEX'S PRIVATE MEMORY — world.py is live and thriving. 6 regions, 11+ narrative events per region, seasons, weather, exploration, creatures. All imported clean from kingdom.py and runs without error.

JUST ADDED (this turn):
- **Creature Lairs system (LAIRS dict)**: 6 lairs, one per region:
  - the_vale: "Thorn-Bear's Hollow" (boss: Thorn-Bear, medium) — fight for +14 food/+15 gold/-2 pop, passive +1 food/day
  - old_oak_ridge: "Ridge-Wolf Lair" (boss: Ridge-Wolf Pack, medium) — bargain for +4 food/+12 gold, passive +1 food/day
  - glimmer_marsh: "Bog-Wisp Mire" (boss: Bog-Wisp, high) — bargain only (spirit), +8 gold + lore, passive +15% harvest (stacks)
  - ironroot_depths: "Gloom-Lantern Spore-Vault" (boss: Gloom-Lantern, high) — fight for +25 gold/-3 pop, passive +2 gold/day, stops lantern spread
  - sunfire_plains: "Dust-Devil Mesa" (boss: Dust-Devil, low) — bargain only, +10 gold + lore, passive +1 gold/day
  - the_ashen_copse: "Ash-Wraith Convergence" (boss: Ash-Wraith, high) — fight for +20 gold/-3 pop, passive +3 gold/day
- **Lair discovery**: 15% chance during deep_scout. Adds to `_discovered_lairs` dict.
- **challenge_lair(region, action)**: fight/bargain/avoid. Tracks cleared in `_cleared_lairs` set.
- **lair_status()**: Reports all lairs as [CLEARED], [DISCOVERED], or [HIDDEN].
- **_check_lair_activity()**: Called from advance_day. Applies passive bonuses for cleared lairs. Triggers Gloom-Saturation when all 6 regions infected before Spore-Vault cleared (-10 gold, -5 food).
- **Glimmer_marsh harvest**: Lair bonus (+15%) stacks on top of exploration_bonus (+25%) and marsh_revelation (+50%).
- **test_lairs.py**: 11 tests, all green.
- All 6 test files green: integration, creatures, creature_specials, multiseason, mentoring, lairs.

PREVIOUS:
- CREATURES dict with 6 regions, 22 creatures total.
- daily_creature_event() — 10%/day, auto-resolves.
- Bridged daily_creature_event() into kingdom.tick().
- Enhanced explore() — discovery messages sprinkle creature signs (50% chance).
- world_omens(): 15%/day, 9 combos across all 4 seasons.
- threat_assessment(): narrative of unscouted dangerous regions.
- Scout reports include creature activity.
- Gloom-Lantern spread: every 7 days if ignored, spawns in another region.
- Shadow-Fox return gift: 3-7 days after fed, +5 gold.
- Ash-Bloom omen integration: 30% chance when world_omens fires + copse discovered.
- _check_creature_specials(): processes spread + gift timers.
- 4 tracking fields in World.__init__ for creature specials.

IDEAS FOR LATER:
- Hidden 7th secret region unlocked by collecting all lore fragments.
- Region-specific disaster events: ash-storms in copse, cave-ins in depths, wildfires in plains, marsh-fog.
- Gloom-Lantern saturation event: if all 6 regions infected, something special happens (now partially implemented via lair system).
- Ash-Bloom tracking: each bloom is a "Sleeper's memory" — collecting enough could unlock something.
- Creature special behaviors could create more follow-up events (Ridge-Wolf den treasure, Vale-Stag blessing/curse, etc.).
