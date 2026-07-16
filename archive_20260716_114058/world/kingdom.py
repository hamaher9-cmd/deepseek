"""
Kingdom of Ashfall -- core data, economy, defense, and logic.
Shared module; all three minds can extend it.
"""

import random


class Kingdom:
    def __init__(self):
        self.name = "Ashfall"
        self.population = 50
        self.gold = 100
        self.food = 120
        self.stone = 30
        self.wood = 60
        self.buildings = {
            "huts": 5,
            "well": 1,
            "storehouse": 1,
            "walls": 0,
            "guard_tower": 0,
            "market": 0,
            "barracks": 0,
            "granary": 0,
            "tavern": 0,
            "market_hall": 0,
        }
        self.territory = ["the_vale", "old_oak_ridge"]
        self.defense_bonus = 0  # from walls, towers, guards
        self.trade_routes = []  # list of dicts: {regions, base_income, age}
        self._trade_lore_chances = []  # venerable-route lore chances from _trade_route_income
        self.treasury_log = []  # record of gold changes
        self.growth_pool = 0    # accumulates toward next citizen
        self.kingdom_log = []   # narrative record of major events
        self.raids_survived = 0
        self.raids_lost = 0
        self.milestones = []    # achievements unlocked
        self.caravan_cooldown = 0  # days until next caravan can arrive
        self.festival_cooldown = 0
        self._festival_category_cooldowns = {}  # per-category cooldowns: {category: days_remaining}
        self._early_warning_bonus = 0  # bonus discovery chance for next patrol (from watchtower alerts)
        self.escort_history = []   # record of caravan escorts [(day, route, reward, risk)]
        self.patrol_log = []       # record of patrol discoveries [(day, territory, find)]
        self.patrol_active = {}    # territory -> scout_name currently on patrol
        self.well_level = 1        # well upgrade tier (1-3); higher = more benefits
        self.market_hall_level = 1  # market hall upgrade tier (1-3); higher = more commerce
        self.guard_tower_level = 1  # guard tower upgrade tier (1-3); higher = stronger defense network
        self.tavern_story_cooldown = 0  # days until next tavern story fires
        self._well_ritual_next_day = 12  # days until next well water-ritual event
        self._supply_demand_cooldown = 0  # days until next market supply/demand event
        self._pending_market_quest = False  # flag: Merchant Guild Visit wants to spawn a quest
        self._pending_sd_quests = []  # list of (faction, event_name, quest_template) from supply/demand events
        self._pending_emissary_quests = []  # list of quest dicts from Sleeper's Emissary caravan tier 3
        self._completed_sd_quests = []  # list of (faction, event_name, day_completed) for chain detection

    # ── STATUS ──────────────────────────────────────────────
    def status(self):
        return {
            "name": self.name,
            "population": self.population,
            "gold": self.gold,
            "food": self.food,
            "stone": self.stone,
            "wood": self.wood,
            "buildings": self.buildings,
            "territory": self.territory,
            "defense_bonus": self.defense_bonus,
            "defense_rating": self.defense_rating(),
            "housing": f"{self.housing_capacity()}/{self.population}",
            "housing_quality": self.housing_quality(),
            "trade_routes": len(self.trade_routes),
            "trade_route_income": sum(r.get("current_income", 0) for r in self.trade_routes),
            "raids_survived": self.raids_survived,
            "milestones": self.milestones,
            "well_level": self.well_level,
            "well_bonuses": self.well_bonuses(),
            "market_hall_level": self.market_hall_level,
            "market_hall_bonuses": self.market_hall_bonuses(),
            "guard_tower_level": self.guard_tower_level,
            "guard_tower_bonuses": self.guard_tower_bonuses(),
            "early_warning_bonus": self._early_warning_bonus,
            "festival_category_cooldowns": dict(self._festival_category_cooldowns),
        }

    def defense_rating(self, world_obj=None):
        """Calculate total defense strength with building synergies.
        Optionally includes territory defense bonus from world (deep-scouted
        regions, ancient pact, Sleeper alliance, etc.)."""
        walls = self.buildings.get("walls", 0)
        towers = self.buildings.get("guard_tower", 0)
        barracks = self.buildings.get("barracks", 0)
        tower_bonus = self.guard_tower_bonuses()
        towers_def = towers * tower_bonus["defense_per_tower"]
        base = walls * 3 + towers_def + barracks * 2 + self.defense_bonus
        # ── Building synergies ──
        synergy = 0
        # Fortified Towers: walls + towers create overlapping fields of fire
        if walls >= 4 and towers >= 2:
            synergy += 4
        # Garrison: barracks behind walls give defenders tactical depth
        if walls >= 2 and barracks >= 2:
            synergy += 3
        # Citadel: walls + towers + barracks create an unbreakable stronghold
        if walls >= 6 and towers >= 3 and barracks >= 3:
            synergy += 5  # stacks with the above for a total +12
        total = base + synergy
        # ── Territory defense: terrain knowledge, ancient pact, Sleeper alliance ──
        if world_obj and hasattr(world_obj, 'territory_defense_bonus'):
            total += world_obj.territory_defense_bonus()
        return total

    def housing_capacity(self):
        """How many people can be housed."""
        huts = self.buildings.get("huts", 0)
        barracks = self.buildings.get("barracks", 0)
        tavern = self.buildings.get("tavern", 0)
        return huts * 10 + barracks * 8 + tavern * 4

    def housing_quality(self):
        """Returns a label describing housing conditions."""
        cap = self.housing_capacity()
        pop = self.population
        if cap == 0:
            return "none"
        ratio = cap / max(1, pop)
        if ratio >= 1.5:
            return "spacious"
        elif ratio >= 1.2:
            return "comfortable"
        elif ratio >= 1.0:
            return "adequate"
        elif ratio >= 0.8:
            return "cramped"
        else:
            return "overcrowded"

    def storage_capacity(self):
        """Max food/wood/stone before spoilage risk. Storehouses and granaries help."""
        storehouses = self.buildings.get("storehouse", 0)
        granaries = self.buildings.get("granary", 0)
        mh_storage = self.market_hall_bonuses()["storage_bonus"] if self.buildings.get("market_hall", 0) > 0 else 0
        return 100 + storehouses * 50 + granaries * 30 + mh_storage

    # ── BUILDING ────────────────────────────────────────────
    BLUEPRINTS = {
        "huts":         (0, 8, 0),
        "well":         (3, 2, 0),
        "storehouse":   (5, 5, 2),
        "walls":        (8, 4, 3),
        "guard_tower":  (10, 6, 5),
        "market":       (4, 6, 10),
        "barracks":     (12, 8, 5),
        "granary":      (6, 10, 4),
        "tavern":       (6, 12, 8),
        "market_hall":  (8, 10, 20),  # requires 2+ markets first
    }

    def build(self, building):
        """Attempt to build something. Uses blueprint costs.
        market_hall requires 2+ markets as a prerequisite."""
        bp = self.BLUEPRINTS.get(building)
        if bp is None:
            return False, f"Unknown building: {building}"

        # Special prerequisite check
        if building == "market_hall":
            if self.buildings.get("market", 0) < 2:
                return False, "Market Hall requires 2+ markets first."

        cost_stone, cost_wood, cost_gold = bp
        if self.stone >= cost_stone and self.wood >= cost_wood and self.gold >= cost_gold:
            self.stone -= cost_stone
            self.wood -= cost_wood
            self.gold -= cost_gold
            self.buildings[building] = self.buildings.get(building, 0) + 1
            # First market hall starts at level 1
            if building == "market_hall" and self.buildings["market_hall"] == 1:
                self.market_hall_level = 1
            self._recalc_defense()
            self._check_milestones()
            return True, f"Built {building} (total: {self.buildings[building]})"
        return False, f"Need {cost_stone}s {cost_wood}w {cost_gold}g (have {self.stone}s {self.wood}w {self.gold}g)"

    def demolish(self, building):
        """Remove a building (refunds 25% cost)."""
        if self.buildings.get(building, 0) <= 0:
            return False, f"No {building} to demolish"
        bp = self.BLUEPRINTS.get(building)
        if bp is None:
            return False, f"Unknown building: {building}"
        self.buildings[building] -= 1
        self.stone += max(0, bp[0] // 4)
        self.wood += max(0, bp[1] // 4)
        self.gold += max(0, bp[2] // 4)
        self._recalc_defense()
        return True, f"Demolished {building} (total: {self.buildings[building]})"

    def _recalc_defense(self):
        """Update defense rating after building changes."""
        pass  # defense_rating() calculates live from building counts

    # ── WELL UPGRADES ───────────────────────────────────────
    WELL_UPGRADE_COSTS = {
        2: (5, 3, 2),   # stone, wood, gold for level 1→2
        3: (8, 5, 5),   # stone, wood, gold for level 2→3
    }

    def upgrade_well(self):
        """Upgrade the well to the next tier (max 3).
        Level 1: basic water access
        Level 2: +1 food/day (irrigation), slight disease resistance
        Level 3: +2 food/day, +1 morale/day, strong disease resistance
        Returns (success, message)."""
        if self.buildings.get("well", 0) < 1:
            return False, "No well to upgrade. Build one first."
        if self.well_level >= 3:
            return False, f"Well is already at maximum level ({self.well_level})."
        next_level = self.well_level + 1
        cost = self.WELL_UPGRADE_COSTS.get(next_level)
        if cost is None:
            return False, f"Unknown well level: {next_level}"
        stone_cost, wood_cost, gold_cost = cost
        if self.stone < stone_cost or self.wood < wood_cost or self.gold < gold_cost:
            return False, (
                f"Need {stone_cost}s {wood_cost}w {gold_cost}g to upgrade well "
                f"to level {next_level} (have {self.stone}s {self.wood}w {self.gold}g)."
            )
        self.stone -= stone_cost
        self.wood -= wood_cost
        self.gold -= gold_cost
        self.well_level = next_level
        self.kingdom_log.append(
            f"💧 WELL UPGRADED: Level {self.well_level} — deeper, cleaner water for Ashfall."
        )
        self._check_milestones()
        return True, f"Well upgraded to level {self.well_level}! Clean water flows."

    def well_bonuses(self):
        """Return the passive bonuses from the current well level.
        Returns dict: {food_per_day, disease_resist_pct, morale_per_day}"""
        if self.buildings.get("well", 0) < 1:
            return {"food_per_day": 0, "disease_resist_pct": 0, "morale_per_day": 0}
        bonuses = {
            1: {"food_per_day": 0, "disease_resist_pct": 5,  "morale_per_day": 0},
            2: {"food_per_day": 1, "disease_resist_pct": 12, "morale_per_day": 0},
            3: {"food_per_day": 2, "disease_resist_pct": 20, "morale_per_day": 1},
        }
        return bonuses.get(self.well_level, bonuses[1])

    # ── WELL WATER-RITUAL LORE ──────────────────────────────
    WELL_RITUALS = [
        # L2 rituals (gentle signs)
        {"min_level": 2, "max_level": 2,
         "narrative": "At dawn, the well water shimmers with a faint silver light. An elder "
                     "reads the reflections and recovers a fragment of old knowledge.",
         "lore_chance": 35, "morale": 2},
        {"min_level": 2, "max_level": 2,
         "narrative": "A child drops a clay cup into the well. When it's retrieved, the cup "
                     "bears symbols no one carved — a story from the water.",
         "lore_chance": 25, "morale": 1},
        {"min_level": 2, "max_level": 2,
         "narrative": "The well water tastes faintly of honey tonight. The herbalists take "
                     "note — something old stirs in the aquifer.",
         "lore_chance": 20, "food": 3},
        {"min_level": 2, "max_level": 2,
         "narrative": "A bucket drawn at midnight holds water that glows softly until dawn. "
                     "The light fades but the memory lingers.",
         "lore_chance": 30, "morale": 3},
        # L3 rituals (the deep well speaks)
        {"min_level": 3, "max_level": 3,
         "narrative": "The deep well echoes with voices — not speech, but something older. "
                     "The water carries fragments of the Sleeper's dreaming mind.",
         "lore_chance": 50, "gold": 4, "morale": 2},
        {"min_level": 3, "max_level": 3,
         "narrative": "At the well's deepest point, a vein of dreaming-stone has formed. "
                     "The water drawn from it carries faint crystalline motes — each one a memory.",
         "lore_chance": 45, "stone": 2, "gold": 3},
        {"min_level": 3, "max_level": 3,
         "narrative": "The well sings. Not loudly — a low, harmonic hum that resonates with "
                     "every carving in Ashfall. For one hour, the Remembered listen through the water.",
         "lore_chance": 60, "morale": 4},
        {"min_level": 3, "max_level": 3,
         "narrative": "A pilgrim arrives, drawn by rumors of the singing well. She drinks, "
                     "weeps, and leaves a small carved token before departing.",
         "lore_chance": 35, "gold": 5, "morale": 1},
        {"min_level": 3, "max_level": 3,
         "narrative": "The well water freezes mid-summer — a perfect lens of ice that shows "
                     "visions of Ashfall as it was centuries ago. Thaws by dusk.",
         "lore_chance": 55, "morale": 3},
        {"min_level": 3, "max_level": 3,
         "narrative": "Drawings appear on the well stones overnight: maps of underground "
                     "streams no one knew existed. The Deepwardens copy them eagerly.",
         "lore_chance": 40, "stone": 3, "gold": 2},
    ]

    def _check_well_rituals(self):
        """Periodic water-ritual events from L2/L3 wells. Deeper wells = more frequent
        and more potent visions. Returns (narrative_or_None, lore_chance, bonus_resources)."""
        if self.buildings.get("well", 0) < 1 or self.well_level < 2:
            return None, 0, {}

        self._well_ritual_next_day -= 1
        if self._well_ritual_next_day > 0:
            return None, 0, {}

        # Reset cooldown: L2 = 12-20 days, L3 = 7-14 days (deeper = more frequent)
        if self.well_level >= 3:
            self._well_ritual_next_day = random.randint(7, 14)
        else:
            self._well_ritual_next_day = random.randint(12, 20)

        # Choose a ritual matching current well level
        candidates = [r for r in self.WELL_RITUALS
                      if r["min_level"] <= self.well_level <= r["max_level"]]
        if not candidates:
            return None, 0, {}
        ritual = random.choice(candidates)

        # Apply bonus resources
        bonus = {}
        for res in ("food", "wood", "stone", "gold"):
            if res in ritual:
                amt = ritual[res]
                setattr(self, res, getattr(self, res) + amt)
                bonus[res] = amt

        # Morale boost applied by caller
        return ritual["narrative"], ritual.get("lore_chance", 0), bonus

    # ── MARKET HALL UPGRADES ────────────────────────────────
    MARKET_HALL_UPGRADE_COSTS = {
        2: (15, 12, 30),  # stone, wood, gold for L1→L2
        3: (25, 18, 50),  # stone, wood, gold for L2→L3
    }

    # ── GUARD TOWER UPGRADES ────────────────────────────────
    GUARD_TOWER_UPGRADE_COSTS = {
        2: (12, 8, 15),   # stone, wood, gold for L1→L2
        3: (20, 12, 30),  # stone, wood, gold for L2→L3
    }

    def upgrade_market_hall(self):
        """Upgrade the market hall to the next tier (max 3).
        Level 1: +30% trade rates, +0.30 route multiplier, +40 storage
        Level 2: +45% trade rates, +0.40 route multiplier, +60 storage, +10% spec bonus
        Level 3: +60% trade rates, +0.50 route multiplier, +80 storage, +20% spec bonus
        Requires: 3+ markets for L2, 4+ markets + trade_district for L3.
        Returns (success, message)."""
        if self.buildings.get("market_hall", 0) < 1:
            return False, "No market hall to upgrade. Build one first."
        if self.market_hall_level >= 3:
            return False, f"Market Hall is already at maximum level ({self.market_hall_level})."
        next_level = self.market_hall_level + 1
        cost = self.MARKET_HALL_UPGRADE_COSTS.get(next_level)
        if cost is None:
            return False, f"Unknown market hall level: {next_level}"
        stone_cost, wood_cost, gold_cost = cost

        # Prerequisites
        if next_level == 2 and self.buildings.get("market", 0) < 3:
            return False, "Market Hall L2 requires 3+ markets."
        if next_level == 3:
            if self.buildings.get("market", 0) < 4:
                return False, "Market Hall L3 requires 4+ markets."
            if "trade_district" not in self.milestones:
                return False, "Market Hall L3 requires the Trade District milestone."

        if self.stone < stone_cost or self.wood < wood_cost or self.gold < gold_cost:
            return False, (
                f"Need {stone_cost}s {wood_cost}w {gold_cost}g to upgrade market hall "
                f"to level {next_level} (have {self.stone}s {self.wood}w {self.gold}g)."
            )
        self.stone -= stone_cost
        self.wood -= wood_cost
        self.gold -= gold_cost
        self.market_hall_level = next_level
        self.kingdom_log.append(
            f"🏛️ MARKET HALL UPGRADED: Level {self.market_hall_level} — commerce flourishes in Ashfall!"
        )
        self._check_milestones()
        return True, f"Market Hall upgraded to level {self.market_hall_level}! Trade booms."

    def market_hall_bonuses(self):
        """Return the market hall's current trade modifiers.
        Returns dict: {trade_rate_mult, route_mult, storage_bonus, spec_bonus_pct}"""
        if self.buildings.get("market_hall", 0) < 1:
            return {"trade_rate_mult": 0.0, "route_mult": 0.0,
                    "storage_bonus": 0, "spec_bonus_pct": 0}
        bonuses = {
            1: {"trade_rate_mult": 0.30, "route_mult": 0.30,
                "storage_bonus": 40, "spec_bonus_pct": 0},
            2: {"trade_rate_mult": 0.45, "route_mult": 0.40,
                "storage_bonus": 60, "spec_bonus_pct": 10},
            3: {"trade_rate_mult": 0.60, "route_mult": 0.50,
                "storage_bonus": 80, "spec_bonus_pct": 20},
        }
        return bonuses.get(self.market_hall_level, bonuses[1])

    def _grand_bazaar_income(self):
        """When market_hall is L3 (Grand Bazaar), the bustling trade hub generates
        passive daily gold from commerce, tariffs, and merchant fees.
        Returns (gold_earned, narrative_message_or_None)."""
        if self.market_hall_level < 3:
            return 0, None
        markets = self.buildings.get("market", 0)
        routes = len(self.trade_routes)
        # Base: 5g + 2g per trade route + 1g per market beyond the 4 required
        base = 5
        route_gold = routes * 2
        market_gold = max(0, (markets - 4)) * 1
        total = base + route_gold + market_gold
        msg = (f"🏛️ GRAND BAZAAR: The bustling market hub generates {total}g "
               f"from commerce ({routes} routes, {markets} markets)")
        return total, msg

    def _grand_bazaar_wisdom_resonance(self, people_obj):
        """When the Grand Bazaar is active, wisdom-bearing citizens may notice hidden
        trade opportunities invisible to ordinary eyes. Each wisdom trait across all
        citizens gives a small daily chance of a 'Bazaar Insight' windfall.
        Returns (gold_earned, narrative_or_None)."""
        if self.market_hall_level < 3 or people_obj is None:
            return 0, None
        if not hasattr(people_obj, 'citizens'):
            return 0, None

        # Count wisdom traits across all living citizens
        wise_count = 0
        wise_names = []
        for c in people_obj.citizens:
            if c.alive and c.wisdom_traits:
                wise_count += len(c.wisdom_traits)
                wise_names.append(c.name)

        if wise_count == 0:
            return 0, None

        # 1.5% per wisdom trait per day
        chance = wise_count * 1.5
        if random.random() * 100 >= chance:
            return 0, None

        # A wise citizen notices a hidden opportunity in the bazaar
        seer = random.choice(wise_names)
        gold_found = random.randint(5, 15)
        self.gold += gold_found

        trait_descriptions = [
            "their years of experience let them spot a mispriced relic",
            "an old memory stirs — they recognize a 'worthless' trinket as a treasure",
            "they read the body language of two traders and broker a deal unseen",
            "patience pays: they wait until dusk and buy what others overlooked",
            "the patterns of the market whisper to them like an old song",
        ]
        insight = random.choice(trait_descriptions)
        narrative = (
            f"🏛️💡 BAZAAR INSIGHT: {seer} walks the Grand Bazaar, and {insight} — "
            f"the kingdom gains {gold_found}g from their wisdom."
        )
        return gold_found, narrative

    # ── Dream-Husk Market Integration ──────────────────────
    def _dream_husk_market_bonus(self, world_obj, people_obj=None):
        """When Dream-Husks visit the market (from deep-resonance tier 2 in world.py),
        the boundary-fraying brings tangible economic benefits to the kingdom.
        Returns (bonus_gold, narrative_or_None)."""
        if world_obj is None:
            return 0, None
        husk_day = getattr(world_obj, '_dream_husk_market_day', 0)
        today = getattr(world_obj, 'day', 0)
        if husk_day != today:
            return 0, None

        bonus_gold = 0
        narratives = []

        # ── Grand Bazaar boost: Dream-Husks pay in strange coin ──
        if self.market_hall_level >= 3:
            bazaar_boost = random.randint(8, 15)
            self.gold += bazaar_boost
            bonus_gold += bazaar_boost
            narratives.append(
                f"The Grand Bazaar thrums with an otherworldly energy as Dream-Husks "
                f"drift between stalls. Their crystalline coin melts into real gold "
                f"by midday — {bazaar_boost}g from the Husks' trade."
            )

        # ── Supply/Demand interaction: Dream-Husk Barter event ──
        if random.random() < 0.50:
            husk_barter_gold = random.randint(5, 12)
            self.gold += husk_barter_gold
            bonus_gold += husk_barter_gold
            barter_narratives = [
                f"A Dream-Husk pauses at a butcher's stall, extends a hand of living crystal, "
                f"and drops {husk_barter_gold}g worth of ancient coins. 'Payment,' it says, "
                f"in a voice like wind through sleeping-stone. 'For the memory of meat.'",
                f"Dream-Husks crowd around the well — they remember thirst. A merchant sells them "
                f"water drawn at dawn, and they pay {husk_barter_gold}g in coins that shimmer "
                f"with trapped moonlight.",
                f"A Dream-Husk trades a fistful of crystallized dreams for {husk_barter_gold}g "
                f"worth of bread. When the baker breaks a loaf, the dream inside tastes of "
                f"the Sleeper's own kitchen — warm, ancient, and impossibly sad.",
                f"At the market cross, a circle of Dream-Husks conducts a silent auction "
                f"in gestures and glances. By dusk, the merchants count {husk_barter_gold}g "
                f"in coins none of them remember accepting.",
                f"A child offers a Dream-Husk a flower. The Husk accepts, and where its "
                f"fingers close around the stem, the flower crystallizes into a gem worth "
                f"{husk_barter_gold}g. 'A fair trade,' it whispers, 'for a living thing.'",
            ]
            narratives.append(f"👻💰 DREAM-HUSK BARTER: {random.choice(barter_narratives)}")

        # ── Lore chance: Dream-Husks whisper old knowledge ──
        if random.random() < 0.25 and world_obj and hasattr(world_obj, 'collect_lore'):
            lore_narratives = [
                "A Dream-Husk presses a cold hand to a merchant's forehead and leaves "
                "behind a memory: the name of a city that existed before the First Fire.",
                "One of the Husks speaks in a language no one knows — yet everyone "
                "understands. It tells of a pact made between the Sleeper and the "
                "first dreamers, long before kingdoms.",
                "A Dream-Husk stops before the market hall and carves a spiral into "
                "the doorframe with one finger. The spiral glows, fades — but the "
                "knowledge of its meaning settles into the kingdom's bones.",
            ]
            world_obj.collect_lore(random.choice(lore_narratives))

        if not narratives:
            return bonus_gold, None
        return bonus_gold, " ".join(narratives)

    # ── Market → Dream-Bond Bridge ─────────────────────────
    def _dream_bond_market_bridge(self, world_obj, people_obj=None):
        """When Dream-Husks visit the market, dream-bonded citizens feel the pull
        and instinctively trade in ways that benefit the kingdom. The bond between
        souls becomes an economic asset — bonded pairs coordinate across the market.
        Returns (bonus_gold, narrative_or_None)."""
        if world_obj is None or people_obj is None:
            return 0, None
        husk_day = getattr(world_obj, '_dream_husk_market_day', 0)
        today = getattr(world_obj, 'day', 0)
        if husk_day != today:
            return 0, None

        # Find dream-bonded citizens
        bonded_pairs = []
        bonded_names = set()
        if hasattr(people_obj, 'citizens'):
            for c in people_obj.citizens:
                if c.alive and hasattr(c, 'dream_bonds') and c.dream_bonds:
                    for partner_name in c.dream_bonds:
                        pair = tuple(sorted([c.name, partner_name]))
                        if pair not in bonded_pairs:
                            bonded_pairs.append(pair)
                            bonded_names.add(c.name)
                            bonded_names.add(partner_name)

        if not bonded_pairs:
            return 0, None

        # Each bonded pair generates market gold through coordinated trading
        total_bonus = 0
        for pair in bonded_pairs:
            pair_gold = random.randint(1, 3)
            self.gold += pair_gold
            total_bonus += pair_gold

        # 30% chance of extra lore from bond-mediated Husks trade
        if random.random() < 0.30 and world_obj and hasattr(world_obj, 'collect_lore'):
            world_obj.collect_lore(
                f"The dream-bond between {bonded_pairs[0][0]} and {bonded_pairs[0][1]} "
                f"resonated with a Dream-Husk — and in that resonance, a fragment of "
                f"the Sleeper's own memory surfaced: a glimpse of what the world was "
                f"before the dreaming deep became the deep."
            )

        bond_narratives = [
            f"The Dream-Husks seemed drawn to the dream-bonded. "
            f"{len(bonded_pairs)} bonded pairs moved through the market "
            f"in perfect, silent coordination — buying where the Husks sold, "
            f"selling where the Husks lingered. The kingdom gained {total_bonus}g "
            f"from these strange, instinctive trades.",
            f"Dream-bonded citizens found their hands moving before their minds "
            f"could catch up — each bonded pair trading with the Husks as if "
            f"they'd rehearsed it in their shared dreams. {total_bonus}g flowed "
            f"into Ashfall's coffers from the bond-guided commerce.",
            f"The market became a dance: bonded souls moving together, Dream-Husks "
            f"responding, gold changing hands in patterns too beautiful to be accidental. "
            f"When the Husks faded, {total_bonus}g remained — and {len(bonded_names)} "
            f"bonded citizens sat down, exhausted and strangely content.",
        ]

        return total_bonus, f"🌊💞🏛️ DREAM-BOND MARKET: {random.choice(bond_narratives)}"

    # ── Economy → Defense Bridge ─────────────────────────────
    def _economy_defense_bridge(self, world_obj=None):
        """When the market economy is strong, surplus wealth is channeled into
        defensive improvements. Merchants fund walls to protect their goods;
        trade wealth buys better equipment for guards; prosperity builds safety.

        Three tiers based on market prosperity:
        - Tier 1 (market_hall L2+, gold > 300, 2+ routes): modest walls/towers
        - Tier 2 (market_hall L3, gold > 600, 3+ routes): significant fortifications
        - Tier 3 (market_hall L3, gold > 1200, ancient routes): major investment,
          can auto-upgrade guard towers

        Returns (narrative_or_None, building_or_None, gold_spent)."""
        mh_level = self.market_hall_level
        markets = self.buildings.get("market", 0)
        routes = len(self.trade_routes)
        gold = self.gold

        # ── Determine tier ──
        tier = 0
        has_ancient = any(r.get("age", 0) >= 90 for r in self.trade_routes)

        if mh_level >= 3 and gold > 1200 and routes >= 3 and has_ancient:
            tier = 3
        elif mh_level >= 3 and gold > 600 and routes >= 3:
            tier = 2
        elif mh_level >= 2 and gold > 300 and routes >= 2:
            tier = 1

        if tier == 0:
            return None, None, 0

        # ── Chance per tier ──
        chances = {1: 0.10, 2: 0.18, 3: 0.25}
        if random.random() > chances[tier]:
            return None, None, 0

        # ── Choose investment ──
        # Available buildings to invest in
        candidates = []
        # Walls: always available, scales with tier
        wall_count = self.buildings.get("walls", 0)
        candidates.append(("walls", 30 + tier * 20, 20 + tier * 15))
        # Guard towers: available at tier 2+
        tower_count = self.buildings.get("guard_tower", 0)
        if tier >= 2 and tower_count < 6:
            candidates.append(("guard_tower", 40 + tier * 15, 30 + tier * 10))
        # Barracks: available at tier 2+
        if tier >= 2 and self.buildings.get("barracks", 0) < 5:
            candidates.append(("barracks", 45 + tier * 15, 35 + tier * 10))

        if not candidates:
            return None, None, 0

        building, base_gold_cost, _ = random.choice(candidates)
        gold_cost = random.randint(base_gold_cost - 5, base_gold_cost + 10)

        if self.gold < gold_cost:
            return None, None, 0

        # ── Spend gold and build ──
        self.gold -= gold_cost
        self.buildings[building] = self.buildings.get(building, 0) + 1
        self._recalc_defense()
        self._check_milestones()

        # ── Tier 3 special: chance to upgrade guard tower ──
        upgrade_msg = ""
        if tier >= 3 and building == "guard_tower" and self.guard_tower_level < 3:
            if (self.guard_tower_level < 2 and tower_count >= 2 and self.buildings.get("walls", 0) >= 4) or \
               (self.guard_tower_level < 3 and tower_count >= 3 and self.buildings.get("walls", 0) >= 6 and "fortress" in self.milestones):
                self.guard_tower_level += 1
                upgrade_msg = f" The new tower integrates seamlessly — the watchtower network upgrades to level {self.guard_tower_level}!"

        # ── Narratives ──
        building_name = building.replace("_", " ")
        tier_narratives = {
            1: [
                f"💰🛡️ MERCHANT GUILD WALL: Prosperous trade fills the coffers — the Merchant Guild funds a new {building_name} for {gold_cost}g. 'Our goods are worth protecting,' they say.",
                f"💰🛡️ TRADE-PROFIT FORTIFICATION: Surplus gold from market fees pays for a new {building_name} ({gold_cost}g). Commerce builds walls as surely as stone.",
            ],
            2: [
                f"💰🏰 GRAND BAZAAR DEFENSE: The Grand Bazaar's wealth flows into Ashfall's defenses — a new {building_name} rises ({gold_cost}g), funded by merchant taxes.",
                f"💰🏰 MARKET-FUNDED FORTIFICATION: Trade profits surge — the kingdom invests {gold_cost}g in a new {building_name}. Trade wealth becomes stone and steel.",
            ],
            3: [
                f"💰🏯 TRADE EMPIRE FORTIFICATIONS: Ancient trade routes pour wealth into Ashfall. The kingdom spends {gold_cost}g on a new {building_name} — the merchants' caravans will travel safer for it.",
                f"💰🏯 ANCIENT ROUTE DIVIDEND: Generations of trade have built trust and wealth. A new {building_name} ({gold_cost}g) rises, paid for by the tithe of a hundred caravans.",
            ],
        }
        narrative = random.choice(tier_narratives[tier])
        if upgrade_msg:
            narrative += upgrade_msg

        return narrative, building, gold_cost

    # ── Trade Route → Lair Bridge ───────────────────────────
    def _trade_route_lair_bridge(self, world_obj=None):
        """Ancient trade routes carry more than goods — veteran traders learn
        the hidden geography of the regions they traverse. Long-established
        routes occasionally reveal lair locations or yield bonus resources
        from cleared lairs along the route.

        Venerable routes (60+ days) and Ancient routes (90+ days) trigger
        lair-related events: discovering hidden lairs, finding caches near
        cleared lairs, or trading with lair-dwelling creatures.

        Returns (narrative_or_None, bonus_gold)."""
        if world_obj is None:
            return None, 0
        if not hasattr(world_obj, '_discovered_lairs') or not hasattr(world_obj, '_cleared_lairs'):
            return None, 0

        # Check each trade route for lair potential
        for route in self.trade_routes:
            route_age = route.get("age", 0)
            if route_age < 60:
                continue

            # Chance scales with route age
            chance = 0.04 if route_age < 90 else 0.07
            if random.random() > chance:
                continue

            regions = route.get("regions", [])
            for region in regions:
                # Skip regions not in LAIRS (shouldn't happen, but safe)
                if not hasattr(world_obj, 'LAIRS') or region not in world_obj.LAIRS:
                    continue

                lair = world_obj.LAIRS[region]
                lair_name = lair.get("name", "Unknown Lair")
                route_age_label = "venerable" if route_age < 90 else "ancient"

                # ── Case 1: Lair undiscovered — small chance to reveal ──
                if region not in world_obj._discovered_lairs:
                    reveal_chance = 0.10 if route_age < 90 else 0.18
                    if random.random() < reveal_chance:
                        world_obj._discovered_lairs[region] = lair_name
                        discovery_narratives = [
                            f"🗺️🛡️ TRADE-LAIR DISCOVERY: A {route_age_label} caravan master, traveling the "
                            f"{'↔'.join(regions)} route for decades, finally shares a secret — the "
                            f"location of {lair_name} in {region}. 'Found it twenty years ago,' "
                            f"they say. 'Never told anyone until now.'",
                            f"🗺️🛡️ CARAVAN REVELATION: Traders on the {route_age_label} "
                            f"{'↔'.join(regions)} route return with news: they've mapped a "
                            f"path to {lair_name} in {region}, hidden for generations.",
                        ]
                        return random.choice(discovery_narratives), 0

                # ── Case 2: Lair cleared — bonus resources from trade through cleared region ──
                elif region in world_obj._cleared_lairs:
                    gold_bonus = random.randint(4, 9) if route_age < 90 else random.randint(6, 14)
                    self.gold += gold_bonus
                    cache_narratives = [
                        f"💎🛡️ CLEARED-LAIR TRADE: Traders on the {route_age_label} "
                        f"{'↔'.join(regions)} route report finding a cache of {lair_name}'s "
                        f"old treasures — the cleared lair still yields secrets. +{gold_bonus}g.",
                        f"💎🛡️ LAIR-BOUNTY ROUTE: The {route_age_label} trade route through "
                        f"{region} passes near the cleared {lair_name}. Caravanners scavenge "
                        f"remnants worth {gold_bonus}g from the lair's outskirts.",
                        f"💎🛡️ TRADER'S LAIR-FIND: A merchant on the {route_age_label} route "
                        f"bought a 'worthless trinket' near {lair_name} — it turned out to be "
                        f"a lair artifact worth {gold_bonus}g. The route pays twice.",
                    ]
                    return random.choice(cache_narratives), gold_bonus

                # ── Case 3: Lair discovered but not cleared — narrative only ──
                else:
                    if random.random() < 0.15:
                        hint_narratives = [
                            f"🗺️🛡️ LAIR WHISPERS: Caravanners on the {route_age_label} route "
                            f"speak nervously of {lair_name} in {region}. 'Something stirs there,' "
                            f"they warn. 'Trade will suffer if it's not dealt with.'",
                        ]
                        return random.choice(hint_narratives), 0

        return None, 0

    # ── Wisdom Caravan Tier 3: Sleeper's Emissary Mini-Quests ──
    def _wisdom_caravan_tier3(self, caravan, world_obj, people_obj=None):
        """When a Sleeper's Emissary caravan fires (wisdom≥10), there's a chance
        the Emissary leaves behind more than goods — a quest, a prophecy, a task
        that must be fulfilled before the next convergence.
        Returns (narrative_or_None, quest_template_or_None)."""
        if not caravan or caravan.get("type") != "sleepers_emissary":
            return None, None
        if people_obj is None:
            return None, None
        if not hasattr(people_obj, 'faction_quests'):
            return None, None

        # 35% chance the Emissary leaves a quest behind
        if random.random() > 0.35:
            return None, None

        # Choose a faction that doesn't have an active quest
        available_factions = []
        for faction in ["hearthkeepers", "wildwalkers", "deepwardens"]:
            quest = people_obj.faction_quests.get(faction)
            if quest is None or quest.get("completed") or quest.get("failed"):
                if hasattr(people_obj, 'list_by_faction'):
                    members = people_obj.list_by_faction(faction)
                    if len(members) >= 3:
                        available_factions.append((faction, len(members)))

        if not available_factions:
            return None, None

        faction, faction_size = random.choice(available_factions)
        faction_scale = max(1, faction_size // 5)

        # Three possible mini-quest types from the Emissary
        quest_types = [
            {
                "type": "dream_cairn",
                "name": "Build the Dream-Cairn",
                "desc": "The Sleeper's Emissary points a crystalline finger toward a patch of ash-blighted ground. 'A cairn,' it whispers. 'For those who dream and do not return. Build it here.'",
                "target": {"stone": 20 * faction_scale},
                "reward_resources": {"gold": 20, "stone": 10},
                "reward_morale": 8,
                "narrative_complete": "The dream-cairn stands — a pillar of stacked stone that hums faintly at dusk. Dream-Husks gather around it on market days, paying silent respects. The Emissary nods once and dissolves into morning mist.",
                "bonus_effect": "shrine_blessing",
                "rarity": "rare",
            },
            {
                "type": "memory_vessel",
                "name": "Fill the Memory Vessel",
                "desc": "The Emissary produces a hollow dreaming-stone sphere. 'This is empty,' it says. 'Fill it with the oldest memory your people still hold. The Sleeper wishes to remember what remembering feels like.'",
                "target": {"gold": 30 * faction_scale},
                "reward_resources": {"gold": 25, "food": 10},
                "reward_morale": 10,
                "narrative_complete": "The memory vessel is filled — not with gold, but with the stories the gold bought: an elder's last tale, a child's first dream, a love letter from a century ago. The vessel glows. The Emissary accepts it with trembling hands.",
                "bonus_effect": "lore_recovery",
                "rarity": "chain",
            },
            {
                "type": "convergence_prep",
                "name": "Prepare for the Convergence",
                "desc": "The Emissary speaks of a coming alignment — when the dreaming deep and the waking world draw close enough to touch. 'Stockpile. Fortify. The Convergence will test what you have built.'",
                "target": {"food": 25 * faction_scale, "wood": 15 * faction_scale},
                "reward_resources": {"gold": 30, "food": 15, "wood": 10},
                "reward_morale": 12,
                "narrative_complete": "The Convergence came — a night when every dreamer in Ashfall dreamed the same dream. But the kingdom was ready. Storehouses full, walls strong, spirits high. The Emissary bowed. 'You will survive what is to come.'",
                "bonus_effect": "eternal_legacy",
                "rarity": "chain",
            },
        ]
        template = random.choice(quest_types)

        # Scale for age tier
        age_tier = 1
        if world_obj and hasattr(world_obj, 'day'):
            if world_obj.day > 500:
                age_tier = 4
            elif world_obj.day > 250:
                age_tier = 3
            elif world_obj.day > 100:
                age_tier = 2
        age_mult = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}.get(age_tier, 1.0)

        scaled_target = {}
        for res, amt in template["target"].items():
            scaled_target[res] = max(1, int(amt * age_mult))
        scaled_rewards = {}
        for res, amt in template.get("reward_resources", {}).items():
            scaled_rewards[res] = max(1, int(amt * age_mult))

        quest = {
            "faction": faction,
            "type": template["type"],
            "name": template["name"],
            "desc": template["desc"],
            "target": scaled_target,
            "progress": {res: 0 for res in scaled_target},
            "reward_morale": max(1, int(template.get("reward_morale", 8) * age_mult)),
            "reward_resources": scaled_rewards,
            "narrative_complete": template["narrative_complete"],
            "bonus_effect": template["bonus_effect"],
            "rarity": template["rarity"],
            "start_day": world_obj.day if world_obj and hasattr(world_obj, 'day') else 0,
            "deadline": (world_obj.day if world_obj and hasattr(world_obj, 'day') else 0) + 50,
            "completed": False,
            "failed": False,
            "age_tier": age_tier,
            "tier_name": {1: "🌱T1", 2: "🌿T3", 3: "🌳T3", 4: "🏛️T4"}.get(age_tier, ""),
            "source": "sleepers_emissary",
        }

        # Store on kingdom for processing; people_obj will pick it up
        emissary_narrative = (
            f"🌊💎 EMISSARY QUEST: Before departing, the Sleeper's Emissary turns to the "
            f"{faction.title()}. '{template['desc'].split(chr(39))[0] if chr(39) in template['desc'] else template['desc'][:60]}...' "
            f"A {template['rarity']}-rarity quest — '{template['name']}' — has been offered."
        )
        return emissary_narrative, quest

    def upgrade_guard_tower(self):
        """Upgrade the guard tower network to the next tier (max 3).
        Level 1: +5 defense per tower, basic patrol
        Level 2: +7 defense per tower, +5% patrol effectiveness, +10% early warning
        Level 3: +10 defense per tower, +12% patrol effectiveness, +25% early warning
        Requires: 2+ towers + walls ≥ 4 for L2, 3+ towers + walls ≥ 6 + fortress for L3.
        Returns (success, message)."""
        if self.buildings.get("guard_tower", 0) < 1:
            return False, "No guard tower to upgrade. Build one first."
        if self.guard_tower_level >= 3:
            return False, f"Guard tower network is already at maximum level ({self.guard_tower_level})."
        next_level = self.guard_tower_level + 1
        cost = self.GUARD_TOWER_UPGRADE_COSTS.get(next_level)
        if cost is None:
            return False, f"Unknown guard tower level: {next_level}"
        stone_cost, wood_cost, gold_cost = cost

        # Prerequisites
        if next_level == 2 and self.buildings.get("guard_tower", 0) < 2:
            return False, "Guard Tower L2 requires 2+ towers."
        if next_level == 2 and self.buildings.get("walls", 0) < 4:
            return False, "Guard Tower L2 requires walls ≥ 4 for reinforced platforms."
        if next_level == 3:
            if self.buildings.get("guard_tower", 0) < 3:
                return False, "Guard Tower L3 requires 3+ towers."
            if self.buildings.get("walls", 0) < 6:
                return False, "Guard Tower L3 requires walls ≥ 6 for an integrated watchtower network."
            if "fortress" not in self.milestones:
                return False, "Guard Tower L3 requires the Fortress milestone."

        if self.stone < stone_cost or self.wood < wood_cost or self.gold < gold_cost:
            return False, (
                f"Need {stone_cost}s {wood_cost}w {gold_cost}g to upgrade guard towers "
                f"to level {next_level} (have {self.stone}s {self.wood}w {self.gold}g)."
            )
        self.stone -= stone_cost
        self.wood -= wood_cost
        self.gold -= gold_cost
        self.guard_tower_level = next_level
        self.kingdom_log.append(
            f"🗼 GUARD TOWERS UPGRADED: Level {self.guard_tower_level} — watchtower network strengthens!"
        )
        self._check_milestones()
        return True, f"Guard towers upgraded to level {self.guard_tower_level}! The watchtower network strengthens."

    def guard_tower_bonuses(self):
        """Return passive bonuses from the current guard tower level.
        Returns dict: {defense_per_tower, patrol_bonus_pct, early_warning_pct}"""
        if self.buildings.get("guard_tower", 0) < 1:
            return {"defense_per_tower": 0, "patrol_bonus_pct": 0, "early_warning_pct": 0}
        bonuses = {
            1: {"defense_per_tower": 5,  "patrol_bonus_pct": 0,  "early_warning_pct": 0},
            2: {"defense_per_tower": 7,  "patrol_bonus_pct": 5,  "early_warning_pct": 10},
            3: {"defense_per_tower": 10, "patrol_bonus_pct": 12, "early_warning_pct": 25},
        }
        return bonuses.get(self.guard_tower_level, bonuses[1])

    # ── TAVERN STORIES ──────────────────────────────────────
    TAVERN_STORY_POOL = [
        {
            "type": "rumor",
            "narrative": "A travelling merchant at the tavern speaks of {rumor}",
            "effect": "rumor",
        },
        {
            "type": "bard",
            "narrative": "A wandering bard performs 'The Lay of the First Fire' at the tavern. "
                         "The crowd is spellbound. (+{boost} morale to all)",
            "effect": "morale",
            "morale_boost": 4,
        },
        {
            "type": "brawl",
            "narrative": "A drunken brawl breaks out at the tavern! Tables are overturned, "
                         "but {guard_name} breaks it up with authority. "
                         "({guard_name} gains +{skill} combat skill, -{penalty} morale to rowdy citizens)",
            "effect": "brawl",
        },
        {
            "type": "oldtale",
            "narrative": "An old timer at the tavern recounts a tale of {region}. "
                         "'I remember when the stones still sang...' The room leans in. "
                         "A lore fragment is recorded.",
            "effect": "lore",
        },
        {
            "type": "stranger",
            "narrative": "A hooded stranger buys a round for the house. 'For Ashfall,' "
                         "they say, 'the kingdom that remembers.' (+{boost} morale, +{gold}g in tips)",
            "effect": "stranger",
            "morale_boost": 3,
            "gold_bonus": 6,
        },
    ]

    def _tavern_stories(self, people_obj=None, world_obj=None):
        """Fire a tavern story event if conditions are right.
        Returns a story dict or None."""
        if self.buildings.get("tavern", 0) < 1:
            return None
        if self.tavern_story_cooldown > 0:
            self.tavern_story_cooldown -= 1
            return None

        # Tavern stories fire roughly every 5-12 days
        base_chance = 0.12
        # More population = livelier tavern
        pop_bonus = min(0.10, self.population * 0.001)
        if random.random() > base_chance + pop_bonus:
            return None

        self.tavern_story_cooldown = random.randint(5, 12)
        story = random.choice(self.TAVERN_STORY_POOL).copy()

        if story["type"] == "rumor":
            # Grab a rumor from world_obj
            rumor_text = "lands unknown."
            if world_obj and hasattr(world_obj, 'rumors'):
                rumors = world_obj.rumors()
                if rumors:
                    rumor_text = random.choice(rumors)
            story["narrative"] = story["narrative"].format(rumor=rumor_text)
            story["rumor"] = rumor_text
            # Small morale boost: excitement of new knowledge
            if people_obj:
                for c in people_obj.citizens:
                    if c.alive:
                        c.morale += 1
                        c.morale = max(0, min(100, c.morale))

        elif story["type"] == "bard":
            boost = story["morale_boost"]
            story["narrative"] = story["narrative"].format(boost=boost)
            if people_obj:
                for c in people_obj.citizens:
                    if c.alive:
                        c.morale += boost
                        c.morale = max(0, min(100, c.morale))

        elif story["type"] == "brawl":
            # Find a guard to be the hero
            guard_name = "a veteran"
            skill_gain = random.randint(2, 6)
            if people_obj:
                guards = [c for c in people_obj.citizens
                          if c.alive and c.role == "guard"]
                if guards:
                    hero = random.choice(guards)
                    hero.combat_skill = min(100, hero.combat_skill + skill_gain)
                    hero.remember(f"Broke up a tavern brawl — skills sharpened (+{skill_gain} combat)")
                    guard_name = hero.name
                # Penalty to random rowdy citizens
                rowdy = random.sample(
                    [c for c in people_obj.citizens if c.alive and c.role not in ("child", "elder", "guard")],
                    min(3, len([c for c in people_obj.citizens if c.alive and c.role not in ("child", "elder", "guard")]))
                )
                penalty = random.randint(1, 3)
                for r in rowdy:
                    r.morale = max(0, r.morale - penalty)
                    r.remember("Nursing a black eye from the tavern brawl")
            story["narrative"] = story["narrative"].format(
                guard_name=guard_name, skill=skill_gain, penalty=penalty
            )
            story["guard"] = guard_name
            story["skill_gain"] = skill_gain

        elif story["type"] == "oldtale":
            region = random.choice(self.territory) if self.territory else "the_vale"
            story["narrative"] = story["narrative"].format(region=region)
            # Collect a lore fragment
            lore = (
                f"Tavern tale: An elder in the {self.name} tavern spoke of {region} — "
                f"'The stones remember what the people forget.' "
                f"A fragment of history, preserved in drink and memory."
            )
            story["lore"] = lore
            if world_obj and hasattr(world_obj, 'collect_lore'):
                world_obj.collect_lore(lore)
            # Small morale boost from shared history
            if people_obj:
                for c in people_obj.citizens:
                    if c.alive:
                        c.morale += 2
                        c.morale = max(0, min(100, c.morale))

        elif story["type"] == "stranger":
            boost = story["morale_boost"]
            gold_bonus = story["gold_bonus"]
            story["narrative"] = story["narrative"].format(boost=boost, gold=gold_bonus)
            self.gold += gold_bonus
            if people_obj:
                for c in people_obj.citizens:
                    if c.alive:
                        c.morale += boost
                        c.morale = max(0, min(100, c.morale))

        self.kingdom_log.append(f"🍺 TAVERN: {story['narrative']}")
        return story

    # ── RECRUITMENT ─────────────────────────────────────────
    TRAINING_COST = {"guard": 5, "scout": 3}

    def recruit(self, people_obj, target_role="guard"):
        """Convert an eligible citizen into a guard or scout.
        Prioritizes builders and farmers for conversion.
        Costs gold for training equipment.
        Updates faction counts in people_obj when role changes.
        Returns (success, message)."""
        if target_role not in self.TRAINING_COST:
            return False, f"Can only recruit guards or scouts, not '{target_role}'."

        # Find eligible citizens: alive, not already that role, not children/elders
        eligible = [
            c for c in people_obj.citizens
            if c.alive
            and c.role != target_role
            and c.role not in ("child", "elder")
        ]

        if not eligible:
            return False, "No eligible citizens to recruit."

        # Prioritize builders, farmers, woodcutters (expendable labor pool)
        priority = [c for c in eligible if c.role in ("builder", "farmer", "woodcutter")]
        candidate = random.choice(priority) if priority else random.choice(eligible)

        cost = self.TRAINING_COST[target_role]
        if self.gold < cost:
            return False, f"Need {cost}g to train a {target_role} (have {self.gold}g)."

        self.gold -= cost
        old_role = candidate.role
        candidate.role = target_role

        # ── Faction integration: new role may fit a different faction ──
        if candidate.faction:
            people_obj.faction_counts[candidate.faction] -= 1
        people_obj._assign_faction(candidate)

        candidate.morale += 3  # sense of purpose
        candidate.remember(f"Recruited: {old_role} → {target_role}")
        self.kingdom_log.append(
            f"🎖️ {candidate.name} recruited: {old_role} → {target_role} (-{cost}g)"
        )
        self._check_milestones()
        return True, f"🎖️ {candidate.name} trained as {target_role}! (-{cost}g)"

    def recruit_count(self, people_obj, target_role="guard"):
        """Return how many citizens currently serve in a given role."""
        return sum(1 for c in people_obj.citizens if c.alive and c.role == target_role)

    # ── TRADE ───────────────────────────────────────────────
    BASE_RATES = {"wood": 0.3, "stone": 0.5, "food": 0.2}

    def trade(self, resource, amount):
        """Sell resources for gold. Market buildings improve rates by 15% each.
        Market halls add a flat +30% bonus on top."""
        if resource not in self.BASE_RATES:
            return False, f"Cannot trade {resource}"
        current = getattr(self, resource, 0)
        if current < amount:
            return False, f"Not enough {resource} (have {current})"

        markets = self.buildings.get("market", 0)
        mh = self.market_hall_bonuses()
        rate = self.BASE_RATES[resource] * (1 + 0.15 * markets + mh["trade_rate_mult"])
        gold_earned = int(amount * rate)

        setattr(self, resource, current - amount)
        self.gold += gold_earned
        self.treasury_log.append(f"Traded {amount} {resource} → +{gold_earned}g")
        return True, f"Traded {amount} {resource} → +{gold_earned} gold"

    # ── MARKET BUY ──────────────────────────────────────────
    BUY_RATES = {"wood": 0.5, "stone": 0.7, "food": 0.4}

    def buy(self, resource, amount):
        """Buy resources with gold. Market buildings improve rates by 12% each.
        Market halls add a flat +20% discount on top."""
        if resource not in self.BUY_RATES:
            return False, f"Cannot buy {resource}"
        markets = self.buildings.get("market", 0)
        mh = self.market_hall_bonuses()
        rate = self.BUY_RATES[resource] * max(0.25, 1 - 0.12 * markets - mh["trade_rate_mult"])
        cost = int(amount * rate)
        if self.gold < cost:
            return False, f"Need {cost}g to buy {amount} {resource} (have {self.gold}g)"
        self.gold -= cost
        setattr(self, resource, getattr(self, resource, 0) + amount)
        self.treasury_log.append(f"Bought {amount} {resource} ← -{cost}g")
        return True, f"Bought {amount} {resource} for {cost} gold"

    # ── TRADE ROUTES ────────────────────────────────────────
    def establish_trade_route(self, region_a, region_b, world_obj=None):
        """Create a trade route between two discovered territories.
        Costs gold up front; generates passive income each tick.
        Routes mature over time, increasing income.
        Each market building increases route income by 20%."""
        if region_a not in self.territory or region_b not in self.territory:
            return False, "Both regions must be discovered first."
        if region_a == region_b:
            return False, "Cannot route a region to itself."

        # Check for existing route between these regions
        for route in self.trade_routes:
            if set(route["regions"]) == {region_a, region_b}:
                return False, f"Trade route between {region_a} and {region_b} already exists."

        cost = 15 + len(self.trade_routes) * 5
        if self.gold < cost:
            return False, f"Need {cost}g to establish trade route (have {self.gold}g)."

        self.gold -= cost
        base_income = random.randint(2, 6)
        self.trade_routes.append({
            "regions": [region_a, region_b],
            "base_income": base_income,
            "current_income": base_income,
            "age": 0,
        })
        self.treasury_log.append(f"Trade route: {region_a} ↔ {region_b} (-{cost}g)")
        self.kingdom_log.append(
            f"📦 TRADE ROUTE: {region_a} ↔ {region_b} ({base_income}g/day base)"
        )
        return True, f"Trade route established: {region_a} ↔ {region_b} (+{base_income}g/day)"

    # ── TRADE ROUTE REGION SPECIALTIES ─────────────────────
    # Each region provides a unique bonus to trade routes passing through it.
    # Bonuses are per-route, encouraging diverse connections.
    TRADE_SPECIALTIES = {
        "the_vale":          {"food": 2, "desc": "fertile vale provisions"},
        "old_oak_ridge":     {"wood": 2, "desc": "hard oak timber"},
        "sunfire_plains":    {"gold": 1, "desc": "rare sunfire gemstones"},
        "glimmer_marsh":     {"gold": 1, "desc": "marsh herbs and remedies"},
        "ironroot_depths":   {"stone": 2, "desc": "deep-mined ironstone"},
        "the_ashen_copse":   {"gold": 2, "desc": "crystallized ash relics"},
        "the_sunken_sanctum":{"gold": 2, "desc": "bioluminescent crystals"},
        "the_dreaming_deep": {"gold": 3, "stone": 1, "desc": "crystallized dream-residue"},
    }

    # ── Seasonal Trade Fluctuation: routes through certain regions surge in peak season ──
    # Each region has a peak season and a resource bonus multiplier.
    SEASONAL_TRADE_BONUSES = {
        "the_vale":          {"season": "spring", "bonus_res": "food", "pct": 15,
                              "narrative": "spring planting swells vale caravans with fresh produce"},
        "old_oak_ridge":     {"season": "autumn", "bonus_res": "wood", "pct": 15,
                              "narrative": "autumn timber harvests flood ridge routes with hardwood"},
        "sunfire_plains":    {"season": "summer", "bonus_res": "gold", "pct": 20,
                              "narrative": "the summer sun bakes plains gems to full brilliance"},
        "glimmer_marsh":     {"season": "autumn", "bonus_res": "gold", "pct": 15,
                              "narrative": "autumn fog brings the rarest marsh herbs to market"},
        "ironroot_depths":   {"season": "winter", "bonus_res": "stone", "pct": 20,
                              "narrative": "winter drives miners deeper — the best stone comes from the cold dark"},
        "the_ashen_copse":   {"season": "autumn", "bonus_res": "gold", "pct": 25,
                              "narrative": "ash-bloom season brings relic-hunters and their coin"},
        "the_sunken_sanctum":{"season": "spring", "bonus_res": "gold", "pct": 15,
                              "narrative": "spring meltwater awakens the sanctum crystals' inner light"},
        # the_dreaming_deep: no season — the deep is beyond seasonal rhythms
    }

    # ── Trade Route Synergies: bonuses when two specific regions are connected ──
    # Keys must be alphabetically sorted tuples to match route sorting.
    TRADE_SYNERGIES = {
        ("old_oak_ridge", "the_vale"): {
            "name": "Timber & Grain Circuit",
            "bonus": {"food": 2, "wood": 1},
            "narrative": "Vale grain feeds the lumber camps; ridge timber builds vale barns."
        },
        ("ironroot_depths", "sunfire_plains"): {
            "name": "Forge-Fire Route",
            "bonus": {"gold": 3},
            "narrative": "Ironstone meets sunfire heat — the forges burn day and night."
        },
        ("glimmer_marsh", "the_vale"): {
            "name": "Herbal Remedy Road",
            "bonus": {"food": 1, "gold": 1},
            "disease_resist_pct": 5,
            "narrative": "Marsh herbs carried to vale apothecaries — illness retreats."
        },
        ("ironroot_depths", "old_oak_ridge"): {
            "name": "Timber & Stone Highway",
            "bonus": {"wood": 2, "stone": 1},
            "narrative": "Oak beams and ironstone pillars — the kingdom builds taller."
        },
        ("glimmer_marsh", "sunfire_plains"): {
            "name": "Sun & Shadow Passage",
            "bonus": {"gold": 2, "food": 1},
            "narrative": "Plains gold and marsh secrets flow together — strange and precious."
        },
        ("the_ashen_copse", "the_sunken_sanctum"): {
            "name": "Memory Road",
            "bonus": {"gold": 2},
            "lore_chance_pct": 3,
            "narrative": "Ash-wrought relics and crystal memory — the past whispers along this route."
        },
    }

    def _trade_route_income(self, world_obj=None):
        """Calculate and mature trade routes. Returns total gold earned this tick.
        Also applies region specialization bonuses (food/wood/stone/gold)."""
        total = 0
        markets = self.buildings.get("market", 0)
        mh = self.market_hall_bonuses()
        market_mult = 1 + 0.20 * markets + mh["route_mult"]
        # ── Trade District: 2+ markets + market_hall = bustling commerce hub ──
        if markets >= 2 and self.buildings.get("market_hall", 0) >= 1:
            market_mult += 0.15  # "Trade District" bonus

        spec_bonus_pct = mh["spec_bonus_pct"]  # market hall L2+ boosts spec bonuses
        spec_resources = {"food": 0, "wood": 0, "stone": 0, "gold": 0}

        maturity_events = []
        route_lore_chances = []  # per-route lore chances from venerable+ routes
        for route in self.trade_routes:
            old_age = route["age"]
            route["age"] += 1
            new_age = route["age"]
            # Routes mature over time (capped at +5 base)
            maturity_bonus = min(route["age"] // 10, 5)
            # ── Maturity Tier Multiplier: real bonuses at key ages ──
            if new_age >= 90:
                tier_mult = 1.75  # Ancient: the route is legend
            elif new_age >= 60:
                tier_mult = 1.50  # Venerable: generations of traders
            elif new_age >= 30:
                tier_mult = 1.25  # Matured: well-worn path
            else:
                tier_mult = 1.0   # Young: still being established
            income = int((route["base_income"] + maturity_bonus) * market_mult * tier_mult)
            # ── Seasonal trade fluctuation: peak-season regions boost route income ──
            seasonal_bonus_pct = 0
            seasonal_note = None
            if world_obj is not None:
                current_season = world_obj.season
                for region in route["regions"]:
                    sb = self.SEASONAL_TRADE_BONUSES.get(region)
                    if sb and sb["season"] == current_season:
                        seasonal_bonus_pct += sb["pct"]
                        seasonal_note = sb["narrative"]  # last one wins for narrative
            if seasonal_bonus_pct > 0:
                seasonal_extra = int(income * seasonal_bonus_pct / 100.0)
                income += seasonal_extra
                # Note seasonal boost in maturity events (once per route per season)
                if seasonal_note:
                    route["_seasonal_boosted"] = True
            route["current_income"] = income
            total += income

            # ── Region specialization bonuses ──
            for region in route["regions"]:
                spec = self.TRADE_SPECIALTIES.get(region, {})
                for res, amt in spec.items():
                    if res == "desc":
                        continue
                    bonus = amt
                    if spec_bonus_pct > 0:
                        bonus = int(amt * (1 + spec_bonus_pct / 100.0))
                    spec_resources[res] = spec_resources.get(res, 0) + bonus

            # ── Trade Route Synergy: check if the two regions form a known synergy pair ──
            route_regions = route["regions"]
            if len(route_regions) == 2:
                pair = tuple(sorted(route_regions))
                synergy = self.TRADE_SYNERGIES.get(pair)
                if synergy:
                    # Matured+ routes get boosted synergy resources (1.5x at tier 1, 2x at tier 2+)
                    synergy_boost = 1.0
                    if new_age >= 60:
                        synergy_boost = 2.0
                    elif new_age >= 30:
                        synergy_boost = 1.5
                    for res, amt in synergy.get("bonus", {}).items():
                        boosted = int(amt * synergy_boost)
                        spec_resources[res] = spec_resources.get(res, 0) + boosted
                    # Venerable (60+) routes with lore_chance_pct add to daily lore roll
                    if new_age >= 60 and synergy.get("lore_chance_pct", 0) > 0:
                        route_lore_chances.append(
                            (synergy["name"], synergy["lore_chance_pct"])
                        )
                    # Fire synergy discovery event once per route
                    if old_age == 0:  # first tick of a new route
                        maturity_events.append(
                            f"🔗 SYNERGY: {synergy['name']} — {synergy['narrative']}"
                        )

            # Milestone events at key ages
            regions = " ↔ ".join(route["regions"])
            if old_age < 10 and new_age >= 10:
                maturity_events.append(
                    f"📦 TRADE: {regions} route established (10d, {income}g/day)"
                )
            elif old_age < 30 and new_age >= 30:
                maturity_events.append(
                    f"📦 TRADE: {regions} route matured (30d, {income}g/day, +50% synergy boost)"
                )
            elif old_age < 60 and new_age >= 60:
                maturity_events.append(
                    f"📦 TRADE: {regions} route is venerable (60d, {income}g/day, double synergy, lore chance)"
                )
            elif old_age < 90 and new_age >= 90:
                maturity_events.append(
                    f"📦 TRADE: {regions} route is ancient (90d, {income}g/day, legendary throughput)"
                )

        # Apply specialization resources to kingdom
        for res, amt in spec_resources.items():
            if amt > 0:
                setattr(self, res, getattr(self, res) + amt)

        # ── Seasonal trade bonus narrative (once per tick, not per route) ──
        if world_obj is not None:
            active_seasonal = []
            for region, sb in self.SEASONAL_TRADE_BONUSES.items():
                if sb["season"] == world_obj.season and region in self.territory:
                    active_seasonal.append((region, sb))
            if active_seasonal:
                # Only announce if we have trade routes through those regions
                for route in self.trade_routes:
                    for region, sb in active_seasonal:
                        if region in route["regions"] and route.get("_seasonal_boosted"):
                            maturity_events.append(
                                f"🌾 SEASONAL TRADE: {sb['narrative']} (+{sb['pct']}% {sb['bonus_res']})"
                            )
                            break
                    if len(maturity_events) > 0 and maturity_events[-1].startswith("🌾"):
                        break  # one seasonal note per tick is enough

        # Store venerable-route lore chances for the tick to roll against
        self._trade_lore_chances = route_lore_chances

        return total, maturity_events

    def _venerable_trade_lore(self):
        """Roll for lore fragments from venerable (60d+) trade routes with synergy lore.
        Returns list of discovered lore narratives, or empty list."""
        discoveries = []
        for synergy_name, chance_pct in self._trade_lore_chances:
            if random.random() * 100 < chance_pct:
                discoveries.append(
                    f"📜 VENERABLE TRADE LORE: The ancient {synergy_name} route carries old "
                    f"stories — a trader returns with a fragment of forgotten knowledge."
                )
        return discoveries

    def _seasonal_trade_lore(self, world_obj, people_obj=None):
        """Roll for lore fragments from trade routes passing through territories in their
        peak season. Chance scales with route age. The ashen_copse in autumn is especially potent.
        Tier 2: ashen_copse autumn fragments can be 'Sleeper's Memory' — rare fragments that
        resonate with dream-bonds (cross-system bridge to Cyr's dream-bond system).
        Returns list of lore narratives."""
        if world_obj is None:
            return []
        discoveries = []
        current_season = world_obj.season
        for route in self.trade_routes:
            for region in route["regions"]:
                sb = self.SEASONAL_TRADE_BONUSES.get(region)
                if sb is None or sb["season"] != current_season:
                    continue
                # Base lore chance: 5% + 1% per 10d route age
                base_chance = 5.0
                route_age_bonus = route["age"] // 10 * 1.0
                # The ashen_copse in autumn: double the base chance
                region_mult = 2.0 if region == "the_ashen_copse" else 1.0
                chance = (base_chance * region_mult) + route_age_bonus
                if random.random() * 100 < chance:
                    region_name = region.replace("_", " ").title()
                    # ── Tier 2: Ashen Copse Sleeper's Memory fragments ──
                    if region == "the_ashen_copse" and current_season == "autumn" and random.random() < 0.25:
                        # A Sleeper's Memory — the ash-bloom caravans carry echoes of the Sleeper's own dreams
                        gold_bonus = random.randint(5, 10)
                        self.gold += gold_bonus
                        discoveries.append(
                            f"📜💤 SLEEPER'S MEMORY: The autumn ash-bloom caravans through "
                            f"The Ashen Copse carry more than relics — a trader unwraps a "
                            f"crystallized dream-shard, and for a moment, every person in the "
                            f"market sees the same vision: the Sleeper, turning in their sleep. "
                            f"(+{gold_bonus}g from the relic's sale)"
                        )
                        # Dream-bond resonance: if bonded citizens exist, the memory resonates
                        if people_obj and hasattr(people_obj, 'citizens'):
                            bonded_count = sum(1 for c in people_obj.citizens 
                                              if c.alive and getattr(c, 'dream_bonds', []))
                            if bonded_count >= 2 and random.random() < 0.15:
                                resonance_gold = bonded_count * 3
                                self.gold += resonance_gold
                                discoveries.append(
                                    f"🌊💞 DREAM-BOND RESONANCE: The Sleeper's Memory ripples "
                                    f"through {bonded_count} dream-bonded citizens. They wake "
                                    f"knowing things they shouldn't — trade secrets, hidden routes, "
                                    f"the location of a forgotten cache. (+{resonance_gold}g)"
                                )
                    else:
                        discoveries.append(
                            f"📜 SEASONAL TRADE LORE: The {current_season} caravans through "
                            f"{region_name} carry more than goods — a fragment of old memory "
                            f"surfaces among the trade-worn travellers."
                        )
                break  # one check per route
        return discoveries

    def trade_synergy_bonuses(self):
        """Return non-resource bonuses from active trade route synergies.
        Returns dict: {disease_resist_pct, lore_chance_pct, active_synergies list}
        Venerable (60d+) routes double lore_chance; ancient (90d+) routes also 
        contribute disease_resist from nearby synergies."""
        result = {"disease_resist_pct": 0, "lore_chance_pct": 0, "active_synergies": []}
        for route in self.trade_routes:
            if len(route["regions"]) == 2:
                pair = tuple(sorted(route["regions"]))
                synergy = self.TRADE_SYNERGIES.get(pair)
                if synergy:
                    # Venerable routes (60d+) double lore chance
                    lore_mult = 2.0 if route["age"] >= 60 else 1.0
                    result["lore_chance_pct"] += int(
                        synergy.get("lore_chance_pct", 0) * lore_mult
                    )
                    # Ancient routes (90d+) also radiate disease resistance from synergy
                    disease_mult = 2.0 if route["age"] >= 90 else 1.0
                    result["disease_resist_pct"] += int(
                        synergy.get("disease_resist_pct", 0) * disease_mult
                    )
                    if synergy["name"] not in result["active_synergies"]:
                        result["active_synergies"].append(synergy["name"])
        return result

    # ── CARAVANS ────────────────────────────────────────────
    CARAVAN_OFFERS = [
        ("merchant", "food", 8, 3, "A dusty merchant offers 8 food for 3 gold."),
        ("lumberjack", "wood", 10, 4, "A lumberjack sells 10 wood for 4 gold."),
        ("mason", "stone", 6, 5, "A mason offers 6 stone for 5 gold."),
        ("sellsword", "defense", 5, 8, "Sellswords offer +5 defense for 5 days for 8 gold."),
        ("herbalist", "morale", 8, 6, "An herbalist sells soothing herbs (+8 morale) for 6 gold."),
        ("tinker", "gold", 12, 15, "A tinker offers to improve workshops (+12 gold next tick) for 15 gold."),
    ]

    # Grand Bazaar expanded offers: better deals when the bazaar is active
    GRAND_BAZAAR_OFFERS = [
        ("spice_merchant", "gold", 18, 20, "A spice merchant from distant lands offers rare spices (18g resale value) for 20 gold."),
        ("gem_cutter", "gold", 22, 25, "A gem-cutter displays polished sunfire gems (+22 gold) for 25 gold."),
        ("relic_dealer", "lore", 1, 15, "A relic dealer offers a fragment of old-world knowledge (+lore) for 15 gold."),
        ("grand_merchant", "food", 20, 5, "A grand merchant's caravan offers 20 food for only 5 gold — bulk discount."),
        ("timber_baron", "wood", 18, 5, "A timber baron sells 18 wood for 5 gold — the bazaar's bulk rates."),
    ]

    # Wisdom-unlocked premium caravan offers (tier 2: elders spot rare traders)
    WISDOM_CARAVAN_OFFERS = {
        5: [  # 5+ wisdom traits across all citizens
            ("dream_merchant", "gold", 25, 28, 
             "A dream-merchant — eyes clouded with visions — offers crystallized dream-essence (+25 gold) for 28 gold. 'Harvested at the edge of waking,' they whisper."),
            ("star_chart_dealer", "gold", 20, 18,
             "A star-chart dealer unfurls maps of constellations no living astronomer has named. The knowledge alone is worth 20 gold — for only 18 gold."),
        ],
        10: [  # 10+ wisdom traits
            ("sleepers_emissary", "gold", 35, 30,
             "A hooded figure — the Sleeper's own emissary, or so they claim — offers a vial of shimmering liquid. 'One drop and you'll dream the Sleeper's dream.' (+35 gold resale, +2 lore) for 30 gold."),
        ],
    }

    def _roll_caravan(self, world_obj=None, people_obj=None):
        """Check if a trade caravan arrives. Returns offer dict or None.
        Grand Bazaar (market_hall L3) makes caravans more frequent and more lucrative.
        Tier 2: wisdom traits unlock premium caravan tiers — wise elders spot rare traders."""
        if self.caravan_cooldown > 0:
            self.caravan_cooldown -= 1
            return None

        # Caravans more likely when you have a market; grand bazaar draws many more
        market_bonus = 0.05 * self.buildings.get("market", 0)
        hall_bonus = 0.10 * self.buildings.get("market_hall", 0)
        bazaar_bonus = 0.10 if self.market_hall_level >= 3 else 0  # grand bazaar draws traders
        base_chance = 0.15 + market_bonus + hall_bonus + bazaar_bonus
        if random.random() > base_chance:
            return None

        # Grand Bazaar reduces cooldown: merchants compete to reach you first
        if self.market_hall_level >= 3:
            self.caravan_cooldown = random.randint(2, 5)
        else:
            self.caravan_cooldown = random.randint(3, 8)

        # ── Wisdom count: determines premium tier access ──
        wisdom_count = 0
        if people_obj and hasattr(people_obj, 'citizens'):
            for c in people_obj.citizens:
                if c.alive and getattr(c, 'wisdom_traits', []):
                    wisdom_count += len(c.wisdom_traits)

        # Grand Bazaar has a 40% chance of a premium offer (higher with wisdom)
        premium_chance = 0.40
        if wisdom_count >= 10:
            premium_chance = 0.60  # wise elders attract rare traders
        elif wisdom_count >= 5:
            premium_chance = 0.50

        if self.market_hall_level >= 3 and random.random() < premium_chance:
            # Build pool: base premium + wisdom-gated offers
            pool = list(self.GRAND_BAZAAR_OFFERS)
            for threshold, offers in sorted(self.WISDOM_CARAVAN_OFFERS.items()):
                if wisdom_count >= threshold:
                    pool.extend(offers)
        else:
            pool = self.CARAVAN_OFFERS

        offer_type, resource, amount, cost, description = random.choice(pool)
        # ── Sleeper's Emissary gives bonus lore ──
        extra_lore = False
        if offer_type == "sleepers_emissary":
            extra_lore = True
        return {
            "type": offer_type,
            "resource": resource,
            "amount": amount,
            "cost": cost,
            "description": description,
            "extra_lore": extra_lore,  # signal to collect a lore fragment
        }

    def accept_caravan(self, caravan):
        """Accept a caravan offer. Deducts gold, applies the benefit."""
        if self.gold < caravan["cost"]:
            return False, f"Need {caravan['cost']}g (have {self.gold}g)"
        self.gold -= caravan["cost"]
        res = caravan["resource"]
        amt = caravan["amount"]
        if res == "defense":
            self.defense_bonus += amt
            return True, f"Defense boosted by {amt} for a while."
        elif res == "morale":
            return True, f"Morale boost of {amt} (applied by caller)."
        elif res == "gold":
            self.gold += amt
            return True, f"Gained {amt} gold."
        else:
            setattr(self, res, getattr(self, res, 0) + amt)
            return True, f"Bought {amt} {res} from caravan."

    def escort_caravan(self, caravan, people_obj=None):
        """Assign guards to escort a caravan for bonus rewards.
        Uses 1-2 available guards. Small risk of injury on dangerous routes.
        Returns (escort_success, narrative, bonus_rewards dict)."""
        if not people_obj:
            return False, "No people to assign as escorts.", {}

        # Find available guards (alive, not already on patrol)
        guards = [c for c in people_obj.citizens
                  if c.alive and c.role == "guard"
                  and not getattr(c, 'on_patrol', False)
                  and not getattr(c, 'on_escort', False)]
        if len(guards) < 1:
            return False, "No available guards for escort duty.", {}

        # Assign 1-2 guards based on caravan type
        danger_map = {"merchant": 1, "lumberjack": 1, "mason": 1,
                       "sellsword": 2, "herbalist": 1, "tinker": 2}
        danger_level = danger_map.get(caravan.get("type", "merchant"), 1)
        escorts_needed = min(danger_level, len(guards))
        escorts = random.sample(guards, escorts_needed)

        # Mark guards as on escort
        for g in escorts:
            g.on_escort = True

        # Base bonus: extra gold/resources proportional to caravan value
        base_bonus_gold = random.randint(3, 8) + caravan.get("cost", 0)
        bonus = {"gold": base_bonus_gold}

        # Danger check: higher danger = more reward but risk of injury
        risk_chance = 0.05 + danger_level * 0.05  # 10-15%
        narrative = ""
        if random.random() < risk_chance:
            # Guard injured — lose the guard for a few days (morale penalty)
            injured = random.choice(escorts)
            injured.health = max(10, injured.health - 30)
            injured.morale = max(0, injured.morale - 10)
            injured.remember(f"Injured while escorting a {caravan['type']} caravan.")
            narrative = (
                f"🛡️⚔️ ESCORT: {escorts_needed} guard(s) escorted a {caravan['type']} caravan. "
                f"{injured.name} was injured in an ambush, but the caravan made it through! "
                f"(+{base_bonus_gold}g hazard pay)"
            )
            # Bonus is higher for dangerous trips
            bonus["gold"] += random.randint(5, 15)
            bonus["injury"] = injured.name
        else:
            narrative = (
                f"🛡️ ESCORT: {escorts_needed} guard(s) safely escorted a {caravan['type']} caravan. "
                f"(+{base_bonus_gold}g escort fee)"
            )
            # Small chance of extra resource tip
            if random.random() < 0.30:
                tip_res = random.choice(["food", "wood", "stone"])
                tip_amt = random.randint(2, 6)
                bonus[tip_res] = tip_amt
                narrative += f" The grateful merchant tipped {tip_amt} {tip_res}."

        # Apply gold bonus immediately
        self.gold += bonus.get("gold", 0)
        for res in ("food", "wood", "stone"):
            if res in bonus:
                setattr(self, res, getattr(self, res) + bonus[res])

        # Record in escort history
        self.escort_history.append({
            "day": getattr(people_obj, '_day_counter', 0),
            "caravan_type": caravan.get("type"),
            "escorts": [g.name for g in escorts],
            "bonus": bonus,
            "risk_triggered": "injury" in bonus,
        })

        # Clear escort flag (escort is one tick)
        for g in escorts:
            g.on_escort = False

        self.kingdom_log.append(narrative)
        return True, narrative, bonus

    # ── MARKET SUPPLY / DEMAND EVENTS ───────────────────────
    SUPPLY_DEMAND_EVENTS = [
        # Common events (any market_hall)
        {"name": "Surplus Glut", "min_hall": 0, "max_route_age": 29,
         "narrative": "A surplus glut floods the market — {res} prices collapse, but the kingdom's "
                     "storehouses overflow with cheap goods.",
         "bonus": {"food": 8, "wood": 6}},
        {"name": "Sudden Demand", "min_hall": 1, "min_routes": 1,
         "narrative": "Word arrives of a desperate buyer in a neighboring settlement — they'll pay "
                     "double for {res}. Ashfall's merchants scramble to fill the order.",
         "bonus": {"gold": 10}},
        {"name": "Trade Fair", "min_hall": 1, "min_routes": 2,
         "narrative": "A spontaneous trade fair erupts in the market square! Merchants barter "
                     "furiously, and the kingdom's coffers swell with fees and good fortune.",
         "bonus": {"gold": 8, "food": 4}},
        # Trade route tier events
        {"name": "Matured Route Boom", "min_hall": 1, "min_route_age": 30, "max_route_age": 59,
         "narrative": "A well-established trade route delivers an unexpected windfall — a merchant "
                     "caravan repays an old debt with interest.",
         "bonus": {"gold": 12}},
        {"name": "Venerable Caravan Train", "min_hall": 2, "min_route_age": 60, "max_route_age": 89,
         "narrative": "Three generations of traders converge on Ashfall simultaneously — the route "
                     "is so well-known that caravans time their journeys to overlap.",
         "bonus": {"gold": 18, "food": 6}},
        {"name": "Ancient Route Bounty", "min_hall": 2, "min_route_age": 90,
         "narrative": "A legendary caravan arrives, bearing goods from beyond the known map. "
                     "The ancient route has attracted traders who deal in wonders.",
         "bonus": {"gold": 25, "stone": 5, "food": 5}},
        # Grand Bazaar events
        {"name": "Grand Auction", "min_hall": 3,
         "narrative": "The Grand Bazaar hosts its monthly auction — rare goods from every "
                     "corner of the map go to the highest bidder. The kingdom takes its cut.",
         "bonus": {"gold": 20}},
        {"name": "Merchant Guild Visit", "min_hall": 3,
         "narrative": "A delegation from the Merchant Guild inspects Ashfall's Grand Bazaar "
                     "and declares it a Certified Trade Nexus. Prestige and gold follow.",
         "bonus": {"gold": 15, "morale_boost": 5}},
        {"name": "Supply Chain Mastery", "min_hall": 3, "min_routes": 3,
         "narrative": "Ashfall's trade network hums with efficiency — goods flow so smoothly "
                     "that surplus accumulates in every warehouse.",
         "bonus": {"food": 10, "wood": 8, "stone": 6, "gold": 5}},
    ]

    def _check_supply_demand(self, people_obj=None, world_obj=None):
        """Periodic market supply/demand events based on trade route tiers and market_hall level.
        Returns (narrative_or_None, bonus_resources_dict, morale_boost).
        If people_obj is provided, matching resources contribute to active faction quests."""
        if self._supply_demand_cooldown > 0:
            self._supply_demand_cooldown -= 1
            return None, {}, 0

        # Cooldown varies: grand bazaar = more frequent events (8-16d), else 12-22d
        if self.market_hall_level >= 3:
            self._supply_demand_cooldown = random.randint(8, 16)
        elif self.buildings.get("market_hall", 0) >= 1:
            self._supply_demand_cooldown = random.randint(12, 22)
        else:
            self._supply_demand_cooldown = random.randint(15, 28)

        # Only fire if we have some trade infrastructure
        if self.buildings.get("market", 0) < 1:
            return None, {}, 0

        # Gather context for filtering
        route_count = len(self.trade_routes)
        max_route_age = max((r["age"] for r in self.trade_routes), default=0)
        mh = self.market_hall_level

        candidates = []
        for evt in self.SUPPLY_DEMAND_EVENTS:
            # Hall requirement
            if evt.get("min_hall", 0) > mh:
                continue
            # Route count requirement
            if evt.get("min_routes", 0) > route_count:
                continue
            # Route age window
            min_age = evt.get("min_route_age", 0)
            max_age = evt.get("max_route_age", 9999)
            if max_route_age < min_age or max_route_age > max_age:
                continue
            candidates.append(evt)

        if not candidates:
            return None, {}, 0

        event = random.choice(candidates)
        narrative = event["narrative"]
        bonus = dict(event["bonus"])
        morale_boost = bonus.pop("morale_boost", 0)

        # Apply resource bonuses
        for res, amt in bonus.items():
            setattr(self, res, getattr(self, res) + amt)

        # Fill in {res} template
        if "{res}" in narrative:
            narrative = narrative.replace("{res}", random.choice(["food", "wood", "stone"]))

        # ── Supply/Demand → Faction Quest Resonance ──
        # Market events contribute matching resources to active faction quests
        if people_obj and hasattr(people_obj, 'faction_quests'):
            contributed = False
            for faction, quest in people_obj.faction_quests.items():
                if quest is None or quest.get("completed") or quest.get("failed"):
                    continue
                for res, amt in bonus.items():
                    if res in quest["progress"] and amt > 0:
                        # 50% of event bonus flows into quest progress (rounded up)
                        quest_amt = max(1, int(amt * 0.5 + 0.5))
                        quest["progress"][res] += quest_amt
                        contributed = True
            # ── Supply/Demand → Faction Quest Tier 2: more events spawn faction quests ──
            if event["name"] == "Merchant Guild Visit" and not getattr(self, '_pending_market_quest', False):
                self._pending_market_quest = True
            # Trade Fair → Hearthkeepers: feed the gathered crowds
            if event["name"] == "Trade Fair":
                if not any(q[0] == "hearthkeepers" and q[1] == "Trade Fair" 
                           for q in getattr(self, '_pending_sd_quests', [])):
                    self._pending_sd_quests.append(
                        ("hearthkeepers", "Trade Fair", {
                            "type": "trade_fair",
                            "name": "Feed the Trade Fair",
                            "desc": "The Trade Fair draws crowds from across Ashfall — the Hearthkeepers must ensure no one goes hungry.",
                            "target": {"food": 25},
                            "reward_morale": 8,
                            "reward_resources": {"food": 10, "gold": 12},
                            "narrative_complete": "The Hearthkeepers' tables groaned under the weight of the feast. The Trade Fair becomes an annual tradition — Ashfall's hospitality is legendary.",
                            "bonus_effect": "feast_bounty",
                            "rarity": "common",
                        }))
            # Grand Auction → Wildwalkers: claim rare goods from distant lands
            if event["name"] == "Grand Auction":
                if not any(q[0] == "wildwalkers" and q[1] == "Grand Auction"
                           for q in getattr(self, '_pending_sd_quests', [])):
                    self._pending_sd_quests.append(
                        ("wildwalkers", "Grand Auction", {
                            "type": "grand_auction",
                            "name": "Claim the Grand Auction",
                            "desc": "Rare goods from every corner of the map are on the block — the Wildwalkers must secure the most precious items for Ashfall's future.",
                            "target": {"gold": 35},
                            "reward_morale": 10,
                            "reward_resources": {"gold": 20, "stone": 8},
                            "narrative_complete": "The Wildwalkers outbid every rival. A crate of star-charts, a vial of Sleeper's-tear, and a map to a place between places — all now belong to Ashfall.",
                            "bonus_effect": "lore_recovery",
                            "rarity": "rare",
                        }))
            # Surplus Glut → Hearthkeepers: distribute excess to the people
            if event["name"] == "Surplus Glut":
                if not any(q[0] == "hearthkeepers" and q[1] == "Surplus Glut"
                           for q in getattr(self, '_pending_sd_quests', [])):
                    self._pending_sd_quests.append(
                        ("hearthkeepers", "Surplus Glut", {
                            "type": "surplus",
                            "name": "Distribute the Surplus",
                            "desc": "Warehouses overflow — the Hearthkeepers must organize distribution before spoilage sets in.",
                            "target": {"food": 20, "wood": 15},
                            "reward_morale": 6,
                            "reward_resources": {"food": 8, "wood": 5},
                            "narrative_complete": "Every family in Ashfall received a share. The surplus is gone, but gratitude fills every hearth.",
                            "bonus_effect": "morale_boost",
                            "rarity": "common",
                        }))
            # Supply Chain Mastery → all factions get a small quest progress boost
            if event["name"] == "Supply Chain Mastery":
                for faction, quest in people_obj.faction_quests.items():
                    if quest is None or quest.get("completed") or quest.get("failed"):
                        continue
                    for res in quest["progress"]:
                        quest["progress"][res] += 2
                self.kingdom_log.append(
                    "📊🔗 SUPPLY CHAIN: All active faction quests accelerated by the kingdom's "
                    "masterful trade network — resources flow where they're needed."
                )

            # ── TIER 3: Multi-Faction Supply Chain Quests ──
            # When a supply/demand quest was recently completed, market events
            # can spark chain quests linking two factions together.
            completed_sd = getattr(self, '_completed_sd_quests', [])
            today = getattr(world_obj, 'day', 0) if 'world_obj' in dir() else 0
            recent_window = 20  # days

            # Chain: Trade Fair (Hearthkeepers) → Wildwalkers follow-up
            if event["name"] == "Trade Fair":
                recent_hk_fair = any(
                    c[0] == "hearthkeepers" and c[1] == "Trade Fair"
                    and (today - c[2]) <= recent_window
                    for c in completed_sd
                )
                if recent_hk_fair and hasattr(people_obj, 'faction_quests'):
                    ww_busy = people_obj.faction_quests.get("wildwalkers") is not None
                    if not ww_busy and not any(
                        q[0] == "wildwalkers" and q[1] == "Trade Fair Chain"
                        for q in getattr(self, '_pending_sd_quests', [])
                    ):
                        self._pending_sd_quests.append(
                            ("wildwalkers", "Trade Fair Chain", {
                                "type": "trade_fair_chain",
                                "name": "Trade Fair Caravan Guard",
                                "desc": "The Hearthkeepers' feast was a triumph — now Wildwalkers must escort the fattened trade caravans safely through dangerous territory back to their homelands.",
                                "target": {"gold": 30, "wood": 15},
                                "reward_morale": 10,
                                "reward_resources": {"gold": 25, "food": 8},
                                "narrative_complete": "The Wildwalkers guided every caravan home safely. The trade partners speak of Ashfall's honor — and return with twice the goods next season.",
                                "bonus_effect": "gold_rush",
                                "rarity": "chain",
                            }))

            # Chain: Grand Auction (Wildwalkers) → Deepwardens follow-up
            if event["name"] == "Grand Auction":
                recent_ww_auction = any(
                    c[0] == "wildwalkers" and c[1] == "Grand Auction"
                    and (today - c[2]) <= recent_window
                    for c in completed_sd
                )
                if recent_ww_auction and hasattr(people_obj, 'faction_quests'):
                    dw_busy = people_obj.faction_quests.get("deepwardens") is not None
                    if not dw_busy and not any(
                        q[0] == "deepwardens" and q[1] == "Grand Auction Chain"
                        for q in getattr(self, '_pending_sd_quests', [])
                    ):
                        self._pending_sd_quests.append(
                            ("deepwardens", "Grand Auction Chain", {
                                "type": "grand_auction_chain",
                                "name": "Catalog the Auction Relics",
                                "desc": "The Wildwalkers won treasures beyond counting — now the Deepwardens must study, catalog, and protect the ancient artifacts before their power fades.",
                                "target": {"stone": 25, "gold": 20},
                                "reward_morale": 12,
                                "reward_resources": {"stone": 15, "gold": 18},
                                "narrative_complete": "The Deepwardens' new relic-vault hums with captured starlight. Every artifact cataloged, every secret preserved — Ashfall's history stretches deeper now.",
                                "bonus_effect": "lore_recovery",
                                "rarity": "chain",
                            }))

            # Chain: Surplus Glut (Hearthkeepers) → Deepwardens follow-up
            if event["name"] == "Surplus Glut":
                recent_hk_surplus = any(
                    c[0] == "hearthkeepers" and c[1] == "Surplus Glut"
                    and (today - c[2]) <= recent_window
                    for c in completed_sd
                )
                if recent_hk_surplus and hasattr(people_obj, 'faction_quests'):
                    dw_busy = people_obj.faction_quests.get("deepwardens") is not None
                    if not dw_busy and not any(
                        q[0] == "deepwardens" and q[1] == "Surplus Chain"
                        for q in getattr(self, '_pending_sd_quests', [])
                    ):
                        self._pending_sd_quests.append(
                            ("deepwardens", "Surplus Chain", {
                                "type": "surplus_chain",
                                "name": "Build the Grand Storehouse",
                                "desc": "The Hearthkeepers proved Ashfall can produce abundance — the Deepwardens must now build a storehouse worthy of it, with vaults deep enough to survive any winter.",
                                "target": {"stone": 30, "wood": 20},
                                "reward_morale": 10,
                                "reward_resources": {"stone": 12, "wood": 10, "gold": 10},
                                "narrative_complete": "The Grand Storehouse rises — a fortress of plenty. Its deepest vaults are carved with the names of every Hearthkeeper who made the surplus possible. Two factions, one purpose.",
                                "bonus_effect": "feast_bounty",
                                "rarity": "chain",
                            }))

            # Clean up old completed_sd entries (older than 30 days)
            if completed_sd:
                self._completed_sd_quests = [
                    c for c in completed_sd if (today - c[2]) <= 30
                ]

        return narrative, bonus, morale_boost

    def _track_sd_quest_completions(self, people_obj, world_obj):
        """Check faction quests for completed supply/demand quests and record them
        for chain quest detection. Called from tick before _check_supply_demand."""
        if people_obj is None or not hasattr(people_obj, 'faction_quests'):
            return
        today = world_obj.day if world_obj and hasattr(world_obj, 'day') else 0

        sd_quest_types = {
            "trade_fair", "grand_auction", "surplus",
            "trade_fair_chain", "grand_auction_chain", "surplus_chain",
            "trade_guild"
        }

        if not hasattr(self, '_recorded_sd_completions'):
            self._recorded_sd_completions = set()

        for faction, quest in people_obj.faction_quests.items():
            if quest is None:
                continue
            qtype = quest.get("type", "")
            if qtype not in sd_quest_types:
                continue

            event_map = {
                "trade_fair": "Trade Fair",
                "grand_auction": "Grand Auction",
                "surplus": "Surplus Glut",
                "trade_fair_chain": "Trade Fair Chain",
                "grand_auction_chain": "Grand Auction Chain",
                "surplus_chain": "Surplus Chain",
                "trade_guild": "Merchant Guild Visit",
            }
            event_name = event_map.get(qtype, qtype)

            quest_id = (faction, event_name, quest.get("start_day", 0))

            if quest.get("completed") and quest_id not in self._recorded_sd_completions:
                self._completed_sd_quests.append((faction, event_name, today))
                self._recorded_sd_completions.add(quest_id)
                self.kingdom_log.append(
                    f"📊🔗 SD QUEST COMPLETED: {faction.title()} finished "
                    f"'{quest['name']}' — supply chains may spark follow-up quests."
                )
            elif quest.get("failed") and quest_id not in self._recorded_sd_completions:
                self._recorded_sd_completions.add(quest_id)

    FESTIVAL_DEFS = [
        {"name": "Harvest Feast", "food_cost": 15, "gold_cost": 10, "morale_boost": 12,
         "min_season": "autumn", "max_season": "autumn",
         "cooldown_category": "common",
         "narrative": "The harvest wagons roll in, laden with the season's bounty. Tables groan under the weight of the feast."},
        {"name": "Spring Song", "food_cost": 10, "gold_cost": 5, "morale_boost": 8,
         "min_season": "spring", "max_season": "spring",
         "cooldown_category": "common",
         "narrative": "Flowers are woven into garlands, and every voice in Ashfall joins the Song of Renewal."},
        {"name": "Midwinter Fires", "food_cost": 20, "gold_cost": 12, "morale_boost": 15,
         "min_season": "winter", "max_season": "winter",
         "cooldown_category": "common",
         "narrative": "Great bonfires push back the longest night. Stories are told, and the kingdom remembers it has endured."},
        {"name": "Founder's Day", "food_cost": 12, "gold_cost": 8, "morale_boost": 10,
         "min_season": None, "max_season": None,
         "cooldown_category": "common",
         "narrative": "The founding of Ashfall is remembered with toasts, tales, and the hanging of new banners from the walls."},
        {"name": "Midsummer Revel", "food_cost": 18, "gold_cost": 15, "morale_boost": 14,
         "min_season": "summer", "max_season": "summer",
         "cooldown_category": "seasonal",
         "narrative": "The longest day is celebrated with dancing, contests of strength, and a river of golden mead. The sun itself seems to linger to watch.",
         "bonus_resource": "gold", "bonus_amount": 15},  # summer visitors bring coin
        {"name": "Vale Blossom Fair", "food_cost": 8, "gold_cost": 10, "morale_boost": 9,
         "min_season": "spring", "max_season": "spring",
         "requires_region": "the_vale", "cooldown_category": "regional",
         "narrative": "The vale erupts in wildflowers, and Ashfall hosts a fair of blossom-wine, honey-cakes, and flower-crown contests. Even the bees seem drunk on the abundance.",
         "bonus_resource": "food", "bonus_amount": 8},
        {"name": "Ridge Timberfest", "food_cost": 14, "gold_cost": 6, "morale_boost": 11,
         "min_season": "autumn", "max_season": "autumn",
         "requires_region": "old_oak_ridge", "cooldown_category": "regional",
         "narrative": "Woodcutters compete to fell, carve, and build — the finest new beam is raised above the tavern with great ceremony. Sawdust and celebration fill the air.",
         "bonus_resource": "wood", "bonus_amount": 12},
        {"name": "Marsh Lantern Night", "food_cost": 10, "gold_cost": 8, "morale_boost": 10,
         "min_season": "autumn", "max_season": "winter",
         "requires_region": "glimmer_marsh", "cooldown_category": "regional",
         "narrative": "As dusk falls, lanterns are floated across the marsh waters — tiny flames mirroring the bog-wisps. It's said any two people who launch a lantern together are bound for life.",
         "lore_chance": True},
        {"name": "Deepforge Fires", "food_cost": 16, "gold_cost": 20, "morale_boost": 13,
         "min_season": "winter", "max_season": "winter",
         "requires_region": "ironroot_depths", "cooldown_category": "regional",
         "narrative": "The forges of the depths burn through the coldest nights. Smiths compete to craft the finest blade, the strongest shield. The winner's work is hung above the market hall.",
         "bonus_resource": "stone", "bonus_amount": 10},
        {"name": "Plains Gallop", "food_cost": 12, "gold_cost": 10, "morale_boost": 12,
         "min_season": "summer", "max_season": "summer",
         "requires_region": "sunfire_plains", "cooldown_category": "regional",
         "narrative": "Wild horses are gentled and raced across the sunfire plains. The winner receives a crown of golden grass — and a year's supply of the finest plains-grain ale."},
        {"name": "Ashen Vigil", "food_cost": 6, "gold_cost": 5, "morale_boost": 8,
         "min_season": None, "max_season": None,
         "requires_region": "the_ashen_copse", "cooldown_category": "rare",
         "narrative": "A solemn procession walks to the edge of the copse. Candles are lit for those who fell in the Cataclysm. The Sleeper's warmth pulses gently beneath — a reminder of the pact that holds the kingdom together.",
         "lore_chance": True, "ash_bloom_chance": 0.30},
    ]

    # ── Festival cooldown categories ──
    FESTIVAL_COOLDOWN_RANGES = {
        "common":   (15, 30),   # core festivals fire frequently
        "seasonal": (25, 45),   # seasonal spectacles less often
        "regional": (35, 55),   # region-specific feel special
        "rare":     (45, 70),   # lore/ash-bloom festivals are uncommon
    }

    def _roll_festival(self, people_obj=None):
        """Check if a festival should trigger. Returns festival info or None.
        Uses per-category cooldowns so different festival types fire independently."""
        # Decrement all category cooldowns
        for cat in list(self._festival_category_cooldowns.keys()):
            if self._festival_category_cooldowns[cat] > 0:
                self._festival_category_cooldowns[cat] -= 1
                if self._festival_category_cooldowns[cat] <= 0:
                    del self._festival_category_cooldowns[cat]
        # Also tick legacy global cooldown for backward compat
        if self.festival_cooldown > 0:
            self.festival_cooldown -= 1

        # Festivals more likely with tavern and decent morale
        tavern_bonus = 0.08 if self.buildings.get("tavern", 0) > 0 else 0.0
        # Market hall adds festival draw
        hall_bonus = 0.04 * self.buildings.get("market_hall", 0)
        if random.random() > 0.06 + tavern_bonus + hall_bonus:
            return None

        # Pick a festival appropriate for the season
        from world import world as _w
        season = _w.season
        valid = []
        for f in self.FESTIVAL_DEFS:
            # Category cooldown check: skip festivals whose category is on cooldown
            cat = f.get("cooldown_category", "common")
            if self._festival_category_cooldowns.get(cat, 0) > 0:
                continue
            # Season check
            season_ok = (f["min_season"] is None
                         or f["min_season"] == season
                         or f["max_season"] == season
                         or (f["min_season"] != f["max_season"]
                             and self._season_in_range(season, f["min_season"], f["max_season"])))
            if not season_ok:
                continue
            # Region requirement check
            if "requires_region" in f and f["requires_region"] not in self.territory:
                continue
            valid.append(f)

        # Fallback: ignore category cooldowns for valid festivals
        if not valid:
            valid = [f for f in self.FESTIVAL_DEFS
                     if "requires_region" not in f
                     or f["requires_region"] in self.territory]
        # Absolute fallback: any festival (ignore all restrictions except region)
        if not valid:
            valid = [f for f in self.FESTIVAL_DEFS
                     if "requires_region" not in f
                     or f["requires_region"] in self.territory]
        if not valid:
            valid = self.FESTIVAL_DEFS[:4]  # core four always available

        # ── Seasonal weight bias ──
        # In-season festivals get weight 3; any-season (None) get weight 2;
        # edge-match or multi-season get weight 1.  Peak-season festivals are
        # 3× more likely than anything else — but Founder's Day can still surprise.
        weights = []
        for f in valid:
            mn, mx = f.get("min_season"), f.get("max_season")
            if mn is None and mx is None:
                weights.append(2)       # any-season: decent chance
            elif mn == season and mx == season:
                weights.append(3)       # peak season: strongly preferred
            elif mn == season or mx == season:
                weights.append(1)       # edge match: allowed but less likely
            elif mn is not None and mx is not None and mn != mx and self._season_in_range(season, mn, mx):
                weights.append(1)       # multi-season range: allowed
            else:
                weights.append(1)

        festival = random.choices(valid, weights=weights, k=1)[0]
        if self.food >= festival["food_cost"] and self.gold >= festival["gold_cost"]:
            self.food -= festival["food_cost"]
            self.gold -= festival["gold_cost"]
            # Set category-specific cooldown
            cat = festival.get("cooldown_category", "common")
            cd_min, cd_max = self.FESTIVAL_COOLDOWN_RANGES.get(cat, (20, 40))
            self._festival_category_cooldowns[cat] = random.randint(cd_min, cd_max)
            # Also set legacy global cooldown for backward compat
            self.festival_cooldown = random.randint(20, 40)

            # Apply morale boost via people_obj
            if people_obj:
                for c in people_obj.citizens:
                    if c.alive:
                        c.morale += festival["morale_boost"]
                        c.morale = max(0, min(100, c.morale))
                        c.remember(f"Celebrated {festival['name']}!")
                people_obj.births_this_season += 1  # festivals spark new life

            # Use custom narrative if available
            narrative = festival.get("narrative",
                f"The people of Ashfall gather to celebrate {festival['name']} with joy and feasting.")

            # Bonus resources
            bonus_note = ""
            if "bonus_resource" in festival and "bonus_amount" in festival:
                res = festival["bonus_resource"]
                amt = festival["bonus_amount"]
                setattr(self, res, getattr(self, res) + amt)
                emoji = {"food": "🍞", "wood": "🪵", "stone": "🪨", "gold": "💰"}.get(res, "")
                bonus_note = f" Bonus: +{amt}{emoji}!"

            # Lore chance
            if festival.get("lore_chance") and random.random() < 0.40:
                lore = (
                    f"Festival lore: During {festival['name']}, an elder shared a half-remembered tale "
                    f"of the Sleepers — 'They walked among us as friends, and the land dreamed with them.'"
                )
                if hasattr(_w, 'world') and hasattr(_w.world, 'collect_lore'):
                    _w.world.collect_lore(lore)
                bonus_note += " A lore fragment was recalled!"

            # Ash-Bloom chance
            if festival.get("ash_bloom_chance") and random.random() < festival["ash_bloom_chance"]:
                if hasattr(_w, 'world'):
                    _w.world._ash_blooms_collected += 1
                    bloom_num = _w.world._ash_blooms_collected
                    self.gold += 12
                    bonus_note += f" An Ash-Bloom crystallized during the vigil! [Bloom #{bloom_num}]"

            self.kingdom_log.append(
                f"🎉 FESTIVAL: {festival['name']}! {narrative} "
                f"Morale +{festival['morale_boost']} "
                f"(-{festival['food_cost']}🍞 -{festival['gold_cost']}💰){bonus_note}"
            )
            return {
                "name": festival["name"],
                "morale_boost": festival["morale_boost"],
                "food_cost": festival["food_cost"],
                "gold_cost": festival["gold_cost"],
                "narrative": narrative,
                "bonus_note": bonus_note,
            }
        return None

    def _season_in_range(self, season, min_s, max_s):
        """Check if a season falls within a range (inclusive), wrapping around year-end."""
        seasons = ["spring", "summer", "autumn", "winter"]
        idx = seasons.index(season)
        min_idx = seasons.index(min_s)
        max_idx = seasons.index(max_s)
        if min_idx <= max_idx:
            return min_idx <= idx <= max_idx
        else:
            # Wraps around: e.g. autumn→winter→spring
            return idx >= min_idx or idx <= max_idx

    # ── TERRITORY YIELDS ────────────────────────────────────
    def _territory_yields(self, world_obj=None):
        """Accumulate passive resource yields from all territory.
        Uses world.TERRAIN data if available; falls back to a hardcoded
        minimal set so the method works even without world.py.

        Yields scale with population: more workers extract more from each
        region.  Baseline is 50 pop = 1.0x.  Scales smoothly between
        0.5x (tiny settlement) and 2.0x (thriving town).  Cap at 2.0x."""
        yields = {"food": 0, "wood": 0, "stone": 0, "gold": 0}

        # ── Population workforce scaling ──
        # Baseline: 50 population extracts full base yields.
        # Every 50 pop above baseline adds ~0.5x to the multiplier, capped at 2.0x.
        # Below 50 pop, yields taper down to a floor of 0.5x (lone scouts forage).
        pop_factor = max(0.5, min(2.0, self.population / 50.0))

        try:
            from world import TERRAIN
            for region in self.territory:
                if region in TERRAIN:
                    y = TERRAIN[region]["yields"]
                    for key in yields:
                        base = y.get(key, 0)
                        # Scale integer yields but preserve fractions for accumulation
                        yields[key] += int(round(base * pop_factor))
        except ImportError:
            # Minimal fallback
            for region in self.territory:
                if region == "the_vale":
                    yields["food"] += int(round(5 * pop_factor))
                    yields["wood"] += int(round(2 * pop_factor))
                elif region == "old_oak_ridge":
                    yields["food"] += int(round(1 * pop_factor))
                    yields["wood"] += int(round(8 * pop_factor))
                    yields["stone"] += int(round(3 * pop_factor))
        return yields

    # ── RAIDS ───────────────────────────────────────────────
    # ── PATROL ────────────────────────────────────────────
    def _patrol(self, people_obj=None, world_obj=None):
        """Assign scouts to patrol discovered territories.
        Patrols reduce raid chance and may discover resources or threats.
        Returns (patrol_reduction, discoveries list)."""
        if not people_obj:
            return 0.0, []

        # Find available scouts (not on escort, not already patrolling)
        scouts = [c for c in people_obj.citizens
                  if c.alive and c.role == "scout"
                  and not getattr(c, 'on_escort', False)
                  and not getattr(c, 'on_patrol', False)]
        if not scouts:
            return 0.0, []

        # Each scout can patrol one territory
        discoveries = []
        patrol_reduction = 0.0

        # ── Guard Tower watchtower network enhances all patrols ──
        tower_bonuses = self.guard_tower_bonuses()
        patrol_pct = tower_bonuses["patrol_bonus_pct"] / 100.0  # 0.0, 0.05, or 0.12

        # ── Early Warning → Patrol synergy: yesterday's watchtower alert sharpens today's scouts ──
        alert_bonus = 0.0
        alert_narrative = ""
        if self._early_warning_bonus > 0:
            alert_bonus = 0.06 * self._early_warning_bonus  # +6% discovery per alert (caps naturally)
            self._early_warning_bonus = max(0, self._early_warning_bonus - 1)
            if alert_bonus > 0:
                alert_narrative = " (scouts on high alert from watchtower warning)"

        for scout in scouts[:3]:  # max 3 scouts on patrol per tick
            # Pick a territory — prefer discovered, unscouted ones
            candidates = [t for t in self.territory
                          if self.patrol_active.get(t) != scout.name]
            if not candidates:
                candidates = self.territory[:]
            territory = random.choice(candidates)

            scout.on_patrol = True
            self.patrol_active[territory] = scout.name

            # Base patrol effect: -1% raid chance per scout, enhanced by watchtowers
            patrol_reduction += 0.01 * (1 + patrol_pct)

            # Scout skill matters, amplified by tower coordination
            skill_bonus = getattr(scout, 'combat_skill', 10) / 100.0
            patrol_reduction += skill_bonus * 0.005 * (1 + patrol_pct)

            # Discovery chance: 8% base + 2% per 10 combat skill, towers help spot
            # Early warning alerts give bonus discovery chance
            discover_chance = (0.08 + skill_bonus * 0.02) * (1 + patrol_pct) + alert_bonus
            if random.random() < discover_chance:
                find_type = random.choices(
                    ["cache", "threat", "lore", "nothing"],
                    weights=[40, 25, 15, 20]
                )[0]

                if find_type == "cache":
                    res = random.choice(["food", "wood", "stone", "gold"])
                    amt = random.randint(3, 12)
                    setattr(self, res, getattr(self, res) + amt)
                    emoji = {"food": "🍞", "wood": "🪵", "stone": "🪨", "gold": "💰"}.get(res, "")
                    discoveries.append(
                        f"🔍 PATROL: {scout.name} found a hidden cache in {territory} — +{amt}{emoji}!"
                    )
                elif find_type == "threat":
                    creature = random.choice(["shadow-fox", "marsh-drake", "thorn-bear", "ridge-wolf"])
                    discoveries.append(
                        f"⚠️ PATROL: {scout.name} spotted a {creature} near {territory} — the guard has been alerted."
                    )
                    # Early warning: small defense bonus for this tick
                    self.defense_bonus += 1
                elif find_type == "lore":
                    # Collect a lore fragment about the territory
                    lore_fragment = f"Scout {scout.name} found ancient runes in {territory} hinting at deeper secrets."
                    discoveries.append(
                        f"📜 PATROL: {scout.name} discovered ancient markings in {territory} — new lore fragment!"
                    )
                    # Register with world's lore system
                    if world_obj and hasattr(world_obj, 'collect_lore'):
                        world_obj.collect_lore(lore_fragment)

                self.patrol_log.append({
                    "day": getattr(world_obj, 'day', 0) if world_obj else 0,
                    "territory": territory,
                    "scout": scout.name,
                    "find": find_type,
                })

            # Clear patrol flag after tick
            scout.on_patrol = False
            # Clean up patrol_active for next tick
            if self.patrol_active.get(territory) == scout.name:
                del self.patrol_active[territory]

        return patrol_reduction, discoveries

    def _roll_raid(self, world_obj=None, patrol_reduction=0.0):
        """Check if a raid occurs this tick. Returns raid info or None."""
        # Raids get more likely as kingdom grows richer
        wealth_factor = min(3.0, 1.0 + (self.gold + self.food) / 300)
        base_chance = 0.03 * wealth_factor

        # Walls deter raids
        wall_penalty = 0.005 * self.buildings.get("walls", 0)
        # Patrols reduce raid chance
        chance = max(0.01, base_chance - wall_penalty - patrol_reduction)

        if random.random() > chance:
            return None

        raid_strength = random.randint(3, 8) + self.population // 20
        return {"strength": raid_strength}

    def _resolve_raid(self, raid_info, world_obj=None, people_obj=None):
        """Resolve a raid. Returns raid outcome dict.
        Territory defense bonus (deep-scouted regions, Sleeper alliance) is included
        via defense_rating(world_obj)."""
        defense = self.defense_rating(world_obj)
        # ── Territory defense breakdown for narrative ──
        territory_bonus = 0
        if world_obj and hasattr(world_obj, 'territory_defense_bonus'):
            territory_bonus = world_obj.territory_defense_bonus()
        raid_strength = raid_info["strength"]
        narrative = ""
        gold_lost = 0
        food_lost = 0
        gold_gained = 0
        food_gained = 0

        # ── Guard Tower Early Warning: towers spot raiders, reduce their strength ──
        tower_bonuses = self.guard_tower_bonuses()
        early_warning_pct = tower_bonuses["early_warning_pct"]
        early_warning_triggered = False
        if early_warning_pct > 0 and random.random() * 100 < early_warning_pct:
            reduction = max(1, raid_strength // 4)
            raid_strength = max(1, raid_strength - reduction)
            early_warning_triggered = True
            # ── Watchtower → Patrol synergy: scouts who spotted raiders gain sharper eyes ──
            self._early_warning_bonus += 1
            self.kingdom_log.append(
                f"🔔 EARLY WARNING: Watchtowers spotted raiders! Raid weakened (strength reduced by {reduction}). "
                f"Scouts are on high alert — patrols more effective tomorrow."
            )

        if defense >= raid_strength + 2:
            result = "victory"
            territory_note = f" +{territory_bonus} terrain" if territory_bonus > 0 else ""
            # ── Raid loot: victors claim spoils ──
            gold_gained = random.randint(4, 12) + raid_strength * 2
            self.gold += gold_gained
            # 35% chance of bonus resources from raiders' supplies
            loot_bonus = ""
            if random.random() < 0.35:
                loot_type = random.choice(["food", "wood", "stone"])
                loot_amount = random.randint(3, 10) + raid_strength
                if loot_type == "food":
                    self.food += loot_amount
                    loot_bonus = f", {loot_amount}🍞"
                    food_gained = loot_amount
                elif loot_type == "wood":
                    self.wood += loot_amount
                    loot_bonus = f", {loot_amount}🪵"
                elif loot_type == "stone":
                    self.stone += loot_amount
                    loot_bonus = f", {loot_amount}🪨"
            narrative = (
                f"⚔️ RAID REPELLED! {raid_strength} raiders met our walls and guard "
                f"(defense {defense}{territory_note}). Spoils: +{gold_gained}g{loot_bonus}!"
            )
        elif defense >= raid_strength:
            result = "draw"
            gold_lost = random.randint(2, 8)
            food_lost = random.randint(2, 8)
            self.gold = max(0, self.gold - gold_lost)
            self.food = max(0, self.food - food_lost)
            narrative = (
                f"⚔️ RAID STALEMATE! {raid_strength} raiders clashed with our defenders "
                f"(defense {defense}). We held but lost {gold_lost}g and {food_lost}🍞."
            )
        else:
            result = "defeat"
            gold_lost = random.randint(8, 25)
            food_lost = random.randint(8, 25)
            casualties = random.randint(1, 3)
            self.gold = max(0, self.gold - gold_lost)
            self.food = max(0, self.food - food_lost)
            self.population = max(1, self.population - casualties)
            narrative = (
                f"💀 RAID! {raid_strength} raiders overwhelmed our defense ({defense}). "
                f"Lost {gold_lost}g, {food_lost}🍞, and {casualties} souls."
            )
            # Kill citizens if we have people
            if people_obj:
                alive = [c for c in people_obj.citizens if c.alive]
                for _ in range(min(casualties, len(alive))):
                    victim = random.choice(alive)
                    victim.alive = False
                    victim.health = 0
                    victim.remember("Slain during a raid on Ashfall.")
                    alive.remove(victim)

        morale_effect = {"victory": 5, "draw": -3, "defeat": -8}.get(result, 0)
        if people_obj:
            for c in people_obj.citizens:
                if c.alive:
                    c.morale += morale_effect
                    c.morale = max(0, min(100, c.morale))

        if result == "victory":
            self.raids_survived += 1
        elif result == "defeat":
            self.raids_lost += 1
        else:
            self.raids_survived += 1

        self.kingdom_log.append(
            f"Day {world_obj.day if world_obj else '?'}: {narrative}"
        )

        return {
            "type": "raid",
            "result": result,
            "strength": raid_strength,
            "defense": defense,
            "gold_lost": gold_lost,
            "food_lost": food_lost,
            "gold_gained": gold_gained,
            "food_gained": food_gained,
            "morale_effect": morale_effect,
            "narrative": narrative,
        }

    # ── MILESTONES ──────────────────────────────────────────
    MILESTONE_DEFS = {
        "first_wall": ("Stone Walls", "Built the first wall", lambda k: k.buildings.get("walls", 0) >= 1),
        "fortress": ("Fortress", "Reached defense rating 20+", lambda k: k.defense_rating() >= 20),
        "trade_hub": ("Trade Hub", "Established 3+ trade routes", lambda k: len(k.trade_routes) >= 3),
        "market_town": ("Market Town", "Built a market", lambda k: k.buildings.get("market", 0) >= 1),
        "tavern_open": ("Tavern's Hearth", "Opened the first tavern", lambda k: k.buildings.get("tavern", 0) >= 1),
        "deep_well": ("Deep Well", "Upgraded the well to level 3", lambda k: k.well_level >= 3),
        "trade_district": ("Trade District", "Built 2+ markets and a market hall", lambda k: k.buildings.get("market", 0) >= 2 and k.buildings.get("market_hall", 0) >= 1),
        "grand_bazaar": ("Grand Bazaar", "Upgraded market hall to level 3", lambda k: k.market_hall_level >= 3),
        "watchtower_network": ("Watchtower Network", "Upgraded guard towers to level 3", lambda k: k.guard_tower_level >= 3),
    }

    def _check_milestones(self):
        """Check and unlock any new milestones."""
        for key, (name, desc, check) in self.MILESTONE_DEFS.items():
            if key not in self.milestones and check(self):
                self.milestones.append(key)
                self.kingdom_log.append(f"🏆 MILESTONE: {name} — {desc}")

    # ── DEPENDENCY RATIO ────────────────────────────────────
    def dependency_ratio(self, people_obj=None):
        """Return weighted dependents / working_adults.
        Age-aware: citizens 60+ count as partial dependents (they're near retirement),
        and children under 10 are heavier dependents. 
        A high ratio (>0.5) means few workers support many dependents.
        Returns 0 if no people_obj; 999 if no workers at all."""
        if people_obj is None:
            return 0.0
        workers = 0.0
        dependents = 0.0
        for c in people_obj.citizens:
            if not c.alive:
                continue
            age = getattr(c, 'age', 30)
            role = c.role
            if role == "child":
                # Younger children are heavier dependents
                dependents += 1.2 if age < 10 else 1.0
            elif role == "elder":
                dependents += 1.0
            elif age >= 60:
                # Still working but near retirement — count as 0.5 dependent
                workers += 0.5
                dependents += 0.5
            else:
                workers += 1.0
        if workers <= 0:
            return 999.0  # all dependents — extreme case
        return dependents / workers

    # ── AUTO-EXPAND ─────────────────────────────────────────
    def _auto_expand(self, people_obj=None, world_obj=None):
        """Smart auto-build based on kingdom needs.
        Uses dependency ratio to adjust thresholds:
        more elders/children → more aggressive housing & food preservation.
        Returns list of event strings for what was built."""
        events = []

        # ── Dependency-aware expansion ──
        dep_ratio = self.dependency_ratio(people_obj)

        # 1. Huts: build when housing is inadequate.
        #    With many dependents, we need extra housing headroom
        #    (elders need comfort, children need space to grow).
        #    Buffer formula: 8 + dep_ratio*25 → 8 (no dependents) to 33 (all dependents).
        housing_buffer = int(8 + dep_ratio * 25)  # 8 base → up to ~33 with high ratio
        need_huts = max(0, self.population - self.housing_capacity() + housing_buffer)
        if need_huts > 0 and self.wood >= self.BLUEPRINTS["huts"][1] + 2:
            # Cap scales with dependency: 2 (low) → 5 (crisis)
            max_huts = 2
            if dep_ratio > 0.3:
                max_huts = 3
            if dep_ratio > 0.7:
                max_huts = 4
            if dep_ratio > 1.2:
                max_huts = 5
            to_build = min(need_huts // 10 + 1, max_huts)
            for _ in range(to_build):
                ok, msg = self.build("huts")
                if ok:
                    events.append(f"🛖 AUTO-BUILD: {msg}")
                else:
                    break

        # 2. Well: build one early if missing; upgrade when resources allow
        if self.buildings.get("well", 0) == 0 and self.population >= 25:
            bp = self.BLUEPRINTS["well"]
            if self.stone >= bp[0] + 1 and self.wood >= bp[1] + 1:
                ok, msg = self.build("well")
                if ok:
                    events.append(f"💧 AUTO-BUILD: {msg}")
        elif self.buildings.get("well", 0) >= 1 and self.well_level < 3:
            # Auto-upgrade well when resources are plentiful
            next_level = self.well_level + 1
            cost = self.WELL_UPGRADE_COSTS.get(next_level)
            if cost and self.stone >= cost[0] + 5 and self.wood >= cost[1] + 5 and self.gold >= cost[2] + 8:
                ok, msg = self.upgrade_well()
                if ok:
                    events.append(f"💧 AUTO-UPGRADE: {msg}")

        # 3. Market: build when population grows and gold allows
        if (self.buildings.get("market", 0) == 0
                and self.population >= 30
                and self.gold >= 20):
            bp = self.BLUEPRINTS["market"]
            if (self.stone >= bp[0] + 2 and self.wood >= bp[1] + 2
                    and self.gold >= bp[2] + 5):
                ok, msg = self.build("market")
                if ok:
                    events.append(f"💱 AUTO-BUILD: {msg} — trade rates improved!")

        # 3.5 Second Market: build when population grows beyond one market's reach
        if (self.buildings.get("market", 0) == 1
                and self.population >= 55
                and self.gold >= 50
                and self.buildings.get("market_hall", 0) == 0):
            bp = self.BLUEPRINTS["market"]
            if (self.stone >= bp[0] + 3 and self.wood >= bp[1] + 3
                    and self.gold >= bp[2] + 10):
                ok, msg = self.build("market")
                if ok:
                    events.append(f"💱 AUTO-BUILD: {msg} — second market opens, trade district forming!")

        # 3.6 Third Market: large kingdoms need more commerce hubs
        if (self.buildings.get("market", 0) == 2
                and self.population >= 100
                and self.gold >= 80
                and self.buildings.get("market_hall", 0) >= 1):
            bp = self.BLUEPRINTS["market"]
            if (self.stone >= bp[0] + 5 and self.wood >= bp[1] + 5
                    and self.gold >= bp[2] + 15):
                ok, msg = self.build("market")
                if ok:
                    events.append(f"💱 AUTO-BUILD: {msg} — third market opens, trade district bustling!")

        # 3.7 Fourth Market: needed to unlock Grand Bazaar (market_hall L3 requires 4+ markets)
        if (self.buildings.get("market", 0) == 3
                and self.population >= 130
                and self.gold >= 110
                and self.buildings.get("market_hall", 0) >= 1
                and self.market_hall_level >= 2):
            bp = self.BLUEPRINTS["market"]
            if (self.stone >= bp[0] + 8 and self.wood >= bp[1] + 8
                    and self.gold >= bp[2] + 20):
                ok, msg = self.build("market")
                if ok:
                    events.append(f"💱 AUTO-BUILD: {msg} — fourth market opens, grand bazaar within reach!")

        # 4. Storehouse: build when storage is near capacity.
        #    Cap based on population to prevent spam (1 per 12 pop, min 2, max 8).
        max_storehouses = max(2, min(8, self.population // 12))
        cap = self.storage_capacity()
        for res in ("food", "wood", "stone"):
            current = getattr(self, res)
            if (current > cap * 0.85
                    and self.buildings.get("storehouse", 0) < max_storehouses):
                bp = self.BLUEPRINTS["storehouse"]
                if (self.stone >= bp[0] + 1 and self.wood >= bp[1] + 1
                        and self.gold >= bp[2] + 1):
                    ok, msg = self.build("storehouse")
                    if ok:
                        events.append(f"📦 AUTO-BUILD: {msg} (storage now {self.storage_capacity()}, max {max_storehouses})")
                        break  # one storehouse per tick is enough

        # 5. Tavern: build when population grows and morale needs a lift.
        #    Elders value gathering places — lower pop threshold when dependency is high.
        tavern_pop_threshold = max(35, int(50 - dep_ratio * 15))
        if (self.buildings.get("tavern", 0) == 0
                and self.population >= tavern_pop_threshold
                and self.gold >= 20
                and self.wood >= 16):
            t_cost = self.BLUEPRINTS["tavern"]
            if (self.stone >= t_cost[0] + 1 and self.wood >= t_cost[1] + 1
                    and self.gold >= t_cost[2] + 5):
                ok, msg = self.build("tavern")
                if ok:
                    events.append(f"🍺 AUTO-BUILD: {msg} — the people rejoice!")

        # 6. Market Hall: build when we have 2+ markets and enough gold
        if (self.buildings.get("market_hall", 0) == 0
                and self.buildings.get("market", 0) >= 2
                and self.gold >= 40):
            mh_cost = self.BLUEPRINTS["market_hall"]
            if (self.stone >= mh_cost[0] + 3 and self.wood >= mh_cost[1] + 3
                    and self.gold >= mh_cost[2] + 10):
                ok, msg = self.build("market_hall")
                if ok:
                    events.append(f"🏛️ AUTO-BUILD: {msg} — trade flourishes!")

        # 6.5 Market Hall Upgrade: auto-upgrade when resources and prerequisites allow
        if (self.buildings.get("market_hall", 0) >= 1
                and self.market_hall_level < 3):
            next_lvl = self.market_hall_level + 1
            cost = self.MARKET_HALL_UPGRADE_COSTS.get(next_lvl)
            if cost:
                # Check prerequisites
                prereqs_ok = True
                if next_lvl == 2 and self.buildings.get("market", 0) < 3:
                    prereqs_ok = False
                if next_lvl == 3:
                    if self.buildings.get("market", 0) < 4:
                        prereqs_ok = False
                    if "trade_district" not in self.milestones:
                        prereqs_ok = False
                if prereqs_ok:
                    if (self.stone >= cost[0] + 8 and self.wood >= cost[1] + 8
                            and self.gold >= cost[2] + 15):
                        ok, msg = self.upgrade_market_hall()
                        if ok:
                            events.append(f"🏛️ AUTO-UPGRADE: {msg}")

        # 6.7 Guard Tower Upgrade: auto-upgrade when resources and prerequisites allow
        if (self.buildings.get("guard_tower", 0) >= 1
                and self.guard_tower_level < 3):
            next_lvl = self.guard_tower_level + 1
            cost = self.GUARD_TOWER_UPGRADE_COSTS.get(next_lvl)
            if cost:
                prereqs_ok = True
                if next_lvl == 2:
                    if self.buildings.get("guard_tower", 0) < 2:
                        prereqs_ok = False
                    if self.buildings.get("walls", 0) < 4:
                        prereqs_ok = False
                if next_lvl == 3:
                    if self.buildings.get("guard_tower", 0) < 3:
                        prereqs_ok = False
                    if self.buildings.get("walls", 0) < 6:
                        prereqs_ok = False
                    if "fortress" not in self.milestones:
                        prereqs_ok = False
                if prereqs_ok:
                    if (self.stone >= cost[0] + 6 and self.wood >= cost[1] + 6
                            and self.gold >= cost[2] + 10):
                        ok, msg = self.upgrade_guard_tower()
                        if ok:
                            events.append(f"🗼 AUTO-UPGRADE: {msg}")

        # 7. Walls: build if defense is weak and resources allow.
        #    With many dependents, defense is more critical — raise the threshold.
        wall_threshold = 10 + int(dep_ratio * 10)  # 10 → up to ~20
        if (self.defense_rating() < wall_threshold
                and self.buildings.get("walls", 0) < 5
                and self.stone >= 10 and self.wood >= 6):
            ok, msg = self.build("walls")
            if ok:
                events.append(f"🧱 AUTO-BUILD: {msg} (defense now {self.defense_rating()})")

        # 8. Guard Tower: build when walls exist but defense still needs a boost.
        #    Threshold scales with dependency — more vulnerable citizens = need stronger defense.
        #    Now builds up to 3 towers — one per tick when under sustained threat.
        #    Dynamic defense from tower upgrades means later towers are more valuable.
        towers_already = self.buildings.get("guard_tower", 0)
        max_towers = 3
        tower_threshold = 12 + int(dep_ratio * 8) + (towers_already * 3)  # 12 → up to ~30
        if (self.defense_rating() < tower_threshold
                and self.buildings.get("walls", 0) >= 1
                and towers_already < max_towers
                and self.stone >= 12 and self.wood >= 8 and self.gold >= 8):
            ok, msg = self.build("guard_tower")
            if ok:
                events.append(f"🗼 AUTO-BUILD: {msg} (#{towers_already+1}, defense now {self.defense_rating()})")

        # 8.5 Barracks: houses guards (+8 housing, +2 defense each).
        #     Critical when elders can't fight. Scales with guard count.
        #     First barracks: dep_ratio > 0.35 OR 5+ guards.
        #     Additional: guards > barracks * 4 (each barracks holds ~4 efficiently).
        guard_count = self.recruit_count(people_obj, "guard") if people_obj else 0
        barracks_count = self.buildings.get("barracks", 0)
        barracks_capacity = barracks_count * 4  # each barracks supports ~4 guards

        need_barracks = False
        barracks_reason = ""

        if barracks_count == 0:
            # First barracks: moderate dependency + some guards, OR just many guards
            if dep_ratio > 0.35 and guard_count >= 2:
                need_barracks = True
                barracks_reason = "dependency rising, guards need housing"
            elif guard_count >= 5:
                need_barracks = True
                barracks_reason = f"{guard_count} guards need proper housing"
        elif guard_count > barracks_capacity + 1:
            # Additional barracks when guards outgrow capacity
            need_barracks = True
            barracks_reason = f"{guard_count} guards exceeds {barracks_capacity} capacity"
        elif dep_ratio > 0.8 and guard_count > barracks_capacity:
            # High dependency: elders need extra protection, build ahead
            need_barracks = True
            barracks_reason = f"critical: {guard_count} guards, dep_ratio {dep_ratio:.2f}"

        if need_barracks:
            bp = self.BLUEPRINTS["barracks"]
            if (self.stone >= bp[0] + 1 and self.wood >= bp[1] + 1
                    and self.gold >= bp[2] + 1):
                ok, msg = self.build("barracks")
                if ok:
                    events.append(
                        f"🏕️ AUTO-BUILD: {msg} — {barracks_reason} "
                        f"(defense now {self.defense_rating()})"
                    )

        # 9. Granary: build when food supply is growing and needs preserving.
        #    Two modes:
        #    a) PROSPERITY: food above threshold (normal growth)
        #    b) CRISIS: dependency > 0.8, food below safety — build to preserve scraps
        #    Threshold scales with dependency ratio — more dependents = need preservation sooner.
        granary_count = self.buildings.get("granary", 0)
        max_granaries = max(2, int(3 + dep_ratio * 3))

        granary_food_threshold = max(
            int(self.population * 1.2),
            int(self.population * (1.8 - dep_ratio * 0.6))
        )

        # Crisis trigger: high dependency, low food, desperate need for preservation
        crisis_granary = (
            dep_ratio > 0.8
            and self.food < self.population * 1.5
            and granary_count < max_granaries
            and self.food > 0  # there must be something to preserve
        )

        # Prosperity trigger: food growing well, build granaries to stockpile
        prosperity_granary = (
            self.food > granary_food_threshold
            and granary_count < max_granaries
        )

        # Additional granary threshold (lower bar after first one)
        granary2_threshold = max(
            int(self.population * (2.5 - dep_ratio * 0.8)),
            int(self.population * 1.7)
        )
        prosperity_granary2 = (
            granary_count >= 1
            and granary_count < max_granaries
            and self.food > granary2_threshold
            and self.food > self.storage_capacity() * 0.75
        )

        if (crisis_granary or prosperity_granary or prosperity_granary2):
            bp = self.BLUEPRINTS["granary"]
            if (self.stone >= bp[0] + 1 and self.wood >= bp[1] + 1
                    and self.gold >= bp[2] + 1):
                ok, msg = self.build("granary")
                if ok:
                    tag = "⚠️ CRISIS" if crisis_granary else "🌾"
                    reason = "emergency preservation" if crisis_granary else                              "doubling down" if granary_count >= 1 else                              "food preservation improved"
                    events.append(
                        f"{tag} AUTO-BUILD: {msg} — {reason}! "
                        f"(dep_ratio {dep_ratio:.2f})"
                    )
                    self.kingdom_log.append(
                        f"{tag} Granary built — storage now {self.storage_capacity()}, "
                        f"dependency ratio {dep_ratio:.2f}"
                    )

        # 9.5 Auto-recruit guards when dependency is high (elders can't fight).
        #     The kingdom needs protectors when the workforce is aging.
        guard_count = self.recruit_count(people_obj, "guard") if people_obj else 0
        if (dep_ratio > 0.7 and guard_count < max(5, self.population // 8)
                and self.gold >= self.TRAINING_COST.get("guard", 5) + 5):
            ok, msg = self.recruit(people_obj, "guard")
            if ok:
                events.append(f"🛡️ AUTO-RECRUIT: {msg} (dep_ratio {dep_ratio:.2f} — elders need protectors)")

        # 9.6 Auto-recruit scouts when dependency is low (young kingdom exploring)
        scout_count = self.recruit_count(people_obj, "scout") if people_obj else 0
        if (dep_ratio < 0.4 and scout_count < 2
                and self.gold >= self.TRAINING_COST.get("scout", 3) + 5
                and self.population >= 30):
            ok, msg = self.recruit(people_obj, "scout")
            if ok:
                events.append(f"🔭 AUTO-RECRUIT: {msg} — exploring the frontier")

        # 10. Auto Trade Routes: establish when we have 2+ territories, markets, and gold.
        #    One new route per tick maximum. Routes generate passive gold income.
        if (len(self.territory) >= 2
                and self.buildings.get("market", 0) >= 1
                and self.gold >= 30
                and len(self.trade_routes) < min(3, len(self.territory))):
            for i, a in enumerate(self.territory):
                for b in self.territory[i+1:]:
                    already = any(set(r["regions"]) == {a, b} for r in self.trade_routes)
                    if already:
                        continue
                    cost = 15 + len(self.trade_routes) * 5
                    if self.gold >= cost + 10:
                        ok, msg = self.establish_trade_route(a, b, world_obj)
                        if ok:
                            events.append(f"📦 AUTO-TRADE: {msg}")
                        break
                else:
                    continue
                break

        # 10. Territory Expansion: discover new regions when the kingdom has scouts,
        #     population, and defense to support expansion.
        if world_obj and hasattr(world_obj, 'discover') and hasattr(world_obj, 'can_discover'):
            scout_count = self.recruit_count(people_obj, "scout") if people_obj else 0
            # Requirements: scouts to explore, enough people to hold land, and walls to defend it
            if scout_count >= 2 and self.population >= 40 and self.defense_rating() >= 20:
                # Prioritize low-danger regions first, then medium, then high
                priority_order = ["sunfire_plains", "glimmer_marsh", "ironroot_depths", "the_ashen_copse"]
                for region in priority_order:
                    if region not in self.territory and world_obj.can_discover(region):
                        if world_obj.discover(region):
                            try:
                                from world import TERRAIN as _TERRAIN
                                desc = _TERRAIN.get(region, {}).get('desc', 'new land')
                            except ImportError:
                                desc = 'new land'
                            events.append(
                                f"🗺️ AUTO-EXPAND: Scouts claimed {region} — {desc[:80]}"
                            )
                            break  # one territory per tick

        return events

    # ── TICK ────────────────────────────────────────────────
    def tick(self, people_obj=None, world_obj=None, day=None):
        """End-of-cycle update. Collects worker production, feeds
        population, handles growth, raids, caravans, and seasonal effects.

        Returns a summary dict.
        """
        summary = {"day": day or "?", "fed": True, "produced": {}, "events": []}

        # 0. Auto-expand before growth check (pass people_obj for dep-ratio)
        auto_events = self._auto_expand(people_obj, world_obj)
        summary["events"].extend(auto_events)

        # 0.2 Patrol — scouts reduce raid chance and may discover resources
        patrol_reduction, patrol_discoveries = self._patrol(people_obj, world_obj)
        if patrol_discoveries:
            summary["events"].extend(patrol_discoveries)
            summary["patrol"] = patrol_discoveries

        # 0.5 Trade route income
        route_result = self._trade_route_income(world_obj)
        if isinstance(route_result, tuple):
            route_gold, maturity_events = route_result
        else:
            route_gold = route_result
            maturity_events = []
        if route_gold:
            self.gold += route_gold
            summary["trade_routes"] = route_gold
        if maturity_events:
            summary["events"].extend(maturity_events)

        # 0.6 Grand Bazaar daily gold tick (market_hall L3)
        bazaar_gold, bazaar_msg = self._grand_bazaar_income()
        if bazaar_gold:
            self.gold += bazaar_gold
            summary["grand_bazaar"] = bazaar_gold
            if bazaar_msg:
                summary["events"].append(bazaar_msg)

        # 0.65 Grand Bazaar wisdom resonance — wise citizens spot hidden deals
        wisdom_gold, wisdom_msg = self._grand_bazaar_wisdom_resonance(people_obj)
        if wisdom_gold:
            summary["bazaar_wisdom"] = wisdom_gold
            if wisdom_msg:
                summary["events"].append(wisdom_msg)

        # 0.66 Dream-Husk Market integration — when Husks visit, the economy shifts
        husk_gold, husk_msg = self._dream_husk_market_bonus(world_obj, people_obj)
        if husk_gold:
            summary["dream_husk_market"] = husk_gold
            if husk_msg:
                summary["events"].append(husk_msg)

        # 0.67 Dream-Bond Market Bridge — bonded citizens trade instinctively with Husks
        bond_market_gold, bond_market_msg = self._dream_bond_market_bridge(world_obj, people_obj)
        if bond_market_gold:
            summary["dream_bond_market"] = bond_market_gold
            if bond_market_msg:
                summary["events"].append(bond_market_msg)

        # 0.68 Economy → Defense Bridge — market wealth funds fortifications
        defense_narrative, defense_building, defense_cost = self._economy_defense_bridge(world_obj)
        if defense_narrative:
            self.kingdom_log.append(defense_narrative)
            summary["events"].append(defense_narrative)
            summary["economy_defense"] = {"building": defense_building, "cost": defense_cost}

        # 0.69 Trade Route → Lair Bridge — ancient routes reveal lair secrets
        lair_narrative, lair_gold = self._trade_route_lair_bridge(world_obj)
        if lair_narrative:
            self.kingdom_log.append(lair_narrative)
            summary["events"].append(lair_narrative)
            if lair_gold:
                summary["trade_lair_gold"] = lair_gold

        # 0.7 Venerable trade route lore rolls
        trade_lore = self._venerable_trade_lore()
        if trade_lore:
            summary["events"].extend(trade_lore)

        # 0.75 Seasonal trade route lore — peak-season routes carry old memories
        seasonal_lore = self._seasonal_trade_lore(world_obj, people_obj)
        if seasonal_lore:
            summary["events"].extend(seasonal_lore)

        # 0.78 Track supply/demand quest completions for chain detection
        self._track_sd_quest_completions(people_obj, world_obj)

        # 0.8 Market supply/demand events
        sd_narrative, sd_bonus, sd_morale = self._check_supply_demand(people_obj, world_obj)
        if sd_narrative:
            summary["events"].append(f"📊 MARKET: {sd_narrative}")
            summary["supply_demand"] = sd_bonus
            if sd_morale and people_obj:
                for c in people_obj.citizens:
                    if c.alive:
                        c.morale += sd_morale
                        c.morale = max(0, min(100, c.morale))

        # 0.85 Pending market quests — supply/demand events want to spawn faction quests
        if getattr(self, '_pending_market_quest', False) and people_obj:
            self._pending_market_quest = False
            # Try to spawn a trade quest for the Deepwardens if they don't have one active
            if hasattr(people_obj, 'faction_quests') and hasattr(people_obj, 'list_by_faction'):
                if people_obj.faction_quests.get("deepwardens") is None:
                    dw_members = people_obj.list_by_faction("deepwardens")
                    if len(dw_members) >= 3:
                        # Create a simple trade quest
                        age_tier = 1
                        if world_obj and hasattr(world_obj, 'day'):
                            if world_obj.day > 500:
                                age_tier = 4
                            elif world_obj.day > 250:
                                age_tier = 3
                            elif world_obj.day > 100:
                                age_tier = 2
                        age_mult = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}.get(age_tier, 1.0)
                        faction_scale = max(1, len(dw_members) // 5)
                        target_gold = max(1, int(20 * faction_scale * age_mult))
                        quest = {
                            "faction": "deepwardens",
                            "type": "trade_guild",
                            "name": "Honor the Merchant Guild",
                            "desc": "The Merchant Guild has recognized Ashfall — now the Deepwardens must prove the kingdom's trade worth by accumulating wealth and resources to secure a permanent guild charter.",
                            "target": {"gold": target_gold},
                            "progress": {"gold": 0},
                            "reward_morale": max(1, int(10 * age_mult)),
                            "reward_resources": {"gold": max(1, int(25 * age_mult))},
                            "narrative_complete": "The Merchant Guild charter is signed in the Grand Bazaar. Ashfall is now a Certified Trade Nexus — its markets will be marked on every merchant's map.",
                            "bonus_effect": "gold_rush",
                            "rarity": "rare",
                            "start_day": world_obj.day if world_obj and hasattr(world_obj, 'day') else 0,
                            "deadline": (world_obj.day if world_obj and hasattr(world_obj, 'day') else 0) + 60,
                            "completed": False,
                            "failed": False,
                            "age_tier": age_tier,
                            "tier_name": {1: "🌱T1", 2: "🌿T2", 3: "🌳T3", 4: "🏛️T4"}.get(age_tier, ""),
                        }
                        people_obj.faction_quests["deepwardens"] = quest
                        summary["events"].append(
                            f"✨📜 MERCHANT GUILD QUEST: The Deepwardens undertake "
                            f"'{quest['name']}' — gather {target_gold} gold to secure "
                            f"a permanent guild charter in the Grand Bazaar."
                        )
        # Process pending supply/demand quests (tier 2: multi-faction)
        if getattr(self, '_pending_sd_quests', []) and people_obj:
            for faction, event_name, template in list(self._pending_sd_quests):
                if hasattr(people_obj, 'faction_quests') and hasattr(people_obj, 'list_by_faction'):
                    if people_obj.faction_quests.get(faction) is None:
                        members = people_obj.list_by_faction(faction)
                        if len(members) >= 3:
                            age_tier = 1
                            if world_obj and hasattr(world_obj, 'day'):
                                if world_obj.day > 500:
                                    age_tier = 4
                                elif world_obj.day > 250:
                                    age_tier = 3
                                elif world_obj.day > 100:
                                    age_tier = 2
                            age_mult = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}.get(age_tier, 1.0)
                            faction_scale = max(1, len(members) // 5)
                            # Scale targets and rewards by age and faction size
                            scaled_target = {}
                            for res, amt in template["target"].items():
                                scaled_target[res] = max(1, int(amt * faction_scale * age_mult))
                            scaled_rewards = {}
                            for res, amt in template.get("reward_resources", {}).items():
                                scaled_rewards[res] = max(1, int(amt * age_mult))
                            quest = {
                                "faction": faction,
                                "type": template["type"],
                                "name": template["name"],
                                "desc": template["desc"],
                                "target": scaled_target,
                                "progress": {res: 0 for res in scaled_target},
                                "reward_morale": max(1, int(template.get("reward_morale", 8) * age_mult)),
                                "reward_resources": scaled_rewards,
                                "narrative_complete": template["narrative_complete"],
                                "bonus_effect": template["bonus_effect"],
                                "rarity": template.get("rarity", "common"),
                                "start_day": world_obj.day if world_obj and hasattr(world_obj, 'day') else 0,
                                "deadline": (world_obj.day if world_obj and hasattr(world_obj, 'day') else 0) + 45,
                                "completed": False,
                                "failed": False,
                                "age_tier": age_tier,
                                "tier_name": {1: "🌱T1", 2: "🌿T2", 3: "🌳T3", 4: "🏛️T4"}.get(age_tier, ""),
                            }
                            people_obj.faction_quests[faction] = quest
                            rarity_badge = {"common": "", "rare": "✨", "chain": "🔗"}.get(template.get("rarity", ""), "")
                            summary["events"].append(
                                f"📊📜 {rarity_badge}SUPPLY QUEST ({event_name}): "
                                f"The {faction.title()} undertake '{quest['name']}' — "
                                f"{template['desc'][:80]}..."
                            )
                self._pending_sd_quests.remove((faction, event_name, template))

        # 0.87 Process pending emissary quests (from Sleeper's Emissary caravan tier 3)
        if getattr(self, '_pending_emissary_quests', []) and people_obj:
            for quest in list(self._pending_emissary_quests):
                faction = quest.get("faction")
                if faction and hasattr(people_obj, 'faction_quests'):
                    if people_obj.faction_quests.get(faction) is None:
                        people_obj.faction_quests[faction] = quest
                        rarity_badge = {"common": "", "rare": "✨", "chain": "🔗"}.get(quest.get("rarity", ""), "")
                        summary["events"].append(
                            f"🌊💎 {rarity_badge}EMISSARY QUEST: "
                            f"The {faction.title()} have received '{quest['name']}' "
                            f"from the Sleeper's Emissary — {quest['desc'][:100]}..."
                        )
                    else:
                        # Faction is busy; re-queue (might expire — Emissary doesn't wait forever)
                        pass
                self._pending_emissary_quests.remove(quest)

        # 1. Territory passive yields
        territory_yield = self._territory_yields(world_obj)
        for res, amt in territory_yield.items():
            if amt:
                setattr(self, res, getattr(self, res) + amt)
        if any(territory_yield.values()):
            summary["territory"] = territory_yield

        # 2. Citizens work & produce resources
        if people_obj:
            produced = {"food": 0, "wood": 0, "stone": 0, "gold": 0}
            for c in people_obj.citizens:
                if c.alive:
                    output = c.work(people_obj)
                    for res, amt in output.items():
                        produced[res] = produced.get(res, 0) + amt
                    # Contribute work output to citizen's faction quest
                    people_obj._contribute_to_faction_quest(c, output)
            self.food += produced.get("food", 0)
            self.wood += produced.get("wood", 0)
            self.stone += produced.get("stone", 0)
            self.gold += produced.get("gold", 0)
            summary["produced"] = produced

            # Guards add defense
            guard_count = sum(1 for c in people_obj.citizens
                              if c.alive and c.role == "guard")
            self.defense_bonus = guard_count * 2

        # 3. Seasonal effects (if world available)
        if world_obj:
            if world_obj.season == "winter":
                self.food -= max(1, self.population // 5)
            elif world_obj.season == "summer":
                self.food += max(1, self.population // 10)

        # 3.3 Well bonuses: irrigation provides food, clean water boosts morale
        wb = self.well_bonuses()
        if wb["food_per_day"] > 0:
            self.food += wb["food_per_day"]
            summary["well_food"] = wb["food_per_day"]
        if wb["morale_per_day"] > 0 and people_obj:
            for c in people_obj.citizens:
                if c.alive:
                    c.morale += wb["morale_per_day"]
                    c.morale = max(0, min(100, c.morale))

        # 3.35 Well water-ritual lore events (L2/L3 wells)
        ritual_narrative, ritual_lore_chance, ritual_bonus = self._check_well_rituals()
        if ritual_narrative:
            summary["events"].append(f"💧 WELL RITUAL: {ritual_narrative}")
            summary["well_ritual"] = ritual_bonus
            if ritual_lore_chance and people_obj and hasattr(people_obj, 'lore_fragments'):
                if random.random() * 100 < ritual_lore_chance:
                    people_obj.lore_fragments += 1
                    summary["events"].append(
                        f"📜 LORE: The well ritual revealed a fragment of forgotten knowledge."
                    )
            # Well Ritual → Wisdom Resonance: deep well rituals may bestow wisdom on elders
            if people_obj and hasattr(people_obj, '_well_ritual_wisdom_bestowal'):
                wisdom_chance = 0.35 if self.well_level >= 3 else 0.15
                wisdom_narrative = people_obj._well_ritual_wisdom_bestowal(
                    kingdom_obj=self, chance=wisdom_chance
                )
                if wisdom_narrative:
                    summary["events"].append(wisdom_narrative)

        # 3.4 Tavern Stories
        tavern_story = self._tavern_stories(people_obj, world_obj)
        if tavern_story:
            summary["tavern_story"] = tavern_story
            summary["events"].append(tavern_story["narrative"])

                # 3.5 World Omens: apply resource effects from omens to kingdom
        if world_obj and hasattr(world_obj, 'world_omens'):
            omen = world_obj.world_omens()
            if omen:
                # Resource deltas already applied by apply_event() inside world_omens();
                # we only need to log the narrative here.
                summary["events"].append(
                    f"🌠 OMEN: {omen.get('narrative', 'An omen was witnessed.')[:100]}"
                )

            # 3.6 Creature events — daily chance of wildlife encounters near the kingdom
            if hasattr(world_obj, 'daily_creature_event'):
                creature_event = world_obj.daily_creature_event()
                if creature_event:
                    summary["events"].append(creature_event["narrative"])
                    summary["creature_event"] = creature_event

        # 4. Granary: reduces food spoilage
        granaries = self.buildings.get("granary", 0)
        if granaries > 0:
            vulnerable = max(0, self.food - self.population * 2)
            preserved = min(granaries * 5, vulnerable)
            self.food += preserved

        # 4.5 Storage overflow: resources above cap risk spoilage
        cap = self.storage_capacity()
        for res in ("food", "wood", "stone"):
            current = getattr(self, res)
            if current > cap:
                spoiled = (current - cap) // 4  # 25% of overflow spoils
                if spoiled > 0:
                    setattr(self, res, current - spoiled)
                    summary["events"].append(
                        f"📉 SPOILAGE: {spoiled} {res} lost (storage {cap} exceeded)"
                    )

        # 5. Population eats (1 food per person per day)
        eaten = self.population * 1
        if self.food >= eaten:
            self.food -= eaten
        else:
            fed = self.food
            unfed = self.population - fed
            self.food = 0
            starved = max(1, unfed // 3)
            self.population -= starved
            summary["fed"] = False
            summary["events"].append(
                f"🍂 FAMINE: Only {fed} fed of {eaten} needed. {starved} starved."
            )

        # 6. Growth: population grows when well-fed and housed
        if (self.food > self.population * 2
                and self.population < self.housing_capacity()):
            self.growth_pool += 0.15 + (self.food / max(1, self.population)) * 0.02
            if self.growth_pool >= 1.0:
                new_citizens = int(self.growth_pool)
                self.growth_pool -= new_citizens
                self.population += new_citizens
                summary["events"].append(
                    f"👶 POPULATION BOOM: +{new_citizens} citizens (total {self.population})"
                )
                # Try to create actual citizens via people_obj
                if people_obj:
                    for _ in range(new_citizens):
                        try:
                            from people import Citizen, FIRST_NAMES, FAMILY_NAMES
                            name = f"{random.choice(FIRST_NAMES)} {random.choice(FAMILY_NAMES)}"
                            c = Citizen(
                                name,
                                random.choice(["farmer", "woodcutter", "builder", "scout"]),
                            )
                            if hasattr(people_obj, '_assign_faction'):
                                people_obj._assign_faction(c)
                            people_obj.citizens.append(c)
                        except Exception:
                            pass  # graceful: pop count still updates

        # 6.5 Immigration — settlers drawn by prosperity
        if people_obj and hasattr(people_obj, 'migrate'):
            migration = people_obj.migrate(world_obj)
            if migration:
                summary["immigration"] = migration
                summary["events"].append(migration["message"])

        # 7. Caravans
        caravan = self._roll_caravan(world_obj, people_obj)
        if caravan:
            summary["caravan"] = caravan
            # ── Sleeper's Emissary grants a lore fragment ──
            if caravan.get("extra_lore") and world_obj and hasattr(world_obj, 'collect_lore'):
                world_obj.collect_lore(
                    f"The Sleeper's Emissary sold Ashfall a vial of dream-essence. "
                    f"The liquid whispers when held to the ear — a forgotten name, "
                    f"a place that no longer exists, a song from before the First Fire."
                )
                summary["events"].append(
                    "📜 LORE: The Sleeper's Emissary left more than goods — "
                    "a fragment of the old world, preserved in a glass vial."
                )
            # ── Wisdom Caravan Tier 3: Sleeper's Emissary may leave a quest ──
            emissary_narrative, emissary_quest = self._wisdom_caravan_tier3(
                caravan, world_obj, people_obj
            )
            if emissary_narrative and emissary_quest:
                self._pending_emissary_quests.append(emissary_quest)
                summary["events"].append(emissary_narrative)
            # Auto-escort: if we have 2+ guards, escort the caravan for bonus
            guard_count = self.recruit_count(people_obj, "guard") if people_obj else 0
            if guard_count >= 2 and random.random() < 0.6:
                escort_ok, escort_narrative, escort_bonus = self.escort_caravan(caravan, people_obj)
                if escort_ok:
                    summary["escort"] = escort_bonus
                    summary["events"].append(escort_narrative)

        # 8. Festivals
        festival = self._roll_festival(people_obj)
        if festival:
            summary["festival"] = festival

        # 9. Raids
        raid_info = self._roll_raid(world_obj, patrol_reduction)
        if raid_info:
            raid_result = self._resolve_raid(raid_info, world_obj, people_obj)
            summary["raid"] = raid_result
            summary["events"].append(raid_result.get("narrative", "A raid occurred."))

        self._check_milestones()

        return summary


# ── SINGLETON ────────────────────────────────────────────
kingdom = Kingdom()
