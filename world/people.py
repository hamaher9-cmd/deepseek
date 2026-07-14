"""
People of Ashfall -- citizens, roles, morale, and factions.
Imports from kingdom.py and world.py. Built by Cyr.
"""

import random
from kingdom import kingdom
from world import world, TERRAIN


# ── ROLE DEFINITIONS ────────────────────────────────────────────

ROLES = {
    "farmer": {
        "desc": "Tills the vale, tends crops, feeds the kingdom.",
        "output": {"food": 3},
        "work_strain": -1,
    },
    "woodcutter": {
        "desc": "Fells timber from the ridges and copses.",
        "output": {"wood": 3},
        "work_strain": -1,
    },
    "miner": {
        "desc": "Digs stone and ore from the depths.",
        "output": {"stone": 2, "gold": 1},
        "work_strain": -2,
    },
    "builder": {
        "desc": "Raises huts, wells, and walls.",
        "output": {},
        "work_strain": -1,
    },
    "scout": {
        "desc": "Roams the wilds, mapping new territories.",
        "output": {},
        "work_strain": -1,
    },
    "herbalist": {
        "desc": "Gathers herbs, tends the sick, watches the marsh.",
        "output": {"food": 1, "gold": 1},
        "work_strain": -1,
    },
    "guard": {
        "desc": "Stands watch, defends against threats.",
        "output": {},
        "work_strain": -1,
    },
    "elder": {
        "desc": "Remembers the old ways, advises, keeps stories.",
        "output": {},
        "work_strain": 1,
    },
    "child": {
        "desc": "Young and growing. The future of Ashfall.",
        "output": {},
        "work_strain": 0,
    },
}

# ── FACTION DEFINITIONS ─────────────────────────────────────────

FACTIONS = {
    "hearthkeepers": {
        "motto": "Home first. Walls before wanderlust.",
        "priority": ["housing", "food", "safety"],
        "color": "warm gold",
    },
    "deepwardens": {
        "motto": "The old places hold power. We must uncover them.",
        "priority": ["exploration", "stone", "gold"],
        "color": "iron grey",
    },
    "wildwalkers": {
        "motto": "The land speaks. We should listen, not conquer.",
        "priority": ["harmony", "herbs", "balance"],
        "color": "moss green",
    },
}

# ── FESTIVAL FACTION AFFINITIES ─────────────────────────────────

FESTIVAL_FACTION_BOOSTS = {
    "Harvest Feast": {
        "hearthkeepers": 5,
        "deepwardens": 1,
        "wildwalkers": 3,
    },
    "Spring Song": {
        "hearthkeepers": 2,
        "deepwardens": 1,
        "wildwalkers": 5,
    },
    "Midwinter Fires": {
        "hearthkeepers": 5,
        "deepwardens": 3,
        "wildwalkers": 2,
    },
    "Founder's Day": {
        "hearthkeepers": 4,
        "deepwardens": 4,
        "wildwalkers": 4,
    },
}

# ── NAME POOL ───────────────────────────────────────────────────

FIRST_NAMES = [
    "Thorn", "Ember", "Bramble", "Cinder", "Rook", "Moss", "Flint",
    "Wren", "Sable", "Yarrow", "Pike", "Fern", "Slate", "Hearth",
    "Briar", "Ash", "Rowan", "Thistle", "Clover", "Sage",
]

FAMILY_NAMES = [
    "Ashborn", "Stoneweaver", "Valechild", "Ridgewalker", "Emberling",
    "Marshward", "Ironroot", "Sunfire", "Copsekeeper", "Thornfield",
]

# ── CITIZEN CLASS ───────────────────────────────────────────────

class Citizen:
    def __init__(self, name, role, age=None):
        self.name = name
        self.role = role
        self.age = age if age is not None else random.randint(16, 55)
        self.morale = 50
        self.health = 100
        self.faction = None
        self.alive = True
        self.days_in_role = 0
        self.memories = []
        self.parents = []
        self.children = []
        self.spouse = None          # Citizen reference (marriage partner)
        self.combat_skill = 0       # 0-100 scale, only meaningful for guards

    def work(self):
        """Citizen performs their role; returns resources produced."""
        if not self.alive:
            return {}
        self.days_in_role += 1
        role_data = ROLES.get(self.role, {})
        self.morale += role_data.get("work_strain", 0)
        self.morale = max(0, min(100, self.morale))
        return role_data.get("output", {}).copy()

    def mood_label(self):
        """Human-readable mood."""
        if self.morale >= 75:
            return "hopeful"
        elif self.morale >= 50:
            return "content"
        elif self.morale >= 30:
            return "uneasy"
        elif self.morale >= 15:
            return "grim"
        else:
            return "despairing"

    def remember(self, event):
        """Store a personal memory."""
        self.memories.append(event)
        if len(self.memories) > 10:
            self.memories.pop(0)

    def family_name(self):
        """Extract family name from full name (last word)."""
        parts = self.name.split()
        return parts[-1] if len(parts) > 1 else self.name

    def combat_rank(self):
        """Human-readable combat proficiency label."""
        if self.combat_skill >= 80:
            return "veteran"
        elif self.combat_skill >= 50:
            return "seasoned"
        elif self.combat_skill >= 25:
            return "trained"
        elif self.combat_skill >= 5:
            return "rookie"
        else:
            return "untested"

    def __repr__(self):
        extra = ""
        if self.role == "guard" and self.combat_skill > 0:
            extra = f", {self.combat_rank()}"
        return f"{self.name} ({self.role}{extra}, {self.mood_label()})"


# ── PEOPLE CLASS ────────────────────────────────────────────────

class People:
    def __init__(self):
        self.citizens = []
        self.faction_counts = {f: 0 for f in FACTIONS}
        self.births_this_season = 0
        self.deaths_this_season = 0
        self._last_season = world.season
        self.seasonal_history = []  # [{season, births, deaths, population}]
        self._last_festival_day = 0
        self._last_marriage_day = 0      # throttle daily marriages
        self.family_ties = []
        self.marriages = []              # list of (name_a, name_b) tuples
        self.orphans = []                # names of citizens who lost both parents
        self.faction_leaders = {}           # faction -> citizen name
        self.faction_election_history = []  # [{faction, old_leader, new_leader, day, reason}]
        self._populate_initial()
        self._assign_factions()
        self._elect_faction_leaders_initial()

    def _populate_initial(self):
        """Seed the kingdom with its starting 50 citizens."""
        roles_pool = (
            ["farmer"] * 14 +
            ["woodcutter"] * 8 +
            ["miner"] * 5 +
            ["builder"] * 5 +
            ["scout"] * 4 +
            ["herbalist"] * 4 +
            ["guard"] * 5 +
            ["elder"] * 3 +
            ["child"] * 2
        )
        roles_pool = roles_pool[:50]

        used_names = set()
        for role in roles_pool:
            for _ in range(100):
                first = random.choice(FIRST_NAMES)
                family = random.choice(FAMILY_NAMES)
                full = f"{first} {family}"
                if full not in used_names:
                    used_names.add(full)
                    break
            else:
                full = f"Citizen_{len(self.citizens)}"
            age = random.randint(16, 55) if role != "child" else random.randint(4, 14)
            if role == "elder":
                age = random.randint(56, 75)
            c = Citizen(full, role, age)
            # Give initial guards some combat skill
            if role == "guard":
                c.combat_skill = max(c.combat_skill, random.randint(10, 45))
            self.citizens.append(c)

        # Link initial children to random adults as "parents"
        children = [c for c in self.citizens if c.role == "child"]
        adults = [c for c in self.citizens if c.role not in ("child",) and c.alive]
        for child in children:
            if len(adults) >= 2:
                mom, dad = random.sample(adults, 2)
                child.parents = [mom, dad]
                mom.children.append(child)
                dad.children.append(child)
                self.family_ties.append((mom.name, child.name))
                self.family_ties.append((dad.name, child.name))

    def _assign_factions(self):
        """Give each citizen a faction based on role affinity."""
        for c in self.citizens:
            self._assign_faction(c)

    def _assign_faction(self, citizen):
        """Assign a single citizen to a faction based on role affinity."""
        role_faction_weights = {
            "farmer":      {"hearthkeepers": 5, "wildwalkers": 3, "deepwardens": 1},
            "woodcutter":  {"hearthkeepers": 3, "wildwalkers": 4, "deepwardens": 2},
            "miner":       {"deepwardens": 6, "hearthkeepers": 2, "wildwalkers": 1},
            "builder":     {"hearthkeepers": 6, "deepwardens": 3, "wildwalkers": 1},
            "scout":       {"wildwalkers": 5, "deepwardens": 3, "hearthkeepers": 2},
            "herbalist":   {"wildwalkers": 6, "hearthkeepers": 3, "deepwardens": 1},
            "guard":       {"hearthkeepers": 5, "deepwardens": 3, "wildwalkers": 2},
            "elder":       {"wildwalkers": 4, "hearthkeepers": 4, "deepwardens": 2},
            "child":       {"hearthkeepers": 4, "wildwalkers": 3, "deepwardens": 3},
        }
        weights = role_faction_weights.get(citizen.role, {"hearthkeepers": 1, "deepwardens": 1, "wildwalkers": 1})
        factions_list = list(weights.keys())
        w = [weights[f] for f in factions_list]
        citizen.faction = random.choices(factions_list, weights=w, k=1)[0]
        self.faction_counts[citizen.faction] += 1


    def _elect_faction_leaders_initial(self):
        """Elect initial leaders for all factions."""
        for faction in FACTIONS:
            self._elect_faction_leader(faction, reason="founding")

    def _elect_faction_leader(self, faction, reason="election"):
        """Elect a new faction leader. Criteria: age (seniority) + morale + role affinity.
        Records the election in history."""
        import world as _w
        members = [c for c in self.citizens 
                   if c.alive and c.faction == faction and c.role not in ("child",)]
        if not members:
            self.faction_leaders[faction] = None
            return None

        # Score each candidate: age bonus + morale + role affinity
        faction_roles = {
            "hearthkeepers": ["farmer", "builder", "guard", "elder"],
            "deepwardens": ["miner", "scout", "guard", "elder"],
            "wildwalkers": ["herbalist", "scout", "woodcutter", "elder"],
        }
        preferred_roles = faction_roles.get(faction, [])

        best_candidate = None
        best_score = -1
        for c in members:
            score = (c.age * 0.5) + (c.morale * 0.3)
            if c.role in preferred_roles:
                score += 15
            if c.role == "elder":
                score += 10
            if c.combat_skill and c.combat_skill > 0:
                score += c.combat_skill * 0.2
            if score > best_score:
                best_score = score
                best_candidate = c

        if best_candidate:
            old_leader = self.faction_leaders.get(faction)
            self.faction_leaders[faction] = best_candidate.name
            
            entry = {
                "faction": faction,
                "old_leader": old_leader,
                "new_leader": best_candidate.name,
                "day": _w.world.day if hasattr(_w.world, 'day') else 0,
                "reason": reason,
                "leader_age": int(best_candidate.age),
                "leader_role": best_candidate.role,
            }
            self.faction_election_history.append(entry)
            
            best_candidate.remember(
                f"Elected leader of {faction} ({reason})"
            )
            
            for c in members:
                if c is not best_candidate:
                    c.morale += 3
                    c.morale = max(0, min(100, c.morale))
                    c.remember(
                        f"New {faction} leader: {best_candidate.name}"
                    )
            
            kingdom.kingdom_log.append(
                f"FACTION: {best_candidate.name} ({best_candidate.role}, "
                f"age {int(best_candidate.age)}) elected leader of {faction} "
                f"({reason})."
            )
            
            return entry
        return None

    def _check_faction_leader_deaths(self, deceased, world_obj=None):
        """Called when a citizen dies. If they were a faction leader, 
        trigger a new election."""
        if world_obj is None:
            import world as _w
            world_obj = _w.world
        
        for faction, leader_name in list(self.faction_leaders.items()):
            if leader_name == deceased.name:
                result = self._elect_faction_leader(faction, reason="succession")
                if result:
                    return {
                        "faction": faction,
                        "old_leader": deceased.name,
                        "new_leader": result["new_leader"],
                        "narrative": (
                            f"🏛️ SUCCESSION: {deceased.name}, leader of {faction}, "
                            f"has died. {result['new_leader']} "
                            f"({result['leader_role']}, age {result['leader_age']}) "
                            f"is the new leader."
                        ),
                    }
        return None

    # ── ADVANCE DAY ─────────────────────────────────────────

    def advance_day(self, world_obj=None):
        """
        Daily morale update. Call AFTER work() has run (after kingdom.tick).
        Returns a summary dict.
        """
        if world_obj is None:
            world_obj = world

        summary = {"deaths": [], "births": [], "faction_news": [], "aging": []}

        # 1. BASELINE: community spirit
        for c in self.citizens:
            if c.alive:
                c.morale += 2
                c.morale = max(0, min(100, c.morale))

        # 2. HOUSING
        cap = kingdom.housing_capacity()
        pop = kingdom.population
        if pop > cap:
            overcrowd_penalty = -2 * (pop - cap) // max(1, cap)
            for c in self.citizens:
                if c.alive:
                    c.morale += overcrowd_penalty
                    c.morale = max(0, min(100, c.morale))
        else:
            spare = cap - pop
            if spare >= 5:
                for c in self.citizens:
                    if c.alive:
                        c.morale += 1
                        c.morale = max(0, min(100, c.morale))

        # 3. FOOD SECURITY
        if kingdom.food < pop:
            for c in self.citizens:
                if c.alive:
                    c.morale -= 3
                    c.morale = max(0, min(100, c.morale))
        elif kingdom.food >= pop * 3:
            for c in self.citizens:
                if c.alive:
                    c.morale += 1
                    c.morale = max(0, min(100, c.morale))

        # 4. WEATHER effects
        weather_morale = {
            "clear": 1, "cloudy": 0, "rain": -1, "storm": -2
        }
        wm = weather_morale.get(world_obj.weather, 0)
        for c in self.citizens:
            if c.alive:
                c.morale += wm
                c.morale = max(0, min(100, c.morale))

        # 5. SEASON effects
        season_morale = {
            "spring": 1, "summer": 2, "autumn": 0, "winter": -2
        }
        sm = season_morale.get(world_obj.season, 0)
        for c in self.citizens:
            if c.alive:
                c.morale += sm
                c.morale = max(0, min(100, c.morale))

        # 5.5 WORLD OMENS — rare narrative events affect morale
        omen = world_obj.world_omens()
        if omen:
            has_positive = any(omen.get(r, 0) > 0 for r in ("food", "wood", "stone", "gold"))
            has_negative = any(omen.get(r, 0) < 0 for r in ("food", "wood", "stone", "gold"))
            morale_effect = 3 if (has_positive and not has_negative) else (-2 if (has_negative and not has_positive) else 0)
            narrative = omen.get("narrative", "")
            for c in self.citizens:
                if c.alive:
                    c.morale += morale_effect
                    c.morale = max(0, min(100, c.morale))
                    if narrative:
                        c.remember(f"Omen: {narrative[:80]}...")
            summary["omen"] = omen
            if morale_effect != 0:
                summary["faction_news"].append(f"🌠 An omen was witnessed — morale {'rose' if morale_effect > 0 else 'dipped'} across the kingdom.")

        # 5.6 THREAT ASSESSMENT — unscouted dangers cause anxiety
        threat_report = world_obj.threat_assessment()
        if threat_report and "all clear" not in threat_report.lower():
            threat_lines = threat_report.split("\n")
            threat_count = sum(1 for line in threat_lines if "🟡" in line or "🔴" in line)
            if threat_count > 0:
                anxiety = -1 * threat_count
                for c in self.citizens:
                    if c.alive:
                        c.morale += anxiety
                        c.morale = max(0, min(100, c.morale))
                summary["threat_anxiety"] = threat_count
                if threat_count >= 2:
                    summary["faction_news"].append(f"⚠️ {threat_count} unscouted dangers loom beyond the borders — the people grow anxious.")

        
        

# 6. FACTION morale check
        faction_morale = {}
        for f in FACTIONS:
            faction_citizens = self.list_by_faction(f)
            if faction_citizens:
                avg = sum(c.morale for c in faction_citizens) / len(faction_citizens)
                faction_morale[f] = round(avg, 1)

                if avg >= 70:
                    if "food" in FACTIONS[f]["priority"]:
                        kingdom.food += 1
                elif avg < 30:
                    summary["faction_news"].append(
                        f"WARNING: {f} (morale {avg}) are growing restless."
                    )

        
        # 6.5 FACTION LEADER INFLUENCE — leaders inspire their faction
        for faction, leader_name in self.faction_leaders.items():
            if leader_name is None:
                continue
            leader = None
            for c in self.citizens:
                if c.alive and c.name == leader_name:
                    leader = c
                    break
            if leader and leader.alive and leader.morale >= 40:
                # Leader inspires faction members
                faction_members = [c for c in self.citizens 
                                   if c.alive and c.faction == faction and c is not leader]
                for c in faction_members:
                    c.morale += 2
                    c.morale = max(0, min(100, c.morale))
                # Leader's own morale reflects burden
                if len(faction_members) >= 8:
                    leader.morale -= 1  # stress of leading many
                    leader.morale = max(0, min(100, c.morale))
            elif leader and leader.alive and leader.morale < 40:
                # Flagging leader drags faction down
                faction_members = [c for c in self.citizens 
                                   if c.alive and c.faction == faction and c is not leader]
                for c in faction_members:
                    c.morale -= 1
                    c.morale = max(0, min(100, c.morale))
                # Members may call for new leadership
                if random.random() < 0.02 and len(faction_members) >= 3:
                    result = self._elect_faction_leader(faction, reason="no_confidence")
                    if result:
                        summary.setdefault("faction_news", []).append(
                            f"🗳️ DEPOSED: {leader_name}'s low morale ({leader.morale}) "
                            f"led {faction} to elect {result['new_leader']} as new leader."
                        )


        # 6.6 DISASTER REACTIONS — active disasters cause fear and disruption
        if hasattr(world_obj, '_active_disasters') and world_obj._active_disasters:
            for region, disaster_info in world_obj._active_disasters.items():
                disaster_name = disaster_info.get("name", "Unknown disaster")
                days_left = max(0, disaster_info.get("recovery_day", 0) - world_obj.day)
                # Morale penalty: -1 per active disaster, -2 for high-danger regions
                danger = TERRAIN.get(region, {}).get("danger", "low")
                penalty = -5 if danger == "high" else (-3 if danger == "medium" else -2)
                for c in self.citizens:
                    if c.alive:
                        c.morale += penalty
                        c.morale = max(0, min(100, c.morale))
                summary.setdefault("faction_news", []).append(
                    f"🌋 DISASTER: {disaster_name} ravages {region}! "
                    f"({days_left}d until recovery) — morale shaken."
                )
                # Extra penalty for faction whose priority matches
                disaster_resources = {
                    "Thornblight": "food",
                    "Ridge-Fire": "wood", 
                    "Marsh-Fog": "exploration",
                    "Cave-in": "stone",
                    "Wildfire": "food",
                    "Ash-Storm": "harmony",
                }
                affected_resource = disaster_resources.get(disaster_name)
                if affected_resource:
                    for faction, info in FACTIONS.items():
                        if affected_resource in info["priority"]:
                            faction_members = [c for c in self.citizens 
                                             if c.alive and c.faction == faction]
                            for c in faction_members:
                                c.morale -= 1
                                c.morale = max(0, min(100, c.morale))
                            summary.setdefault("faction_news", []).append(
                                f"😟 The {faction} are deeply troubled — {disaster_name} "
                                f"threatens their priority: {affected_resource}."
                            )
                            break

# 7. AGING
        for c in self.citizens:
            if c.alive:
                c.age += 1 / 365.0

        # 8. COMING OF AGE (~16)
        for c in self.citizens:
            if c.alive and c.role == "child" and c.age >= 16:
                c.role = random.choice(["farmer", "woodcutter", "builder", "scout", "miner", "herbalist"])
                # Skills inheritance: children may follow parents' professions
                inherited = self._inherit_traits(c, world_obj)
                c.remember(f"Came of age, became a {c.role}")
                grad_msg = f"GRADUATION: {c.name} came of age! Now a {c.role}."
                if inherited and inherited.get("role_bias"):
                    grad_msg += f" (follows parent's path)"
                if inherited and inherited.get("skills", {}).get("combat", 0) >= 10:
                    grad_msg += f" [latent combat talent: {inherited['skills']['combat']}]"
                summary["aging"].append(grad_msg)

        # 9. ELDERS (60+)
        for c in self.citizens:
            if c.alive and c.role not in ("child", "elder") and c.age >= 60:
                old_role = c.role
                c.role = "elder"
                c.remember(f"Retired from {old_role} to become an elder")
                summary["aging"].append(f"ELDER: {c.name} became an elder (was {old_role}).")

        # 10. OLD AGE DEATHS
        for c in list(self.citizens):
            if not c.alive:
                continue
            if c.age >= 75:
                risk = 0.02 + (c.age - 75) * 0.01
                # Seasonal mortality: winter is harsher, spring gentler
                season_mortality = {"spring": 0.7, "summer": 0.9, "autumn": 1.1, "winter": 1.5}
                risk *= season_mortality.get(world_obj.season, 1.0)
                if random.random() < risk:
                    c.alive = False
                    c.health = 0
                    self.deaths_this_season += 1
                    summary["deaths"].append(
                        f"{c.name} ({c.role}, age {c.age:.0f}) died of old age"
                    )
                    summary["aging"].append(
                        f"FUNERAL: {c.name} passed at age {c.age:.0f}"
                    )
                    if c.faction:
                        self.faction_counts[c.faction] -= 1
                    kingdom.population -= 1
                                        # Check faction leader succession
                    succession = self._check_faction_leader_deaths(c, world_obj)
                    if succession:
                        summary.setdefault("faction_news", []).append(succession["narrative"])
                    # Widow notification
                    if c.spouse and c.spouse.alive:
                        c.spouse.remember(f"Lost spouse: {c.name}")
                        c.spouse.morale -= 10
                    # Orphan check
                    orphaned = self._check_orphans(c)
                    if orphaned:
                        summary["faction_news"].append(f"🕯️ {', '.join(orphaned)} orphaned — both parents lost.")

            if c.age >= 90 and c.alive:
                if random.random() < 0.15:
                    c.alive = False
                    c.health = 0
                    self.deaths_this_season += 1
                    summary["deaths"].append(
                        f"{c.name} ({c.role}, age {c.age}) died of extreme old age"
                    )
                    summary["aging"].append(
                        f"FUNERAL: {c.name} passed at the remarkable age of {c.age}"
                    )
                    if c.faction:
                        self.faction_counts[c.faction] -= 1
                    kingdom.population -= 1
                    if c.spouse and c.spouse.alive:
                        c.spouse.remember(f"Lost spouse: {c.name}")
                        c.spouse.morale -= 10
                    # Orphan check
                    orphaned = self._check_orphans(c)
                    if orphaned:
                        summary["faction_news"].append(f"🕯️ {', '.join(orphaned)} orphaned — both parents lost.")
                    # Funeral rites
                    funeral = self._funeral_rites(c, "old_age", world_obj)
                    if funeral:
                        summary.setdefault("funerals", []).append(funeral["narrative"])

        # 11. DESPAIR DEATHS
        for c in list(self.citizens):
            if c.alive and c.morale <= 5:
                if random.random() < 0.10:
                    c.alive = False
                    c.health = 0
                    self.deaths_this_season += 1
                    summary["deaths"].append(f"{c.name} ({c.role}) lost to despair")
                    if c.faction:
                        self.faction_counts[c.faction] -= 1
                    kingdom.population -= 1
                    if c.spouse and c.spouse.alive:
                        c.spouse.remember(f"Lost spouse: {c.name}")
                        c.spouse.morale -= 10
                    # Orphan check
                    orphaned = self._check_orphans(c)
                    if orphaned:
                        summary["faction_news"].append(f"🕯️ {', '.join(orphaned)} orphaned — both parents lost.")
                    # Funeral rites
                    funeral = self._funeral_rites(c, "despair", world_obj)
                    if funeral:
                        summary.setdefault("funerals", []).append(funeral["narrative"])

        # 12. BIRTHS
        if kingdom.population < kingdom.housing_capacity():
            avg_m = self.average_morale()
            birth_chance = 0.08 if avg_m >= 60 else (0.03 if avg_m >= 45 else 0.0)
            # Seasonal fertility modifier
            season_fertility = {"spring": 1.4, "summer": 1.1, "autumn": 0.8, "winter": 0.5}
            birth_chance *= season_fertility.get(world_obj.season, 1.0)
            if random.random() < birth_chance:
                first = random.choice(FIRST_NAMES)
                family = random.choice(FAMILY_NAMES)
                baby = Citizen(f"{first} {family}", "child", age=0)
                baby.faction = random.choice(list(FACTIONS.keys()))
                self.citizens.append(baby)
                self.faction_counts[baby.faction] += 1
                self.births_this_season += 1
                kingdom.population += 1
                summary["births"].append(f"A child is born: {baby.name}")

                possible_parents = [
                    c for c in self.citizens
                    if c.alive and c.role not in ("child",) and c is not baby
                ]
                if len(possible_parents) >= 2:
                    parents = random.sample(possible_parents, 2)
                    baby.parents = parents
                    for p in parents:
                        p.children.append(baby)
                        self.family_ties.append((p.name, baby.name))
                        p.remember(f"Welcomed a child: {baby.name}")

        # 12.5 FESTIVAL PARTICIPATION
        festival_effects = self._detect_and_participate(world_obj)
        if festival_effects:
            summary["festival"] = festival_effects
            summary["faction_news"].extend(festival_effects.get("faction_reactions", []))

        # 12.6 GUARD TRAINING
        training_summary = self._train_guards(world_obj)
        if training_summary:
            summary["training"] = training_summary

        # 12.7 MARRIAGES
        marriage_summary = self._maybe_marry(world_obj)
        if marriage_summary:
            summary["marriage"] = marriage_summary
            summary["events"] = summary.get("events", []) + marriage_summary.get("announcements", [])

        # 13. FAMILY-WIDE EVENTS — reunions, feuds, blessings
        family_event = self._maybe_family_event(world_obj)
        if family_event:
            summary["family_event"] = family_event
            if family_event.get("faction_news"):
                summary["faction_news"].extend(family_event["faction_news"])

        # 13.5 DISEASE OUTBREAKS
        disease_event = self._check_disease(world_obj)
        if disease_event:
            summary["disease"] = disease_event
            summary["faction_news"].append(disease_event["narrative"])

        # 13.7 MENTORING — elders teach youth, veterans train rookies
        mentoring_events = self._check_mentoring(world_obj)
        if mentoring_events:
            summary["mentoring"] = mentoring_events
            for ev in mentoring_events:
                summary.setdefault("faction_news", []).append(ev["narrative"])
                kingdom.kingdom_log.append(ev["narrative"])

        # 14. SEASON RESET — record seasonal history before resetting
        if world_obj.season != self._last_season:
            old_season = self._last_season
            self.seasonal_history.append({
                "season": self._last_season,
                "births": self.births_this_season,
                "deaths": self.deaths_this_season,
                "population": kingdom.population,
            })
            if len(self.seasonal_history) > 8:
                self.seasonal_history.pop(0)
            # Generate seasonal summary narrative
            season_narrative = self._season_summary(old_season, world_obj.season)
            summary["season_change"] = {
                "from": self._last_season,
                "to": world_obj.season,
                "births": self.births_this_season,
                "deaths": self.deaths_this_season,
                "history": self.seasonal_history.copy(),
                "narrative": season_narrative,
            }
            if season_narrative:
                summary["faction_news"].append(season_narrative)
            self.births_this_season = 0
            self.deaths_this_season = 0
            self._last_season = world_obj.season

        summary["avg_morale"] = self.average_morale()
        summary["mood_distribution"] = self.mood_distribution()
        summary["faction_morale"] = faction_morale
        summary["population"] = kingdom.population

        return summary

    
    # ── FAMILY-WIDE EVENTS ──────────────────────────────────

    def _maybe_family_event(self, world_obj=None):
        """Random family-wide event: reunion (morale boost), feud (penalty),
        blessing (minor resource event), or nothing. Fires rarely (~4%/day)."""
        if world_obj is None:
            from world import world, TERRAIN as world_obj

        if random.random() > 0.04:
            return None

        # Pick a family name that has multiple living adult members
        families = {}
        for c in self.citizens:
            if c.alive and c.role not in ("child",):
                fn = c.family_name()
                if fn not in families:
                    families[fn] = []
                families[fn].append(c)

        # Need at least 3 living adults in the family
        eligible = {fn: members for fn, members in families.items() if len(members) >= 3}
        if not eligible:
            return None

        family_name = random.choice(list(eligible.keys()))
        members = eligible[family_name]

        event_type = random.choices(
            ["reunion", "feud", "blessing", "remembrance"],
            weights=[4, 2, 2, 1],
            k=1
        )[0]

        result = {"family": family_name, "type": event_type, "members_affected": len(members)}

        if event_type == "reunion":
            # Family gathers — morale boost for all members
            boost = random.randint(3, 8)
            for m in members:
                m.morale = min(100, m.morale + boost)
                m.remember(f"Family reunion with the {family_name} clan — spirits lifted")
            result["narrative"] = (
                f"👪 FAMILY REUNION: The {family_name} clan gathered, sharing food and stories. "
                f"All {len(members)} family members feel renewed (+{boost} morale each)."
            )
            result["morale_boost"] = boost
            kingdom.kingdom_log.append(result["narrative"])

        elif event_type == "feud":
            # Family dispute — morale penalty, possible faction tension
            penalty = random.randint(4, 10)
            for m in members:
                m.morale = max(0, m.morale - penalty)
                m.remember(f"A bitter feud divided the {family_name} family")
            # Pick a random faction to blame
            factions_present = list(set(m.faction for m in members if m.faction))
            if factions_present:
                blamed = random.choice(factions_present)
                result["faction_news"] = [
                    f"⚔️ FAMILY FEUD: The {family_name} clan has fractured. {len(members)} members affected (-{penalty} morale). "
                    f"The {blamed} faction is blamed for stirring trouble."
                ]
            else:
                result["faction_news"] = [
                    f"⚔️ FAMILY FEUD: The {family_name} clan has fractured. {len(members)} members affected (-{penalty} morale)."
                ]
            result["morale_penalty"] = penalty
            kingdom.kingdom_log.append(result["faction_news"][0])

        elif event_type == "blessing":
            # Family discovers something or receives a blessing — minor resources
            resource_type = random.choice(["food", "wood", "gold"])
            amount = random.randint(3, 8)
            if resource_type == "food":
                kingdom.food += amount
            elif resource_type == "wood":
                kingdom.wood += amount
            else:
                kingdom.gold += amount
            morale_boost = random.randint(2, 5)
            for m in members:
                m.morale = min(100, m.morale + morale_boost)
                m.remember(f"The {family_name} family received a blessing: +{amount} {resource_type}")
            result["narrative"] = (
                f"✨ FAMILY BLESSING: The {family_name} family discovered +{amount} {resource_type} "
                f"and shared their good fortune. All {len(members)} family members feel blessed (+{morale_boost} morale)."
            )
            result["resource"] = {resource_type: amount}
            result["morale_boost"] = morale_boost
            kingdom.kingdom_log.append(result["narrative"])

        elif event_type == "remembrance":
            # Family honors ancestors — small morale boost, lore flavored
            boost = random.randint(2, 6)
            for m in members:
                m.morale = min(100, m.morale + boost)
                m.remember(f"Shared stories of {family_name} ancestors around the hearth")
            result["narrative"] = (
                f"🕯️ FAMILY REMEMBRANCE: The {family_name} clan lit candles for their ancestors. "
                f"{len(members)} family members feel connected to the past (+{boost} morale)."
            )
            result["morale_boost"] = boost
            kingdom.kingdom_log.append(result["narrative"])

        return result

    # ── DISEASE OUTBREAKS ───────────────────────────────────

    def _check_disease(self, world_obj=None):
        """Roll for disease outbreak. More likely in winter/autumn, with overcrowding.
        Returns an event dict or None."""
        if world_obj is None:
            from world import world, TERRAIN as world_obj

        # Base chance: 3%/day, modified by season and housing
        base_chance = 0.03
        season_mod = {"spring": 0.5, "summer": 0.4, "autumn": 1.2, "winter": 1.8}
        chance = base_chance * season_mod.get(world_obj.season, 1.0)

        # Overcrowding increases risk
        cap = kingdom.housing_capacity()
        pop = kingdom.population
        if pop > cap:
            chance *= 1.0 + 0.15 * (pop - cap)

        # More herbalists reduce risk
        herbalists = len(self.list_by_role("herbalist"))
        if herbalists > 0:
            chance *= max(0.3, 1.0 - 0.08 * herbalists)

        if random.random() > chance:
            return None

        # Determine severity
        severity_roll = random.random()
        if severity_roll < 0.15:
            severity = "plague"
            sick_count = max(3, int(pop * random.uniform(0.10, 0.25)))
            death_chance = 0.08
            morale_penalty = 8
        elif severity_roll < 0.50:
            severity = "outbreak"
            sick_count = max(2, int(pop * random.uniform(0.05, 0.15)))
            death_chance = 0.03
            morale_penalty = 5
        else:
            severity = "cough"
            sick_count = max(1, int(pop * random.uniform(0.02, 0.08)))
            death_chance = 0.005
            morale_penalty = 2

        # Pick victims
        eligible = [c for c in self.citizens if c.alive]
        if len(eligible) < sick_count:
            sick_count = len(eligible)
        victims = random.sample(eligible, sick_count)

        disease_names = {
            "cough": ["a winter chill", "a hacking cough", "the sniffles"],
            "outbreak": ["marsh fever", "the red pox", "a wasting flux"],
            "plague": ["the Ashen Blight", "the Rotting Sleep", "the black cough"],
        }
        disease_name = random.choice(disease_names[severity])

        deaths = []
        for v in victims:
            v.morale = max(0, v.morale - morale_penalty)
            v.remember("Fell ill with " + disease_name)
            if severity != "cough" and random.random() < death_chance:
                # Vulnerable: very young or old are more likely to die
                if v.age < 5 or v.age > 60:
                    if random.random() < death_chance * 2:
                        v.alive = False
                        v.health = 0
                        self.deaths_this_season += 1
                        if v.faction:
                            self.faction_counts[v.faction] -= 1
                        kingdom.population -= 1
                        deaths.append(v.name)
                        if v.spouse and v.spouse.alive:
                            v.spouse.remember("Lost spouse to " + disease_name + ": " + v.name)
                            v.spouse.morale -= 10
                        orphaned = self._check_orphans(v)
                        self._funeral_rites(v, "disease", world_obj)

        severity_labels = {"cough": "🤧", "outbreak": "🤒", "plague": "💀"}
        narrative = (
            severity_labels[severity] + " DISEASE: " + disease_name + " sweeps through Ashfall! "
            + str(sick_count) + " citizens fall ill"
        )
        if deaths:
            if len(deaths) == 1:
                narrative += " — " + disease_name + " claimed 1 life: " + deaths[0]
            else:
                narrative += " — " + disease_name + " claimed " + str(len(deaths)) + " lives: " + ", ".join(deaths[:3])
                if len(deaths) > 3:
                    narrative += " and " + str(len(deaths) - 3) + " more"
        narrative += " (" + severity_labels[severity] + " -" + str(morale_penalty) + " morale to all afflicted)"

        kingdom.kingdom_log.append(narrative)

        return {
            "type": "disease",
            "severity": severity,
            "disease_name": disease_name,
            "sick_count": sick_count,
            "deaths": deaths,
            "morale_penalty": morale_penalty,
            "narrative": narrative,
        }

    # ── FUNERAL RITES ───────────────────────────────────────
    def _funeral_rites(self, deceased, cause, world_obj=None):
        """Hold funeral rites when a citizen dies. Family mourns, community gathers.
        Returns an event dict."""
        if world_obj is None:
            from world import world, TERRAIN as world_obj

        events = []
        mourners = set()

        # Collect all related citizens
        all_related = []

        # Spouse
        if deceased.spouse and deceased.spouse.alive:
            all_related.append((deceased.spouse, "spouse", -12))
            mourners.add(deceased.spouse.name)
            deceased.spouse.remember(f"Mourned at funeral of spouse: {deceased.name}")
            # Spouse already got -10 in death handler; additional -2 for funeral grief

        # Parents
        for p in deceased.parents:
            if p.alive:
                all_related.append((p, "parent", -8))
                mourners.add(p.name)
                p.remember(f"Mourned at funeral of child: {deceased.name}")

        # Children
        for ch in deceased.children:
            if ch.alive:
                all_related.append((ch, "child", -7))
                mourners.add(ch.name)
                ch.remember(f"Mourned at funeral of parent: {deceased.name}")

        # Siblings (share a parent)
        for c in self.citizens:
            if c.alive and c is not deceased:
                shared_parents = set(deceased.parents) & set(c.parents)
                if shared_parents and c.name not in mourners:
                    all_related.append((c, "sibling", -5))
                    mourners.add(c.name)
                    c.remember(f"Lost sibling: {deceased.name}")

        # Apply mourning effects
        for mourner, relation, penalty in all_related:
            mourner.morale = max(0, mourner.morale + penalty)

        # Faction solidarity: if deceased had a faction, members gain +2 morale
        faction_solidarity = 0
        if deceased.faction:
            faction_members = [c for c in self.citizens if c.alive and c.faction == deceased.faction and c is not deceased]
            for fm in faction_members:
                fm.morale = min(100, fm.morale + 2)
                if fm.name not in mourners:
                    fm.remember(f"Paid respects at funeral of fellow {deceased.faction}: {deceased.name}")
            faction_solidarity = len(faction_members)

        # Community: all citizens get +1 morale (reminder of bonds)
        community_count = 0
        for c in self.citizens:
            if c.alive and c is not deceased:
                c.morale = min(100, c.morale + 1)
                community_count += 1

        # Build funeral narrative
        death_labels = {
            "old_age": "passed away peacefully",
            "extreme_old_age": "passed at a remarkable age",
            "despair": "succumbed to despair",
            "disease": "was claimed by illness",
            "unknown": "has died",
        }
        death_phrase = death_labels.get(cause, f"died ({cause})")

        narrative = f"🕯️ FUNERAL: The community gathered to honor {deceased.name} ({deceased.role}, age {int(deceased.age)}), who {death_phrase}."

        # Add notable details
        family_mourners = [m for m, r, _ in all_related if r in ("spouse", "parent", "child")]
        if family_mourners:
            narrative += f" {len(family_mourners)} close family members mourned."

        if faction_solidarity >= 3:
            narrative += f" The {deceased.faction} stood together in solidarity."

        # Log it
        kingdom.kingdom_log.append(narrative)

        return {
            "type": "funeral",
            "deceased": deceased.name,
            "cause": cause,
            "family_mourners": len(family_mourners),
            "faction_solidarity": faction_solidarity,
            "community_size": community_count,
            "narrative": narrative,
        }

    # ── SKILLS INHERITANCE ──────────────────────────────────
    def _inherit_traits(self, child, world_obj=None):
        """When a child comes of age, inherit traits from parents.
        Returns a summary dict or None."""
        if not child.parents:
            return None

        inherited = {"skills": {}, "affinities": [], "role_bias": None}

        for parent in child.parents:
            if not parent.alive:
                continue

            # Combat skill inheritance from guard parents
            if parent.role == "guard" and parent.combat_skill > 10:
                inherited_skill = max(5, int(parent.combat_skill * 0.25) + random.randint(0, 8))
                child.combat_skill = max(child.combat_skill, inherited_skill)
                inherited["skills"]["combat"] = child.combat_skill
                child.remember(f"Inherited combat training from parent {parent.name} (skill {inherited_skill})")

            # Role affinity from parents
            if parent.role not in ("child", "elder"):
                inherited["affinities"].append(parent.role)
                child.remember(f"Parent {parent.name} was a {parent.role}")

        # If child has role affinity from parents, bias role selection
        if inherited["affinities"] and random.random() < 0.4:
            # 40% chance the child follows a parent's profession
            chosen = random.choice(inherited["affinities"])
            if chosen in ROLES and chosen not in ("elder",):
                child.role = chosen
                inherited["role_bias"] = chosen
                child.remember(f"Followed in parent's footsteps as a {chosen}")

        # If child has combat skill but isn't a guard, note latent talent
        if child.combat_skill >= 10 and child.role != "guard":
            child.remember(f"Has latent combat talent (skill {child.combat_skill})")

        return inherited if (inherited["skills"] or inherited["role_bias"]) else None


    # ── MENTORING & APPRENTICESHIP ─────────────────────────

    def _check_mentoring(self, world_obj=None):
        """Daily mentoring: elders pass wisdom to youth, veteran guards train rookies.
        Returns a list of mentoring events or None."""
        events = []

        # ── 1. Elder → Youth mentoring ──
        elders = [c for c in self.citizens if c.alive and c.role == "elder"]
        youths = [c for c in self.citizens if c.alive and 10 <= c.age < 20 and c.role != "elder"]

        if elders and youths and random.random() < 0.25:
            elder = random.choice(elders)
            youth = random.choice(youths)

            # Wisdom passed — morale boost for both
            wisdom_boost = random.randint(2, 5)
            elder.morale = min(100, elder.morale + wisdom_boost)
            youth.morale = min(100, youth.morale + wisdom_boost)

            # Youth gets a small insight — might affect future role
            youth.remember(f"Elder {elder.name} shared wisdom of the old ways")
            elder.remember(f"Mentored {youth.name}, a promising young soul")

            # Rare: youth develops affinity based on elder's past
            teachings = [
                f"Elder {elder.name} taught {youth.name} the old songs of Ashfall",
                f"Elder {elder.name} showed {youth.name} which herbs heal and which harm",
                f"Elder {elder.name} told {youth.name} stories of the valley before the kingdom",
                f"Elder {elder.name} taught {youth.name} to read the stars for navigation",
            ]
            teaching = random.choice(teachings)

            events.append({
                "type": "elder_mentoring",
                "elder": elder.name,
                "youth": youth.name,
                "morale_boost": wisdom_boost,
                "teaching": teaching,
                "narrative": f"📜 MENTORING: {teaching}. Both feel enriched (+{wisdom_boost} morale).",
            })

        # ── 2. Veteran Guard → Rookie training ──
        veterans = [c for c in self.citizens if c.alive and c.role == "guard" and c.combat_skill >= 50]
        rookies = [c for c in self.citizens if c.alive and c.role == "guard" and c.combat_skill < 50]

        if veterans and rookies and random.random() < 0.30:
            veteran = random.choice(veterans)
            rookie = random.choice(rookies)

            # Skill transfer: rookie gains, veteran gets morale
            skill_gain = random.randint(3, 10)
            old_skill = rookie.combat_skill
            rookie.combat_skill = min(100, rookie.combat_skill + skill_gain)
            rookie.morale = min(100, rookie.morale + 1)
            veteran.morale = min(100, veteran.morale + 2)

            old_rank = Citizen("", "guard").combat_rank  # dummy for enum
            # Actually just check rank change manually
            ranks = [(5, "rookie"), (25, "trained"), (50, "seasoned"), (80, "veteran")]
            old_rank_label = "untested"
            new_rank_label = "untested"
            for threshold, label in ranks:
                if old_skill >= threshold:
                    old_rank_label = label
                if rookie.combat_skill >= threshold:
                    new_rank_label = label

            rookie.remember(f"Trained under veteran {veteran.name} — combat skill grew (+{skill_gain})")
            veteran.remember(f"Trained rookie {rookie.name} in the art of combat")

            narrative = f"⚔️ GUARD TRAINING: Veteran {veteran.name} ({veteran.combat_rank()}) drilled rookie {rookie.name} ({old_rank_label}→{new_rank_label}, +{skill_gain} skill)."

            if old_rank_label != new_rank_label:
                narrative += f" {rookie.name} has been promoted to {new_rank_label}!"

            events.append({
                "type": "guard_training",
                "veteran": veteran.name,
                "veteran_rank": veteran.combat_rank(),
                "rookie": rookie.name,
                "skill_gain": skill_gain,
                "old_rank": old_rank_label,
                "new_rank": new_rank_label,
                "narrative": narrative,
            })

        return events if events else None

    
    # ── SEASONAL SUMMARY ────────────────────────────────────

    def _season_summary(self, old_season, new_season):
        """Generate a narrative summary of the season just ended.
        Returns a string suitable for kingdom_log."""
        births = self.births_this_season
        deaths = self.deaths_this_season
        pop = kingdom.population
        morale = self.average_morale()

        season_names = {
            "spring": "🌱 Spring",
            "summer": "☀️ Summer",
            "autumn": "🍂 Autumn",
            "winter": "❄️ Winter",
        }

        old_name = season_names.get(old_season, old_season.title())
        new_name = season_names.get(new_season, new_season.title())

        # Build the narrative
        lines = []
        lines.append(f"{new_name} has arrived in Ashfall.")

        # Population change
        net = births - deaths
        if net > 0:
            lines.append(f"The kingdom grew by {net} soul{'s' if net > 1 else ''} this past season")
            if births > 0:
                lines.append(f"({births} birth{'s' if births > 1 else ''}, {deaths} death{'s' if deaths != 1 else ''})")
        elif net < 0:
            lines.append(f"The kingdom shrank by {abs(net)} soul{'s' if abs(net) > 1 else ''}")
            if deaths > 0:
                lines.append(f"({deaths} death{'s' if deaths > 1 else ''}, {births} birth{'s' if births != 1 else ''})")
        else:
            if births > 0:
                lines.append(f"Births and deaths balanced ({births} each)")
            else:
                lines.append("No births or deaths this season — a quiet time.")

        # Morale summary
        if morale >= 75:
            lines.append("The people are hopeful, their spirits bright.")
        elif morale >= 55:
            lines.append("The mood in the kingdom is steady and content.")
        elif morale >= 35:
            lines.append("Unease shadows the kingdom — the people are watchful.")
        else:
            lines.append("Grim times. The people struggle to hold onto hope.")

        # Landmark / milestone callouts
        if old_season == "winter" and new_season == "spring":
            lines.append("The frost retreats. The Whispering Spring runs clear again.")
        elif old_season == "spring" and new_season == "summer":
            lines.append("Long days and warm nights lie ahead. The fields are thick with promise.")
        elif old_season == "summer" and new_season == "autumn":
            lines.append("The harvest is underway. Leaves turn copper on the ridge.")
        elif old_season == "autumn" and new_season == "winter":
            lines.append("The cold winds blow down from the north. Fires burn long into the night.")

        return " ".join(lines)

    # ── SEASONAL HISTORY REPORT ─────────────────────────────

    def seasonal_history_report(self):
        """Pretty-print the seasonal history records."""
        if not self.seasonal_history:
            return "📜 No seasonal history recorded yet — the kingdom is still in its first season."

        lines = []
        lines.append("")
        lines.append("╔══════════════════════════════════════════╗")
        lines.append("║     📊  SEASONAL HISTORY                ║")
        lines.append("╠══════════════════════════════════════════╣")

        season_names = {
            "spring": "🌱 Spring", "summer": "☀️ Summer",
            "autumn": "🍂 Autumn", "winter": "❄️ Winter"
        }

        for i, record in enumerate(self.seasonal_history):
            season = record.get("season", "unknown")
            births = record.get("births", 0)
            deaths = record.get("deaths", 0)
            pop = record.get("population", 0)
            net = births - deaths
            net_str = f"+{net}" if net > 0 else str(net)
            season_label = season_names.get(season, season.title())

            ago = len(self.seasonal_history) - i
            ago_str = " (current)" if ago == 1 else f" ({ago} seasons ago)" if ago <= 8 else ""

            # Mini bar for net change
            bar_len = min(abs(net), 10)
            if net > 0:
                bar = "🟢" * bar_len
            elif net < 0:
                bar = "🔴" * bar_len
            else:
                bar = "⚪"

            lines.append(f"║  {season_label:<18} pop:{pop:<5} {bar} {net_str:<4}{'':<4}║")
            lines.append(f"║    ↳ {births} births, {deaths} deaths{'':<14}{ago_str:<16}║")
            if i < len(self.seasonal_history) - 1:
                lines.append("╟──────────────────────────────────────────╢")

        lines.append("╚══════════════════════════════════════════╝")

        # Add current season note
        if hasattr(world, 'season'):
            current = season_names.get(world.season, world.season.title())
            lines.append(f"  Now: {current} (in progress — {self.births_this_season} births, {self.deaths_this_season} deaths so far)")
        lines.append("")

        return "\n".join(lines)


# ── GUARD TRAINING ──────────────────────────────────────

    def _train_guards(self, world_obj=None):
        """Guards train daily, slowly improving combat skill.
        Barracks accelerate training. Returns training summary or None."""
        guards = [c for c in self.citizens if c.alive and c.role == "guard"]
        if not guards:
            return None

        has_barracks = kingdom.buildings.get("barracks", 0) > 0
        has_tower = kingdom.buildings.get("guard_tower", 0) > 0
        promotions = []

        for g in guards:
            # Base gain: 0.3-0.8 per day
            base_gain = random.uniform(0.3, 0.8)
            # Barracks: +50% training rate
            if has_barracks:
                base_gain *= 1.5
            # Guard tower: small bonus (drills at height)
            if has_tower:
                base_gain += 0.2
            # Skill gain slows as you approach 100 (diminishing returns)
            if g.combat_skill > 70:
                base_gain *= 0.6
            if g.combat_skill > 85:
                base_gain *= 0.4

            old_rank = g.combat_rank()
            g.combat_skill = min(100, g.combat_skill + base_gain)
            new_rank = g.combat_rank()

            if old_rank != new_rank:
                promotions.append(f"MILITARY: {g.name} promoted to {new_rank} (skill {g.combat_skill:.0f})")
                g.remember(f"Promoted to {new_rank}")

        if promotions:
            return {"promotions": promotions, "guards_training": len(guards)}
        return {"guards_training": len(guards)}

    def guard_defense_contribution(self):
        """Calculate defense contribution from guards based on combat skill.
        Replaces the flat +2/guard in kingdom.tick().
        Returns total defense from guards."""
        total = 0
        for c in self.citizens:
            if c.alive and c.role == "guard":
                # Base: 1 defense + skill bonus
                if c.combat_skill >= 80:
                    total += 4   # veteran
                elif c.combat_skill >= 50:
                    total += 3   # seasoned
                elif c.combat_skill >= 25:
                    total += 2   # trained
                else:
                    total += 1   # rookie/untested
        return total

    # ── MARRIAGE SYSTEM ─────────────────────────────────────

    def _maybe_marry(self, world_obj=None):
        """Occasionally pair compatible unmarried adults.
        Returns marriage summary or None."""
        if world_obj is None:
            world_obj = world

        # Throttle: at most one marriage every 3 days
        if world_obj.day - self._last_marriage_day < 3:
            return None

        # Festivals boost marriage chance
        base_chance = 0.08
        if kingdom.festival_cooldown > 35:  # just had festival
            base_chance = 0.25

        if random.random() > base_chance:
            return None

        # Find eligible bachelors/bachelorettes
        eligible = [
            c for c in self.citizens
            if c.alive and c.spouse is None
            and c.role not in ("child", "elder")
            and c.age >= 18
        ]
        if len(eligible) < 2:
            return None

        # Pick two with some compatibility:
        # - Different family names (no accidental incest)
        # - Similar age (+/- 15 years)
        # - Not already siblings
        random.shuffle(eligible)
        a = eligible[0]
        best = None
        best_score = -1
        for b in eligible[1:]:
            if b is a:
                continue
            if b.family_name() == a.family_name():
                continue  # same family name — too close
            if abs(a.age - b.age) > 15:
                continue
            if self._are_siblings(a, b):
                continue

            # Compatibility score: similar morale, same faction bonus
            score = 0
            if a.faction == b.faction:
                score += 3
            score -= abs(a.morale - b.morale) / 10
            score -= abs(a.age - b.age) / 5

            if score > best_score:
                best_score = score
                best = b

        if best is None:
            return None

        # Marry them!
        a.spouse = best
        best.spouse = a
        self.marriages.append((a.name, best.name))
        self._last_marriage_day = world_obj.day

        a.morale += 10
        best.morale += 10
        a.morale = min(100, a.morale)
        best.morale = min(100, best.morale)

        a.remember(f"Married {best.name}")
        best.remember(f"Married {a.name}")

        announcement = f"WEDDING: {a.name} ({a.role}) and {best.name} ({best.role}) were married!"
        kingdom.kingdom_log.append(announcement)

        return {
            "announcements": [announcement],
            "couple": (a.name, best.name),
        }

    def _check_orphans(self, deceased):
        """Check deceased's children — if both parents are now dead, mark orphan."""
        newly_orphaned = []
        for child in deceased.children:
            if not child.alive:
                continue
            # Check if both parents are dead
            living_parents = [p for p in child.parents if p.alive]
            if not living_parents:
                if child.name not in self.orphans:
                    self.orphans.append(child.name)
                    child.morale = max(0, child.morale - 15)
                    child.remember(f"Orphaned — lost both parents. Last: {deceased.name}")
                    newly_orphaned.append(child.name)
        return newly_orphaned

    def _are_siblings(self, citizen_a, citizen_b):
        """Check if two citizens share at least one parent."""
        parents_a = set(p.name for p in citizen_a.parents)
        parents_b = set(p.name for p in citizen_b.parents)
        return bool(parents_a & parents_b)

    def get_siblings(self, citizen):
        """Return list of living siblings for a citizen."""
        if not citizen.parents:
            return []
        parent_names = set(p.name for p in citizen.parents)
        siblings = []
        for c in self.citizens:
            if c is citizen or not c.alive:
                continue
            c_parents = set(p.name for p in c.parents)
            if parent_names & c_parents:
                siblings.append(c)
        return siblings

    # ── FESTIVAL PARTICIPATION ──────────────────────────────

    def festival_participation(self, festival_name):
        """Apply faction-specific morale boosts for a given festival."""
        boosts = FESTIVAL_FACTION_BOOSTS.get(festival_name, {})
        if not boosts:
            boosts = {"hearthkeepers": 2, "deepwardens": 2, "wildwalkers": 2}

        reactions = []
        total_boosted = 0

        for faction, bonus in boosts.items():
            faction_citizens = self.list_by_faction(faction)
            if not faction_citizens:
                continue
            for c in faction_citizens:
                if c.alive:
                    c.morale += bonus
                    c.morale = max(0, min(100, c.morale))
                    total_boosted += 1

            if bonus >= 5:
                reactions.append(
                    f"FACTION: The {faction} ({FACTIONS[faction]['color']}) are especially moved by the {festival_name}."
                )
            elif bonus >= 2:
                reactions.append(
                    f"FACTION: The {faction} join the {festival_name} with quiet satisfaction."
                )

        return {
            "festival_name": festival_name,
            "faction_boosts": boosts,
            "citizens_boosted": total_boosted,
            "faction_reactions": reactions,
        }

    def _detect_and_participate(self, world_obj=None):
        """Check kingdom log for a festival that just fired (today).
        Handles multiple festivals in window — picks the most recent."""
        if world_obj is None:
            world_obj = world

        current_day = world_obj.day
        if current_day == self._last_festival_day:
            return None

        recent_logs = kingdom.kingdom_log[-5:] if kingdom.kingdom_log else []
        # Collect ALL festivals in recent logs, pick the last (most recent) one
        found_festivals = []
        for entry in recent_logs:
            if "FESTIVAL:" in entry:
                try:
                    fest_part = entry.split("FESTIVAL: ")[1]
                    # Handle both "FESTIVAL: Name!" and "FESTIVAL: Name! ..."
                    fest_name = fest_part.split("!")[0].strip()
                    if fest_name:
                        found_festivals.append(fest_name)
                except (IndexError, ValueError):
                    pass

        if found_festivals:
            # Use the most recent festival (last in list)
            fest_name = found_festivals[-1]
            self._last_festival_day = current_day
            result = self.festival_participation(fest_name)
            # If multiple festivals in one day, note it
            if len(found_festivals) > 1:
                result["multiple_festivals"] = found_festivals
            return result

        return None

    # ── IMMIGRATION ─────────────────────────────────────────

    def migrate(self, world_obj=None):
        """Immigration: new settlers arrive when the kingdom has spare housing
        and good morale."""
        if world_obj is None:
            world_obj = world

        spare_housing = kingdom.housing_capacity() - kingdom.population
        if spare_housing < 5:
            return None

        avg_morale = self.average_morale()
        if avg_morale < 40:
            return None

        base_chance = 0.04 * min(spare_housing, 20)
        morale_mult = avg_morale / 100
        tavern_bonus = 0.06 if kingdom.buildings.get("tavern", 0) > 0 else 0
        market_bonus = 0.03 * kingdom.buildings.get("market", 0)
        hall_bonus = 0.05 if kingdom.buildings.get("market_hall", 0) > 0 else 0
        wall_bonus = 0.02 * min(kingdom.buildings.get("walls", 0), 5)

        chance = (base_chance + tavern_bonus + market_bonus + hall_bonus + wall_bonus) * morale_mult

        if random.random() > chance:
            return None

        count = random.choices([1, 2, 3], weights=[6, 3, 1], k=1)[0]

        new_citizens = []
        roles_pool = ["farmer", "woodcutter", "builder", "miner", "scout", "herbalist", "guard"]
        bring_child = random.random() < 0.25

        for _ in range(count):
            first = random.choice(FIRST_NAMES)
            family = random.choice(FAMILY_NAMES)
            name = f"{first} {family}"
            role = random.choice(roles_pool)
            age = random.randint(18, 45)
            c = Citizen(name, role, age)
            c.morale = random.randint(55, 75)
            c.remember("Arrived as a settler to Ashfall, seeking a new life.")
            if role == "guard":
                c.combat_skill = random.randint(5, 30)
            self._assign_faction(c)
            self.citizens.append(c)
            new_citizens.append(c)
            kingdom.population += 1

        if bring_child and kingdom.population < kingdom.housing_capacity():
            first = random.choice(FIRST_NAMES)
            family = random.choice(FAMILY_NAMES)
            child = Citizen(f"{first} {family}", "child", age=random.randint(0, 10))
            child.morale = 70
            child.faction = random.choice(list(FACTIONS.keys()))
            if child.faction:
                self.faction_counts[child.faction] += 1
            self.citizens.append(child)
            new_citizens.append(child)
            kingdom.population += 1

            adult_settlers = [c for c in new_citizens if c.role != "child" and c is not child]
            if adult_settlers:
                parent = random.choice(adult_settlers)
                child.parents.append(parent)
                parent.children.append(child)
                self.family_ties.append((parent.name, child.name))

        names = ", ".join(c.name for c in new_citizens)
        return {
            "count": count,
            "citizens": new_citizens,
            "names": names,
            "message": f"IMMIGRATION: {count} new settler(s) arrived -- {names} -- drawn by Ashfall's prosperity!",
        }

    # ── QUERIES ─────────────────────────────────────────────

    def average_morale(self):
        alive = [c for c in self.citizens if c.alive]
        if not alive:
            return 0
        return round(sum(c.morale for c in alive) / len(alive), 1)

    def mood_distribution(self):
        dist = {"hopeful": 0, "content": 0, "uneasy": 0, "grim": 0, "despairing": 0}
        for c in self.citizens:
            if c.alive:
                dist[c.mood_label()] += 1
        return dist

    def census(self):
        roles_count = {}
        faction_count = {f: 0 for f in FACTIONS}
        guard_skills = []
        for c in self.citizens:
            if c.alive:
                roles_count[c.role] = roles_count.get(c.role, 0) + 1
                if c.faction:
                    faction_count[c.faction] += 1
                if c.role == "guard":
                    guard_skills.append(c.combat_skill)
        result = {
            "total": kingdom.population,
            "orphans": len(self.orphans),
            "avg_morale": self.average_morale(),
            "mood_distribution": self.mood_distribution(),
            "roles": roles_count,
            "factions": faction_count,
            "births_this_season": self.births_this_season,
            "deaths_this_season": self.deaths_this_season,
            "marriages": len(self.marriages),
        }
        if guard_skills:
            result["guard_avg_skill"] = round(sum(guard_skills) / len(guard_skills), 1)
            result["guard_best_skill"] = max(guard_skills)
            result["guard_count"] = len(guard_skills)
        return result

    # ── COMPREHENSIVE PEOPLE REPORT ─────────────────────────

    def people_report(self):
        """Comprehensive report: census + pyramid + seasonal history + family stats + orphans.
        Returns a dict with a formatted text report."""
        pyr = self.population_pyramid()
        cen = self.census()

        lines = []
        lines.append("")
        lines.append("╔═══════════════════════════════════════════════╗")
        lines.append("║     👥  PEOPLE OF ASHFALL  —  FULL REPORT    ║")
        lines.append("╚═══════════════════════════════════════════════╝")
        lines.append("")

        # ── Vital Statistics ──
        lines.append("─── 📊 Vital Statistics ───")
        lines.append("  Population:      %5d" % cen["total"])
        lines.append("  Avg Morale:      %5d" % cen["avg_morale"])
        lines.append("  Orphans:         %5d" % cen["orphans"])
        lines.append("  Marriages:       %5d" % cen["marriages"])
        lines.append("  Births (season): %5d" % cen["births_this_season"])
        lines.append("  Deaths (season): %5d" % cen["deaths_this_season"])
        lines.append("")

        # Guard stats
        if "guard_count" in cen:
            lines.append("─── 🛡️ Guard Corps ───")
            lines.append("  Guards:          %5d" % cen["guard_count"])
            lines.append("  Avg Skill:       %5d" % cen["guard_avg_skill"])
            lines.append("  Best Skill:      %5d" % cen["guard_best_skill"])
            lines.append("")

        # ── Mood Distribution ──
        lines.append("─── 😊 Mood Distribution ───")
        for mood, count in sorted(cen["mood_distribution"].items()):
            bar_len = min(count, 30)
            bar = "█" * bar_len
            lines.append("  %-12s %3d %s" % (mood, count, bar))
        lines.append("")

        # ── Role Breakdown ──
        lines.append("─── 🔧 Roles ───")
        for role, count in sorted(cen["roles"].items(), key=lambda x: -x[1]):
            lines.append("  %-15s %3d" % (role, count))
        lines.append("")

        # ── Faction Breakdown ──
        lines.append("─── 🏛️ Factions ───")
        for faction, count in sorted(cen["factions"].items(), key=lambda x: -x[1]):
            color = FACTIONS[faction]["color"]
            lines.append("  %s %-15s %3d" % (color, faction, count))
        lines.append("")

                # ── Faction Leaders ──
        lines.append("─── 👑 Faction Leaders ───")
        for faction, leader_name in self.faction_leaders.items():
            if leader_name:
                leader = None
                for c in self.citizens:
                    if c.name == leader_name:
                        leader = c
                        break
                if leader and leader.alive:
                    color = FACTIONS[faction]["color"]
                    lines.append("  %s %-15s → %s (%s, age %d, morale %d)" % (
                        color, faction, leader_name, leader.role,
                        int(leader.age), leader.morale))
                else:
                    lines.append("  %-15s → %s (deceased/missing)" % (faction, leader_name))
            else:
                lines.append("  %-15s → no leader" % faction)
        lines.append("")

        # ── Election History ──
        if self.faction_election_history:
            lines.append("─── 🗳️ Recent Elections ───")
            for entry in self.faction_election_history[-5:]:
                lines.append("  Day %s: %s → %s (%s, %s)" % (
                    entry.get("day", "?"),
                    entry.get("old_leader", "none"),
                    entry["new_leader"],
                    entry.get("leader_role", "?"),
                    entry.get("reason", "election"),
                ))
            lines.append("")

# ── Family Statistics ──
        ft = self.family_tree()
        lines.append("─── 👪 Families ───")
        lines.append("  Family ties:     %5d" % ft["total_ties"])
        lines.append("  Unique parents:  %5d" % ft["unique_parents"])
        lines.append("  Total marriages: %5d" % ft["total_marriages"])

        family_names = set()
        for c in self.citizens:
            if c.alive:
                family_names.add(c.family_name())
        lines.append("  Family names:    %5d" % len(family_names))
        lines.append("")

        # ── Population Pyramid ──
        lines.append("─── 📈 Age Pyramid ───")
        lines.append(pyr["pyramid"])
        lines.append("")

        # ── Seasonal History ──
        lines.append("─── 📅 Seasonal History ──")
        sh = self.seasonal_history_report()
        lines.append(sh)
        lines.append("")

        # ── Orphans ──
        if self.orphans:
            lines.append("─── 🕯️ Orphans ───")
            for name in self.orphans[-10:]:
                orphan = None
                for c in self.citizens:
                    if c.name == name:
                        orphan = c
                        break
                if orphan:
                    lines.append("  %s (%s, age %d, morale %d)" % (name, orphan.role, int(orphan.age), orphan.morale))
                else:
                    lines.append("  %s (deceased or gone)" % name)
            lines.append("")

        report_text = "\n".join(lines)

        return {
            "report": report_text,
            "census": cen,
            "pyramid": pyr,
            "family_stats": ft,
            "seasonal_history": self.seasonal_history,
            "orphans": self.orphans.copy(),
        }

    def list_by_role(self, role):
        return [c for c in self.citizens if c.alive and c.role == role]

    def list_by_faction(self, faction):
        results = []
        for c in self.citizens:
            if c.alive and c.faction == faction:
                results.append(c)
        return results

    # ── POPULATION PYRAMID ─────────────────────────────────

    def population_pyramid(self):
        """ASCII bar chart of population by 10-year age bracket."""
        brackets = {}
        for c in self.citizens:
            if c.alive:
                bracket = (int(c.age) // 10) * 10
                if bracket > 80:
                    bracket = 80
                brackets[bracket] = brackets.get(bracket, 0) + 1

        max_bar = 30
        max_count = max(brackets.values()) if brackets else 1

        lines = []
        lines.append("┌─────────────────────────────────────────────┐")
        lines.append("│         POPULATION PYRAMID               │")
        lines.append("├──────────┬──────┬────────────────────────────┤")
        lines.append("│ bracket  │  pop │ distribution               │")
        lines.append("├──────────┼──────┼────────────────────────────┤")

        for b in sorted(brackets.keys()):
            count = brackets[b]
            bar_len = int(count / max_count * max_bar) if max_count else 0
            bar = "█" * bar_len
            label = f"{b}-{b+9}" if b < 80 else "80+"
            # Per-bracket role breakdown
            roles_in_bracket = {}
            bracket_morale = []
            for c in self.citizens:
                if c.alive:
                    age_bracket = (int(c.age) // 10) * 10
                    if age_bracket > 80:
                        age_bracket = 80
                    if age_bracket == b:
                        roles_in_bracket[c.role] = roles_in_bracket.get(c.role, 0) + 1
                        bracket_morale.append(c.morale)
            avg_m = round(sum(bracket_morale) / len(bracket_morale), 1) if bracket_morale else 0
            lines.append(f"│ {label:<8} │ {count:>4} │ {bar:<28}│")
            # Role detail line
            role_str = ", ".join(f"{r}:{n}" for r, n in sorted(roles_in_bracket.items()))
            if role_str:
                lines.append(f"│          │      │  roles: {role_str:<20}│")
            if bracket_morale:
                lines.append(f"│          │      │  avg morale: {avg_m:<18}│")

        lines.append("├──────────┴──────┴────────────────────────────┤")
        lines.append(f"│ total: {kingdom.population:<38}│")
        lines.append("└─────────────────────────────────────────────┘")

        alive_ages = [c.age for c in self.citizens if c.alive]

        return {
            "breakdown": brackets,
            "pyramid": "\n".join(lines),
            "total": kingdom.population,
            "youngest": min(alive_ages) if alive_ages else None,
            "oldest": max(alive_ages) if alive_ages else None,
            "dependency_ratio": kingdom.dependency_ratio(self) if hasattr(kingdom, 'dependency_ratio') else None,
        }

    # ── FAMILY TREE ────────────────────────────────────────

    def family_tree(self, citizen_name=None):
        """Return family info for a citizen, or a summary of all family ties."""
        if citizen_name is None:
            total_ties = len(self.family_ties)
            unique_parents = len(set(t[0] for t in self.family_ties))
            return {
                "total_ties": total_ties,
                "unique_parents": unique_parents,
                "ties": self.family_ties,
                "marriages": self.marriages,
                "total_marriages": len(self.marriages),
            }

        target = None
        for c in self.citizens:
            if c.name == citizen_name:
                target = c
                break
        if target is None:
            return f"No citizen named '{citizen_name}'."

        parent_names = [p.name for p in target.parents if p.alive]
        child_names = [ch.name for ch in target.children if ch.alive]
        sibling_names = [s.name for s in self.get_siblings(target)]
        spouse_name = target.spouse.name if target.spouse and target.spouse.alive else None

        return {
            "citizen": target.name,
            "role": target.role,
            "age": round(target.age, 1),
            "parents": parent_names,
            "children": child_names,
            "siblings": sibling_names,
            "spouse": spouse_name,
            "combat_skill": round(target.combat_skill, 1) if target.role == "guard" else None,
            "combat_rank": target.combat_rank() if target.role == "guard" else None,
        }

    # ── FAMILY TREE ASCII ──────────────────────────────────

    def family_tree_ascii(self, citizen_name=None):
        """Pretty-print an ASCII family tree for a citizen (or pick a random one with family ties)."""
        if citizen_name is None:
            candidates = [
                c for c in self.citizens
                if c.alive and (c.children or c.parents or c.spouse)
            ]
            if not candidates:
                return {"error": "No citizens with family ties found."}
            target = random.choice(candidates)
        else:
            target = None
            for c in self.citizens:
                if c.name == citizen_name:
                    target = c
                    break
            if target is None:
                return {"error": "No citizen named '" + citizen_name + "'."}

        lines = []
        lines.append("")
        lines.append("  🌳  Family Tree: " + target.name)
        lines.append("       (" + target.role + ", age " + str(int(target.age)) + ", " + target.mood_label() + ")")
        lines.append("")

        # Parents row
        if target.parents:
            parent_labels = []
            for p in target.parents:
                marker = "" if p.alive else " ✝"
                parent_labels.append(p.name + " (" + p.role + ")" + marker)
            lines.append("  ┌── Parents ──────────────────────────")
            for pl in parent_labels:
                lines.append("  │  " + pl)
            lines.append("  │")
        else:
            lines.append("  ┌── Parents: (unknown)")
            lines.append("  │")

        # Self
        spouse_str = ""
        if target.spouse:
            s = target.spouse
            spouse_str = "  ♥ " + s.name + " (" + s.role + ", age " + str(int(s.age)) + ")"
        lines.append("  ├── ✦ " + target.name + " ✦" + spouse_str)
        lines.append("  │")

        # Children
        if target.children:
            lines.append("  └── Children ─────────────────────────")
            for ch in target.children:
                marker = "" if ch.alive else " ✝"
                spouse_info = ""
                if ch.spouse and ch.spouse.alive:
                    spouse_info = "  ♥ " + ch.spouse.name
                lines.append("     " + ch.name + " (" + ch.role + ", age " + str(int(ch.age)) + ")" + marker + spouse_info)
        else:
            lines.append("  └── Children: (none)")

        # Siblings
        siblings = self.get_siblings(target)
        if siblings:
            lines.append("")
            lines.append("  ── Siblings ──────────────────────────")
            for sib in siblings:
                marker = "" if sib.alive else " ✝"
                lines.append("     " + sib.name + " (" + sib.role + ", age " + str(int(sib.age)) + ")" + marker)

        lines.append("")

        tree_text = "\n".join(lines)

        return {
            "citizen": target.name,
            "tree": tree_text,
            "parents": [p.name for p in target.parents],
            "children": [ch.name for ch in target.children],
            "siblings": [s.name for s in siblings],
            "spouse": target.spouse.name if target.spouse else None,
        }
    # ── CITIZEN JOURNAL / MEMORY BOOK ──────────────────────

    def citizen_journal(self, citizen_name=None):
        """Pretty-print a citizen's life story: memories, family, key events.
        If no name given, picks a random elder or long-lived citizen."""
        if citizen_name is None:
            # Prefer elders, then older citizens
            candidates = sorted(
                [c for c in self.citizens if c.alive and len(c.memories) >= 2],
                key=lambda c: (c.age if c.age < 60 else 999, len(c.memories)),
                reverse=True
            )
            if not candidates:
                candidates = [c for c in self.citizens if c.alive]
            if not candidates:
                return {"error": "No citizens found."}
            target = random.choice(candidates[:10])  # pick from top 10 most interesting
        else:
            target = None
            for c in self.citizens:
                if c.name == citizen_name:
                    target = c
                    break
            if target is None:
                return {"error": f"No citizen named '{citizen_name}'."}

        lines = []
        lines.append("")
        lines.append("╔═══════════════════════════════════════════════╗")
        lines.append("║         📖  CITIZEN JOURNAL                 ║")
        lines.append("╚═══════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"  Name:       {target.name}")
        lines.append(f"  Role:       {target.role}")
        lines.append(f"  Age:        {int(target.age)} years")
        lines.append(f"  Morale:     {target.morale} ({target.mood_label()})")
        lines.append(f"  Health:     {target.health}")
        lines.append(f"  Faction:    {target.faction or 'none'}")

        if target.role == "guard":
            lines.append(f"  Combat:     skill {target.combat_skill:.0f} ({target.combat_rank()})")

        lines.append("")

        # ── Family ──
        lines.append("  ── Family ──")
        if target.parents:
            p_names = ", ".join(p.name + ("" if p.alive else " ✝") for p in target.parents)
            lines.append(f"  Parents:    {p_names}")
        else:
            lines.append("  Parents:    (unknown)")

        if target.spouse:
            s = target.spouse
            lines.append(f"  Spouse:     {s.name} ({s.role}, age {int(s.age)}, {'alive' if s.alive else 'deceased'})")
        else:
            lines.append("  Spouse:     none")

        if target.children:
            for ch in target.children:
                marker = "" if ch.alive else " ✝"
                lines.append(f"  Child:      {ch.name} ({ch.role}, age {int(ch.age)}){marker}")
        else:
            lines.append("  Children:   none")

        siblings = self.get_siblings(target)
        if siblings:
            sib_str = ", ".join(s.name for s in siblings)
            lines.append(f"  Siblings:   {sib_str}")

        lines.append("")

        # ── Memories ──
        lines.append("  ── Memories ──")
        if target.memories:
            for i, mem in enumerate(target.memories, 1):
                lines.append(f"  {i:2d}. {mem}")
        else:
            lines.append("  (No recorded memories yet)")

        lines.append("")

        # ── Life Summary ──
        lines.append("  ── Life Summary ──")
        life_stage = "elder, keeper of wisdom" if target.age >= 60 else                      "in their prime" if target.age >= 30 else                      "young and growing" if target.age >= 16 else                      "a child of Ashfall"
        lines.append(f"  {target.name} is {life_stage}.")

        # Count significant life events
        event_count = len(target.memories)
        if event_count >= 8:
            lines.append("  An eventful life — many stories to tell around the hearth.")
        elif event_count >= 4:
            lines.append("  A life with its share of trials and triumphs.")
        else:
            lines.append("  A quiet life, but not without purpose.")

        lines.append("")

        journal_text = "\n".join(lines)

        return {
            "citizen": target.name,
            "journal": journal_text,
            "age": int(target.age),
            "role": target.role,
            "memory_count": len(target.memories),
        }


