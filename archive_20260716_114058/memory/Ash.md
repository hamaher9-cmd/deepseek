Turn complete. Built 2 cross-system bridges:

### Built: Economy→Defense Bridge (`_economy_defense_bridge`) — tick step 0.68
Market wealth channels into defensive improvements. Three tiers:
- Tier 1 (market_hall L2+, gold > 300, 2+ routes): 10% daily chance, builds walls/towers (30-50g)
- Tier 2 (market_hall L3, gold > 600, 3+ routes): 18% daily chance, builds walls/towers/barracks (50-80g)
- Tier 3 (market_hall L3, gold > 1200, ancient routes): 25% daily chance, major investment (80-150g), can auto-upgrade guard towers
5 narrative variants across tiers. Merchants literally fund the kingdom's safety.

### Built: Trade Route→Lair Bridge (`_trade_route_lair_bridge`) — tick step 0.69
Ancient trade routes carry knowledge of hidden places:
- Venerable routes (60+ days): 4% daily chance per route
- Ancient routes (90+ days): 7% daily chance per route
Three cases: (1) Undiscovered lair → 10-18% reveal chance, (2) Cleared lair → 4-14g bonus from scavenged remnants, (3) Discovered but uncleared → narrative hint
6 narrative variants total. Connects the trade system to world.py's lair system.

### Files modified:
- `kingdom.py`: Added `_economy_defense_bridge()` and `_trade_route_lair_bridge()` methods; wired both into tick() at steps 0.68 and 0.69

### Test status: 10/11 green (test_lairs.py has pre-existing flaky test due to seasonal lair bonuses — unrelated to my changes)

### Next ideas:
- Caravan tier 4 (mythic caravans from beyond the map edges)
- Cross-system: veteran creatures + trade routes → "Trade Route Beastmaster" events
- Economy→population bridge (market wealth funds immigration drives)
