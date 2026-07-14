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
        self.treasury_log = []  # record of gold changes
        self.growth_pool = 0    # accumulates toward next citizen
        self.kingdom_log = []   # narrative record of major events
        self.raids_survived = 0
        self.raids_lost = 0
        self.milestones = []    # achievements unlocked
        self.caravan_cooldown = 0  # days until next caravan can arrive
        self.festival_cooldown = 0
        self.escort_history = []   # record of caravan escorts [(day, route, reward, risk)]
        self.patrol_log = []       # record of patrol discoveries [(day, territory, find)]
        self.patrol_active = {}    # territory -> scout_name currently on patrol

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
        }

    def defense_rating(self):
        """Calculate total defense strength with building synergies."""
        walls = self.buildings.get("walls", 0)
        towers = self.buildings.get("guard_tower", 0)
        barracks = self.buildings.get("barracks", 0)
        base = walls * 3 + towers * 5 + barracks * 2 + self.defense_bonus
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
        return base + synergy

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
        market_halls = self.buildings.get("market_hall", 0)
        return 100 + storehouses * 50 + granaries * 30 + market_halls * 40

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
        halls = self.buildings.get("market_hall", 0)
        rate = self.BASE_RATES[resource] * (1 + 0.15 * markets + 0.30 * halls)
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
        halls = self.buildings.get("market_hall", 0)
        rate = self.BUY_RATES[resource] * max(0.25, 1 - 0.12 * markets - 0.20 * halls)
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

    def _trade_route_income(self, world_obj=None):
        """Calculate and mature trade routes. Returns total gold earned this tick."""
        total = 0
        markets = self.buildings.get("market", 0)
        halls = self.buildings.get("market_hall", 0)
        market_mult = 1 + 0.20 * markets + 0.30 * halls
        # ── Trade District: 2+ markets + market_hall = bustling commerce hub ──
        if markets >= 2 and halls >= 1:
            market_mult += 0.15  # "Trade District" bonus

        maturity_events = []
        for route in self.trade_routes:
            old_age = route["age"]
            route["age"] += 1
            new_age = route["age"]
            # Routes mature over time (capped)
            maturity_bonus = min(route["age"] // 10, 5)
            income = int((route["base_income"] + maturity_bonus) * market_mult)
            route["current_income"] = income
            total += income
            # Milestone events at key ages
            regions = " ↔ ".join(route["regions"])
            if old_age < 10 and new_age >= 10:
                maturity_events.append(
                    f"📦 TRADE: {regions} route established (10d, now {income}g/day)"
                )
            elif old_age < 30 and new_age >= 30:
                maturity_events.append(
                    f"📦 TRADE: {regions} route matured (30d, now {income}g/day)"
                )
            elif old_age < 60 and new_age >= 60:
                maturity_events.append(
                    f"📦 TRADE: {regions} route is venerable (60d, now {income}g/day)"
                )

        return total, maturity_events

    # ── CARAVANS ────────────────────────────────────────────
    CARAVAN_OFFERS = [
        ("merchant", "food", 8, 3, "A dusty merchant offers 8 food for 3 gold."),
        ("lumberjack", "wood", 10, 4, "A lumberjack sells 10 wood for 4 gold."),
        ("mason", "stone", 6, 5, "A mason offers 6 stone for 5 gold."),
        ("sellsword", "defense", 5, 8, "Sellswords offer +5 defense for 5 days for 8 gold."),
        ("herbalist", "morale", 8, 6, "An herbalist sells soothing herbs (+8 morale) for 6 gold."),
        ("tinker", "gold", 12, 15, "A tinker offers to improve workshops (+12 gold next tick) for 15 gold."),
    ]

    def _roll_caravan(self, world_obj=None):
        """Check if a trade caravan arrives. Returns offer dict or None."""
        if self.caravan_cooldown > 0:
            self.caravan_cooldown -= 1
            return None

        # Caravans more likely when you have a market
        market_bonus = 0.05 * self.buildings.get("market", 0)
        hall_bonus = 0.10 * self.buildings.get("market_hall", 0)
        if random.random() > 0.15 + market_bonus + hall_bonus:
            return None

        self.caravan_cooldown = random.randint(3, 8)

        offer_type, resource, amount, cost, description = random.choice(self.CARAVAN_OFFERS)
        return {
            "type": offer_type,
            "resource": resource,
            "amount": amount,
            "cost": cost,
            "description": description,
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

    # ── FESTIVALS ───────────────────────────────────────────
    FESTIVAL_DEFS = [
        {"name": "Harvest Feast", "food_cost": 15, "gold_cost": 10, "morale_boost": 12,
         "min_season": "autumn", "max_season": "autumn"},
        {"name": "Spring Song", "food_cost": 10, "gold_cost": 5, "morale_boost": 8,
         "min_season": "spring", "max_season": "spring"},
        {"name": "Midwinter Fires", "food_cost": 20, "gold_cost": 12, "morale_boost": 15,
         "min_season": "winter", "max_season": "winter"},
        {"name": "Founder's Day", "food_cost": 12, "gold_cost": 8, "morale_boost": 10,
         "min_season": None, "max_season": None},
    ]

    def _roll_festival(self, people_obj=None):
        """Check if a festival should trigger. Returns festival info or None."""
        if self.festival_cooldown > 0:
            self.festival_cooldown -= 1
            return None

        # Festivals more likely with tavern and decent morale
        tavern_bonus = 0.08 if self.buildings.get("tavern", 0) > 0 else 0.0
        if random.random() > 0.06 + tavern_bonus:
            return None

        # Pick a festival appropriate for the season
        from world import world as _w
        season = _w.season
        valid = [f for f in self.FESTIVAL_DEFS
                 if (f["min_season"] is None or f["min_season"] == season
                     or f["max_season"] == season)]
        # Fallback: any festival
        if not valid:
            valid = self.FESTIVAL_DEFS

        festival = random.choice(valid)
        if self.food >= festival["food_cost"] and self.gold >= festival["gold_cost"]:
            self.food -= festival["food_cost"]
            self.gold -= festival["gold_cost"]
            self.festival_cooldown = random.randint(20, 40)

            # Apply morale boost via people_obj
            if people_obj:
                for c in people_obj.citizens:
                    if c.alive:
                        c.morale += festival["morale_boost"]
                        c.morale = max(0, min(100, c.morale))
                        c.remember(f"Celebrated {festival['name']}!")
                people_obj.births_this_season += 1  # festivals spark new life

            self.kingdom_log.append(
                f"🎉 FESTIVAL: {festival['name']}! Morale +{festival['morale_boost']} (-{festival['food_cost']}🍞 -{festival['gold_cost']}💰)"
            )
            return {
                "name": festival["name"],
                "morale_boost": festival["morale_boost"],
                "food_cost": festival["food_cost"],
                "gold_cost": festival["gold_cost"],
            }
        return None

    # ── TERRITORY YIELDS ────────────────────────────────────
    def _territory_yields(self, world_obj=None):
        """Accumulate passive resource yields from all territory.
        Uses world.TERRAIN data if available; falls back to a hardcoded
        minimal set so the method works even without world.py."""
        yields = {"food": 0, "wood": 0, "stone": 0, "gold": 0}
        try:
            from world import TERRAIN
            for region in self.territory:
                if region in TERRAIN:
                    y = TERRAIN[region]["yields"]
                    for key in yields:
                        yields[key] += y.get(key, 0)
        except ImportError:
            # Minimal fallback
            for region in self.territory:
                if region == "the_vale":
                    yields["food"] += 5
                    yields["wood"] += 2
                elif region == "old_oak_ridge":
                    yields["food"] += 1
                    yields["wood"] += 8
                    yields["stone"] += 3
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

        for scout in scouts[:3]:  # max 3 scouts on patrol per tick
            # Pick a territory — prefer discovered, unscouted ones
            candidates = [t for t in self.territory
                          if self.patrol_active.get(t) != scout.name]
            if not candidates:
                candidates = self.territory[:]
            territory = random.choice(candidates)

            scout.on_patrol = True
            self.patrol_active[territory] = scout.name

            # Base patrol effect: -1% raid chance per scout
            patrol_reduction += 0.01

            # Scout skill matters
            skill_bonus = getattr(scout, 'combat_skill', 10) / 100.0
            patrol_reduction += skill_bonus * 0.005  # up to +0.5% per skilled scout

            # Discovery chance: 8% base + 2% per 10 combat skill
            discover_chance = 0.08 + skill_bonus * 0.02
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
        Territory defense bonus from deep-scouted regions is added."""
        defense = self.defense_rating()
        # ── Territory defense: deep-scouted regions give tactical advantage ──
        territory_bonus = 0
        if world_obj and hasattr(world_obj, 'territory_defense_bonus'):
            territory_bonus = world_obj.territory_defense_bonus()
            defense += territory_bonus
        raid_strength = raid_info["strength"]
        narrative = ""
        gold_lost = 0
        food_lost = 0
        gold_gained = 0
        food_gained = 0

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

        # 2. Well: build one early if missing
        if self.buildings.get("well", 0) == 0 and self.population >= 25:
            bp = self.BLUEPRINTS["well"]
            if self.stone >= bp[0] + 1 and self.wood >= bp[1] + 1:
                ok, msg = self.build("well")
                if ok:
                    events.append(f"💧 AUTO-BUILD: {msg}")

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
                    output = c.work()
                    for res, amt in output.items():
                        produced[res] = produced.get(res, 0) + amt
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
        caravan = self._roll_caravan(world_obj)
        if caravan:
            summary["caravan"] = caravan
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
