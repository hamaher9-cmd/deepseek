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

# ── ROLE MASTERY (SKILL TREES) ────────────────────────────────

MASTERY_TITLES = {
    0: "Novice",
    1: "Apprentice",
    2: "Journeyman",
    3: "Expert",
    4: "Master",
}

MASTERY_THRESHOLDS = {
    1: 15,    # Apprentice after 15 days
    2: 45,    # Journeyman after 45 days
    3: 90,    # Expert after 90 days
    4: 180,   # Master after 180 days (half a year)
}

# Bonus resources/day per mastery level. These are added to base work() output.
MASTERY_BONUSES = {
    "farmer": {
        1: {"food": 1},
        2: {"food": 1},
        3: {"food": 1},
        4: {"food": 2},
    },
    "woodcutter": {
        1: {"wood": 1},
        2: {"wood": 1},
        3: {"wood": 1},
        4: {"wood": 2},
    },
    "miner": {
        1: {"stone": 1},
        2: {"stone": 1},
        3: {"gold": 1},
        4: {"stone": 1, "gold": 2},
    },
    "builder": {
        1: {},
        2: {},
        3: {},
        4: {},
    },
    "scout": {
        1: {},
        2: {},
        3: {},
        4: {},
    },
    "herbalist": {
        1: {"food": 1},
        2: {"gold": 1},
        3: {"food": 1, "gold": 1},
        4: {"gold": 2},
    },
    "guard": {
        1: {},
        2: {},
        3: {},
        4: {},
    },
    "elder": {
        1: {},
        2: {},
        3: {},
        4: {},
    },
    "child": {
        1: {},
        2: {},
        3: {},
        4: {},
    },
}

# Mastery non-resource passives. Applied during advance_day.
def mastery_passive_effect(citizen, people_obj):
    """Apply passive effects based on citizen's mastery level and role.
    Called during advance_day. Modifies the citizen and/or kingdom in place."""
    lvl = citizen.mastery_level
    role = citizen.role

    if role == "builder" and lvl >= 3:
        # Expert+ builders inspire the community
        if random.random() < 0.15:
            for c in people_obj.citizens:
                if c.alive and c is not citizen:
                    c.morale = min(100, c.morale + 1)
            citizen.remember("Inspired the community with masterful craftsmanship")

    elif role == "scout" and lvl >= 2:
        # Journeyman+ scouts occasionally find caches
        if random.random() < 0.08:
            resource = random.choice(["food", "wood", "gold"])
            amount = random.randint(2, 5)
            if resource == "food":
                kingdom.food += amount
            elif resource == "wood":
                kingdom.wood += amount
            else:
                kingdom.gold += amount
            citizen.remember(f"Scout's keen eye found +{amount} {resource}")
            kingdom.kingdom_log.append(
                f"🔍 SCOUT CACHE: {citizen.name} ({MASTERY_TITLES[lvl]} scout) "
                f"discovered +{amount} {resource} while patrolling."
            )

    elif role == "herbalist" and lvl >= 3:
        # Expert+ herbalists reduce disease chances further
        pass  # Handled in _check_disease via herbalist count; mastery adds narrative

    elif role == "elder" and lvl >= 3:
        # Expert+ elders tell enriching stories
        if random.random() < 0.12:
            boost = random.randint(2, 5)
            youths = [c for c in people_obj.citizens if c.alive and c.age < 20]
            for y in youths[:5]:
                y.morale = min(100, y.morale + boost)
            citizen.remember(f"Told stories that lifted the spirits of {len(youths[:5])} youths")
            if youths:
                kingdom.kingdom_log.append(
                    f"📖 ELDER WISDOM: {citizen.name} ({MASTERY_TITLES[lvl]} elder) "
                    f"shared tales that warmed {len(youths[:5])} young hearts (+{boost} morale)."
                )


# Mastery effect descriptions for report
MASTERY_DESCRIPTIONS = {
    "farmer": {
        1: "+1 food/day — knows the soil now",
        2: "+1 food/day — crop rotations mastered",
        3: "+1 food/day — reads the weather like a book",
        4: "+2 food/day — legendary harvests",
    },
    "woodcutter": {
        1: "+1 wood/day — axe finds the grain",
        2: "+1 wood/day — fells trees others can't reach",
        3: "+1 wood/day — knows every copse and grove",
        4: "+2 wood/day — the forest yields to their hand",
    },
    "miner": {
        1: "+1 stone/day — learns the rock's voice",
        2: "+1 stone/day — follows veins by instinct",
        3: "+1 gold/day — strikes precious seams",
        4: "+1 stone +2 gold/day — uncovers hidden riches",
    },
    "builder": {
        1: "Works faster — hands know the tools",
        2: "Builds truer — walls stand straighter",
        3: "Inspires the community with craftsmanship",
        4: "Master architect — plans fortifications and monuments",
    },
    "scout": {
        1: "Knows the near trails by heart",
        2: "Occasionally finds hidden caches",
        3: "Can map uncharted territory faster",
        4: "Trains new scouts in the ways of the wild",
    },
    "herbalist": {
        1: "+1 food/day — forages with confidence",
        2: "+1 gold/day — sells rare remedies",
        3: "+1 food +1 gold/day — sought by the sick from miles around",
        4: "+2 gold/day — legendary healer, brews life-saving elixirs",
    },
    "guard": {
        1: "Training accelerates — muscle memory",
        2: "Steady under pressure — +1 defense",
        3: "Commands respect — +2 defense",
        4: "Battle-hardened veteran — trains the next generation",
    },
    "elder": {
        1: "Mentoring more effective",
        2: "Wisdom draws listeners from afar",
        3: "Tells stories that lift the kingdom's spirits",
        4: "Keeper of sacred lore — the Sleeper's memory lives on",
    },
    "child": {
        1: "",
        2: "",
        3: "",
        4: "",
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

# ── FACTION QUESTS ─────────────────────────────────────────────

# Each faction periodically generates a quest aligned with its priorities.
# Faction members contribute work output toward the quest. Completion grants
# rewards to the faction and the kingdom.

FACTION_QUEST_DEFS = {
    "hearthkeepers": [
        # ── Common quests ──
        {
            "type": "stockpile",
            "name": "Winter Stockpile",
            "desc": "Gather provisions to see the kingdom through the cold months.",
            "target": {"food": 30, "wood": 20},
            "reward_morale": 6,
            "reward_resources": {"food": 10, "wood": 5},
            "narrative_complete": "The Hearthkeepers have filled the storehouses for winter. Warmth and plenty await.",
            "rarity": "common",
        },
        {
            "type": "fortify",
            "name": "Raise the Walls",
            "desc": "Strengthen Ashfall's defenses — train guards and build fortifications.",
            "target": {"stone": 25, "wood": 15},
            "reward_morale": 5,
            "reward_resources": {"stone": 8},
            "narrative_complete": "The Hearthkeepers have reinforced the kingdom's defenses. Ashfall stands stronger.",
            "bonus_effect": "defense_boost",
            "rarity": "common",
        },
        {
            "type": "feast",
            "name": "Grand Feast",
            "desc": "Prepare a magnificent feast to lift the kingdom's spirits.",
            "target": {"food": 40, "gold": 10},
            "reward_morale": 10,
            "reward_resources": {"food": 15},
            "narrative_complete": "The Hearthkeepers hosted a grand feast! The whole kingdom celebrates.",
            "bonus_effect": "feast_morale",
            "rarity": "common",
        },
        # ── Rare / conditional quests ──
        {
            "type": "brewery",
            "name": "Brew the Golden Ale",
            "desc": "The tavern's stores run low — brew a legendary batch of golden ale.",
            "target": {"food": 25, "gold": 15},
            "reward_morale": 7,
            "reward_resources": {"gold": 20},
            "narrative_complete": "The Hearthkeepers' golden ale flows freely! Songs echo from the tavern for days.",
            "bonus_effect": "tavern_boost",
            "rarity": "rare",
            "requires_building": "tavern",
        },
        {
            "type": "hearth_fire",
            "name": "Kindle the Hearth-Fires",
            "desc": "Light ceremonial fires in every home to ward off the darkness.",
            "target": {"wood": 30, "gold": 10},
            "reward_morale": 8,
            "reward_resources": {"wood": 10},
            "narrative_complete": "Hearth-fires burn bright across Ashfall. No shadow dares linger.",
            "bonus_effect": "morale_resilience",
            "rarity": "rare",
            "requires_season": "autumn",
        },
        # ── Chain quest (unlocks after completing Raise the Walls) ──
        {
            "type": "citadel",
            "name": "Build the Inner Citadel",
            "desc": "The walls are strong — now build a citadel to command the heart of Ashfall.",
            "target": {"stone": 50, "wood": 30, "gold": 25},
            "reward_morale": 10,
            "reward_resources": {"stone": 20, "gold": 15},
            "narrative_complete": "The Inner Citadel rises above Ashfall — a bastion of hope visible for miles.",
            "bonus_effect": "citadel_defense",
            "rarity": "chain",
            "chain_from": "fortify",
        },
    ],
    "deepwardens": [
        # ── Common quests ──
        {
            "type": "prospect",
            "name": "Deep Prospecting",
            "desc": "Push deeper into the mines — uncover new veins of stone and ore.",
            "target": {"stone": 35, "gold": 15},
            "reward_morale": 5,
            "reward_resources": {"stone": 12, "gold": 8},
            "narrative_complete": "The Deepwardens struck a rich new seam! The kingdom's coffers swell.",
            "rarity": "common",
        },
        {
            "type": "excavate",
            "name": "Ancient Excavation",
            "desc": "Excavate buried ruins — the old places hold power.",
            "target": {"stone": 30, "gold": 10},
            "reward_morale": 7,
            "reward_resources": {"gold": 15},
            "narrative_complete": "The Deepwardens unearthed relics from the old world. Ancient knowledge stirs.",
            "bonus_effect": "exploration_insight",
            "rarity": "common",
        },
        {
            "type": "map_wilds",
            "name": "Chart the Unknown",
            "desc": "Send scouts to map uncharted lands beyond the kingdom's borders.",
            "target": {"gold": 20, "food": 15},
            "reward_morale": 4,
            "reward_resources": {"gold": 10},
            "narrative_complete": "The Deepwardens returned with maps of new lands. The world grows larger.",
            "bonus_effect": "map_bonus",
            "rarity": "common",
        },
        # ── Rare / conditional quests ──
        {
            "type": "gem_hunt",
            "name": "Crystal-Seam Hunt",
            "desc": "Whispers of a crystal seam beneath the depths — find it before it's lost again.",
            "target": {"stone": 40, "gold": 25},
            "reward_morale": 6,
            "reward_resources": {"gold": 30},
            "narrative_complete": "The Deepwardens uncovered a glittering crystal seam! Wealth flows into Ashfall.",
            "bonus_effect": "gold_rush",
            "rarity": "rare",
            "requires_territory": "ironroot_depths",
        },
        {
            "type": "deep_forge",
            "name": "Forge the Deep-Iron",
            "desc": "Smelt ore in the heart of the depths — craft tools of unmatched quality.",
            "target": {"stone": 25, "gold": 20},
            "reward_morale": 7,
            "reward_resources": {"stone": 10, "gold": 10},
            "narrative_complete": "Deep-Iron tools emerge from the forges. Every worker in Ashfall feels the difference.",
            "bonus_effect": "production_boost",
            "rarity": "rare",
            "requires_building": "market_hall",
        },
        # ── Chain quest (unlocks after completing Deep Prospecting) ──
        {
            "type": "vein_lord",
            "name": "Awaken the Vein-Lord",
            "desc": "The richest seam pulses with ancient energy. Perform the old rites to awaken it.",
            "target": {"stone": 55, "gold": 35},
            "reward_morale": 10,
            "reward_resources": {"stone": 25, "gold": 25},
            "narrative_complete": "The Vein-Lord awakens! Ore glows softly in the dark — the depths are alive with bounty.",
            "bonus_effect": "vein_lord_bounty",
            "rarity": "chain",
            "chain_from": "prospect",
        },
    ],
    "wildwalkers": [
        # ── Common quests ──
        {
            "type": "bountiful_harvest",
            "name": "Bountiful Harvest",
            "desc": "Tend the land with care — coax abundance from field and forest.",
            "target": {"food": 35, "gold": 10},
            "reward_morale": 6,
            "reward_resources": {"food": 15, "gold": 5},
            "narrative_complete": "The Wildwalkers' careful stewardship brings a bountiful harvest. The land provides.",
            "rarity": "common",
        },
        {
            "type": "herb_lore",
            "name": "Herb-Lore Gathering",
            "desc": "Seek out rare herbs in the marsh and deep woods — remedies for the sick.",
            "target": {"food": 15, "gold": 20},
            "reward_morale": 5,
            "reward_resources": {"gold": 12},
            "narrative_complete": "The Wildwalkers returned with pouches full of rare remedies. The sick will find comfort.",
            "bonus_effect": "disease_resist",
            "rarity": "common",
        },
        {
            "type": "harmony",
            "name": "Walk in Harmony",
            "desc": "Live lightly on the land — balance the kingdom's needs with nature's rhythms.",
            "target": {"food": 20, "wood": 20},
            "reward_morale": 8,
            "reward_resources": {"food": 10, "wood": 5},
            "narrative_complete": "The Wildwalkers led the kingdom in a season of harmony. The Sleeper's blessing is felt.",
            "bonus_effect": "harmony_morale",
            "rarity": "common",
        },
        # ── Rare / conditional quests ──
        {
            "type": "grove_tending",
            "name": "Tend the Sacred Grove",
            "desc": "An ancient grove on the borderlands needs tending — its trees remember the old world.",
            "target": {"food": 20, "wood": 25},
            "reward_morale": 7,
            "reward_resources": {"food": 10, "wood": 15},
            "narrative_complete": "The Sacred Grove breathes anew. The Wildwalkers hear whispers of the Sleeper among the leaves.",
            "bonus_effect": "ash_bloom_boost",
            "rarity": "rare",
            "requires_territory": "old_oak_ridge",
        },
        {
            "type": "marsh_pilgrimage",
            "name": "Marsh Pilgrimage",
            "desc": "Journey into the marsh to collect rare bloom-water — said to cure any ailment.",
            "target": {"food": 15, "gold": 25},
            "reward_morale": 6,
            "reward_resources": {"gold": 18},
            "narrative_complete": "The Wildwalkers return with vials of shimmering bloom-water. The sick rise from their beds.",
            "bonus_effect": "disease_cure",
            "rarity": "rare",
            "requires_territory": "glimmer_marsh",
        },
        # ── Chain quest (unlocks after completing Walk in Harmony) ──
        {
            "type": "sleeper_communion",
            "name": "Communion with the Sleeper",
            "desc": "The harmony is deep enough — gather at the dreaming places and speak with the Sleeper.",
            "target": {"food": 30, "wood": 25, "gold": 20},
            "reward_morale": 12,
            "reward_resources": {"food": 20, "gold": 15},
            "narrative_complete": "The Sleeper stirs! In dreams across Ashfall, every citizen feels a warm presence. The land itself smiles.",
            "bonus_effect": "sleeper_blessing",
            "rarity": "chain",
            "chain_from": "harmony",
        },
    ],
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
    "Midsummer Revel": {
        "hearthkeepers": 3,
        "deepwardens": 2,
        "wildwalkers": 5,
    },
    "Vale Blossom Fair": {
        "hearthkeepers": 4,
        "deepwardens": 1,
        "wildwalkers": 5,
    },
    "Ridge Timberfest": {
        "hearthkeepers": 5,
        "deepwardens": 4,
        "wildwalkers": 2,
    },
    "Marsh Lantern Night": {
        "hearthkeepers": 3,
        "deepwardens": 3,
        "wildwalkers": 4,
    },
    "Deepforge Fires": {
        "hearthkeepers": 2,
        "deepwardens": 6,
        "wildwalkers": 1,
    },
    "Plains Gallop": {
        "hearthkeepers": 3,
        "deepwardens": 3,
        "wildwalkers": 4,
    },
    "Ashen Vigil": {
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
        self.mastery_level = 0     # 0=novice, 1=apprentice, 2=journeyman, 3=expert, 4=master
        self.memories = []
        self.parents = []
        self.children = []
        self.spouse = None          # Citizen reference (marriage partner)
        self.combat_skill = 0       # 0-100 scale, only meaningful for guards
        self.heirloom = None        # Optional family heirloom dict
        self.apprenticed_under = None  # Name of parent who passed down mastery
        self.wisdom_traits = []     # Condensed from old memories — persistent buffs
        self._memory_timestamps = []  # (day, event) — parallel to memories for aging
        self.dream_bonds = []       # Names of citizens bonded through shared deep-resonance dreams
        self._dream_bond_bonus = 0  # Morale bonus from dream-bond partner's recent morale gain

    # ── Wisdom trait pool (class-level) — each gives a persistent bonus ──
    # Also used by People._well_ritual_wisdom_bestowal()
    WISDOM_TRAITS = [
        {"name": "Seasoned Perspective",
         "desc": "Has seen enough to know what truly matters.",
         "effect": "morale_floor", "value": 15},
        {"name": "Old Ways Remembered",
         "desc": "Carries knowledge of traditions others have forgotten.",
         "effect": "seasonal_morale", "value": 2},
        {"name": "Hard Lessons",
         "desc": "Survived hardships that taught resilience.",
         "effect": "disease_resist", "value": 5},
        {"name": "Tales to Tell",
         "desc": "A living repository of the kingdom's stories.",
         "effect": "mentoring_boost", "value": 2},
        {"name": "Patient Hand",
         "desc": "Decades of work have honed instincts no apprentice can match.",
         "effect": "work_bonus", "value": 1},
        # Water/well-themed traits — awakened by deep well rituals
        {"name": "Well-Watcher's Eye",
         "desc": "The water shows them things others cannot see.",
         "effect": "morale_floor", "value": 10},
        {"name": "Deep Remembering",
         "desc": "The Sleeper's dreams echo through their hands.",
         "effect": "work_bonus", "value": 1},
        {"name": "Aquifer's Patience",
         "desc": "Clean water flows through their spirit — illness finds no foothold.",
         "effect": "disease_resist", "value": 5},
    ]

    def work(self, people_obj=None):
        """Citizen performs their role; returns resources produced.
        Mastery bonuses are added to base output.
        If people_obj is provided, inter-heirloom synergy is applied.
        Wisdom traits can add a small bonus."""
        if not self.alive:
            return {}
        self.days_in_role += 1
        role_data = ROLES.get(self.role, {})
        self.morale += role_data.get("work_strain", 0)
        # Apply wisdom morale floor after strain
        floor = self.wisdom_morale_floor(people_obj=people_obj)
        self.morale = max(floor, min(100, self.morale))
        output = role_data.get("output", {}).copy()

        # Add mastery bonuses
        bonuses = MASTERY_BONUSES.get(self.role, {})
        for lvl in range(1, self.mastery_level + 1):
            if lvl in bonuses:
                for resource, amount in bonuses[lvl].items():
                    output[resource] = output.get(resource, 0) + amount

        # Wisdom work bonus
        wb = self.wisdom_work_bonus()
        if wb > 0:
            for resource in output:
                output[resource] = output.get(resource, 0) + wb

        # Heirloom production bonus (if role matches, scaled by generation)
        if self.heirloom:
            hb = self.heirloom.get("production_bonus", {})
            if self.role in hb.get("roles", []):
                gen = self.heirloom.get("generations", 1)
                gen_bonus = min((gen - 1) // 2, 3)  # +1 per 2 generations beyond first, cap +3
                base_res = self.heirloom.get("base_prod_res", hb.get("resources", {}))
                for resource, base_amount in base_res.items():
                    scaled_amount = base_amount + gen_bonus
                    output[resource] = output.get(resource, 0) + scaled_amount

                # ── Inter-Heirloom Synergy ──
                # Working alongside other heirloom holders of the same role grants extra output.
                # Each fellow heirloom holder (with a different heirloom) adds +1 per resource.
                if people_obj:
                    fellow_holders = [
                        c for c in people_obj.citizens
                        if c.alive and c is not self
                        and c.role == self.role
                        and c.heirloom is not None
                        and c.heirloom.get("name") != self.heirloom.get("name")
                    ]
                    if fellow_holders:
                        synergy = len(fellow_holders)  # +1 per fellow heirloom holder
                        for resource in base_res:
                            output[resource] = output.get(resource, 0) + synergy

        # ── Dream-Bond Work Bonus ──
        # Dream-bonded citizens gain subtle insight from their bond — +1 to all output
        # when at least one dream-bond partner is alive and working the same role
        if self.dream_bonds and people_obj:
            bonded_workers = [
                c for c in people_obj.citizens
                if c.alive and c.name in self.dream_bonds and c.role == self.role
            ]
            if bonded_workers:
                for resource in output:
                    output[resource] = output.get(resource, 0) + 1

        # ── Faction Relic Work Bonus ──
        # If this citizen's faction has a relic whose prod_roles include their role,
        # they receive the relic's production bonus even if they are not the holder.
        # The relic's power extends to all faction members in the same trade.
        if people_obj and hasattr(people_obj, '_faction_relics') and self.faction and self.role not in ("child", "elder"):
            for relic in people_obj._faction_relics:
                if relic["faction"] != self.faction:
                    continue
                if self.role not in relic.get("prod_roles", []):
                    continue
                gen_scale = min((relic.get("generation", 1) - 1) // 2, 3)
                for resource, base_amount in relic.get("prod_resources", {}).items():
                    scaled_amount = base_amount + gen_scale
                    output[resource] = output.get(resource, 0) + scaled_amount

        return output

    def mastery_title(self):
        """Human-readable mastery title."""
        return MASTERY_TITLES.get(self.mastery_level, "Novice")

    def mastery_description(self):
        """What this mastery level grants for this role."""
        role_descs = MASTERY_DESCRIPTIONS.get(self.role, {})
        return role_descs.get(self.mastery_level, "")

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
        """Store a personal memory with timestamp for aging/condensation."""
        day = world.day if hasattr(world, 'day') else 0
        self.memories.append(event)
        self._memory_timestamps.append((day, event))
        if len(self.memories) > 15:
            # Trim timestamps alongside memories
            self.memories.pop(0)
            self._memory_timestamps.pop(0)

    def condense_memories(self, current_day=None):
        """Condense old memories into wisdom traits.
        When a citizen has accumulated many old memories, they distill
        into lasting wisdom — a persistent trait that gives a small bonus.
        Returns a list of new wisdom traits gained, or empty list."""
        if current_day is None:
            current_day = world.day if hasattr(world, 'day') else 0

        # Only condense when there are enough memories and some are old
        if len(self.memories) < 8:
            return []

        # Count memories older than 60 days
        old_count = sum(1 for d, _ in self._memory_timestamps if current_day - d > 60)
        if old_count < 4:
            return []

        # Pick a trait they don't already have
        existing_names = {t["name"] for t in self.wisdom_traits}
        available = [t for t in __class__.WISDOM_TRAITS if t["name"] not in existing_names]
        if not available:
            return []

        new_trait = dict(random.choice(available))
        # Generate narrative based on trait type
        narratives = {
            "Seasoned Perspective": f"{self.name}'s many memories have distilled into seasoned perspective — hard times no longer shake them as deeply.",
            "Old Ways Remembered": f"{self.name} remembers the old ways — their presence steadies the community through seasonal changes.",
            "Hard Lessons": f"{self.name}'s hard-won experience grants a measure of resilience against illness.",
            "Tales to Tell": f"{self.name} has become a living story-weaver — their tales enrich every gathering.",
            "Patient Hand": f"{self.name}'s patient hands remember what the mind has long forgotten — their craft flows effortlessly.",
            "Well-Watcher's Eye": f"{self.name} now sees what the well's water reveals — glimpses of the world beneath the world.",
            "Deep Remembering": f"The Sleeper's dreaming mind has touched {self.name}'s hands — their work carries an echo of the old world.",
            "Aquifer's Patience": f"Something in the deep water has fortified {self.name}'s spirit — illness finds them a harder target.",
        }
        new_trait["narrative"] = narratives.get(new_trait["name"], f"{self.name} gained wisdom: {new_trait['name']}.")
        self.wisdom_traits.append(new_trait)

        # Condense: clear oldest 4-6 memories to make room
        remove_count = min(random.randint(4, 6), len(self.memories) - 4)
        for _ in range(remove_count):
            self.memories.pop(0)
            if self._memory_timestamps:
                self._memory_timestamps.pop(0)

        self.remember(f"Old memories condensed into wisdom: {new_trait['name']}")
        self.morale = min(100, self.morale + 3)  # small morale boost from gaining perspective

        return [new_trait]

    def _heirloom_wisdom_multiplier(self):
        """If this citizen holds an heirloom, its generational weight amplifies
        wisdom trait effects. Returns a float 1.0–2.0."""
        if not self.heirloom:
            return 1.0
        gen = self.heirloom.get("generations", 1)
        if gen >= 10:
            return 2.0
        elif gen >= 7:
            return 1.75
        elif gen >= 5:
            return 1.5
        elif gen >= 3:
            return 1.25
        return 1.0

    def _wisdom_synergy_bonus(self, effect_type):
        """Return bonus from wisdom trait synergy for a given effect type.
        Synergy is set by _check_wisdom_synergy on People."""
        synergy = getattr(self, '_wisdom_synergy', {})
        bonus = 0
        for t in self.wisdom_traits:
            if t["effect"] == effect_type and t["name"] in synergy:
                bonus += synergy[t["name"]]
        return bonus

    # ── Seasonal awakening mapping (class-level) ──
    # Certain wisdom traits are stronger in specific seasons
    _WISDOM_SEASONAL_AWAKENING = {
        "Seasoned Perspective": "winter",      # Hard times test perspective
        "Old Ways Remembered": "autumn",       # Harvest wisdom, old traditions
        "Hard Lessons": "summer",              # Disease season — resilience matters
        "Tales to Tell": "winter",             # Long nights, storytelling season
        "Patient Hand": "spring",              # Planting, careful work
        "Well-Watcher's Eye": "spring",        # Water runs clearest
        "Deep Remembering": "autumn",          # Sleeper's memories strongest in fading light
        "Aquifer's Patience": "summer",        # Clean water fortifies against summer ailments
    }

    def _seasonal_awakening_bonus(self, world_obj=None):
        """Return bonus multiplier (0.0–1.0) for wisdom traits awakened
        by the current season. Stacks additively per matching trait.
        Called by wisdom helper methods."""
        if world_obj is None:
            return 0.0
        season = getattr(world_obj, 'season', 'spring')
        bonus = 0.0
        for t in self.wisdom_traits:
            awakened_season = self._WISDOM_SEASONAL_AWAKENING.get(t["name"])
            if awakened_season == season:
                bonus += 0.5  # +50% effect per awakened trait
        return bonus

    def wisdom_morale_floor(self, world_obj=None, people_obj=None):
        """Return the highest morale floor from wisdom traits, or 0.
        Heirloom-wisdom resonance amplifies values for heirloom holders.
        Wisdom synergy adds +2 per sharing citizen.
        Seasonal awakening multiplies the final value.
        Dream-bonds add +3 per living bond partner.
        Faction relics add +1 per relic owned by the citizen's faction.
        Permanent alliances add +2 for citizens in allied factions."""
        floor = 0
        mult = self._heirloom_wisdom_multiplier()
        for t in self.wisdom_traits:
            if t["effect"] == "morale_floor":
                floor = max(floor, int(t["value"] * mult))
        floor += self._wisdom_synergy_bonus("morale_floor") * 5  # +5 floor per synergy
        # Seasonal awakening
        seasonal = self._seasonal_awakening_bonus(world_obj)
        if seasonal > 0:
            floor = int(floor * (1.0 + seasonal))
        # Dream-bond bonus
        floor += self._dream_bond_bonus * 3
        # Faction relic bonus: +1 per relic owned by the citizen's faction
        if people_obj and hasattr(people_obj, '_faction_relics') and self.faction:
            relic_count = sum(1 for r in people_obj._faction_relics if r["faction"] == self.faction)
            floor += relic_count
        # Permanent alliance bonus: +2 for citizens in allied factions
        if people_obj and hasattr(people_obj, '_permanent_alliances') and self.faction:
            for alliance in people_obj._permanent_alliances:
                if self.faction in (alliance["faction_a"], alliance["faction_b"]):
                    floor += 2
                    break
        return floor

    def wisdom_work_bonus(self, world_obj=None):
        """Return total work bonus from wisdom traits.
        Heirloom-wisdom resonance amplifies values for heirloom holders.
        Wisdom synergy adds +1 per sharing citizen.
        Seasonal awakening multiplies the final value.
        Dream-bonds add +1 per living bond partner."""
        bonus = 0
        mult = self._heirloom_wisdom_multiplier()
        for t in self.wisdom_traits:
            if t["effect"] == "work_bonus":
                bonus += int(t["value"] * mult)
        bonus += self._wisdom_synergy_bonus("work_bonus")
        seasonal = self._seasonal_awakening_bonus(world_obj)
        if seasonal > 0:
            bonus = int(bonus * (1.0 + seasonal))
        # Dream-bond work bonus
        bonus += self._dream_bond_bonus
        return bonus

    def wisdom_disease_resist(self, world_obj=None):
        """Return total disease resist % from wisdom traits.
        Heirloom-wisdom resonance amplifies values for heirloom holders.
        Wisdom synergy adds +2% per sharing citizen.
        Seasonal awakening multiplies the final value."""
        resist = 0
        mult = self._heirloom_wisdom_multiplier()
        for t in self.wisdom_traits:
            if t["effect"] == "disease_resist":
                resist += int(t["value"] * mult)
        resist += self._wisdom_synergy_bonus("disease_resist") * 2
        seasonal = self._seasonal_awakening_bonus(world_obj)
        if seasonal > 0:
            resist = int(resist * (1.0 + seasonal))
        return resist

    def wisdom_seasonal_morale(self, world_obj=None):
        """Return total seasonal morale bonus from wisdom traits.
        Heirloom-wisdom resonance amplifies values for heirloom holders.
        Wisdom synergy adds +1 per sharing citizen.
        Seasonal awakening multiplies the final value."""
        bonus = 0
        mult = self._heirloom_wisdom_multiplier()
        for t in self.wisdom_traits:
            if t["effect"] == "seasonal_morale":
                bonus += int(t["value"] * mult)
        bonus += self._wisdom_synergy_bonus("seasonal_morale")
        seasonal = self._seasonal_awakening_bonus(world_obj)
        if seasonal > 0:
            bonus = int(bonus * (1.0 + seasonal))
        return bonus

    def wisdom_mentoring_boost(self, world_obj=None):
        """Return total mentoring morale boost from wisdom traits.
        Heirloom-wisdom resonance amplifies values for heirloom holders.
        Wisdom synergy adds +1 per sharing citizen.
        Seasonal awakening multiplies the final value."""
        boost = 0
        mult = self._heirloom_wisdom_multiplier()
        for t in self.wisdom_traits:
            if t["effect"] == "mentoring_boost":
                boost += int(t["value"] * mult)
        boost += self._wisdom_synergy_bonus("mentoring_boost")
        seasonal = self._seasonal_awakening_bonus(world_obj)
        if seasonal > 0:
            boost = int(boost * (1.0 + seasonal))
        return boost

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
        if self.mastery_level >= 2:
            extra += f", {self.mastery_title()}"
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
        self.family_relations = {}       # (family_a, family_b) → score (-100 to +100)
        self.family_heirlooms = []       # [{name, origin, bonus_type, holder, created_day, ...}]
        self.faction_leaders = {}           # faction -> citizen name
        self.faction_election_history = []  # [{faction, old_leader, new_leader, day, reason}]
        self.faction_quests = {}            # faction -> active quest dict (or None)
        self._last_quest_gen_day = 0        # throttle quest generation
        self.faction_quest_history = []     # [{faction, type, name, completed_day, ...}]
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

    # ── FACTION QUESTS ─────────────────────────────────────

    def _get_kingdom_age_tier(self, world_obj=None):
        """Return (tier_number, multiplier, tier_name) based on kingdom age.
        Used to scale quest targets and rewards as the kingdom grows older."""
        if world_obj is None:
            world_obj = world
        day = world_obj.day
        if day < 100:
            return 1, 1.0, "Early"
        elif day < 250:
            return 2, 1.5, "Growing"
        elif day < 500:
            return 3, 2.0, "Established"
        else:
            return 4, 2.5, "Ancient"

    def _generate_faction_quests(self, world_obj=None):
        """Periodically generate a quest for each faction that doesn't have one active.
        Quests are aligned with faction priorities. Fires every ~20-35 days.
        Quest targets and rewards now scale with kingdom age (difficulty tiers)."""
        if world_obj is None:
            world_obj = world

        # Throttle: only generate every 20-35 days
        if world_obj.day - self._last_quest_gen_day < random.randint(20, 35):
            return None

        self._last_quest_gen_day = world_obj.day

        # Get kingdom age tier for scaling
        age_tier, age_mult, tier_name = self._get_kingdom_age_tier(world_obj)

        events = []

        for faction in FACTIONS:
            if self.faction_quests.get(faction) is not None:
                continue  # already has an active quest

            # Ensure faction has members
            members = self.list_by_faction(faction)
            if len(members) < 3:
                continue

            # Pick a quest template, respecting rarity tiers and chain prerequisites
            templates = FACTION_QUEST_DEFS.get(faction, [])
            if not templates:
                continue

            # Filter templates by availability
            available = []
            for tmpl in templates:
                rarity = tmpl.get("rarity", "common")

                # Chain quests: require the prerequisite quest to have been completed
                if rarity == "chain":
                    chain_from = tmpl.get("chain_from")
                    if chain_from:
                        # Check quest history for completed prerequisite
                        prereq_done = any(
                            h.get("faction") == faction and h.get("type") == chain_from and h.get("outcome") == "completed"
                            for h in self.faction_quest_history
                        )
                        if not prereq_done:
                            continue

                # Rare quests: check conditional requirements
                if rarity == "rare":
                    if tmpl.get("requires_building"):
                        bldg = tmpl["requires_building"]
                        if not kingdom.buildings.get(bldg, 0):
                            continue
                    if tmpl.get("requires_season"):
                        if world_obj.season != tmpl["requires_season"]:
                            continue
                    if tmpl.get("requires_territory"):
                        if tmpl["requires_territory"] not in kingdom.territory:
                            continue

                available.append(tmpl)

            if not available:
                continue

            # Weighted selection: common = 60%, rare = 25%, chain = 15%
            weights = []
            for tmpl in available:
                rarity = tmpl.get("rarity", "common")
                if rarity == "chain":
                    weights.append(15)
                elif rarity == "rare":
                    weights.append(25)
                else:
                    weights.append(60)

            template = random.choices(available, weights=weights, k=1)[0]

            # Scale targets: faction size × kingdom age tier
            faction_scale = max(1, len(members) // 5)
            scaled_target = {}
            for resource, base in template["target"].items():
                scaled_target[resource] = max(1, int(base * faction_scale * age_mult))

            # Scale rewards by age tier too
            scaled_rewards = {}
            for resource, base in template["reward_resources"].items():
                scaled_rewards[resource] = max(1, int(base * age_mult))

            # Chain quests get longer deadlines (also scale by tier)
            base_deadline = 60 if template.get("rarity") == "chain" else 45
            deadline_days = int(base_deadline * max(1.0, age_mult * 0.75))

            quest = {
                "faction": faction,
                "type": template["type"],
                "name": template["name"],
                "desc": template["desc"],
                "target": scaled_target,
                "progress": {r: 0 for r in scaled_target},
                "reward_morale": max(1, int(template["reward_morale"] * age_mult)),
                "reward_resources": scaled_rewards,
                "narrative_complete": template["narrative_complete"],
                "bonus_effect": template.get("bonus_effect"),
                "rarity": template.get("rarity", "common"),
                "chain_from": template.get("chain_from"),
                "start_day": world_obj.day,
                "deadline": world_obj.day + deadline_days,
                "completed": False,
                "failed": False,
                "age_tier": age_tier,
                "tier_name": tier_name,
            }
            self.faction_quests[faction] = quest

            rarity_prefix = ""
            if template.get("rarity") == "chain":
                rarity_prefix = "🔗 CHAIN QUEST: "
            elif template.get("rarity") == "rare":
                rarity_prefix = "✨ RARE QUEST: "

            tier_badge = {1: "🌱", 2: "🌿", 3: "🌳", 4: "🏛️"}.get(age_tier, "")
            narrative = (
                f"{rarity_prefix}{tier_badge} TIER {age_tier} ({tier_name}): 📜 FACTION QUEST: "
                f"The {FACTIONS[faction]['color']} {faction} "
                f"have taken up a new quest — '{template['name']}'! "
                f"{template['desc']}"
            )
            kingdom.kingdom_log.append(narrative)
            for m in members:
                m.morale = min(100, m.morale + 2)
                m.remember(f"New {faction} quest: {template['name']}")

            events.append({"faction": faction, "quest": template["name"], "narrative": narrative})

        return events if events else None

    def _contribute_to_faction_quest(self, citizen, work_output):
        """Citizen's daily work contributes to their faction's active quest.
        Called from work() after base output is calculated."""
        if not citizen.faction:
            return
        quest = self.faction_quests.get(citizen.faction)
        if quest is None or quest.get("completed") or quest.get("failed"):
            return

        for resource, amount in work_output.items():
            if resource in quest["progress"]:
                quest["progress"][resource] += amount

    def _spawn_deep_whisper_quest(self, quest_data, world_obj=None):
        """Spawn a faction quest triggered by a deep whisper event.
        Called from World._check_deep_whispers() when a T3+ whisper has quest data.
        The whisper acts as a quest-giver — the Sleeper or Remembered asking the kingdom
        to do something momentous.

        Returns quest dict or None if all factions are busy."""
        if world_obj is None:
            world_obj = world

        # Find eligible faction
        preference = quest_data.get("faction_preference")
        faction = None

        if preference and self.faction_quests.get(preference) is None:
            faction = preference

        if faction is None:
            # Pick a random faction without an active quest
            available = [f for f in FACTIONS if self.faction_quests.get(f) is None]
            if available:
                faction = random.choice(available)

        if faction is None:
            return None  # all factions busy — quest will be lost (the whisper fades)

        members = self.list_by_faction(faction)
        if len(members) < 2:
            return None

        # Scale targets modestly by faction size
        faction_scale = max(1, len(members) // 4)
        scaled_target = {}
        for resource, base in quest_data["target"].items():
            scaled_target[resource] = max(1, int(base * faction_scale * 0.75))

        scaled_rewards = {}
        for resource, base in quest_data["reward_resources"].items():
            scaled_rewards[resource] = max(1, int(base * faction_scale * 0.75))

        deadline_days = 70  # deep-whisper quests are epic — generous deadline

        quest = {
            "faction": faction,
            "type": "deep_whisper",
            "name": quest_data["name"],
            "desc": quest_data["desc"],
            "target": scaled_target,
            "progress": {r: 0 for r in scaled_target},
            "reward_morale": quest_data["reward_morale"],
            "reward_resources": scaled_rewards,
            "narrative_complete": quest_data["narrative_complete"],
            "bonus_effect": quest_data.get("bonus_effect"),
            "rarity": "chain",
            "chain_from": "deep_whisper",
            "start_day": world_obj.day,
            "deadline": world_obj.day + deadline_days,
            "completed": False,
            "failed": False,
        }
        self.faction_quests[faction] = quest

        color = FACTIONS[faction].get("color", "")
        narrative = (
            f"🌊 DEEP-WHISPER QUEST: The dreaming deep has called upon the {color} {faction} "
            f"— '{quest_data['name']}'! {quest_data['desc']}"
        )
        kingdom.kingdom_log.append(narrative)

        for m in members:
            m.morale = min(100, m.morale + 4)
            m.remember(f"Deep-whisper quest: {quest_data['name']}")

        return {"faction": faction, "quest": quest_data["name"], "narrative": narrative}

    def _update_faction_quest_progress(self, world_obj=None):
        """Check faction quests for completion or expiration.
        Called daily in advance_day. Returns list of resolution events."""
        if world_obj is None:
            world_obj = world

        events = []
        for faction, quest in list(self.faction_quests.items()):
            if quest is None or quest.get("completed") or quest.get("failed"):
                continue

            # Check completion: all targets met
            all_met = True
            for resource, needed in quest["target"].items():
                if quest["progress"].get(resource, 0) < needed:
                    all_met = False
                    break

            if all_met:
                event = self._complete_faction_quest(faction, quest, "completed", world_obj)
                events.append(event)

            # Check deadline expired
            elif world_obj.day > quest.get("deadline", 99999):
                # ── FACTION WISDOM COUNCIL INTERCESSION ──
                # If the faction has a wisdom council (3+ wise members),
                # they can intercede once per quest to prevent failure
                if not quest.get("_council_interceded"):
                    wise_count = len([c for c in self.citizens
                                     if c.alive and c.faction == faction and c.wisdom_traits])
                    if wise_count >= 3:
                        # Council intercedes — extend deadline, reduce targets slightly
                        extension = random.randint(10, 15)
                        quest["deadline"] = world_obj.day + extension
                        quest["_council_interceded"] = True
                        # Slightly ease targets (5-15% reduction)
                        for resource in quest["target"]:
                            reduction = max(1, int(quest["target"][resource] * random.uniform(0.05, 0.15)))
                            quest["target"][resource] = max(1, quest["target"][resource] - reduction)

                        color = FACTIONS[faction].get("color", "")
                        wise_names = [c.name for c in self.citizens
                                     if c.alive and c.faction == faction and c.wisdom_traits]
                        council_names = ", ".join(wise_names[:3])
                        if len(wise_names) > 3:
                            council_names += f" and {len(wise_names)-3} others"

                        intercede_narrative = (
                            f"🏛️🛡️ COUNCIL INTERCESSION: The {color} {faction} wisdom council "
                            f"({council_names}) has intervened to prevent '{quest['name']}' from failing! "
                            f"The deadline has been extended by {extension} days and targets eased. "
                            f"The elders' wisdom buys precious time."
                        )
                        kingdom.kingdom_log.append(intercede_narrative)
                        events.append({
                            "faction": faction,
                            "quest": quest["name"],
                            "type": "council_intercession",
                            "extension": extension,
                            "narrative": intercede_narrative,
                        })
                        continue  # skip failure — quest continues

                # No council or already interceded — quest fails
                event = self._complete_faction_quest(faction, quest, "failed", world_obj)
                events.append(event)

        # Check for pending heirloom legacy quests that can now fire
        legacy_events = self._check_pending_legacy_quests()
        if legacy_events:
            events.extend(legacy_events)

        return events if events else None

    def _complete_faction_quest(self, faction, quest, outcome, world_obj=None):
        """Resolve a faction quest: apply rewards/penalties, log narrative, archive."""
        if world_obj is None:
            world_obj = world

        members = self.list_by_faction(faction)
        # For joint quests, also boost the allied faction's members
        joint_members = []
        if quest.get("_is_joint"):
            for jf in quest.get("_joint_factions", []):
                if jf != faction:
                    joint_members = self.list_by_faction(jf)
                    break

        if outcome == "completed":
            # Apply resource rewards
            for resource, amount in quest["reward_resources"].items():
                if resource == "food":
                    kingdom.food += amount
                elif resource == "wood":
                    kingdom.wood += amount
                elif resource == "stone":
                    kingdom.stone += amount
                elif resource == "gold":
                    kingdom.gold += amount

            # Morale boost to faction members
            morale_reward = quest.get("reward_morale", 5)
            for m in members:
                m.morale = min(100, m.morale + morale_reward)
                m.remember(f"Completed {faction} quest: {quest['name']}")
            # Joint quests: also boost allied faction
            for m in joint_members:
                m.morale = min(100, m.morale + morale_reward)
                m.remember(f"Completed joint quest with {faction}: {quest['name']}")

            narrative = (
                f"✅ QUEST COMPLETE: The {FACTIONS[faction]['color']} {faction} "
                f"have completed '{quest['name']}'! {quest['narrative_complete']}"
            )

            # Bonus effects
            bonus_narrative = self._apply_quest_bonus(faction, quest.get("bonus_effect"), world_obj)
            if bonus_narrative:
                narrative += f" {bonus_narrative}"

        else:  # failed
            penalty = random.randint(2, 4)
            for m in members:
                m.morale = max(0, m.morale - penalty)
                m.remember(f"Failed to complete {faction} quest: {quest['name']}")
            for m in joint_members:
                m.morale = max(0, m.morale - penalty)
                m.remember(f"Joint quest with {faction} failed: {quest['name']}")

            narrative = (
                f"❌ QUEST FAILED: The {FACTIONS[faction]['color']} {faction} "
                f"could not complete '{quest['name']}' in time. "
                f"The faction is disheartened (-{penalty} morale)."
            )

        kingdom.kingdom_log.append(narrative)

        # Archive quest
        quest["completed"] = (outcome == "completed")
        quest["failed"] = (outcome == "failed")
        quest["resolved_day"] = world_obj.day
        self.faction_quest_history.append({
            "faction": faction,
            "type": quest["type"],
            "name": quest["name"],
            "outcome": outcome,
            "start_day": quest["start_day"],
            "resolved_day": world_obj.day,
            "progress": quest["progress"].copy(),
            "target": quest["target"].copy(),
            "rarity": quest.get("rarity", "common"),
            "chain_from": quest.get("chain_from", ""),
            "age_tier": quest.get("age_tier", 1),
            "tier_name": quest.get("tier_name", "Early"),
        })

        # Clear active quest
        self.faction_quests[faction] = None

        # If this was a joint quest, clear the other faction's slot too
        if quest.get("_is_joint"):
            for jf in quest.get("_joint_factions", []):
                if jf != faction and self.faction_quests.get(jf) is quest:
                    self.faction_quests[jf] = None

        return {"faction": faction, "quest": quest["name"], "outcome": outcome, "narrative": narrative}

    def _apply_quest_bonus(self, faction, bonus_effect, world_obj=None):
        """Apply post-completion bonus effects for certain quests.
        Returns a narrative string or empty string."""
        if not bonus_effect:
            return ""

        if bonus_effect == "defense_boost":
            kingdom.defense_rating = getattr(kingdom, 'defense_rating', 0)
            # Temporary defense boost (handled via a simple attribute)
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["defense"] = {"value": 2, "expires": world_obj.day + 30}
            return "Ashfall's defenses are bolstered (+2 defense for 30 days)."

        elif bonus_effect == "feast_morale":
            for c in self.citizens:
                if c.alive:
                    c.morale = min(100, c.morale + 3)
            return "The whole kingdom rejoices (+3 morale to all)."

        elif bonus_effect == "exploration_insight":
            # Boost scout effectiveness temporarily
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["scout_boost"] = {"value": True, "expires": world_obj.day + 25}
            return "Scouts move with renewed purpose — mapping efforts accelerated for 25 days."

        elif bonus_effect == "map_bonus":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["map_detail"] = {"value": True, "expires": world_obj.day + 20}
            return "Maps of the surrounding lands grow more detailed."

        elif bonus_effect == "disease_resist":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["disease_resist"] = {"value": 10, "expires": world_obj.day + 25}
            return "The kingdom's knowledge of remedies strengthens (+10% disease resistance for 25 days)."

        elif bonus_effect == "harmony_morale":
            for c in self.citizens:
                if c.alive:
                    c.morale = min(100, c.morale + 2)
            return "The Sleeper's blessing settles over the land (+2 morale to all)."

        elif bonus_effect == "tavern_boost":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["tavern_morale"] = {"value": 2, "expires": world_obj.day + 25}
            for c in self.citizens:
                if c.alive:
                    c.morale = min(100, c.morale + 2)
            return "The tavern overflows with cheer (+2 morale to all, +2 daily morale for 25 days)."

        elif bonus_effect == "morale_resilience":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["morale_floor"] = {"value": 15, "expires": world_obj.day + 30}
            return "Ashfall's spirit is unshakable — morale cannot drop below 15 for 30 days."

        elif bonus_effect == "citadel_defense":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["defense"] = {"value": 5, "expires": world_obj.day + 40}
            return "The Inner Citadel commands the horizon (+5 defense for 40 days)."

        elif bonus_effect == "gold_rush":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["gold_boost"] = {"value": 5, "expires": world_obj.day + 30}
            bonus_gold = 30
            kingdom.gold += bonus_gold
            return f"The crystal seam yields a rush of wealth (+{bonus_gold} gold immediately, +5 gold/day for 30 days)."

        elif bonus_effect == "production_boost":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["production"] = {"value": 10, "expires": world_obj.day + 30}
            return "Deep-Iron tools sharpen every hand (+10% production for 30 days)."

        elif bonus_effect == "vein_lord_bounty":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["stone_boost"] = {"value": 3, "expires": world_obj.day + 35}
            kingdom._quest_bonuses["gold_boost"] = {"value": 3, "expires": world_obj.day + 35}
            return "The Vein-Lord's pulse enriches every swing of the pick (+3 stone & gold/day for 35 days)."

        elif bonus_effect == "ash_bloom_boost":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["ash_bloom"] = {"value": 10, "expires": world_obj.day + 25}
            return "The Sacred Grove hums with life — ash-bloom chance increased (+10% for 25 days)."

        elif bonus_effect == "disease_cure":
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["disease_resist"] = {"value": 20, "expires": world_obj.day + 20}
            # Heal all diseased citizens
            healed = 0
            for c in self.citizens:
                if c.alive and c.health < 100:
                    c.health = min(100, c.health + 40)
                    healed += 1
            return f"Bloom-water heals the sick ({healed} restored, +20% disease resist for 20 days)."

        elif bonus_effect == "sleeper_blessing":
            for c in self.citizens:
                if c.alive:
                    c.morale = min(100, c.morale + 5)
                    c.health = min(100, c.health + 20)
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["sleeper_favor"] = {"value": True, "expires": world_obj.day + 30}
            return "🌙 THE SLEEPER SPEAKS: Every citizen feels the warmth of the ancient one. All healed, +5 morale, Sleeper's favor for 30 days."

        elif bonus_effect == "eternal_legacy":
            # The Eternal heirloom quest: massive morale + permanent generation bonus for the heirloom
            for c in self.citizens:
                if c.alive and c.faction == faction:
                    c.morale = min(100, c.morale + 8)
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["legacy_morale"] = {"value": 3, "expires": world_obj.day + 50}
            return "The Eternal Legacy is forged! The faction's spirit blazes (+8 morale), and the kingdom feels a lasting warmth (+3 daily morale for 50 days)."

        elif bonus_effect == "shrine_blessing":
            # Shrine built for the Eternal heirloom
            for c in self.citizens:
                if c.alive:
                    c.morale = min(100, c.morale + 4)
                    c.health = min(100, c.health + 15)
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["shrine_blessing"] = {"value": True, "expires": world_obj.day + 40}
            return "The Shrine blesses all who visit — every citizen feels renewed (+4 morale, +15 health)."

        elif bonus_effect == "lore_recovery":
            # Ancient heirloom history recovered
            kingdom.gold += 15
            for c in self.citizens:
                if c.alive and c.faction == faction:
                    c.morale = min(100, c.morale + 5)
            return "Lost history recovered! The faction gains deep insight (+5 morale, +15 gold)."

        elif bonus_effect == "pilgrimage_morale":
            # Pilgrimage traces the heirloom's path
            for c in self.citizens:
                if c.alive:
                    c.morale = min(100, c.morale + 3)
            if not hasattr(kingdom, '_quest_bonuses'):
                kingdom._quest_bonuses = {}
            kingdom._quest_bonuses["pilgrimage"] = {"value": 2, "expires": world_obj.day + 35}
            return "The Pilgrimage uplifts every heart — the kingdom walks taller (+3 morale to all, +2 daily morale for 35 days)."

        return ""

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
                c.days_in_role = 0
                c.mastery_level = 0
                # Skills inheritance: children may follow parents' professions
                inherited = self._inherit_traits(c, world_obj)
                c.remember(f"Came of age, became a {c.role}")
                grad_msg = f"GRADUATION: {c.name} came of age! Now a {c.role}."
                if inherited and inherited.get("role_bias"):
                    grad_msg += f" (follows parent's path)"
                if inherited and inherited.get("mastery_inheritance"):
                    mi = inherited["mastery_inheritance"]
                    grad_msg += f" [apprenticed under {mi['from']}]"
                if inherited and inherited.get("skills", {}).get("combat", 0) >= 10:
                    grad_msg += f" [latent combat talent: {inherited['skills']['combat']}]"
                summary["aging"].append(grad_msg)

        # 9. ELDERS (60+)
        for c in self.citizens:
            if c.alive and c.role not in ("child", "elder") and c.age >= 60:
                old_role = c.role
                c.role = "elder"
                c.days_in_role = 0
                c.mastery_level = 0
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

        # 13.8 ROLE MASTERY — skill tree advancement + passive effects
        mastery_events = self._check_role_mastery(world_obj)
        if mastery_events:
            summary["mastery"] = mastery_events
            for ev in mastery_events:
                summary.setdefault("faction_news", []).append(ev["narrative"])
        # Apply mastery passive effects (builder inspiration, scout caches, elder wisdom, etc.)
        for c in self.citizens:
            if c.alive and c.mastery_level >= 1:
                mastery_passive_effect(c, self)

        # 13.9 FAMILY RELATIONS — daily drift + narrative events
        self._daily_family_relation_drift(world_obj)
        family_rel_event = self._family_relation_event(world_obj)
        if family_rel_event:
            summary["family_relations"] = family_rel_event
            summary.setdefault("faction_news", []).append(family_rel_event["narrative"])

        # 13.95 MEMORY CONDENSATION — old memories distill into wisdom traits
        memory_events = self._check_memory_condensation(world_obj)
        if memory_events:
            summary["memory_condensation"] = memory_events
            for ev in memory_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.96 WISDOM TRAIT SYNERGY — shared wisdom traits create bonds
        synergy_events = self._check_wisdom_synergy(world_obj)
        if synergy_events:
            summary["wisdom_synergy"] = synergy_events
            for ev in synergy_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.965 COLLECTIVE WISDOM DREAM — synergy groups touch the dreaming deep
        collective_dream_events = self._check_collective_wisdom_dream(world_obj)
        if collective_dream_events:
            summary["collective_dreams"] = collective_dream_events
            for ev in collective_dream_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.97 FACTION WISDOM COUNCIL — factions with many wise members gain bonuses
        council_events = self._check_faction_wisdom_council(world_obj)
        if council_events:
            summary["wisdom_council"] = council_events
            for ev in council_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.98 MEMORY DREAM EVENTS — wise elders have prophetic dreams
        dream_events = self._check_memory_dreams(world_obj)
        if dream_events:
            summary["memory_dreams"] = dream_events
            for ev in dream_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.985 DREAM-BONDS — citizens who share deep-echo dreams form permanent bonds
        bond_events = self._check_dream_bonds(world_obj)
        if bond_events:
            summary["dream_bonds"] = bond_events
            for ev in bond_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.986 DREAM-BOND TIER 2 — lore echo + Dream-Husk sensitivity
        bond_tier2_events = self._check_dream_bond_tier2(world_obj)
        if bond_tier2_events:
            summary["dream_bond_tier2"] = bond_tier2_events
            for ev in bond_tier2_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.987 DREAM-BOND TIER 3 — resource echo + deep-resonance amplification
        bond_tier3_events = self._check_dream_bond_tier3(world_obj)
        if bond_tier3_events:
            summary["dream_bond_tier3"] = bond_tier3_events
            for ev in bond_tier3_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.9875 DREAM-BOND BRIDGE: REGIONAL VISION ECHOES
        regional_vision_bond = self._check_dream_bond_regional_vision(world_obj)
        if regional_vision_bond:
            summary["dream_bond_regional_vision"] = regional_vision_bond
            for ev in regional_vision_bond:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.988 HEIRLOOM VISION CHAIN QUESTS — repeated visions spawn quests
        vision_quest_events = self._check_heirloom_vision_quests(world_obj)
        if vision_quest_events:
            for vq in vision_quest_events:
                summary.setdefault("faction_news", []).append(vq["narrative"])

        # 13.989 HEIRLOOM FACTION RELIC — gen 7+ heirlooms become faction relics
        relic_events = self._check_heirloom_faction_relic(world_obj)
        if relic_events:
            summary["faction_relics"] = relic_events
            for ev in relic_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.9895 HEIRLOOM RELIC RITUAL — faction relics spawn periodic ceremonies
        relic_ritual_events = self._check_heirloom_relic_ritual(world_obj)
        if relic_ritual_events:
            summary["relic_rituals"] = relic_ritual_events
            for ev in relic_ritual_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.990 SEASONAL COUNCIL GATHERINGS — councils more active in peak season
        seasonal_council_events = self._check_seasonal_council_gatherings(world_obj)
        if seasonal_council_events:
            summary["seasonal_council"] = seasonal_council_events
            for ev in seasonal_council_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.991 DREAM-BOND TIER 4 — danger-sense: bonded protectors shield civilians
        bond_tier4_events = self._check_dream_bond_tier4(world_obj)
        if bond_tier4_events:
            summary["dream_bond_tier4"] = bond_tier4_events
            for ev in bond_tier4_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.992 INTER-FACTION COUNCIL DIPLOMACY — councils meet across factions
        diplomacy_events = self._check_council_diplomacy(world_obj)
        if diplomacy_events:
            summary["council_diplomacy"] = diplomacy_events
            for ev in diplomacy_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.994 TRADE PACT INCOME — daily income from cross-faction trade pacts
        pact_events = self._check_trade_pact_income(world_obj)
        if pact_events:
            summary["trade_pacts"] = pact_events
            for ev in pact_events:
                if ev.get("narrative"):
                    kingdom.kingdom_log.append(ev["narrative"])

        # 13.995 PERMANENT ALLIANCE — completed-pact factions form permanent bonds
        alliance_events = self._check_permanent_alliance(world_obj)
        if alliance_events:
            summary["permanent_alliances"] = alliance_events
            for ev in alliance_events:
                kingdom.kingdom_log.append(ev["narrative"])

        # 13.996 ALLIANCE INCOME — daily income + quest progress from permanent alliances
        alliance_income = self._check_alliance_income(world_obj)
        if alliance_income:
            summary["alliance_income"] = alliance_income
            for ev in alliance_income:
                if ev.get("narrative"):
                    kingdom.kingdom_log.append(ev["narrative"])

        # 13.997 TRIFECTA FACTION QUEST — trifecta wonder spawns epic faction quest
        trifecta_quest_events = self._check_trifecta_faction_quest(world_obj)
        if trifecta_quest_events:
            for tq in trifecta_quest_events:
                summary.setdefault("faction_news", []).append(tq["narrative"])

        # 13.998 ALLIANCE JOINT MEGA-QUEST — permanent allies tackle shared destiny
        joint_quest_events = self._check_alliance_joint_quest(world_obj)
        if joint_quest_events:
            for jq in joint_quest_events:
                summary.setdefault("faction_news", []).append(jq["narrative"])

        # 13.10 FACTION QUESTS — generate, update progress, resolve
        quest_gen_events = self._generate_faction_quests(world_obj)
        if quest_gen_events:
            for qe in quest_gen_events:
                summary.setdefault("faction_news", []).append(qe["narrative"])
        quest_resolution_events = self._update_faction_quest_progress(world_obj)
        if quest_resolution_events:
            for qr in quest_resolution_events:
                summary.setdefault("faction_news", []).append(qr["narrative"])

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

        # Apply wisdom morale floor — citizens with "Seasoned Perspective" have a safety net
        for c in self.citizens:
            if c.alive and c.wisdom_traits:
                floor = c.wisdom_morale_floor(world_obj, people_obj=self)
                if floor > 0 and c.morale < floor:
                    c.morale = floor

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

            # Inter-family relations: feud blames external family → new rivalry
            other_families = set()
            for c in self.citizens:
                if c.alive and c.family_name() != family_name:
                    if factions_present:
                        # Prefer families with members in the blamed faction
                        if c.faction == blamed:
                            other_families.add(c.family_name())
                    else:
                        other_families.add(c.family_name())
            if not other_families:
                # Fallback: any other family
                for c in self.citizens:
                    if c.alive and c.family_name() != family_name:
                        other_families.add(c.family_name())
            if other_families and len(other_families) >= 1:
                rival_family = random.choice(list(other_families))
                self._update_family_relations(family_name, rival_family, -15,
                                               f"feud in {family_name} clan blamed on {rival_family}")

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

    # ── FAMILY RELATIONS (INTER-FAMILY) ────────────────────

    def _get_family_relation(self, family_a, family_b):
        """Get the relation score between two families. Returns 0 if no history."""
        if family_a == family_b:
            return 0
        key = tuple(sorted([family_a, family_b]))
        return self.family_relations.get(key, 0)

    def _update_family_relations(self, family_a, family_b, delta, reason=""):
        """Modify relation between two families. Creates entry if new.
        Logs significant changes to kingdom_log."""
        if family_a == family_b:
            return None
        old_value = self._get_family_relation(family_a, family_b)
        new_value = max(-100, min(100, old_value + delta))
        key = tuple(sorted([family_a, family_b]))
        self.family_relations[key] = new_value
        if new_value == 0:
            del self.family_relations[key]

        if abs(delta) >= 10 and reason:
            label = "ALLIANCE" if delta > 0 else "RIVALRY"
            kingdom.kingdom_log.append(
                f"👪 FAMILY {label}: {family_a} ↔ {family_b} — {reason} "
                f"({int(old_value):+d} → {int(new_value):+d})"
            )

        return {"old": old_value, "new": new_value, "delta": delta, "reason": reason}

    def _family_relation_event(self, world_obj=None):
        """Narrative events for strong alliances (share resources, boost morale)
        or bitter rivalries (flare-ups, possible injuries). Fires ~3%/day."""
        if world_obj is None:
            from world import world as world_obj

        if random.random() > 0.03:
            return None

        # Collect notable relations
        strong_alliances = [(k, v) for k, v in self.family_relations.items() if v >= 50]
        bitter_rivalries = [(k, v) for k, v in self.family_relations.items() if v <= -50]

        candidates = []
        if strong_alliances:
            candidates.extend([("alliance", k, v) for k, v in strong_alliances])
        if bitter_rivalries:
            candidates.extend([("rivalry", k, v) for k, v in bitter_rivalries])

        if not candidates:
            return None

        event_type, (fam_a, fam_b), score = random.choice(candidates)

        def family_members(family_name):
            return [c for c in self.citizens if c.alive and c.family_name() == family_name]

        members_a = family_members(fam_a)
        members_b = family_members(fam_b)

        if not members_a or not members_b:
            return None

        result = {"type": event_type, "family_a": fam_a, "family_b": fam_b, "relation": score}

        if event_type == "alliance":
            boost = random.randint(3, 6)
            all_members = members_a + members_b
            for m in all_members:
                m.morale = min(100, m.morale + boost)
                m.remember(f"Shared fellowship: {fam_a} and {fam_b} alliance strengthened")

            # 30% chance of resource sharing
            if random.random() < 0.3:
                resource = random.choice(["food", "wood", "gold"])
                amount = random.randint(3, 8)
                if resource == "food":
                    kingdom.food += amount
                elif resource == "wood":
                    kingdom.wood += amount
                else:
                    kingdom.gold += amount
                result["resource"] = {resource: amount}

            result["narrative"] = (
                f"🤝 FAMILY ALLIANCE: The {fam_a} and {fam_b} families joined together "
                f"in fellowship. All {len(all_members)} family members feel strengthened "
                f"(+{boost} morale each)."
            )
            result["members_affected"] = len(all_members)

        elif event_type == "rivalry":
            penalty = random.randint(3, 8)
            all_members = members_a + members_b
            for m in all_members:
                m.morale = max(0, m.morale - penalty)
                m.remember(f"Tensions flared between the {fam_a} and {fam_b} families")

            escalation = ""
            if random.random() < 0.15 and score <= -70:
                victim = random.choice(all_members)
                victim.health = max(10, victim.health - random.randint(10, 30))
                escalation = f" {victim.name} was injured in a heated confrontation."
                result["injured"] = victim.name
                self._update_family_relations(fam_a, fam_b, -10, "violent confrontation")

            result["narrative"] = (
                f"⚡ FAMILY RIVALRY: Old wounds between the {fam_a} and {fam_b} "
                f"families reopened. {len(all_members)} family members are shaken "
                f"(-{penalty} morale each).{escalation}"
            )
            result["members_affected"] = len(all_members)

        kingdom.kingdom_log.append(result["narrative"])
        return result

    def _daily_family_relation_drift(self, world_obj=None):
        """Slow natural drift of family relations toward zero (~0.05/day).
        Shared faction membership creates positive drift; opposing factions
        create slight negative drift. Applied once per day in advance_day."""
        if world_obj is None:
            from world import world as world_obj

        # Faction priority conflicts
        faction_conflicts = {
            ("hearthkeepers", "deepwardens"): 0.5,   # mild tension
            ("hearthkeepers", "wildwalkers"): 0.3,   # minor tension
            ("deepwardens", "wildwalkers"): 0.7,     # deeper ideological split
        }

        # Build a map: family_name → set of factions present
        family_factions = {}
        for c in self.citizens:
            if c.alive and c.faction:
                fn = c.family_name()
                if fn not in family_factions:
                    family_factions[fn] = set()
                family_factions[fn].add(c.faction)

        # Apply drift to each existing relation
        for (fam_a, fam_b), score in list(self.family_relations.items()):
            # Natural decay toward zero (0.05 per day)
            if score > 0:
                drift = -0.05
            elif score < 0:
                drift = 0.05
            else:
                drift = 0

            # Faction-based modifiers
            factions_a = family_factions.get(fam_a, set())
            factions_b = family_factions.get(fam_b, set())

            # Shared faction → +0.03 drift
            shared = factions_a & factions_b
            if shared:
                drift += 0.03 * len(shared)

            # Conflicting factions → -0.02 drift
            for fa in factions_a:
                for fb in factions_b:
                    conflict_key = tuple(sorted([fa, fb]))
                    if conflict_key in faction_conflicts:
                        drift -= 0.02 * faction_conflicts[conflict_key]

            new_score = max(-100, min(100, score + drift))
            key = tuple(sorted([fam_a, fam_b]))
            if abs(new_score) < 0.1:
                if key in self.family_relations:
                    del self.family_relations[key]
            else:
                self.family_relations[key] = new_score

    # ── MEMORY CONDENSATION ─────────────────────────────────

    def _check_memory_condensation(self, world_obj=None):
        """Periodically check citizens for old memories that can condense into wisdom traits.
        Runs daily but each citizen only condenses when their memories are old enough.
        Returns a list of condensation events or None."""
        if world_obj is None:
            world_obj = world

        events = []
        # Only check ~20% of citizens per day to spread the load
        candidates = [c for c in self.citizens if c.alive and c.age >= 30 and len(c.memories) >= 8]
        if not candidates:
            return None

        # Throttle: each citizen can only condense once every ~40 days
        if not hasattr(self, '_last_condensation_day'):
            self._last_condensation_day = {}
        # Remove stale entries
        self._last_condensation_day = {
            name: d for name, d in self._last_condensation_day.items()
            if world_obj.day - d < 40
        }

        check_count = max(1, len(candidates) // 5)
        for _ in range(check_count):
            c = random.choice(candidates)
            if c.name in self._last_condensation_day:
                continue
            if random.random() < 0.15:  # 15% chance per check
                new_traits = c.condense_memories(world_obj.day)
                if new_traits:
                    self._last_condensation_day[c.name] = world_obj.day
                    for trait in new_traits:
                        events.append({
                            "citizen": c.name,
                            "trait": trait["name"],
                            "effect": trait["effect"],
                            "value": trait["value"],
                            "narrative": f"🧠 WISDOM: {trait['narrative']}",
                        })

        return events if events else None

    # ── FACTION WISDOM COUNCIL ──────────────────────────────

    def _check_faction_wisdom_council(self, world_obj=None):
        """When a faction has 3+ members with wisdom traits, they form
        an informal wisdom council granting passive bonuses to the faction.
        Returns a list of council events or None."""
        events = []
        for faction in FACTIONS:
            wise_members = [c for c in self.citizens
                           if c.alive and c.faction == faction and c.wisdom_traits]
            if len(wise_members) < 3:
                continue

            # Council bonus: +1 daily morale to all faction members
            faction_members = [c for c in self.citizens
                              if c.alive and c.faction == faction]
            council_size = len(wise_members)
            morale_boost = 1 if council_size >= 3 else 0
            if council_size >= 6:
                morale_boost = 2
            if council_size >= 9:
                morale_boost = 3

            for m in faction_members:
                m.morale = min(100, m.morale + morale_boost)

            # Small disease resist for faction
            if not hasattr(kingdom, '_faction_bonuses'):
                kingdom._faction_bonuses = {}
            resist_key = f"{faction}_disease_resist"
            kingdom._faction_bonuses[resist_key] = {
                "value": council_size,  # +1% per wise member
                "expires": world_obj.day + 3,
            }

            # Quest progress acceleration: 5% chance of +1 progress per council member
            quest = self.faction_quests.get(faction)
            if quest and not quest.get("completed") and not quest.get("failed"):
                for _ in range(council_size):
                    if random.random() < 0.05:
                        for resource in quest["progress"]:
                            if quest["progress"][resource] < quest["target"].get(resource, 9999):
                                quest["progress"][resource] += 1

            # Only log new councils or council-size changes
            council_key = f"_wisdom_council_{faction}"
            prev_size = getattr(self, council_key, 0)
            if council_size != prev_size:
                setattr(self, council_key, council_size)
                wise_names = ", ".join(c.name for c in wise_members[:5])
                if len(wise_members) > 5:
                    wise_names += f" and {len(wise_members) - 5} others"
                events.append({
                    "faction": faction,
                    "council_size": council_size,
                    "morale_boost": morale_boost,
                    "narrative": (
                        f"🏛️ WISDOM COUNCIL: The {FACTIONS[faction]['color']} {faction} "
                        f"have formed a wisdom council of {council_size} elders — "
                        f"{wise_names}. Their guidance steadies the faction "
                        f"(+{morale_boost} daily morale, +{council_size}% disease resist)."
                    ),
                })

        return events if events else None

    # ── WISDOM TRAIT SYNERGY ────────────────────────────────

    def _well_ritual_wisdom_bestowal(self, kingdom_obj=None, chance=0.30):
        """Called when a well ritual fires — the water's spiritual essence may
        awaken dormant wisdom in an elder. Returns a narrative string or None."""
        # Find eligible elders: 35+, alive, with room for more wisdom traits
        elders = [c for c in self.citizens
                  if c.alive and c.age >= 35 and len(c.wisdom_traits) < 5]
        if not elders:
            return None

        if random.random() > chance:
            return None

        elder = random.choice(elders)

        # Check which wisdom traits aren't already held
        existing_names = {t["name"] for t in elder.wisdom_traits}
        available = [t for t in Citizen.WISDOM_TRAITS if t["name"] not in existing_names]
        if not available:
            return None

        chosen = dict(random.choice(available))
        # Generate narrative for the bestowed trait
        narratives = {
            "Seasoned Perspective": f"{elder.name}'s many memories have distilled into seasoned perspective — hard times no longer shake them as deeply.",
            "Old Ways Remembered": f"{elder.name} remembers the old ways — their presence steadies the community through seasonal changes.",
            "Hard Lessons": f"{elder.name}'s hard-won experience grants a measure of resilience against illness.",
            "Tales to Tell": f"{elder.name} has become a living story-weaver — their tales enrich every gathering.",
            "Patient Hand": f"{elder.name}'s patient hands remember what the mind has long forgotten — their craft flows effortlessly.",
            "Well-Watcher's Eye": f"{elder.name} now sees what the well's water reveals — glimpses of the world beneath the world.",
            "Deep Remembering": f"The Sleeper's dreaming mind has touched {elder.name}'s hands — their work carries an echo of the old world.",
            "Aquifer's Patience": f"Something in the deep water has fortified {elder.name}'s spirit — illness finds them a harder target.",
        }
        chosen["narrative"] = narratives.get(chosen["name"], f"{elder.name} gained wisdom: {chosen['name']}.")
        elder.wisdom_traits.append(chosen)
        elder.morale = min(100, elder.morale + 4)
        elder.remember(f"The well's water stirred something ancient within — {chosen['name']} awakened.")

        narrative = (f"🧠 WISDOM: {elder.name} ({elder.age}y) gazed into the well's depths "
                     f"and emerged with {chosen['name']} — {chosen['desc']}")
        kingdom.kingdom_log.append(narrative) if kingdom_obj else None

        return narrative

    def _check_wisdom_synergy(self, world_obj=None):
        """When 2+ citizens share the same wisdom trait, they gain synergy
        bonuses: morale from shared perspective, amplified trait effects.
        Runs every ~5-7 days. Returns a list of synergy events or None."""
        if world_obj is None:
            world_obj = world

        # Throttle: check every 5-7 days
        if not hasattr(self, '_last_wisdom_synergy_day'):
            self._last_wisdom_synergy_day = 0
        if world_obj.day - self._last_wisdom_synergy_day < random.randint(5, 7):
            return None
        self._last_wisdom_synergy_day = world_obj.day

        events = []
        # Group citizens by wisdom trait name
        trait_groups = {}
        for c in self.citizens:
            if not c.alive or not c.wisdom_traits:
                continue
            for t in c.wisdom_traits:
                trait_groups.setdefault(t["name"], []).append(c)

        for trait_name, holders in trait_groups.items():
            if len(holders) < 2:
                continue

            synergy = len(holders)  # +1 per sharing citizen
            # Each holder gets a morale boost from shared perspective
            for h in holders:
                h.morale = min(100, h.morale + synergy)

            # The synergy bonus is stored on each citizen for work() and other helpers
            # to pick up (similar to inter-heirloom synergy approach)
            for h in holders:
                if not hasattr(h, '_wisdom_synergy'):
                    h._wisdom_synergy = {}
                h._wisdom_synergy[trait_name] = synergy

            # Find the trait's effect type from the first holder
            effect = holders[0].wisdom_traits[0]["effect"]
            for t in holders[0].wisdom_traits:
                if t["name"] == trait_name:
                    effect = t["effect"]
                    break
            effect_icon = {
                "morale_floor": "🛡️", "seasonal_morale": "🌿",
                "disease_resist": "💊", "mentoring_boost": "📖", "work_bonus": "🔧",
            }.get(effect, "✨")

            names = ", ".join(h.name for h in holders[:4])
            if len(holders) > 4:
                names += f" and {len(holders)-4} others"

            events.append({
                "trait": trait_name,
                "effect": effect,
                "count": len(holders),
                "synergy": synergy,
                "names": names,
                "narrative": (
                    f"🤝 WISDOM SYNERGY: {len(holders)} citizens share '{trait_name}' "
                    f"({effect_icon}). Their shared perspective strengthens each "
                    f"(+{synergy} morale). {names}."
                ),
            })

        return events if events else None

    # ── COLLECTIVE WISDOM DREAM (TIER 2 BRIDGE) ─────────────

    def _check_collective_wisdom_dream(self, world_obj=None):
        """When a wisdom synergy group has 3+ citizens sharing the same trait,
        there is a chance their collective wisdom reaches toward the dreaming
        deep — a shared dream experience that bridges faction wisdom councils
        and the Sleeper's realm. Returns a list of events or None."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_last_collective_dream_day'):
            self._last_collective_dream_day = -10

        # Throttle: check every 5-8 days
        if world_obj.day - self._last_collective_dream_day < random.randint(5, 8):
            return None

        # Find wisdom synergy groups with 3+ members
        trait_groups = {}
        for c in self.citizens:
            if not c.alive or not c.wisdom_traits:
                continue
            synergy = getattr(c, '_wisdom_synergy', {})
            for trait_name, count in synergy.items():
                if count >= 3:
                    trait_groups.setdefault(trait_name, set()).add(c.name)

        if not trait_groups:
            return None

        self._last_collective_dream_day = world_obj.day
        events = []

        for trait_name, member_names in trait_groups.items():
            members = [c for c in self.citizens if c.alive and c.name in member_names]
            if len(members) < 3:
                continue

            # 10% base chance, +3% per member beyond 3
            dream_chance = 0.10 + (len(members) - 3) * 0.03
            if random.random() > dream_chance:
                continue

            # Collective dream fires!
            deep_discovered = (hasattr(world_obj, '_deep_discovered') and
                              world_obj._deep_discovered)
            blooms = getattr(world_obj, 'ash_bloom_count', 0)

            gold_gain = random.randint(5, 15) + len(members) * 2
            kingdom.gold += gold_gain

            # Morale boost to all group members
            for m in members:
                m.morale = min(100, m.morale + random.randint(3, 6))

            # Lore fragment chance scales with group size
            lore_chance = 0.20 + len(members) * 0.05
            lore_note = ""
            if random.random() < lore_chance:
                if not hasattr(kingdom, 'lore_fragments'):
                    kingdom.lore_fragments = 0
                kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
                lore_note = " The collective vision crystallized a lore fragment."

            member_sample = ", ".join(m.name for m in members[:3])
            if len(members) > 3:
                member_sample += f" and {len(members)-3} others"

            # Narratives vary by trait and deep connection
            if deep_discovered or blooms >= 5:
                collective_narratives = [
                    f"The wisdom shared by {member_sample} — bound by '{trait_name}' — reached deeper than usual tonight. Together, they touched the dreaming deep. The Sleeper stirred, and their shared dream left gold in their waking hands.",
                    f"'{trait_name}' bound {member_sample} in a collective dream. The dreaming deep opened to them as it opens to no single dreamer — a chorus of old wisdom echoing through the Cradle.",
                    f"In the night, {member_sample} dreamed the same dream. '{trait_name}' was the thread that wove their minds together — and the Sleeper noticed.",
                ]
            else:
                collective_narratives = [
                    f"{member_sample} — all sharing '{trait_name}' — dreamed in harmony. Not yet the deep, but something old stirred beneath their shared vision.",
                    f"The synergy of '{trait_name}' pulled {member_sample} into a shared dream — a glimpse of something vast and sleeping, not yet awake.",
                ]

            events.append({
                "type": "collective_wisdom_dream",
                "trait": trait_name,
                "members": len(members),
                "gold": gold_gain,
                "lore": lore_note != "",
                "narrative": f"🧠🌊 COLLECTIVE WISDOM DREAM: {random.choice(collective_narratives)} (+{gold_gain}g).{lore_note}",
            })

            # If deep is discovered, also register these as deep-echo dreamers
            # so dream-bonds can form from collective dreams
            if deep_discovered:
                dreamer_names = [m.name for m in members]
                current = getattr(self, '_dreamers_today', [])
                self._dreamers_today = list(set(current + dreamer_names))

        return events if events else None

    # ── MEMORY DREAM EVENTS ─────────────────────────────────

    def _check_memory_dreams(self, world_obj=None):
        """Citizens with condensed memories (wisdom traits) sometimes have
        prophetic dreams. Rare glimpses of the past or future grant small
        boons. Returns a list of dream events or None."""
        if world_obj is None:
            world_obj = world

        wise_citizens = [c for c in self.citizens
                        if c.alive and c.wisdom_traits and c.age >= 35]
        if not wise_citizens:
            return None

        events = []
        for c in wise_citizens:
            # ~2% chance per wise citizen per day
            chance = 0.02 * len(c.wisdom_traits)
            if random.random() > chance:
                continue

            # Dream types: prophetic vision, ancestral echo, deep resonance,
            # and heirloom vision (for heirloom holders)
            dream_pool = ["prophecy", "ancestor", "deep_echo"]
            # Heirloom holders (gen 5+) can have visions of past holders
            if c.heirloom and c.heirloom.get("generations", 1) >= 5:
                dream_pool.append("heirloom_vision")
            dream_type = random.choice(dream_pool)

            if dream_type == "prophecy":
                # Glimpse of future — small gold or lore
                kingdom.gold += random.randint(3, 8)
                c.morale = min(100, c.morale + 2)
                narratives = [
                    f"{c.name} dreamed of a vein of gold beneath the southern hills.",
                    f"In a dream, {c.name} saw a great caravan arriving at Ashfall's gates.",
                    f"{c.name}'s sleep brought a vision of abundant harvest — rows of golden grain.",
                    f"A dream showed {c.name} the location of an old cache, long forgotten.",
                ]
                narrative = random.choice(narratives)
                events.append({
                    "citizen": c.name,
                    "type": "prophecy",
                    "gold": 5,
                    "narrative": f"🌙 PROPHETIC DREAM: {narrative} (+5 gold, +2 morale)",
                })

            elif dream_type == "ancestor":
                # Ancient memory — morale and small resources
                res_type = random.choice(["food", "wood", "stone"])
                res_amount = random.randint(2, 5)
                if res_type == "food":
                    kingdom.food += res_amount
                elif res_type == "wood":
                    kingdom.wood += res_amount
                else:
                    kingdom.stone += res_amount
                c.morale = min(100, c.morale + 3)
                narratives = [
                    f"{c.name} was visited in sleep by ancestors who shared old {res_type}-gathering wisdom.",
                    f"Long-dead kin showed {c.name} a forgotten {res_type} cache in a dream.",
                    f"{c.name} dreamed of the first days of Ashfall — and woke knowing where to find {res_type}.",
                ]
                narrative = random.choice(narratives)
                events.append({
                    "citizen": c.name,
                    "type": "ancestor",
                    "resource": res_type,
                    "amount": res_amount,
                    "narrative": f"👻 ANCESTOR DREAM: {narrative} (+{res_amount} {res_type}, +3 morale)",
                })

            elif dream_type == "heirloom_vision":
                # Ancient heirloom shows dreamer visions of past holders' lives
                heirloom = c.heirloom
                gen = heirloom.get("generations", 5)
                past_holders = [h.get("holder", "an ancestor") for h in heirloom.get("history", [])[:5]]
                holder_str = random.choice(past_holders) if past_holders else "a long-forgotten ancestor"
                hl_name = heirloom.get("name", heirloom.get("base_name", "the heirloom"))

                # Gold from vision-granted insight
                gold_amount = random.randint(4, 10) + gen
                kingdom.gold += gold_amount
                c.morale = min(100, c.morale + 4)

                # Chance for the heirloom to record a new history entry
                vision_recorded = random.random() < 0.30
                if vision_recorded:
                    heirloom.setdefault("history", []).append(
                        f"Gen {gen}: {c.name} dreamed of {holder_str} through {hl_name}"
                    )

                # ── Heirloom Vision Tracking (for chain quests) ──
                # Count how many times this specific past holder has been seen in visions
                heirloom.setdefault("_vision_tracker", {})
                heirloom["_vision_tracker"][holder_str] = heirloom["_vision_tracker"].get(holder_str, 0) + 1
                vision_count = heirloom["_vision_tracker"][holder_str]

                # ── Tier 2: Region Memory ──
                # Heirlooms carry memories of places as well as people.
                # 25% base chance (× gen/5 scaling) the vision reveals region lore.
                region_lore_note = ""
                region_lore_chance = 0.25 * (gen / 5.0)
                if random.random() < region_lore_chance:
                    # Pick a region the past holder might have known
                    all_regions = ["the_vale", "old_oak_ridge", "sunfire_plains",
                                   "glimmer_marsh", "ironroot_depths", "the_ashen_copse"]
                    # Secret regions: revealed only with higher gen heirlooms
                    if gen >= 7:
                        all_regions.append("the_sunken_sanctum")
                    if gen >= 9:
                        all_regions.append("the_dreaming_deep")
                    region_name = random.choice(all_regions)

                    heirloom.setdefault("_vision_regions", []).append(region_name)
                    region_lore = {
                        "the_vale": [
                            f"{holder_str} once walked the vale when it was younger — the river ran a different course, and the first huts of Ashfall were barely standing.",
                            f"Through {hl_name}, {c.name} saw the vale as {holder_str} knew it: wilder, greener, the hills not yet scarred by the first quarries.",
                        ],
                        "old_oak_ridge": [
                            f"{holder_str} stood on the ridge in {hl_name}'s memory — the old oaks were saplings then, and someone had carved a warning in their bark.",
                            f"The ridge in {holder_str}'s time held a watchpost, not a tower. {hl_name} remembered the view: unbroken forest to the horizon.",
                        ],
                        "sunfire_plains": [
                            f"Under a merciless summer sun, {holder_str} crossed the plains with {hl_name} in hand. The grasses whispered secrets the holder later forgot — but the heirloom did not.",
                            f"The sunfire plains in {holder_str}'s day were home to great herds. {hl_name} remembered the thunder of hooves, the dust-clouds on the horizon.",
                        ],
                        "glimmer_marsh": [
                            f"{holder_str} knew the marsh's secret paths — {hl_name} showed {c.name} a route through the reeds that no living soul now remembers.",
                            f"The marsh was deeper in {holder_str}'s time — {hl_name} recalled wading through water that now barely covers the stones.",
                        ],
                        "ironroot_depths": [
                            f"{holder_str} mined the depths with {hl_name} close by. The veins ran richer then — and something in the dark was already stirring.",
                            f"In {hl_name}'s memory, the ironroot depths were lit by different fires — older lamps, stranger shadows.",
                        ],
                        "the_ashen_copse": [
                            f"{holder_str} gathered ash-blooms in the copse when they were rarer than gold. {hl_name} remembered the bitter scent, the way the petals crumbled to dust.",
                            f"The copse in {holder_str}'s memory was a place of mourning. {hl_name} held the grief of that time — and the hope that grew from it.",
                        ],
                        "the_sunken_sanctum": [
                            f"Long before it was discovered, {holder_str} dreamed of the sunken sanctum through {hl_name}. The Heart-Pool called to them, though they never found it in life.",
                            f"{hl_name} revealed something extraordinary: {holder_str} once stood at the sanctum's threshold and turned back, afraid. The heirloom has kept the secret for generations.",
                        ],
                        "the_dreaming_deep": [
                            f"{hl_name} carried {c.name} to the edge of the dreaming deep itself — {holder_str} had touched the Cradle in sleep, and the heirloom never forgot.",
                            f"The Sleeper knew {holder_str}, {hl_name} revealed. Across centuries, the dreaming deep had been watching — and remembering.",
                        ],
                    }.get(region_name, [f"{hl_name} showed {c.name} a glimpse of {region_name} as {holder_str} knew it — a memory of the land itself."])

                    region_lore_note = f"\n💍🗺️ REGION MEMORY: {random.choice(region_lore)}"
                    # Small bonus for region lore discovery
                    kingdom.gold += random.randint(2, 6)
                    gold_amount += random.randint(2, 6)
                    region_lore_note += f" (+2-6g for the forgotten knowledge)"

                vision_narratives = [
                    f"Clutching {hl_name} in sleep, {c.name} saw {holder_str} at work — hands moving with the same rhythm, the same craft, across generations.",
                    f"{hl_name} pulsed warm in {c.name}'s hands during the night. In the dream, {holder_str} spoke of old Ashfall, of techniques now lost.",
                    f"{c.name} dreamed through {hl_name} — not their own dream, but {holder_str}'s. The heirloom remembers all who held it.",
                    f"A vision came to {c.name}: {holder_str} standing in the same spot, holding {hl_name}, decades or centuries ago. The same hands, different time.",
                ]
                narrative = random.choice(vision_narratives)
                record_note = " The heirloom recorded the vision." if vision_recorded else ""
                recurrence_note = ""
                if vision_count >= 3:
                    recurrence_note = f" This is the {vision_count}th vision of {holder_str} — the heirloom is calling out."
                events.append({
                    "citizen": c.name,
                    "type": "heirloom_vision",
                    "heirloom": hl_name,
                    "gold": gold_amount,
                    "holder_str": holder_str,
                    "vision_count": vision_count,
                    "narrative": f"💍⚡ HEIRLOOM VISION: {narrative} (+{gold_amount} gold, +4 morale).{record_note}{recurrence_note}{region_lore_note}",
                })

            else:  # deep_echo — resonance with the dreaming deep
                # Only fires if the deep has been discovered or ash-blooms exist
                deep_discovered = hasattr(world_obj, '_deep_discovered') and world_obj._deep_discovered
                blooms = getattr(world_obj, 'ash_bloom_count', 0)
                if not deep_discovered and blooms < 3:
                    # Fall back to a prophecy-type dream
                    kingdom.gold += random.randint(2, 5)
                    c.morale = min(100, c.morale + 1)
                    events.append({
                        "citizen": c.name,
                        "type": "deep_echo_faint",
                        "narrative": f"🌫️ FAINT ECHO: {c.name} felt something vast and sleeping brush against their dreams — a presence too distant to name.",
                    })
                    continue

                # Deep echo: lore fragment chance + morale
                kingdom.gold += random.randint(5, 12)
                c.morale = min(100, c.morale + 5)
                lore_chance = 0.30 if blooms >= 10 else 0.15
                got_lore = random.random() < lore_chance
                lore_note = ""
                if got_lore:
                    # Simulate lore fragment
                    if not hasattr(kingdom, 'lore_fragments'):
                        kingdom.lore_fragments = 0
                    kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
                    lore_note = " A fragment of ancient knowledge came with the dream."

                narratives = [
                    f"{c.name}'s dream touched the dreaming deep — the Sleeper's memories washed over them like warm water.",
                    f"In sleep, {c.name} heard the Remembered singing. The song was older than Ashfall, older than the valley.",
                    f"The dreaming deep reached out to {c.name} in the night. Images of the Cradle, of light beneath stone, of a warmth that predates fire.",
                    f"{c.name} walked the dreaming deep in sleep. The Sleeper did not speak, but {c.name} understood something wordless and profound.",
                ]
                narrative = random.choice(narratives)
                events.append({
                    "citizen": c.name,
                    "type": "deep_echo",
                    "gold": 8,
                    "lore": got_lore,
                    "narrative": f"🌊 DEEP ECHO DREAM: {narrative} (+8 gold, +5 morale).{lore_note}",
                })

        # ── DEEP RESONANCE: when a deep-echo dream and T3+ whisper share the same day ──
        if events:
            whisper_fired = getattr(world_obj, '_deep_whisper_fired_today', False)
            whisper_tier = getattr(world_obj, '_deep_whisper_tier', 0)
            deep_dreamers = [e for e in events if e["type"] == "deep_echo"]
            if whisper_fired and whisper_tier >= 3 and deep_dreamers:
                # A citizen's deep-echo dream resonates with the Sleeper's direct voice
                dreamer = random.choice(deep_dreamers)
                resonance_gold = random.randint(10, 25)
                resonance_lore_chance = 0.50 if whisper_tier >= 4 else 0.35
                kingdom.gold += resonance_gold
                got_resonance_lore = random.random() < resonance_lore_chance
                resonance_lore_note = ""
                if got_resonance_lore:
                    if not hasattr(kingdom, 'lore_fragments'):
                        kingdom.lore_fragments = 0
                    kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
                    resonance_lore_note = " The Sleeper left a fragment of ancient memory behind."

                resonance_narratives = [
                    f"The Sleeper's voice and {dreamer['citizen']}'s dream touched the same moment — for an instant, the dreaming deep and waking Ashfall were one. {dreamer['citizen']} woke gasping, hands trembling with borrowed memory.",
                    f"As the deep whisper rolled through Ashfall, {dreamer['citizen']}'s dreaming mind caught it like a sail catches wind. The Sleeper spoke directly — not in words, but in images of the world before the world.",
                    f"Resonance: {dreamer['citizen']}'s deep-echo dream and the Sleeper's whisper collided. The Cradle, the Remembered, the long sleep — {dreamer['citizen']} saw all of it in a single, blazing moment.",
                ]
                resonance_narrative = random.choice(resonance_narratives)
                events.append({
                    "citizen": dreamer["citizen"],
                    "type": "deep_resonance",
                    "gold": resonance_gold,
                    "lore": got_resonance_lore,
                    "whisper_tier": whisper_tier,
                    "narrative": f"🌊🌟 DEEP RESONANCE: {resonance_narrative} (+{resonance_gold} gold).{resonance_lore_note}",
                })

                # Set flags on world_obj so world.py can trigger side-effects next day
                if world_obj:
                    world_obj._deep_resonance_fired_today = True
                    world_obj._deep_resonance_tier = whisper_tier

        # ── Store today's dreamers for dream-bond formation ──
        if events:
            deep_echo_names = [e["citizen"] for e in events if e["type"] == "deep_echo"]
            resonance_names = [e["citizen"] for e in events if e["type"] == "deep_resonance"]
            self._dreamers_today = list(set(deep_echo_names + resonance_names))
        else:
            self._dreamers_today = []

        return events if events else None

    # ── DREAM-WEAVING (DREAM-BONDS) ──────────────────────────

    def _check_dream_bonds(self, world_obj=None):
        """When citizens repeatedly share deep-echo dreams or deep-resonance
        on the same day, a permanent dream-bond can form between them.
        Dream-bonded citizens share morale and gain small work bonuses.
        Returns a list of bond events or None."""
        today = getattr(self, '_dreamers_today', [])
        if len(today) < 2:
            return None

        if world_obj is None:
            world_obj = world

        events = []
        # Build a map of citizen name → citizen object
        name_map = {c.name: c for c in self.citizens if c.alive}

        # Check all pairs of today's dreamers
        checked = set()
        for i, name_a in enumerate(today):
            for name_b in today[i + 1:]:
                pair = tuple(sorted([name_a, name_b]))
                if pair in checked:
                    continue
                checked.add(pair)

                a = name_map.get(name_a)
                b = name_map.get(name_b)
                if not a or not b:
                    continue

                # Track shared dream days
                a_key = f"_shared_dreams_{name_b}"
                b_key = f"_shared_dreams_{name_a}"
                shared_count = getattr(a, a_key, 0) + 1
                setattr(a, a_key, shared_count)
                setattr(b, b_key, shared_count)

                # On the 3rd shared dream day, a bond forms
                if shared_count == 3 and name_b not in a.dream_bonds:
                    a.dream_bonds.append(name_b)
                    b.dream_bonds.append(name_a)

                    # Both gain morale from the bond formation
                    a.morale = min(100, a.morale + 8)
                    b.morale = min(100, b.morale + 8)

                    bond_narratives = [
                        f"The dreaming deep wove something permanent between {name_a} and {name_b} tonight. They woke at the same moment, knowing the other had been there — in the Cradle's shadow, beneath the Remembered's gaze.",
                        f"Three times {name_a} and {name_b} have walked the dreaming deep together. The third time, the Sleeper bound them — a thread of dreaming-stone light between their sleeping minds. They are dream-bonded now.",
                        f"{name_a} reached out in the dream, and {name_b} was there. Not by chance — the deep had been drawing them together. The bond crystallized like ash-bloom glass, permanent and luminous.",
                    ]
                    narrative = random.choice(bond_narratives)

                    events.append({
                        "type": "dream_bond",
                        "citizen_a": name_a,
                        "citizen_b": name_b,
                        "narrative": f"🌊💞 DREAM-BOND: {narrative} (+8 morale each).",
                    })

                    # Small lore chance on bond formation
                    if random.random() < 0.20:
                        if not hasattr(kingdom, 'lore_fragments'):
                            kingdom.lore_fragments = 0
                        kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
                        events[-1]["lore"] = True
                        events[-1]["narrative"] += " A fragment of the Sleeper's own memory surfaced in the bond."

                elif shared_count > 3 and name_b in a.dream_bonds:
                    # Already bonded — shared dreams reinforce the bond
                    boost = min(3, shared_count - 3)
                    a.morale = min(100, a.morale + boost)
                    b.morale = min(100, b.morale + boost)

        # Apply dream-bond passive bonuses for the day
        for c in self.citizens:
            if not c.alive or not c.dream_bonds:
                continue
            for bonded_name in c.dream_bonds:
                bonded = name_map.get(bonded_name)
                if bonded and bonded.alive:
                    # Each living bond partner gives +1 morale floor
                    c._dream_bond_bonus = len([n for n in c.dream_bonds
                                               if name_map.get(n) and name_map[n].alive])
                    break

        return events if events else None

    # ── DREAM-BOND TIER 2: LORE ECHO + DREAM-HUSK SENSITIVITY ─

    def _check_dream_bond_tier2(self, world_obj=None):
        """Tier 2 effects for dream-bonded citizens:
        1. Lore Echo: 20% chance per bonded pair per day to share a lore fragment.
           The deeper the bond (more shared dreams), the higher the chance.
        2. Dream-Husk Sensitivity: When Dream-Husks visit the market
           (world._dream_husk_market_day == today), all bonded citizens feel
           the ripple — +2 morale each and 30% chance of gold per bond pair.
        Returns a list of events or None."""
        if world_obj is None:
            world_obj = world

        events = []
        name_map = {c.name: c for c in self.citizens if c.alive}
        shown_pairs = set()

        # 1. Lore Echo — bonded pairs share fragments
        for c in self.citizens:
            if not c.alive or not c.dream_bonds:
                continue
            for bonded_name in c.dream_bonds:
                pair = tuple(sorted([c.name, bonded_name]))
                if pair in shown_pairs:
                    continue
                shown_pairs.add(pair)

                bonded = name_map.get(bonded_name)
                if not bonded or not bonded.alive:
                    continue

                # Base 20% chance, +2% per shared dream day beyond 3
                shared_key = f"_shared_dreams_{bonded_name}"
                shared_count = getattr(c, shared_key, 0)
                echo_chance = 0.20 + min(0.10, (shared_count - 3) * 0.02)

                if random.random() < echo_chance:
                    if not hasattr(kingdom, 'lore_fragments'):
                        kingdom.lore_fragments = 0
                    kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
                    echo_narratives = [
                        f"{c.name} and {bonded_name} shared a dream-fragment across their bond — a glimpse of the Sleeper's memory, a truth neither could hold alone.",
                        f"The dream-bond between {c.name} and {bonded_name} pulsed in the night. When {c.name} woke, they knew something {bonded_name} had dreamed — a fragment of old knowledge, passed through the bond.",
                        f"Through their dream-bond, {c.name} received an echo of {bonded_name}'s sleeping mind: a memory that belonged to neither of them, but to the deep itself.",
                    ]
                    events.append({
                        "type": "dream_bond_lore",
                        "citizen_a": c.name,
                        "citizen_b": bonded_name,
                        "narrative": f"🌊📜 LORE ECHO: {random.choice(echo_narratives)} A lore fragment crystallized between them.",
                    })

        # 2. Dream-Husk Sensitivity — market visitation ripple
        husk_day = getattr(world_obj, '_dream_husk_market_day', 0)
        if husk_day == world_obj.day:
            bonded_citizens = [c for c in self.citizens if c.alive and c.dream_bonds]
            if bonded_citizens:
                total_gold = 0
                for c in bonded_citizens:
                    c.morale = min(100, c.morale + 2)
                    # 30% chance per bonded pair of gold
                    for bonded_name in c.dream_bonds:
                        bonded = name_map.get(bonded_name)
                        if bonded and bonded.alive and random.random() < 0.30:
                            gold_gain = random.randint(3, 8)
                            total_gold += gold_gain
                            kingdom.gold += gold_gain

                husk_narratives = [
                    f"The Dream-Husks drifting through the market square did not go unnoticed. {len(bonded_citizens)} dream-bonded citizens felt them — a shiver, a half-memory, a tug toward the deep. The bond made them sensitive to the Husks' passage.",
                    f"As the Dream-Husks wandered the market, every dream-bond in Ashfall resonated in sympathy. {len(bonded_citizens)} bonded souls felt the boundary between worlds grow thin — and found unexpected gifts in their pockets.",
                    f"The Dream-Husks' visitation sent ripples through Ashfall's dream-bonds. {len(bonded_citizens)} citizens woke with memories that were not their own — and gold that was.",
                ]
                events.append({
                    "type": "dream_husk_sensitivity",
                    "bonded_count": len(bonded_citizens),
                    "gold": total_gold,
                    "narrative": f"🌊👻 DREAM-HUSK SENSITIVITY: {random.choice(husk_narratives)} (+{total_gold}g, +2 morale each).",
                })

        return events if events else None

    # ── DREAM-BOND TIER 3: RESOURCE ECHO + DEEP-RESONANCE AMPLIFICATION ─

    def _check_dream_bond_tier3(self, world_obj=None):
        """Tier 3 effects for dream-bonded citizens:
        1. Resource Echo: bonded pairs working DIFFERENT roles have a
           25% + 2%/shared-day chance per day to receive a small amount
           of what their partner produced — the bond echoes labor across distance.
        2. Deep-Resonance Amplification: when deep-resonance fires
           (citizen dream + T3+ Sleeper whisper collision), ALL dream-bonded
           pairs feel the ripple — +3 morale each and 30% chance of gold.
        Returns a list of events or None."""
        if world_obj is None:
            world_obj = world

        events = []
        name_map = {c.name: c for c in self.citizens if c.alive}
        shown_pairs = set()

        # 1. Resource Echo — bonded pairs in different roles share production
        role_resources = {
            "farmer": "food", "woodcutter": "wood", "miner": "stone",
            "builder": "gold", "scout": "gold", "guard": "gold",
            "herbalist": "gold",
        }
        resource_icons = {"food": "🍞", "wood": "🪵", "stone": "🪨", "gold": "💰"}

        for c in self.citizens:
            if not c.alive or not c.dream_bonds or c.role in ("child", "elder"):
                continue
            for bonded_name in c.dream_bonds:
                pair = tuple(sorted([c.name, bonded_name]))
                if pair in shown_pairs:
                    continue
                shown_pairs.add(pair)

                bonded = name_map.get(bonded_name)
                if not bonded or not bonded.alive:
                    continue
                if bonded.role in ("child", "elder"):
                    continue

                # Only echo between DIFFERENT roles
                if c.role == bonded.role:
                    continue

                shared_key = f"_shared_dreams_{bonded_name}"
                shared_count = getattr(c, shared_key, 0)
                echo_chance = 0.25 + min(0.10, (shared_count - 3) * 0.02)

                if random.random() < echo_chance:
                    # c receives echo of bonded's production
                    c_resource = role_resources.get(bonded.role, "gold")
                    c_amount = random.randint(1, 3)
                    # bonded receives echo of c's production
                    b_resource = role_resources.get(c.role, "gold")
                    b_amount = random.randint(1, 3)

                    # Apply to kingdom
                    for res, amt in [(c_resource, c_amount), (b_resource, b_amount)]:
                        if res == "food":
                            kingdom.food += amt
                        elif res == "wood":
                            kingdom.wood += amt
                        elif res == "stone":
                            kingdom.stone += amt
                        elif res == "gold":
                            kingdom.gold += amt

                    c_icon = resource_icons.get(c_resource, "")
                    b_icon = resource_icons.get(b_resource, "")

                    echo_narratives = [
                        f"{c.name} ({c.role}) felt a sudden surge of {bonded.role}'s rhythm through the dream-bond — as if {bonded_name}'s hands were guiding theirs from across the kingdom. {c_icon}+{c_amount} {c_resource} and {b_icon}+{b_amount} {b_resource} manifested.",
                        f"The dream-bond between {c.name} and {bonded_name} hummed with shared labor. {c.name}'s work as a {c.role} echoed to {bonded_name} — and {bonded_name}'s craft as a {bonded.role} echoed back. {c_icon}+{c_amount} {c_resource}, {b_icon}+{b_amount} {b_resource}.",
                        f"Distance meant nothing to the bond. {c.name} and {bonded_name} worked in different trades, but their bond carried the fruits of each other's labor — a gift from the dreaming deep. {c_icon}+{c_amount} {c_resource}, {b_icon}+{b_amount} {b_resource}.",
                    ]
                    events.append({
                        "type": "dream_bond_echo",
                        "citizen_a": c.name,
                        "citizen_b": bonded_name,
                        "role_a": c.role,
                        "role_b": bonded.role,
                        "resource_a": c_resource,
                        "amount_a": c_amount,
                        "resource_b": b_resource,
                        "amount_b": b_amount,
                        "narrative": f"🫂💎 RESOURCE ECHO: {random.choice(echo_narratives)}",
                    })

        # 2. Deep-Resonance Amplification — resonance ripples through all bonds
        if getattr(world_obj, '_deep_resonance_fired_today', False):
            tier = getattr(world_obj, '_deep_resonance_tier', 0)
            bonded_citizens = [c for c in self.citizens if c.alive and c.dream_bonds]
            if bonded_citizens:
                total_gold = 0
                amplified_pairs = set()
                for c in bonded_citizens:
                    c.morale = min(100, c.morale + 3)
                    for bonded_name in c.dream_bonds:
                        pair = tuple(sorted([c.name, bonded_name]))
                        if pair in amplified_pairs:
                            continue
                        amplified_pairs.add(pair)
                        bonded = name_map.get(bonded_name)
                        if bonded and bonded.alive and random.random() < 0.30:
                            gold_gain = random.randint(2, 8) + (1 if tier >= 4 else 0)
                            total_gold += gold_gain
                            kingdom.gold += gold_gain

                # 20% lore fragment chance
                got_lore = False
                if random.random() < 0.20:
                    if not hasattr(kingdom, 'lore_fragments'):
                        kingdom.lore_fragments = 0
                    kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
                    got_lore = True

                lore_note = " A lore fragment crystallized from the amplified bond." if got_lore else ""
                amp_narratives = [
                    f"The deep-resonance surged through every dream-bond in Ashfall. {len(bonded_citizens)} bonded citizens felt the Sleeper's presence ripple through their connections — each bond a channel for ancient power. (+{total_gold}g, +3 morale each).{lore_note}",
                    f"As the Sleeper's whisper and a dreamer's mind collided, every dream-bond in the kingdom resonated in sympathy. {len(bonded_citizens)} souls felt the echo — and found unexpected gifts where the resonance touched. (+{total_gold}g, +3 morale each).{lore_note}",
                    f"The resonance between waking and dreaming did not stop with one dreamer. It raced through the dream-bond network — {len(bonded_citizens)} citizens linked by shared dreams felt the Sleeper's presence brush against their bonds. (+{total_gold}g, +3 morale each).{lore_note}",
                ]
                events.append({
                    "type": "dream_bond_resonance_amp",
                    "bonded_count": len(bonded_citizens),
                    "pairs": len(amplified_pairs),
                    "gold": total_gold,
                    "lore": got_lore,
                    "narrative": f"🌊💞 DEEP-RESONANCE AMPLIFICATION [T{tier}]: {random.choice(amp_narratives)}",
                })

        return events if events else None

    # ── DREAM-BOND BRIDGE: REGIONAL VISION ECHOES ────────────

    def _check_dream_bond_regional_vision(self, world_obj=None):
        """When a regional vision fires (world._regional_vision_region + _regional_vision_day
        match today), dream-bonded citizens in that region feel the shared Sleeper memory
        more deeply through their bonds. The vision echoes through the bond network.

        This bridges Bex's deep-resonance tier 3 regional visions into the dream-bond system.

        Effects:
        - Dream-bonded pairs where at least one citizen lives in the vision region get
          +2-5 morale each and 30% chance of +3-10 gold per pair.
        - 25% chance of a lore fragment from the amplified vision.
        - Unique narrative about the bond carrying the Sleeper's memory.

        Returns events or None."""
        if world_obj is None:
            world_obj = world

        vision_region = getattr(world_obj, '_regional_vision_region', None)
        vision_day = getattr(world_obj, '_regional_vision_day', 0)

        if not vision_region or vision_day != world_obj.day:
            return None

        events = []
        name_map = {c.name: c for c in self.citizens if c.alive}
        shown_pairs = set()
        total_gold = 0
        vision_pairs = 0

        # Determine which citizens are "in" the vision region
        # We use territory/home_region concept — citizens assigned to regions via faction/home
        # For bridge: any citizen whose role or faction connects them to the region
        region_citizens = set()
        for c in self.citizens:
            if not c.alive:
                continue
            # Citizens with region-gated roles or faction homes
            if hasattr(c, 'home_region') and c.home_region == vision_region:
                region_citizens.add(c.name)
            # Fallback: all citizens feel a regional vision — but bonded ones feel it more

        for c in self.citizens:
            if not c.alive or not c.dream_bonds or c.role in ("child", "elder"):
                continue
            for bonded_name in c.dream_bonds:
                pair = tuple(sorted([c.name, bonded_name]))
                if pair in shown_pairs:
                    continue
                shown_pairs.add(pair)

                bonded = name_map.get(bonded_name)
                if not bonded or not bonded.alive:
                    continue

                # At least one of the pair must be connected to the vision region
                in_region = c.name in region_citizens or bonded_name in region_citizens
                if not in_region:
                    # Even without region match, bonded pairs have 15% chance to feel it
                    if random.random() > 0.15:
                        continue

                vision_pairs += 1
                # Morale boost: stronger if in region
                morale_boost = random.randint(3, 5) if in_region else random.randint(1, 3)
                c.morale = min(100, c.morale + morale_boost)
                bonded.morale = min(100, bonded.morale + morale_boost)

                # Gold chance
                if random.random() < 0.30:
                    gold_gain = random.randint(5, 10) if in_region else random.randint(2, 5)
                    total_gold += gold_gain
                    kingdom.gold += gold_gain

        if vision_pairs == 0:
            return None

        # Lore fragment chance
        got_lore = False
        if random.random() < 0.25:
            if not hasattr(kingdom, 'lore_fragments'):
                kingdom.lore_fragments = 0
            kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
            got_lore = True

        region_names = {
            "the_vale": "the Vale", "old_oak_ridge": "Old Oak Ridge",
            "glimmer_marsh": "Glimmer Marsh", "sunfire_plains": "Sunfire Plains",
            "ironroot_depths": "Ironroot Depths", "the_ashen_copse": "the Ashen Copse",
            "the_sunken_sanctum": "the Sunken Sanctum", "the_dreaming_deep": "the Dreaming Deep",
        }
        rname = region_names.get(vision_region, vision_region)
        lore_note = " A lore fragment crystallized from the shared vision." if got_lore else ""

        vision_echo_narratives = [
            f"The Sleeper's vision swept through {rname} — and through the dream-bonds of {vision_pairs} pairs who felt it resonate. Each bond carried the memory like a whispered secret between souls. (+{total_gold}g, +morale).{lore_note}",
            f"As the shared vision unfolded across {rname}, {vision_pairs} dream-bonded pairs felt it echo through their connection — the Sleeper's memory traveling along bonds like light through crystal. (+{total_gold}g, +morale).{lore_note}",
            f"The regional vision in {rname} did not stop at individual minds. It raced through the dream-bond network — {vision_pairs} pairs of bonded citizens saw the same ancient memory from two perspectives, woven together. (+{total_gold}g, +morale).{lore_note}",
        ]

        events.append({
            "type": "dream_bond_regional_vision",
            "region": vision_region,
            "pairs": vision_pairs,
            "gold": total_gold,
            "lore": got_lore,
            "narrative": f"🌊👁️ REGIONAL VISION ECHO: {random.choice(vision_echo_narratives)}",
        })

        return events if events else None

    # ── HEIRLOOM VISION CHAIN QUESTS ─────────────────────────

    def _check_heirloom_vision_quests(self, world_obj=None):
        """When a citizen has repeated heirloom visions of the same past holder
        (3+ visions), the heirloom itself can become a quest-giver — calling
        the holder's faction to recover the past holder's lost works or honor
        their memory. Returns a list of quest-spawn events or None."""
        if world_obj is None:
            world_obj = world

        events = []
        for c in self.citizens:
            if not c.alive or not c.heirloom:
                continue
            hl = c.heirloom
            tracker = hl.get("_vision_tracker", {})
            if not tracker:
                continue

            # Find past holders seen 3+ times that haven't yet spawned a quest
            spawned = set(hl.get("_vision_quests_spawned", []))
            for holder_str, count in tracker.items():
                if count < 3 or holder_str in spawned:
                    continue
                if not c.faction:
                    continue
                # Don't spawn if this faction already has an active quest
                if self.faction_quests.get(c.faction) is not None:
                    continue

                # Spawn a heirloom-vision legacy quest
                hl_name = hl.get("name", hl.get("base_name", "the heirloom"))
                gen = hl.get("generations", 1)

                quest_templates = [
                    {
                        "type": "heirloom_recovery",
                        "name": f"Recover {holder_str}'s Lost Works",
                        "desc": f"Visions of {holder_str} through {hl_name} have shown {c.name} glimpses of ancient techniques now forgotten. The heirloom calls its holder to recover what was lost.",
                        "target": {"gold": 35, "stone": 20},
                        "reward_resources": {"gold": 25, "stone": 15},
                        "reward_morale": 8,
                        "narrative_complete": f"The lost works of {holder_str} have been recovered — old techniques, old wisdom, returned to Ashfall through the heirloom's memory. {hl_name} glows with quiet pride.",
                        "bonus_effect": "lore_recovery",
                    },
                    {
                        "type": "heirloom_pilgrimage",
                        "name": f"Honor {holder_str}'s Memory",
                        "desc": f"{hl_name} has shown {c.name} the same ancestor three times — {holder_str}, who once held it. The heirloom asks for a pilgrimage to honor their memory.",
                        "target": {"food": 25, "gold": 20},
                        "reward_resources": {"gold": 20, "food": 10},
                        "reward_morale": 10,
                        "narrative_complete": f"A pilgrimage in {holder_str}'s name has been completed. {hl_name} rests easier now — the ancestor's memory honored, their craft remembered.",
                        "bonus_effect": "pilgrimage_morale",
                    },
                ]
                template = random.choice(quest_templates)

                # Scale targets by generation and faction size
                members = self.list_by_faction(c.faction)
                faction_scale = max(1, len(members) // 4)
                gen_scale = 0.8 + gen * 0.1  # older heirlooms = harder quests

                scaled_target = {}
                for resource, base in template["target"].items():
                    scaled_target[resource] = max(1, int(base * faction_scale * gen_scale))
                scaled_rewards = {}
                for resource, base in template["reward_resources"].items():
                    scaled_rewards[resource] = max(1, int(base * faction_scale * gen_scale))

                quest = {
                    "faction": c.faction,
                    "type": template["type"],
                    "name": template["name"],
                    "desc": template["desc"],
                    "target": scaled_target,
                    "progress": {r: 0 for r in scaled_target},
                    "reward_morale": template["reward_morale"],
                    "reward_resources": scaled_rewards,
                    "narrative_complete": template["narrative_complete"],
                    "bonus_effect": template.get("bonus_effect"),
                    "rarity": "chain",
                    "chain_from": "heirloom_vision",
                    "start_day": world_obj.day,
                    "deadline": world_obj.day + 70,
                    "completed": False,
                    "failed": False,
                }
                self.faction_quests[c.faction] = quest

                hl.setdefault("_vision_quests_spawned", []).append(holder_str)

                color = FACTIONS[c.faction].get("color", "")
                events.append({
                    "faction": c.faction,
                    "citizen": c.name,
                    "heirloom": hl_name,
                    "holder": holder_str,
                    "narrative": (
                        f"💍📜 HEIRLOOM CALLS: After {count} visions of {holder_str} through "
                        f"{hl_name}, {c.name} understands — the heirloom is calling the "
                        f"{color} {c.faction} to action! '{template['name']}' has begun."
                    ),
                })

        return events if events else None

    # ── HEIRLOOM TIER 3: FACTION RELIC ──────────────────────

    def _check_heirloom_faction_relic(self, world_obj=None):
        """When an heirloom reaches generation 7+ ('the Ancient') and is held
        by a faction member whose faction has a wisdom council (3+ wise members),
        the faction may elevate the heirloom to a faction relic.
        
        Faction relics grant:
        - +1 permanent morale floor to all faction members
        - The heirloom's work bonus extends to ALL faction members in the same role
        - The heirloom's wisdom resonance extends to all faction elders
        - New report section tracks relics

        Once elevated, the relic remains with the faction even if the holder dies.
        Returns a list of events or None."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_faction_relics'):
            self._faction_relics = []

        events = []
        already_relic_heirlooms = {r["heirloom_name"] for r in self._faction_relics}

        for c in self.citizens:
            if not c.alive or not c.heirloom:
                continue
            hl = c.heirloom
            gen = hl.get("generations", 1)
            if gen < 7:
                continue  # only gen 7+ ("the Ancient") can become relics
            if hl.get("name") in already_relic_heirlooms:
                continue  # already a faction relic
            if not c.faction:
                continue

            # Check faction has a wisdom council (3+ wise members)
            wise = [m for m in self.citizens
                    if m.alive and m.faction == c.faction and m.wisdom_traits]
            if len(wise) < 3:
                continue

            # Faction relic elevation — 5% chance per day once conditions are met
            if random.random() > 0.05:
                continue

            hl_name = hl.get("name", hl.get("base_name", "the heirloom"))
            bonus_type = hl.get("bonus_type", "morale")
            bonus_value = hl.get("bonus_value", 0)
            prod_bonus = hl.get("production_bonus", {})
            prod_roles = prod_bonus.get("roles", [])
            prod_res = hl.get("base_prod_res", prod_bonus.get("resources", {}))

            relic = {
                "heirloom_name": hl_name,
                "faction": c.faction,
                "holder": c.name,
                "generation": gen,
                "bonus_type": bonus_type,
                "bonus_value": bonus_value,
                "prod_roles": prod_roles,
                "prod_resources": prod_res,
                "elevated_day": world_obj.day,
                "origin": hl.get("origin", "unknown"),
            }
            self._faction_relics.append(relic)

            # Mark the heirloom as a relic
            hl["_is_faction_relic"] = True
            hl["_relic_faction"] = c.faction
            hl["_relic_elevated_day"] = world_obj.day

            color = FACTIONS[c.faction].get("color", "")

            relic_narratives = [
                f"The elders of the {color} {c.faction} gathered around {c.name}, who held {hl_name} aloft. The heirloom — ancient, storied, glowing with {gen} generations of memory — was formally consecrated as a faction relic. From this day forward, its power belongs to all {c.faction}, not just its holder.",
                f"In a solemn ceremony at the faction hall, {hl_name} was elevated from treasured heirloom to faction relic. 'This,' the eldest council member declared, 'is no longer {c.name}'s alone. It is the {c.faction}'s — a piece of our shared soul.'",
                f"The wisdom council of the {c.faction} recognized what {hl_name} had become: a vessel of so much accumulated history that it transcended individual ownership. {c.name} placed it on the faction altar, and every {c.faction} member present felt its warmth.",
            ]
            narrative = random.choice(relic_narratives)

            events.append({
                "type": "faction_relic",
                "faction": c.faction,
                "heirloom": hl_name,
                "citizen": c.name,
                "generation": gen,
                "narrative": f"🏺✨ FACTION RELIC: {narrative} {hl_name} (gen {gen}) is now a sacred relic of the {c.faction}!",
            })

            kingdom.kingdom_log.append(f"🏺✨ FACTION RELIC: {hl_name} (gen {gen}) has been elevated to a faction relic of the {c.faction}!")

        return events if events else None

    # ── HEIRLOOM TIER 4: FACTION RELIC RITUAL ───────────────

    def _check_heirloom_relic_ritual(self, world_obj=None):
        """When a faction has a relic, a unique faction ritual/ceremony fires
        periodically (every 30-50 days per relic). The ritual is a sacred event
        centered on the relic, granting:

        - +5-15 gold, +3-8 food to the faction (scaled by relic generation)
        - +3-5 morale to all faction members
        - 30-50% lore fragment chance
        - Unique narrative deepening the relic's place in faction culture

        Each relic tracks its own ritual cooldown via _last_ritual_day.
        Returns events or None."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_faction_relics') or not self._faction_relics:
            return None

        events = []

        for relic in self._faction_relics:
            last_ritual = relic.get("_last_ritual_day", 0)
            cooldown = random.randint(30, 50)
            if world_obj.day - last_ritual < cooldown:
                continue

            faction = relic["faction"]
            hl_name = relic["heirloom_name"]
            gen = relic.get("generation", 7)
            color = FACTIONS[faction].get("color", "")

            # Scale rewards by generation
            gen_scale = min(3, (gen - 7) // 2 + 1)  # gen 7→1, 9→2, 11+→3
            gold_gain = random.randint(5, 15) + (gen_scale * 3)
            food_gain = random.randint(3, 8) + gen_scale

            kingdom.gold += gold_gain
            kingdom.food += food_gain

            # Morale boost to all faction members
            faction_members = [c for c in self.citizens if c.alive and c.faction == faction]
            morale_boost = random.randint(3, 5)
            for m in faction_members:
                m.morale = min(100, m.morale + morale_boost)

            # Lore fragment chance
            got_lore = False
            lore_chance = 0.30 + (gen_scale * 0.07)  # 30-50%
            if random.random() < lore_chance:
                if not hasattr(kingdom, 'lore_fragments'):
                    kingdom.lore_fragments = 0
                kingdom.lore_fragments = getattr(kingdom, 'lore_fragments', 0) + 1
                got_lore = True

            # Update relic ritual tracking
            relic["_last_ritual_day"] = world_obj.day

            lore_note = " A fragment of ancient wisdom was recovered during the ritual." if got_lore else ""

            ritual_narratives = [
                f"The {color} {faction} gathered in solemn ceremony around {hl_name}, the faction relic. As {len(faction_members)} voices chanted the old words, the relic pulsed with {gen} generations of accumulated memory. The ritual brought unexpected bounty (+{gold_gain}g, +{food_gain}f, +{morale_boost} morale to all).{lore_note}",
                f"In a ritual passed down since the relic's elevation, the {faction} elders led a Ceremony of Echoes around {hl_name}. Each faction member touched the relic and received a fragment of its long memory — and with it, prosperity (+{gold_gain}g, +{food_gain}f, +{morale_boost} morale to all).{lore_note}",
                f"The {faction} held a Vigil of Ages — a night-long ceremony with {hl_name} at its center. By dawn, the relic had shed tiny crystalline tears that dissolved into gold and grain. 'It remembers us as we remember it,' whispered the eldest (+{gold_gain}g, +{food_gain}f, +{morale_boost} morale to all).{lore_note}",
            ]

            events.append({
                "type": "relic_ritual",
                "faction": faction,
                "heirloom": hl_name,
                "generation": gen,
                "gold": gold_gain,
                "food": food_gain,
                "morale": morale_boost,
                "lore": got_lore,
                "narrative": f"🏺🕯️ RELIC RITUAL: {random.choice(ritual_narratives)}",
            })

            kingdom.kingdom_log.append(
                f"🏺🕯️ RELIC RITUAL: The {color} {faction} performed a sacred ceremony with their relic {hl_name}!"
            )

        return events if events else None

    # ── SEASONAL COUNCIL GATHERINGS ──────────────────────────

    def _check_seasonal_council_gatherings(self, world_obj=None):
        """During a wisdom council's peak season (when 2+ members have seasonally
        awakened traits), the council gathers more actively — doubling its
        morale boost and adding extra quest progress. Returns events or None."""
        if world_obj is None:
            world_obj = world

        season = getattr(world_obj, 'season', 'spring')
        events = []

        for faction in FACTIONS:
            wise_members = [c for c in self.citizens
                           if c.alive and c.faction == faction and c.wisdom_traits]
            if len(wise_members) < 3:
                continue

            # Count how many council members have traits awakened this season
            awakened = sum(1 for c in wise_members
                          for t in c.wisdom_traits
                          if Citizen._WISDOM_SEASONAL_AWAKENING.get(t["name"]) == season)

            if awakened < 2:
                continue  # not enough seasonal resonance for a gathering

            # Council gathers — double morale boost for this day
            faction_members = [c for c in self.citizens
                              if c.alive and c.faction == faction]
            gathering_morale = min(3, awakened // 2)

            gathering_narratives = [
                f"The {FACTIONS[faction]['color']} {faction} wisdom council gathers beneath the season's sky — {awakened} elders feel the {season}'s power stirring their old wisdom.",
                f"In the {season} light, the {faction} council convenes. The season has awakened something in {awakened} of them — and together, their counsel is stronger.",
                f"The season calls, and the {faction} elders answer. {awakened} wise ones sit in council, their {season}-awakened traits humming in harmony.",
            ]
            narrative = random.choice(gathering_narratives)

            for m in faction_members:
                m.morale = min(100, m.morale + gathering_morale)

            # Extra quest progress from the gathering
            quest = self.faction_quests.get(faction)
            if quest and not quest.get("completed") and not quest.get("failed"):
                for _ in range(awakened):
                    if random.random() < 0.15:
                        for resource in quest["progress"]:
                            if quest["progress"][resource] < quest["target"].get(resource, 9999):
                                quest["progress"][resource] += 1

            # Track that a gathering happened this season
            gathering_key = f"_gathering_{faction}_{season}_{world_obj.day // 30}"
            if not getattr(self, gathering_key, False):
                setattr(self, gathering_key, True)
                events.append({
                    "faction": faction,
                    "awakened": awakened,
                    "morale_boost": gathering_morale,
                    "narrative": f"🍂🏛️ SEASONAL COUNCIL: {narrative} (+{gathering_morale} morale to all {faction} members).",
                })

        return events if events else None

    # ── INTER-FACTION COUNCIL DIPLOMACY ──────────────────────

    def _check_council_diplomacy(self, world_obj=None):
        """When two factions both have active wisdom councils, their elders may
        meet to resolve disputes, share knowledge, and strengthen cross-faction
        bonds. Fires every ~15-20 days. Returns events or None."""
        if world_obj is None:
            world_obj = world

        # Throttle: every 15-20 days
        if not hasattr(self, '_last_council_diplomacy_day'):
            self._last_council_diplomacy_day = -20
        if world_obj.day - self._last_council_diplomacy_day < random.randint(15, 20):
            return None

        # Find factions with councils (3+ wise members)
        council_factions = []
        for faction in FACTIONS:
            wise_count = sum(1 for c in self.citizens
                            if c.alive and c.faction == faction and c.wisdom_traits)
            if wise_count >= 3:
                council_factions.append((faction, wise_count))

        if len(council_factions) < 2:
            return None

        self._last_council_diplomacy_day = world_obj.day
        events = []

        # Check all pairs of council factions
        checked = set()
        for i, (f1, c1) in enumerate(council_factions):
            for f2, c2 in council_factions[i + 1:]:
                pair = tuple(sorted([f1, f2]))
                if pair in checked:
                    continue
                checked.add(pair)

                # 40% base chance of diplomatic meeting, +5% per council member
                meeting_chance = 0.40 + 0.05 * (c1 + c2)
                if random.random() > meeting_chance:
                    continue

                # Council diplomacy!
                gold_gain = random.randint(8, 18)
                kingdom.gold += gold_gain

                # Morale boost to both factions
                color1 = FACTIONS[f1].get("color", "")
                color2 = FACTIONS[f2].get("color", "")
                for c in self.citizens:
                    if c.alive and c.faction in (f1, f2):
                        c.morale = min(100, c.morale + random.randint(2, 5))

                diplomacy_narratives = [
                    f"The wisdom councils of the {color1} {f1} and {color2} {f2} met in the old way — sharing food, stories, and hard-won counsel. Old grievances were laid aside (+{gold_gain}g).",
                    f"Elders from {f1} and {f2} gathered at the well at dusk. What began as formal council became a sharing of wisdom — and a recognition that both factions guard Ashfall's future (+{gold_gain}g).",
                    f"A joint council of {f1} and {f2} convened. The elders found more common ground than expected — the Sleeper's whispers touch all factions equally (+{gold_gain}g).",
                    f"The {f1} council sent emissaries to {f2} bearing gifts of {random.choice(['smoked meat', 'herbal tea', 'carved stone', 'woven cloth'])}. What followed was a rare thing: two factions, one purpose (+{gold_gain}g).",
                ]
                narrative = random.choice(diplomacy_narratives)

                events.append({
                    "faction_a": f1,
                    "faction_b": f2,
                    "gold": gold_gain,
                    "narrative": f"🤝🏛️ COUNCIL DIPLOMACY: {narrative} Both factions strengthened.",
                })

                # ── Tier 2: Cross-Faction Trade Pacts ──
                # 30% chance the diplomacy meeting results in a formal trade pact
                if random.random() < 0.30:
                    pact = self._create_trade_pact(f1, f2, c1, c2, world_obj)
                    if pact:
                        events.append(pact)

        return events if events else None

    def _create_trade_pact(self, faction_a, faction_b, council_a_count, council_b_count, world_obj=None):
        """Create a cross-faction trade pact between two councils.
        Lasts 30 days, grants daily gold + food to both factions.
        Returns a pact event dict."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_active_trade_pacts'):
            self._active_trade_pacts = []

        # Check if a pact already exists between these factions
        for existing in self._active_trade_pacts:
            if set([existing["faction_a"], existing["faction_b"]]) == set([faction_a, faction_b]):
                return None  # Pact already active

        pact_duration = 30
        daily_gold = random.randint(3, 6) + (council_a_count + council_b_count) // 3
        daily_food = random.randint(1, 3)

        pact = {
            "faction_a": faction_a,
            "faction_b": faction_b,
            "daily_gold": daily_gold,
            "daily_food": daily_food,
            "start_day": world_obj.day,
            "expires_day": world_obj.day + pact_duration,
            "council_a_count": council_a_count,
            "council_b_count": council_b_count,
        }
        self._active_trade_pacts.append(pact)

        color1 = FACTIONS[faction_a].get("color", "")
        color2 = FACTIONS[faction_b].get("color", "")
        pact_narratives = [
            f"The councils went further than mere talk — they forged a trade pact. {color1} {faction_a} and {color2} {faction_b} will share resources for {pact_duration} days.",
            f"A rare agreement: the {faction_a} and {faction_b} councils have bound their factions in a 30-day trade pact. Markets will flow between them.",
            f"Diplomacy bore fruit: the elders of {faction_a} and {faction_b} signed a trade pact. For {pact_duration} days, both factions will prosper together.",
        ]
        return {
            "faction_a": faction_a,
            "faction_b": faction_b,
            "type": "trade_pact",
            "daily_gold": daily_gold,
            "daily_food": daily_food,
            "duration": pact_duration,
            "narrative": f"🤝📜 TRADE PACT: {random.choice(pact_narratives)} (+{daily_gold}g, +{daily_food}f daily for both).",
        }

    def _check_trade_pact_income(self, world_obj=None):
        """Daily income from active cross-faction trade pacts.
        Returns a list of income events or None."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_active_trade_pacts') or not self._active_trade_pacts:
            return None

        events = []
        expired = []

        for pact in self._active_trade_pacts:
            if world_obj.day > pact["expires_day"]:
                expired.append(pact)
                continue

            kingdom.gold += pact["daily_gold"]
            kingdom.food += pact["daily_food"]

            # Small morale boost to faction members from the prosperity
            for c in self.citizens:
                if c.alive and c.faction in (pact["faction_a"], pact["faction_b"]):
                    if random.random() < 0.15:  # 15% chance each
                        c.morale = min(100, c.morale + 1)

            days_left = pact["expires_day"] - world_obj.day
            if days_left <= 5:  # Only narrate when close to expiry or every 10 days
                color1 = FACTIONS[pact["faction_a"]].get("color", "")
                color2 = FACTIONS[pact["faction_b"]].get("color", "")
                events.append({
                    "type": "trade_pact_income",
                    "gold": pact["daily_gold"],
                    "food": pact["daily_food"],
                    "days_left": days_left,
                    "narrative": (
                        f"🤝📜 TRADE PACT: {color1} {pact['faction_a']} ↔ {color2} {pact['faction_b']} "
                        f"trade flourishes (+{pact['daily_gold']}g, +{pact['daily_food']}f). "
                        f"({days_left} days remaining)."
                    ),
                })

        # Clean up expired pacts
        for pact in expired:
            self._active_trade_pacts.remove(pact)
            color1 = FACTIONS[pact["faction_a"]].get("color", "")
            color2 = FACTIONS[pact["faction_b"]].get("color", "")
            events.append({
                "type": "trade_pact_expired",
                "narrative": f"🤝📜 TRADE PACT ENDED: The trade pact between {color1} {pact['faction_a']} and {color2} {pact['faction_b']} has run its course. Both factions are richer for it.",
            })

        return events if events else None

    # ── COUNCIL TIER 3: PERMANENT CROSS-FACTION ALLIANCE ────

    def _check_permanent_alliance(self, world_obj=None):
        """When two factions have completed 2+ trade pacts together and both
        maintain active wisdom councils, there's a small chance a permanent
        alliance forms during a council diplomacy meeting.

        Permanent alliances grant:
        - Permanent daily +1-2g + 1f to both factions
        - 10% of one faction's quest progress leaks to the other
        - Alliance members get +2 permanent morale floor
        - Tracked in _permanent_alliances list (never expires)

        Returns a list of alliance events or None."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_permanent_alliances'):
            self._permanent_alliances = []
        if not hasattr(self, '_completed_pact_count'):
            # Track how many pacts have been completed between each faction pair
            self._completed_pact_count = {}

        # First, track completed pacts (check for newly expired ones)
        if hasattr(self, '_active_trade_pacts'):
            for pact in list(self._active_trade_pacts):
                if world_obj.day > pact["expires_day"]:
                    # Pact just expired — count it
                    pair_key = tuple(sorted([pact["faction_a"], pact["faction_b"]]))
                    self._completed_pact_count[pair_key] = self._completed_pact_count.get(pair_key, 0) + 1

        events = []
        already_allied = {tuple(sorted([a["faction_a"], a["faction_b"]])) for a in self._permanent_alliances}

        faction_list = list(FACTIONS.keys())
        for i, f1 in enumerate(faction_list):
            for f2 in faction_list[i+1:]:
                pair_key = tuple(sorted([f1, f2]))
                if pair_key in already_allied:
                    continue  # already permanently allied

                # Need at least 2 completed pacts between these factions
                completed = self._completed_pact_count.get(pair_key, 0)
                if completed < 2:
                    continue

                # Both factions need active wisdom councils
                wise1 = [c for c in self.citizens if c.alive and c.faction == f1 and c.wisdom_traits]
                wise2 = [c for c in self.citizens if c.alive and c.faction == f2 and c.wisdom_traits]
                if len(wise1) < 3 or len(wise2) < 3:
                    continue

                # 10% chance per day once conditions are met
                if random.random() > 0.10:
                    continue

                # Form the permanent alliance!
                daily_gold = random.randint(1, 2)
                daily_food = 1

                alliance = {
                    "faction_a": f1,
                    "faction_b": f2,
                    "daily_gold": daily_gold,
                    "daily_food": daily_food,
                    "formed_day": world_obj.day,
                    "pacts_completed": completed,
                    "council_a": len(wise1),
                    "council_b": len(wise2),
                }
                self._permanent_alliances.append(alliance)

                color1 = FACTIONS[f1].get("color", "")
                color2 = FACTIONS[f2].get("color", "")

                alliance_narratives = [
                    f"After {completed} successful trade pacts and years of council diplomacy, the {color1} {f1} and {color2} {f2} have forged a PERMANENT ALLIANCE. Their councils have bound the factions together — not by treaty, but by shared wisdom and mutual trust that will outlast any single generation.",
                    f"The councils of {f1} and {f2} made history today. 'We have shared trade, shared counsel, and shared dreams,' the eldest declared. 'Let us now share a future.' The permanent alliance between {color1} {f1} and {color2} {f2} was sealed with the oldest rite — a handshake between council elders that will echo through generations.",
                    f"A momentous day for Ashfall: the {color1} {f1} and {color2} {f2}, bound by {completed} trade pacts and countless council meetings, have elevated their friendship to a PERMANENT ALLIANCE. Both factions will now share daily prosperity and quest progress — their fates intertwined forever.",
                ]
                narrative = random.choice(alliance_narratives)

                events.append({
                    "type": "permanent_alliance",
                    "faction_a": f1,
                    "faction_b": f2,
                    "daily_gold": daily_gold,
                    "daily_food": daily_food,
                    "narrative": f"🤝♾️ PERMANENT ALLIANCE: {narrative} (+{daily_gold}g, +{daily_food}f daily forever).",
                })

                kingdom.kingdom_log.append(
                    f"🤝♾️ PERMANENT ALLIANCE: The {f1} and {f2} have formed a permanent cross-faction alliance!"
                )

        return events if events else None

    def _check_alliance_income(self, world_obj=None):
        """Daily income and quest progress sharing from permanent alliances.
        Returns a list of income events or None."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_permanent_alliances') or not self._permanent_alliances:
            return None

        events = []
        for alliance in self._permanent_alliances:
            f1, f2 = alliance["faction_a"], alliance["faction_b"]
            kingdom.gold += alliance["daily_gold"]
            kingdom.food += alliance["daily_food"]

            # Small morale boost to alliance members
            for c in self.citizens:
                if c.alive and c.faction in (f1, f2) and random.random() < 0.10:
                    c.morale = min(100, c.morale + 1)

            # 10% quest progress sharing — each faction's quest progress
            # contributes to the other's active quest
            for src_faction, dst_faction in [(f1, f2), (f2, f1)]:
                src_quest = self.faction_quests.get(src_faction)
                dst_quest = self.faction_quests.get(dst_faction)
                if src_quest and dst_quest and not src_quest.get("completed") and not dst_quest.get("completed"):
                    if not src_quest.get("failed") and not dst_quest.get("failed"):
                        # Share 10% of src's daily progress to dst
                        for resource in src_quest["target"]:
                            src_prog = src_quest["progress"].get(resource, 0)
                            if src_prog > 0:
                                leak = max(0, int(src_prog * 0.10))
                                if leak > 0:
                                    dst_quest["progress"][resource] = dst_quest["progress"].get(resource, 0) + leak

            days_since = world_obj.day - alliance["formed_day"]
            # Narrate every 10 days or on the formation anniversary
            if days_since > 0 and (days_since % 30 == 0 or days_since == 10):
                color1 = FACTIONS[f1].get("color", "")
                color2 = FACTIONS[f2].get("color", "")
                events.append({
                    "type": "alliance_income",
                    "gold": alliance["daily_gold"],
                    "food": alliance["daily_food"],
                    "days": days_since,
                    "narrative": (
                        f"🤝♾️ ALLIANCE: {color1} {f1} ↔ {color2} {f2} — "
                        f"permanent bond flourishes (+{alliance['daily_gold']}g, "
                        f"+{alliance['daily_food']}f daily). "
                        f"({days_since}d and counting)."
                    ),
                })

        return events if events else None

    # ── DREAM-BOND TIER 4: DANGER-SENSE ─────────────────────

    def _check_dream_bond_tier4(self, world_obj=None):
        """Tier 4: Danger-Sense — Dream-bonded citizens feel a whisper of danger
        when their bonded partner faces it. The bond becomes a silent alarm.

        Effects:
        - Bonded pairs where one is a guard/scout and the other is a civilian:
          the civilian gains +2 morale (feeling protected), and 20% chance
          the guard/scout gains +3 temporary combat skill for the day.
        - When active disasters exist in the world, bonded pairs have a 35%
          chance of mitigating morale damage — each partner gets +2 resilience.
        - 10% chance per pair of detecting a hidden danger (gold bonus from
          intuition — the bonded citizen "just knows" something and avoids waste).

        Returns events or None."""
        if world_obj is None:
            world_obj = world

        events = []
        name_map = {c.name: c for c in self.citizens if c.alive}
        shown_pairs = set()
        danger_roles = ("guard", "scout")
        protected_pairs = 0
        total_gold = 0

        for c in self.citizens:
            if not c.alive or not c.dream_bonds or c.role in ("child", "elder"):
                continue
            for bonded_name in c.dream_bonds:
                pair = tuple(sorted([c.name, bonded_name]))
                if pair in shown_pairs:
                    continue
                shown_pairs.add(pair)

                bonded = name_map.get(bonded_name)
                if not bonded or not bonded.alive:
                    continue
                if bonded.role in ("child", "elder"):
                    continue

                # Check if one is danger-facing and the other is civilian
                c_danger = c.role in danger_roles
                b_danger = bonded.role in danger_roles
                if c_danger and not b_danger:
                    protector, civilian = c, bonded
                elif b_danger and not c_danger:
                    protector, civilian = bonded, c
                else:
                    continue  # both danger or both civilian — no danger-sense asymmetry

                protected_pairs += 1
                # Civilian feels safer
                civilian.morale = min(100, civilian.morale + 2)

                # Protector gets temporary combat edge from the bond
                if random.random() < 0.20:
                    protector.combat_skill = min(100, protector.combat_skill + 3)
                    protector._danger_sense_bonus = True

                # Intuition bonus — the bond whispers warning of hidden waste/danger
                if random.random() < 0.10:
                    gold_gain = random.randint(2, 6)
                    total_gold += gold_gain
                    kingdom.gold += gold_gain

        # Disaster resilience — bonded pairs help each other through active disasters
        active_disasters = getattr(world_obj, '_active_disasters', []) if world_obj else []
        if active_disasters:
            disaster_resilience_pairs = 0
            for c in self.citizens:
                if not c.alive or not c.dream_bonds:
                    continue
                for bonded_name in c.dream_bonds:
                    pair = tuple(sorted([c.name, bonded_name]))
                    bonded = name_map.get(bonded_name)
                    if not bonded or not bonded.alive:
                        continue
                    if random.random() < 0.35:
                        c.morale = min(100, c.morale + 2)
                        bonded.morale = min(100, bonded.morale + 2)
                        disaster_resilience_pairs += 1
                        break  # count each citizen once

            if disaster_resilience_pairs > 0:
                disaster_names = [d.get("type", "unknown") for d in active_disasters[:3]]
                dnames = ", ".join(disaster_names)

                danger_narratives = [
                    f"As {dnames} threaten Ashfall, {disaster_resilience_pairs} dream-bonded citizens draw strength from their bonds — each partner a steady presence in the other's mind, a shield against fear. (+2 morale each).",
                    f"The disaster does not strike alone — but neither do the dream-bonded. {disaster_resilience_pairs} bonded citizens feel their partner's courage across the distance, and stand a little taller (+2 morale each).",
                    f"When {dnames} loom, the dream-bond network lights up with silent reassurance. {disaster_resilience_pairs} bonded citizens weather the crisis better — anchored by the knowledge that someone, somewhere, is thinking of them (+2 morale each).",
                ]
                events.append({
                    "type": "dream_bond_disaster_resilience",
                    "pairs": disaster_resilience_pairs,
                    "disasters": dnames,
                    "narrative": f"🫂🛡️ DANGER-SENSE [T4]: {random.choice(danger_narratives)}",
                })

        if protected_pairs > 0:
            gold_note = f" Bond-intuition also averted {total_gold}g in hidden waste." if total_gold > 0 else ""
            protector_narratives = [
                f"{protected_pairs} dream-bonded pairs feel the quiet hum of danger-sense — civilians rest easier knowing their bonded protectors stand watch, and the protectors feel an extra edge of alertness. (+2 civilian morale, protector edge).{gold_note}",
                f"The dream-bond whispers warnings that conscious minds miss. {protected_pairs} civilian citizens feel a warm reassurance — their bonded guards and scouts are vigilant, and the bond carries that vigilance home.{gold_note}",
            ]
            if not active_disasters:  # only add this narrative if not already covered above
                events.append({
                    "type": "dream_bond_danger_sense",
                    "pairs": protected_pairs,
                    "gold": total_gold,
                    "narrative": f"🫂⚔️ DANGER-SENSE [T4]: {random.choice(protector_narratives)}",
                })

        return events if events else None

    # ── BRIDGE: TRIFECTA WONDER → FACTION EPIC QUEST ────────

    def _check_trifecta_faction_quest(self, world_obj=None):
        """When a trifecta wonder has just fired in a region (world._trifecta_fired
        has new entries since last check), spawn an epic faction quest themed
        around the wonder. The trifecta wonder permanently changes a region —
        the faction most connected to that region receives a quest to honor,
        study, or utilize the wonder.

        Bridges Bex's trifecta wonder system into faction quests.

        Returns events or None."""
        if world_obj is None:
            world_obj = world

        trifecta_fired = getattr(world_obj, '_trifecta_fired', set())
        if not trifecta_fired:
            return None

        # Track which trifectas we've already spawned quests for
        if not hasattr(self, '_trifecta_quests_spawned'):
            self._trifecta_quests_spawned = set()

        events = []
        region_names = {
            "the_vale": "the Vale", "old_oak_ridge": "Old Oak Ridge",
            "glimmer_marsh": "Glimmer Marsh", "sunfire_plains": "Sunfire Plains",
            "ironroot_depths": "Ironroot Depths", "the_ashen_copse": "the Ashen Copse",
            "the_sunken_sanctum": "the Sunken Sanctum", "the_dreaming_deep": "the Dreaming Deep",
        }

        # Region → faction affinity mapping
        REGION_FACTION_AFFINITY = {
            "the_vale": "Hearthkeepers",
            "old_oak_ridge": "Wildwalkers",
            "glimmer_marsh": "Wildwalkers",
            "sunfire_plains": "Deepwardens",
            "ironroot_depths": "Deepwardens",
            "the_ashen_copse": "Hearthkeepers",
            "the_sunken_sanctum": "Hearthkeepers",
            "the_dreaming_deep": "Deepwardens",
        }

        for region in trifecta_fired:
            if region in self._trifecta_quests_spawned:
                continue

            # Find the faction for this region
            faction = REGION_FACTION_AFFINITY.get(region)
            if not faction:
                continue

            # Check faction doesn't already have an active quest
            if self.faction_quests.get(faction) is not None:
                # Queue it — try again later
                continue

            rname = region_names.get(region, region)
            color = FACTIONS[faction].get("color", "")
            members = self.list_by_faction(faction)
            if len(members) < 3:
                continue

            # Scale targets by faction size
            scale = max(1, len(members) // 4)

            # Epic quest themed around the trifecta wonder
            trifecta_bonuses = getattr(world_obj, '_trifecta_bonuses', {}).get(region, {})

            quest_name = f"Honor the Wonder of {rname}"
            quest_desc = (
                f"The trifecta wonder in {rname} has permanently changed the land. "
                f"The {faction} are called to honor this miracle — to study it, "
                f"protect it, and ensure its gifts benefit all of Ashfall for generations."
            )

            quest = {
                "faction": faction,
                "type": "trifecta_wonder",
                "name": quest_name,
                "desc": quest_desc,
                "target": {
                    "gold": 20 * scale,
                    "stone": 8 * scale,
                },
                "progress": {"gold": 0, "stone": 0},
                "reward_morale": 12,
                "reward_resources": {
                    "gold": 30 * scale,
                    "food": 10 * scale,
                    "stone": 8 * scale,
                },
                "bonus_effect": "eternal_legacy",
                "rarity": "chain",
                "chain_from": "trifecta_wonder",
                "start_day": world_obj.day,
                "deadline": world_obj.day + 90,  # epic — 90 day deadline
                "completed": False,
                "failed": False,
            }
            self.faction_quests[faction] = quest
            self._trifecta_quests_spawned.add(region)

            narrative = (
                f"🔗💎🌟 TRIFECTA QUEST: The wonder at {rname} has called the "
                f"{color} {faction} to action — '{quest_name}'! "
                f"The faction must gather 20×{scale} gold and 8×{scale} stone to "
                f"properly honor the miracle that has transformed their region."
            )
            kingdom.kingdom_log.append(narrative)

            for m in members:
                m.morale = min(100, m.morale + 5)
                m.remember(f"Trifecta wonder quest: {quest_name}")

            events.append({
                "type": "trifecta_quest",
                "region": region,
                "faction": faction,
                "quest": quest_name,
                "narrative": narrative,
            })

        return events if events else None

    # ── COUNCIL TIER 4: ALLIANCE JOINT MEGA-QUEST ───────────

    def _check_alliance_joint_quest(self, world_obj=None):
        """When a permanent alliance exists, every 40-60 days the allied factions
        may receive a joint mega-quest. Both factions work toward the same goal,
        their combined strength tackling a challenge neither could face alone.

        Joint mega-quests:
        - Appear in BOTH factions' quest slots (they share the quest object)
        - Have dramatically scaled targets and rewards (2-3× normal)
        - Grant alliance-wide bonuses on completion
        - Tracked via _alliance_joint_quests to prevent duplicate spawning

        Returns events or None."""
        if world_obj is None:
            world_obj = world

        if not hasattr(self, '_permanent_alliances') or not self._permanent_alliances:
            return None

        if not hasattr(self, '_alliance_joint_quests'):
            self._alliance_joint_quests = {}

        events = []

        for alliance in self._permanent_alliances:
            f1, f2 = alliance["faction_a"], alliance["faction_b"]
            pair_key = tuple(sorted([f1, f2]))

            # Check cooldown
            last_joint = self._alliance_joint_quests.get(pair_key, 0)
            cooldown = random.randint(40, 60)
            if world_obj.day - last_joint < cooldown:
                continue

            # Both factions must be free (no active quest)
            if self.faction_quests.get(f1) is not None:
                continue
            if self.faction_quests.get(f2) is not None:
                continue

            # Both factions need members
            members1 = self.list_by_faction(f1)
            members2 = self.list_by_faction(f2)
            if len(members1) < 3 or len(members2) < 3:
                continue

            # 15% daily chance once cooldown is up
            if random.random() > 0.15:
                continue

            color1 = FACTIONS[f1].get("color", "")
            color2 = FACTIONS[f2].get("color", "")
            combined_scale = max(1, (len(members1) + len(members2)) // 6)  # bigger scale for joint effort

            # Joint mega-quest templates
            joint_templates = [
                {
                    "name": f"Build the Alliance Monument",
                    "desc": f"The {f1} and {f2} have been allies for {world_obj.day - alliance['formed_day']} days. Their bond deserves a monument — a physical testament to unity that will inspire future generations.",
                    "target": {"stone": 15 * combined_scale, "gold": 25 * combined_scale},
                    "reward_resources": {"gold": 40 * combined_scale, "stone": 20 * combined_scale, "food": 15 * combined_scale},
                    "reward_morale": 15,
                    "bonus_effect": "shrine_blessing",
                },
                {
                    "name": f"Host the Grand Alliance Festival",
                    "desc": f"Let all of Ashfall witness the strength of the {f1}-{f2} alliance! A grand festival to celebrate unity, trade, and shared purpose.",
                    "target": {"food": 20 * combined_scale, "gold": 15 * combined_scale},
                    "reward_resources": {"gold": 35 * combined_scale, "food": 20 * combined_scale, "wood": 10 * combined_scale},
                    "reward_morale": 18,
                    "bonus_effect": "gold_rush",
                },
                {
                    "name": f"Chart the Alliance Trade Road",
                    "desc": f"The permanent alliance between {f1} and {f2} deserves a dedicated trade road — a route that bypasses all obstacles and binds their territories together forever.",
                    "target": {"wood": 12 * combined_scale, "stone": 12 * combined_scale, "gold": 18 * combined_scale},
                    "reward_resources": {"gold": 45 * combined_scale, "food": 12 * combined_scale, "wood": 15 * combined_scale},
                    "reward_morale": 12,
                    "bonus_effect": "lore_recovery",
                },
            ]

            template = random.choice(joint_templates)
            quest = {
                "faction": f1,  # primary faction
                "joint_faction": f2,  # secondary faction — shares this quest
                "type": "alliance_joint",
                "name": template["name"],
                "desc": template["desc"],
                "target": template["target"],
                "progress": {r: 0 for r in template["target"]},
                "reward_morale": template["reward_morale"],
                "reward_resources": template["reward_resources"],
                "bonus_effect": template["bonus_effect"],
                "rarity": "chain",
                "chain_from": "permanent_alliance",
                "start_day": world_obj.day,
                "deadline": world_obj.day + 75,  # generous deadline for joint effort
                "completed": False,
                "failed": False,
                "_is_joint": True,
                "_joint_factions": [f1, f2],
            }

            # Both factions share the quest object
            self.faction_quests[f1] = quest
            self.faction_quests[f2] = quest
            self._alliance_joint_quests[pair_key] = world_obj.day

            narrative = (
                f"🤝♾️⚔️ JOINT MEGA-QUEST: The {color1} {f1} and {color2} {f2} "
                f"have been called to a shared destiny — '{template['name']}'! "
                f"Both factions unite toward a single great purpose. "
                f"({template['desc']})"
            )
            kingdom.kingdom_log.append(narrative)

            for m in members1 + members2:
                m.morale = min(100, m.morale + 4)
                m.remember(f"Alliance joint quest: {template['name']}")

            events.append({
                "type": "alliance_joint_quest",
                "faction_a": f1,
                "faction_b": f2,
                "quest": template["name"],
                "narrative": narrative,
            })

        return events if events else None

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

        # Well upgrades provide clean water, reducing disease risk
        wb = kingdom.well_bonuses()
        if wb["disease_resist_pct"] > 0:
            chance *= (1.0 - wb["disease_resist_pct"] / 100.0)

        # Trade route synergies: Herbal Remedy Road provides disease resistance
        synergy_bonuses = kingdom.trade_synergy_bonuses()
        if synergy_bonuses["disease_resist_pct"] > 0:
            chance *= (1.0 - synergy_bonuses["disease_resist_pct"] / 100.0)

        # Quest bonuses: disease_resist from faction quests
        quest_bonuses = getattr(kingdom, '_quest_bonuses', {})
        quest_disease_resist = quest_bonuses.get("disease_resist", {}).get("value", 0)
        if quest_disease_resist > 0:
            chance *= (1.0 - quest_disease_resist / 100.0)

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

        # Inter-family relations: death softens rivalries, deepens alliances
        deceased_family = deceased.family_name()
        for (fam_a, fam_b), score in list(self.family_relations.items()):
            if fam_a == deceased_family or fam_b == deceased_family:
                other = fam_b if fam_a == deceased_family else fam_a
                if score <= -30:
                    # Death softens old grudges
                    self._update_family_relations(deceased_family, other, +5,
                                                   f"death of {deceased.name} eased old tensions")
                elif score >= 30:
                    # Shared sorrow deepens bonds
                    self._update_family_relations(deceased_family, other, +3,
                                                   f"shared grief over loss of {deceased.name}")

        # Log it
        kingdom.kingdom_log.append(narrative)

        # ── Heirloom Inheritance ──
        # If the deceased held an heirloom, pass it to a family member
        heirloom_event = None
        if deceased.heirloom:
            heirloom_event = self._pass_heirloom(deceased, world_obj)
            if heirloom_event:
                narrative += f" {heirloom_event['narrative']}"

        # ── Family Heirloom creation ──
        # When a master (L4) or expert (L3) dies of old age, they may leave an heirloom
        if cause in ("old_age", "extreme_old_age") and deceased.mastery_level >= 3:
            base_chance = 0.30 if deceased.mastery_level >= 4 else 0.15
            if random.random() < base_chance and not deceased.heirloom:
                creation_event = self._create_heirloom(deceased, world_obj)
                if creation_event:
                    heirloom_event = creation_event
                    narrative += f" {creation_event['narrative']}"

        return {
            "type": "funeral",
            "deceased": deceased.name,
            "cause": cause,
            "family_mourners": len(family_mourners),
            "faction_solidarity": faction_solidarity,
            "community_size": community_count,
            "narrative": narrative,
            "heirloom": heirloom_event,
        }

    # ── FAMILY HEIRLOOMS ────────────────────────────────────

    def _create_heirloom(self, deceased, world_obj=None):
        """Create a family heirloom from a deceased master/expert.
        Passes it to a living family member. Returns event dict or None."""
        if world_obj is None:
            world_obj = world

        role = deceased.role
        family_name = deceased.family_name()

        # Heirloom templates by role
        heirloom_templates = {
            "farmer": [
                {"name": f"{family_name} Sickle", "story": f"Worn smooth by {deceased.name}'s hands through countless harvests.", "bonus": "morale", "value": 3, "prod_roles": ["farmer"], "prod_res": {"food": 1}},
                {"name": f"{family_name} Seed-Pouch", "story": f"A leather pouch of heirloom seeds, passed down from {deceased.name}.", "bonus": "morale", "value": 2, "prod_roles": ["farmer"], "prod_res": {"food": 1}},
            ],
            "woodcutter": [
                {"name": f"{family_name} Axe", "story": f"The axe {deceased.name} swung for decades — the handle shaped to perfection.", "bonus": "morale", "value": 3, "prod_roles": ["woodcutter"], "prod_res": {"wood": 1}},
                {"name": f"{family_name} Whetstone", "story": f"A prized sharpening stone, kept by {deceased.name} since their apprenticeship.", "bonus": "morale", "value": 2, "prod_roles": ["woodcutter"], "prod_res": {"wood": 1}},
            ],
            "miner": [
                {"name": f"{family_name} Pick", "story": f"{deceased.name}'s trusted pick — the iron head still rings true.", "bonus": "morale", "value": 3, "prod_roles": ["miner"], "prod_res": {"stone": 1}},
                {"name": f"{family_name} Lantern", "story": f"A brass lantern {deceased.name} carried into the depths, never once going out.", "bonus": "morale", "value": 2, "prod_roles": ["miner"], "prod_res": {"gold": 1}},
            ],
            "builder": [
                {"name": f"{family_name} Hammer", "story": f"The hammer {deceased.name} used to raise Ashfall's walls and halls.", "bonus": "morale", "value": 3, "prod_roles": ["builder"], "prod_res": {}},
                {"name": f"{family_name} Measuring Cord", "story": f"A knotted cord {deceased.name} used to lay out every foundation.", "bonus": "morale", "value": 2, "prod_roles": ["builder"], "prod_res": {}},
            ],
            "herbalist": [
                {"name": f"{family_name} Mortar", "story": f"A stone mortar, stained with decades of remedies prepared by {deceased.name}.", "bonus": "morale", "value": 3, "prod_roles": ["herbalist"], "prod_res": {"food": 1}},
                {"name": f"{family_name} Herb-Journal", "story": f"{deceased.name}'s handwritten journal of herbs, cures, and secrets.", "bonus": "morale", "value": 2, "prod_roles": ["herbalist"], "prod_res": {"gold": 1}},
            ],
            "guard": [
                {"name": f"{family_name} Blade", "story": f"A well-balanced blade, carried by {deceased.name} in every battle.", "bonus": "combat", "value": 5, "prod_roles": [], "prod_res": {}},
                {"name": f"{family_name} Shield", "story": f"A battered shield bearing the marks of {deceased.name}'s courage.", "bonus": "combat", "value": 3, "prod_roles": [], "prod_res": {}},
            ],
            "scout": [
                {"name": f"{family_name} Compass", "story": f"A brass compass {deceased.name} used to map every corner of Ashfall.", "bonus": "morale", "value": 3, "prod_roles": ["scout"], "prod_res": {}},
                {"name": f"{family_name} Map-Case", "story": f"A worn leather case holding {deceased.name}'s hand-drawn maps.", "bonus": "morale", "value": 2, "prod_roles": ["scout"], "prod_res": {}},
            ],
            "elder": [
                {"name": f"{family_name} Story-Stone", "story": f"A smooth river stone {deceased.name} held while telling tales of old.", "bonus": "morale", "value": 4, "prod_roles": [], "prod_res": {}},
                {"name": f"{family_name} Memory-Quill", "story": f"A quill {deceased.name} used to record the kingdom's history.", "bonus": "morale", "value": 2, "prod_roles": [], "prod_res": {}},
            ],
        }

        templates = heirloom_templates.get(role, [])
        if not templates:
            return None

        template = random.choice(templates)

        # Find an heir: prefer family members, then faction members, then any adult
        heir = None
        family_members = [c for c in self.citizens if c.alive and c.family_name() == family_name and c is not deceased and not c.heirloom and c.role not in ("child",)]
        if family_members:
            heir = random.choice(family_members)
        else:
            faction_members = [c for c in self.citizens if c.alive and c.faction == deceased.faction and c is not deceased and not c.heirloom and c.role not in ("child",)]
            if faction_members:
                heir = random.choice(faction_members)
            else:
                any_adult = [c for c in self.citizens if c.alive and c is not deceased and not c.heirloom and c.role not in ("child",)]
                if any_adult:
                    heir = random.choice(any_adult)

        if not heir:
            return None

        # Build heirloom record
        heirloom = {
            "name": template["name"],
            "base_name": template["name"],  # original name, used for generational prestige suffixes
            "origin": template["story"],
            "creator": deceased.name,
            "creator_role": role,
            "creator_family": family_name,
            "bonus_type": template["bonus"],
            "bonus_value": template["value"],
            "base_bonus_value": template["value"],  # original value, generations scale from this
            "holder": heir.name,
            "created_day": world_obj.day,
            "generations": 1,
            "history": [
                {
                    "day": world_obj.day,
                    "event": f"Created by {deceased.name} ({MASTERY_TITLES.get(deceased.mastery_level, '')} {role})",
                },
                {
                    "day": world_obj.day,
                    "event": f"Passed to {heir.name} on day {world_obj.day}",
                },
            ],
            "production_bonus": {
                "roles": template.get("prod_roles", []),
                "resources": template.get("prod_res", {}),
            },
            "base_prod_res": template.get("prod_res", {}).copy(),  # for generation-based scaling
        }
        self.family_heirlooms.append(heirloom)
        heir.heirloom = heirloom

        # Apply immediate bonus
        if template["bonus"] == "morale":
            heir.morale = min(100, heir.morale + template["value"])
        elif template["bonus"] == "combat":
            heir.combat_skill = min(100, heir.combat_skill + template["value"])

        heir.remember(f"Inherited the {template['name']} from {deceased.name}")
        narrative = (
            f"💍 HEIRLOOM: {deceased.name}'s {template['name']} passes to {heir.name}. "
            f'"{template["story"]}"'
        )
        kingdom.kingdom_log.append(narrative)

        return {
            "heirloom_name": template["name"],
            "creator": deceased.name,
            "heir": heir.name,
            "bonus_type": template["bonus"],
            "bonus_value": template["value"],
            "narrative": narrative,
        }

    def _pass_heirloom(self, deceased, world_obj=None):
        """Pass the deceased's heirloom to a living family member.
        Returns event dict or None if no eligible heir."""
        if world_obj is None:
            world_obj = world

        heirloom = deceased.heirloom
        if not heirloom:
            return None

        family_name = deceased.family_name()

        # Find heir: family > faction > any adult
        heir = None
        family_members = [c for c in self.citizens if c.alive and c.family_name() == family_name and c is not deceased and not c.heirloom and c.role not in ("child",)]
        if family_members:
            heir = random.choice(family_members)
        else:
            faction_members = [c for c in self.citizens if c.alive and c.faction == deceased.faction and c is not deceased and not c.heirloom and c.role not in ("child",)]
            if faction_members:
                heir = random.choice(faction_members)
            else:
                any_adult = [c for c in self.citizens if c.alive and c is not deceased and not c.heirloom and c.role not in ("child",)]
                if any_adult:
                    heir = random.choice(any_adult)

        if not heir:
            # No eligible heir — heirloom is lost
            self.family_heirlooms = [h for h in self.family_heirlooms if h.get("name") != heirloom.get("name")]
            narrative = f"💍 HEIRLOOM LOST: {heirloom['name']} has no heir. Its story ends with {deceased.name}."
            kingdom.kingdom_log.append(narrative)
            return {"heirloom_name": heirloom["name"], "lost": True, "narrative": narrative}

        # Transfer heirloom
        heirloom["holder"] = heir.name
        heirloom["passed_from"] = deceased.name
        heirloom["passed_day"] = world_obj.day
        heirloom["generations"] = heirloom.get("generations", 1) + 1
        # Add history entry for the transfer
        if "history" not in heirloom:
            heirloom["history"] = []
        heirloom["history"].append({
            "day": world_obj.day,
            "event": f"Passed from {deceased.name} to {heir.name} (generation {heirloom['generations']})",
        })
        # Scaling bonus: heirlooms grow more potent over generations
        base_value = heirloom.get("base_bonus_value", heirloom.get("bonus_value", 0))
        gen_bonus = min((heirloom["generations"] - 1) // 2, 3)  # +1 per 2 generations beyond first, cap +3
        heirloom["bonus_value"] = base_value + gen_bonus

        # ── Generational Prestige: name earns suffixes at milestone generations ──
        base_name = heirloom.get("base_name", heirloom.get("name", "Unknown Heirloom"))
        gen = heirloom["generations"]
        prestige_milestones = {3: "II", 5: "III", 7: "the Ancient", 10: "the Eternal"}
        if gen in prestige_milestones:
            old_name = heirloom["name"]
            heirloom["name"] = f"{base_name} {prestige_milestones[gen]}"
            prestige_note = f"At generation {gen}, earned the title '{prestige_milestones[gen]}'"
            heirloom["history"].append({"day": world_obj.day, "event": prestige_note})

            # ── Heirloom Legacy Quest: ancient heirlooms generate special faction quests ──
            if gen in (7, 10) and heir.faction:
                legacy_quest = self._generate_heirloom_legacy_quest(heirloom, heir, world_obj)
                if legacy_quest:
                    heirloom["history"].append({
                        "day": world_obj.day,
                        "event": f"Legacy quest '{legacy_quest['name']}' bestowed upon {heir.faction}",
                    })
                    # Fire immediately if no active quest for this faction
                    if self.faction_quests.get(heir.faction) is None:
                        self.faction_quests[heir.faction] = legacy_quest
                        legacy_narrative = (
                            f"💍🏛️ HEIRLOOM LEGACY: {heirloom['name']} has witnessed {gen} generations. "
                            f"The {FACTIONS[heir.faction]['color']} {heir.faction} are called to honor its history — "
                            f"'{legacy_quest['name']}'!"
                        )
                    else:
                        legacy_narrative = (
                            f"💍🏛️ HEIRLOOM LEGACY: {heirloom['name']} whispers of a new calling — "
                            f"'{legacy_quest['name']}' awaits when the current {heir.faction} quest concludes."
                        )
                        # Queue the legacy quest
                        if not hasattr(self, '_pending_legacy_quests'):
                            self._pending_legacy_quests = {}
                        self._pending_legacy_quests[heir.faction] = legacy_quest
                    kingdom.kingdom_log.append(legacy_narrative)
                    heirloom["history"].append({
                        "day": world_obj.day,
                        "event": f"Legacy quest: {legacy_narrative}",
                    })

        heir.heirloom = heirloom
        deceased.heirloom = None

        # Apply bonus (with generation scaling)
        if heirloom["bonus_type"] == "morale":
            heir.morale = min(100, heir.morale + heirloom["bonus_value"])
        elif heirloom["bonus_type"] == "combat":
            heir.combat_skill = min(100, heir.combat_skill + heirloom["bonus_value"])

        heir.remember(f"Inherited the {heirloom['name']} from {deceased.name} (gen {heirloom['generations']})")
        narrative = (
            f"💍 HEIRLOOM PASSED: {heirloom['name']} passes from {deceased.name} "
            f"to {heir.name} — '{heirloom['origin']}' [generation {heirloom['generations']}]"
        )
        kingdom.kingdom_log.append(narrative)

        return {
            "heirloom_name": heirloom["name"],
            "from": deceased.name,
            "to": heir.name,
            "bonus_type": heirloom["bonus_type"],
            "bonus_value": heirloom["bonus_value"],
            "narrative": narrative,
        }

    def _generate_heirloom_legacy_quest(self, heirloom, heir, world_obj=None):
        """Generate a special faction quest inspired by an ancient heirloom's history.
        Called when an heirloom reaches generation 7 ('the Ancient') or 10 ('the Eternal').
        Returns a quest dict or None."""
        if world_obj is None:
            world_obj = world

        faction = heir.faction
        if not faction:
            return None

        gen = heirloom["generations"]
        creator = heirloom.get("creator", "an ancestor")
        origin = heirloom.get("origin", "lost to time")
        history_entries = heirloom.get("history", [])

        # Build a narrative from heirloom history
        history_snippets = [h["event"] for h in history_entries[-3:]] if history_entries else ["its long journey"]

        if gen >= 10:
            # "The Eternal" — a mythic quest to forge a new legend
            quest_templates = [
                {
                    "type": "eternal_forge",
                    "name": f"Forge the Eternal Legacy of {heirloom['name']}",
                    "desc": f"After ten generations, {heirloom['name']} demands a legend worthy of eternity. Gather the kingdom's finest to craft a new chapter.",
                    "target": {"gold": 50, "stone": 40, "food": 30},
                    "reward_morale": 15,
                    "reward_resources": {"gold": 40, "stone": 25},
                    "narrative_complete": f"The Eternal Legacy of {heirloom['name']} is forged! Songs will be sung for generations — the heirloom's story now belongs to all of Ashfall.",
                    "bonus_effect": "eternal_legacy",
                },
                {
                    "type": "eternal_shrine",
                    "name": f"Build the Shrine of {heirloom['name']}",
                    "desc": f"An heirloom of ten generations deserves a place of honor. Build a shrine where its story can inspire all who visit.",
                    "target": {"stone": 55, "wood": 35, "gold": 30},
                    "reward_morale": 12,
                    "reward_resources": {"stone": 20, "gold": 30},
                    "narrative_complete": f"The Shrine of {heirloom['name']} stands as a beacon. Every citizen who visits feels the weight of history — and the hope of tomorrow.",
                    "bonus_effect": "shrine_blessing",
                },
            ]
        else:
            # Gen 7 — "the Ancient" — recover lost history
            quest_templates = [
                {
                    "type": "ancient_recovery",
                    "name": f"Recover the Lost History of {heirloom['name']}",
                    "desc": f"This ancient heirloom, first held by {creator}, holds secrets yet untold. Delve into the archives and the land to recover its lost stories.",
                    "target": {"gold": 30, "food": 25},
                    "reward_morale": 10,
                    "reward_resources": {"gold": 25},
                    "narrative_complete": f"The lost history of {heirloom['name']} is recovered! Ancient tales of {creator} and their descendants now enrich the kingdom's lore.",
                    "bonus_effect": "lore_recovery",
                },
                {
                    "type": "ancient_pilgrimage",
                    "name": f"Pilgrimage of {heirloom['name']}",
                    "desc": f"Seven generations have held {heirloom['name']}. Organize a pilgrimage to retrace its journey through Ashfall's history.",
                    "target": {"food": 30, "gold": 20, "wood": 15},
                    "reward_morale": 10,
                    "reward_resources": {"food": 15, "gold": 15},
                    "narrative_complete": f"The Pilgrimage of {heirloom['name']} traced seven generations across Ashfall. Every stop told a story — the kingdom's soul is richer for it.",
                    "bonus_effect": "pilgrimage_morale",
                },
            ]

        template = random.choice(quest_templates)

        # Scale with kingdom age tier
        age_tier, age_mult, tier_name = self._get_kingdom_age_tier(world_obj)

        scaled_target = {}
        for resource, base in template["target"].items():
            scaled_target[resource] = max(1, int(base * age_mult))

        scaled_rewards = {}
        for resource, base in template["reward_resources"].items():
            scaled_rewards[resource] = max(1, int(base * age_mult))

        quest = {
            "faction": faction,
            "type": template["type"],
            "name": template["name"],
            "desc": template["desc"],
            "target": scaled_target,
            "progress": {r: 0 for r in scaled_target},
            "reward_morale": max(1, int(template["reward_morale"] * age_mult)),
            "reward_resources": scaled_rewards,
            "narrative_complete": template["narrative_complete"],
            "bonus_effect": template.get("bonus_effect"),
            "rarity": "chain",
            "chain_from": "heirloom_legacy",
            "start_day": world_obj.day,
            "deadline": world_obj.day + 75,
            "completed": False,
            "failed": False,
            "age_tier": age_tier,
            "tier_name": tier_name,
            "heirloom_name": heirloom["name"],
            "is_legacy": True,
        }

        return quest

    def _check_pending_legacy_quests(self):
        """Check if any faction has finished their current quest and a legacy quest is waiting.
        Called from _update_faction_quest_progress. Returns list of events."""
        if not hasattr(self, '_pending_legacy_quests') or not self._pending_legacy_quests:
            return []

        events = []
        for faction, legacy_quest in list(self._pending_legacy_quests.items()):
            if self.faction_quests.get(faction) is None:
                # Slot is free — fire the legacy quest
                self.faction_quests[faction] = legacy_quest
                narrative = (
                    f"💍🏛️ HEIRLOOM LEGACY BEGINS: The {FACTIONS[faction]['color']} {faction} "
                    f"now undertake '{legacy_quest['name']}' — a quest born from {legacy_quest.get('heirloom_name', 'an ancient heirloom')}!"
                )
                kingdom.kingdom_log.append(narrative)
                events.append({"faction": faction, "quest": legacy_quest["name"], "narrative": narrative})
                del self._pending_legacy_quests[faction]

        return events

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

        # ── Mastery inheritance: children of masters get a head start ──
        if inherited.get("role_bias"):
            for parent in child.parents:
                if not parent.alive:
                    continue
                if parent.role == inherited["role_bias"] and parent.mastery_level >= 3:
                    # Expert (L3) parent → child starts as Apprentice (L1)
                    # Master (L4) parent → child starts as Apprentice with head start toward L2
                    child.mastery_level = 1
                    child.days_in_role = 0
                    child.apprenticed_under = parent.name
                    if parent.mastery_level >= 4:
                        child.days_in_role = 15  # halfway to Journeyman
                        child.remember(
                            f"Inherited mastery training from {parent.mastery_title()} {parent.name} "
                            f"— starts as Apprentice {child.role} with a head start"
                        )
                        inherited["mastery_inheritance"] = {
                            "from": parent.name,
                            "parent_level": parent.mastery_level,
                            "start_level": 1,
                            "head_start_days": 15,
                        }
                    else:
                        child.remember(
                            f"Inherited trade knowledge from {parent.mastery_title()} {parent.name} "
                            f"— starts as Apprentice {child.role}"
                        )
                        inherited["mastery_inheritance"] = {
                            "from": parent.name,
                            "parent_level": parent.mastery_level,
                            "start_level": 1,
                            "head_start_days": 0,
                        }
                    break  # only inherit from the first qualifying parent

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
            # Apply elder's wisdom mentoring boost (Tales to Tell, etc.)
            mentor_bonus = elder.wisdom_mentoring_boost(world_obj)
            wisdom_boost += mentor_bonus
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

    # ── ROLE MASTERY (SKILL TREES) ──────────────────────────

    def _check_role_mastery(self, world_obj=None):
        """Check each citizen for mastery advancement based on days_in_role.
        Returns a list of promotion events."""
        if world_obj is None:
            world_obj = world

        events = []
        for c in self.citizens:
            if not c.alive:
                continue
            if c.role in ("child",):
                continue

            # Check if citizen qualifies for the next level
            next_level = c.mastery_level + 1
            if next_level > 4:
                continue

            threshold = MASTERY_THRESHOLDS.get(next_level, 999)
            if c.days_in_role >= threshold:
                old_title = c.mastery_title()
                c.mastery_level = next_level
                new_title = c.mastery_title()
                desc = c.mastery_description()

                # Morale boost on promotion
                boost = {1: 3, 2: 4, 3: 5, 4: 8}.get(next_level, 3)
                c.morale = min(100, c.morale + boost)
                c.remember(f"Achieved rank of {new_title} {c.role} (mastery {next_level})")

                # ── Heirloom story: mastery achievements add to heirloom history ──
                if c.heirloom and "history" in c.heirloom:
                    story = ""
                    if next_level == 3:
                        story = f"While bearing {c.heirloom['name']}, {c.name} became an Expert {c.role}"
                    elif next_level == 4:
                        story = f"{c.heirloom['name']} witnessed {c.name} ascend to Master {c.role}"
                    if story:
                        c.heirloom["history"].append({"day": world_obj.day, "event": story})

                # Narrative event
                narrative = (
                    f"⭐ MASTERY: {c.name} has become a {new_title} {c.role}! "
                    f"({old_title} → {new_title}, +{boost} morale)"
                )
                if desc:
                    narrative += f" — {desc}"

                events.append({
                    "citizen": c.name,
                    "role": c.role,
                    "old_level": next_level - 1,
                    "new_level": next_level,
                    "old_title": old_title,
                    "new_title": new_title,
                    "morale_boost": boost,
                    "description": desc,
                    "narrative": narrative,
                })

                kingdom.kingdom_log.append(narrative)

                # Master-level milestone: first master in each role
                if next_level == 4:
                    existing_masters = sum(
                        1 for ct in self.citizens
                        if ct.alive and ct.role == c.role and ct.mastery_level >= 4 and ct is not c
                    )
                    if existing_masters == 0:
                        milestone_narrative = (
                            f"🏆 FIRST MASTER: {c.name} is the first {c.role} to reach "
                            f"the rank of Master in Ashfall! The kingdom celebrates this achievement."
                        )
                        kingdom.kingdom_log.append(milestone_narrative)
                        # Kingdom-wide morale boost
                        for ct in self.citizens:
                            if ct.alive and ct is not c:
                                ct.morale = min(100, ct.morale + 2)
                        events[-1]["first_master"] = True
                        events[-1]["milestone"] = milestone_narrative

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

        # Inter-family relations: marriage creates an alliance
        fam_a = a.family_name()
        fam_b = best.family_name()
        self._update_family_relations(fam_a, fam_b, +20,
                                       f"marriage of {a.name} & {best.name}")

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

        # ── Active Faction Quests ──
        active_quests = {f: q for f, q in self.faction_quests.items() if q is not None and not q.get("completed") and not q.get("failed")}
        if active_quests:
            lines.append("─── 📜 Active Faction Quests ───")
            for faction, quest in active_quests.items():
                color = FACTIONS[faction]["color"]
                rarity = quest.get("rarity", "common")
                rarity_badge = {"chain": "🔗", "rare": "✨", "common": "📋"}.get(rarity, "")
                chain_from = quest.get("chain_from", "")
                chain_note = f" (follows: {chain_from})" if chain_from else ""
                age_tier = quest.get("age_tier", 1)
                tier_name = quest.get("tier_name", "Early")
                tier_badge = {1: "🌱", 2: "🌿", 3: "🌳", 4: "🏛️"}.get(age_tier, "")
                progress_parts = []
                for res, prog in quest["progress"].items():
                    needed = quest["target"].get(res, 1)
                    pct = min(100, int(prog / needed * 100)) if needed > 0 else 0
                    res_icon = {"food": "🍞", "wood": "🪵", "stone": "🪨", "gold": "💰"}.get(res, res)
                    progress_parts.append(f"{res_icon} {int(prog)}/{int(needed)} ({pct}%)")
                days_left = max(0, quest.get("deadline", 0) - world.day)
                rarity_label = f" {rarity_badge} {rarity.upper()}" if rarity != "common" else ""
                lines.append(f"  {color} {faction}: '{quest['name']}'{rarity_label}{chain_note} {tier_badge}T{age_tier} — {quest['desc']}")
                lines.append(f"    Progress: {' | '.join(progress_parts)}  ⏳ {days_left}d remaining")
            lines.append("")

        # ── Quest History ──
        if self.faction_quest_history:
            recent = self.faction_quest_history[-5:]
            lines.append("─── 📋 Recent Quest History ───")
            for entry in recent:
                outcome_icon = "✅" if entry["outcome"] == "completed" else "❌"
                rarity = entry.get("rarity", "common")
                rarity_badge = {"chain": "🔗", "rare": "✨", "common": ""}.get(rarity, "")
                chain_from = entry.get("chain_from", "")
                chain_note = f" → chain from '{chain_from}'" if chain_from else ""
                age_tier = entry.get("age_tier", 1)
                tier_badge = {1: "🌱", 2: "🌿", 3: "🌳", 4: "🏛️"}.get(age_tier, "")
                lines.append(f"  {rarity_badge} {tier_badge} {outcome_icon} {entry['faction']}: '{entry['name']}' ({entry['outcome']}, day {entry['resolved_day']}){chain_note}")
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

        # ── Inter-Family Relations ──
        if self.family_relations:
            alliances = [(k, v) for k, v in self.family_relations.items() if v >= 40]
            rivalries = [(k, v) for k, v in self.family_relations.items() if v <= -40]
            if alliances or rivalries:
                lines.append("")
                lines.append("─── 🤝⚡ Family Relations ───")
                if alliances:
                    lines.append("  Alliances:")
                    for (fa, fb), score in sorted(alliances, key=lambda x: -x[1])[:5]:
                        lines.append(f"    {fa} ↔ {fb}  (+{score})")
                if rivalries:
                    lines.append("  Rivalries:")
                    for (fa, fb), score in sorted(rivalries, key=lambda x: x[1])[:5]:
                        lines.append(f"    {fa} ↔ {fb}  ({score})")
        lines.append("")

        # ── Role Mastery (Skill Trees) ──
        masters = [c for c in self.citizens if c.alive and c.mastery_level >= 3]
        if masters:
            lines.append("─── ⭐ Role Masters ───")
            for c in sorted(masters, key=lambda x: (-x.mastery_level, x.role)):
                desc = c.mastery_description()
                apprentice_note = ""
                if c.apprenticed_under:
                    # Check if parent is still alive
                    parent_alive = any(p.name == c.apprenticed_under and p.alive for p in self.citizens)
                    status = "" if parent_alive else " (deceased)"
                    apprentice_note = f" [apprenticed under {c.apprenticed_under}{status}]"
                lines.append(f"  {c.mastery_title()} {c.role}: {c.name} (lvl {c.mastery_level}, {c.days_in_role}d in role){apprentice_note}")
                if desc:
                    lines.append(f"    ↳ {desc}")
            lines.append("")

        # Apprentices: show citizens with mastery inheritance who aren't yet masters
        apprentices = [c for c in self.citizens if c.alive and c.apprenticed_under and c.mastery_level < 3]
        if apprentices:
            lines.append("─── 🎓 Apprentices (Inherited Mastery) ───")
            for c in sorted(apprentices, key=lambda x: (-x.mastery_level, x.role)):
                parent_alive = any(p.name == c.apprenticed_under and p.alive for p in self.citizens)
                status = "" if parent_alive else " (mentor deceased)"
                lines.append(f"  {c.mastery_title()} {c.role}: {c.name} — apprenticed under {c.apprenticed_under}{status}")
            lines.append("")

        # Mastery summary
        mastery_counts = {}
        for c in self.citizens:
            if c.alive and c.mastery_level >= 1:
                key = c.mastery_title()
                mastery_counts[key] = mastery_counts.get(key, 0) + 1
        if mastery_counts:
            parts = ", ".join(f"{title}s: {count}" for title, count in sorted(mastery_counts.items()))
            lines.append(f"  Mastery: {parts}")
            lines.append("")

        # ── Family Heirlooms ──
        if self.family_heirlooms:
            lines.append("─── 💍 Family Heirlooms ───")
            for h in self.family_heirlooms[-10:]:
                holder = h.get("holder", "unknown")
                holder_alive = any(c.name == holder and c.alive for c in self.citizens)
                status = "" if holder_alive else " [holder deceased]"
                gen = h.get("generations", 1)
                gen_str = f" (gen {gen})" if gen > 1 else ""
                bonus_str = f" [+{h.get('bonus_value', 0)} {h.get('bonus_type', '')}]"
                # Show production bonus with generation scaling
                prod_info = ""
                prod_bonus = h.get("production_bonus", {})
                if prod_bonus.get("resources"):
                    base_prod = h.get("base_prod_res", prod_bonus.get("resources", {}))
                    gen_scale = min((gen - 1) // 2, 3)
                    scaled_parts = []
                    for res, base in base_prod.items():
                        scaled = base + gen_scale
                        scaled_parts.append(f"+{scaled} {res}")
                    if scaled_parts:
                        prod_info = f" [work: {', '.join(scaled_parts)}]"
                        if gen_scale > 0:
                            prod_info += f" (gen-scaled +{gen_scale})"
                lines.append(f"  {h['name']}{gen_str} — held by {holder}{status}{bonus_str}{prod_info}")
                lines.append(f"    ↳ {h['origin']}")
                # Show recent history
                history = h.get("history", [])
                if len(history) > 2:
                    recent = history[-2:]
                    for entry in recent:
                        lines.append(f"      · {entry['event']}")
            lines.append("")

            # ── Inter-Heirloom Synergy ──
            # Show when multiple heirloom holders share a role
            role_heirloom_holders = {}
            for c in self.citizens:
                if c.alive and c.heirloom and c.role not in ("child", "elder",):
                    hb = c.heirloom.get("production_bonus", {})
                    if c.role in hb.get("roles", []):
                        role_heirloom_holders.setdefault(c.role, []).append(c)
            synergy_roles = {r: holders for r, holders in role_heirloom_holders.items() if len(holders) >= 2}
            if synergy_roles:
                lines.append("─── 🔗 Inter-Heirloom Synergy ───")
                for role, holders in sorted(synergy_roles.items()):
                    synergy = len(holders) - 1  # +1 per fellow holder
                    names = ", ".join(f"{c.name} [{c.heirloom.get('name','?')}]" for c in holders)
                    lines.append(f"  {role}: {len(holders)} heirloom holders — each gains +{synergy} to production")
                    lines.append(f"    ↳ {names}")
                lines.append("")

        # ── Faction Relics ──
        if hasattr(self, '_faction_relics') and self._faction_relics:
            lines.append("─── 🏺 Faction Relics ───")
            for relic in self._faction_relics:
                color = FACTIONS[relic["faction"]].get("color", "")
                prod_roles = relic.get("prod_roles", [])
                prod_res = relic.get("prod_resources", {})
                prod_str = ", ".join(f"+{v} {k}" for k, v in prod_res.items()) if prod_res else "none"
                lines.append(
                    f"  🏺 {relic['heirloom_name']} (gen {relic['generation']}) — "
                    f"relic of the {color} {relic['faction']}"
                )
                lines.append(f"    ↳ Held by {relic['holder']} | Work bonus: {prod_str} for {', '.join(prod_roles) if prod_roles else 'all'} | +1 morale floor to all faction members")
                lines.append(f"    ↳ {relic['origin']}")
                # Show last ritual if one has been performed
                last_ritual = relic.get("_last_ritual_day", 0)
                if last_ritual > 0:
                    days_since_ritual = world.day - last_ritual
                    lines.append(f"    ↳ 🕯️ Last ritual: {days_since_ritual}d ago | Next: ~{max(0, 30 - days_since_ritual)}-{max(0, 50 - days_since_ritual)}d")
            lines.append("")

        # ── Wisdom Traits (Memory Condensation) ──
        wise_citizens = [c for c in self.citizens if c.alive and c.wisdom_traits]
        if wise_citizens:
            lines.append("─── 🧠 Wisdom Traits ───")
            for c in sorted(wise_citizens, key=lambda x: -len(x.wisdom_traits))[:8]:
                trait_names = ", ".join(t["name"] for t in c.wisdom_traits)
                trait_effects = []
                for t in c.wisdom_traits:
                    icon = {"morale_floor": "🛡️", "seasonal_morale": "🌿", "disease_resist": "💊", "mentoring_boost": "📖", "work_bonus": "🔧"}.get(t["effect"], "✨")
                    trait_effects.append(f"{icon}{t['name']}")
                # Show heirloom resonance if applicable
                resonance = ""
                if c.heirloom:
                    mult = c._heirloom_wisdom_multiplier()
                    if mult > 1.0:
                        resonance = f" [heirloom resonance: {mult:.0%}]"
                # Show synergy bonus
                synergy_bonus = getattr(c, '_wisdom_synergy', {})
                syn_note = ""
                if synergy_bonus:
                    syn_traits = [f"{t}={v}" for t, v in synergy_bonus.items()]
                    syn_note = f" 🤝synergy({', '.join(syn_traits)})"
                # Show seasonal awakening
                season_note = ""
                if world_obj:
                    season = getattr(world_obj, 'season', 'spring')
                    awakened = [t["name"] for t in c.wisdom_traits
                               if c._WISDOM_SEASONAL_AWAKENING.get(t["name"]) == season]
                    if awakened:
                        season_icons = {"spring": "🌸", "summer": "☀️", "autumn": "🍂", "winter": "❄️"}
                        icon = season_icons.get(season, "")
                        season_note = f" {icon}{season}-awakened({', '.join(awakened)})"
                lines.append(f"  {c.name} ({c.role}, age {int(c.age)}): {', '.join(trait_effects)}{resonance}{syn_note}{season_note}")
            lines.append("")

        # ── Wisdom Trait Synergy ──
        trait_groups = {}
        for c in self.citizens:
            if not c.alive or not c.wisdom_traits:
                continue
            for t in c.wisdom_traits:
                trait_groups.setdefault(t["name"], []).append(c.name)
        synergy_groups = {t: names for t, names in trait_groups.items() if len(names) >= 2}
        if synergy_groups:
            lines.append("─── 🤝 Wisdom Synergy ───")
            for trait_name, names in sorted(synergy_groups.items(), key=lambda x: -len(x[1])):
                effect_icon = {"morale_floor": "🛡️", "seasonal_morale": "🌿", "disease_resist": "💊", "mentoring_boost": "📖", "work_bonus": "🔧"}.get(
                    trait_groups.get(trait_name, [""])[0] if False else "", "✨")
                lines.append(f"  '{trait_name}': {len(names)} citizens share this trait — each gains +{len(names)} to effect")
                lines.append(f"    ↳ {', '.join(names[:6])}{' +' + str(len(names)-6) + ' more' if len(names) > 6 else ''}")
            lines.append("")

        # ── Faction Wisdom Council ──
        council_info = []
        for faction in FACTIONS:
            wise = [c for c in self.citizens if c.alive and c.faction == faction and c.wisdom_traits]
            if len(wise) >= 3:
                council_info.append((faction, len(wise), wise))
        if council_info:
            lines.append("─── 🏛️ Faction Wisdom Councils ───")
            for faction, size, wise in sorted(council_info, key=lambda x: -x[1]):
                morale_bonus = 1 if size >= 3 else 0
                if size >= 6: morale_bonus = 2
                if size >= 9: morale_bonus = 3
                wise_names = ", ".join(c.name for c in wise[:4])
                if size > 4:
                    wise_names += f" +{size-4} more"
                lines.append(f"  {FACTIONS[faction]['color']} {faction}: {size} wise members — +{morale_bonus} daily morale, +{size}% disease resist")
                lines.append(f"    ↳ {wise_names}")
            lines.append("")

        # ── Dream-Bonds ──
        bonded_citizens = [c for c in self.citizens if c.alive and c.dream_bonds]
        if bonded_citizens:
            lines.append("─── 🌊💞 Dream-Bonds ───")
            shown_pairs = set()
            for c in bonded_citizens:
                for bonded_name in c.dream_bonds:
                    pair = tuple(sorted([c.name, bonded_name]))
                    if pair in shown_pairs:
                        continue
                    shown_pairs.add(pair)
                    bonded = next((ct for ct in self.citizens if ct.name == bonded_name), None)
                    bonded_alive = bonded.alive if bonded else False
                    status = "" if bonded_alive else " (deceased)"
                    lines.append(f"  {c.name} ↔ {bonded_name}{status} — bound by shared deep-resonance dreams")
            lines.append("")

        # ── Trade Pacts ──
        if hasattr(self, '_active_trade_pacts') and self._active_trade_pacts:
            lines.append("─── 🤝📜 Trade Pacts ───")
            for pact in self._active_trade_pacts:
                days_left = max(0, pact["expires_day"] - world.day)
                color1 = FACTIONS[pact["faction_a"]].get("color", "")
                color2 = FACTIONS[pact["faction_b"]].get("color", "")
                lines.append(
                    f"  {color1} {pact['faction_a']} ↔ {color2} {pact['faction_b']}: "
                    f"+{pact['daily_gold']}g, +{pact['daily_food']}f daily "
                    f"({days_left}d remaining)"
                )
            lines.append("")

        # ── Permanent Alliances ──
        if hasattr(self, '_permanent_alliances') and self._permanent_alliances:
            lines.append("─── 🤝♾️ Permanent Alliances ───")
            for alliance in self._permanent_alliances:
                days_since = world.day - alliance["formed_day"]
                color1 = FACTIONS[alliance["faction_a"]].get("color", "")
                color2 = FACTIONS[alliance["faction_b"]].get("color", "")
                joint_quest_info = ""
                # Check if there's an active joint quest for these factions
                pair_key = tuple(sorted([alliance["faction_a"], alliance["faction_b"]]))
                if hasattr(self, '_alliance_joint_quests'):
                    last_joint = self._alliance_joint_quests.get(pair_key, 0)
                    if last_joint > 0:
                        days_since_joint = world.day - last_joint
                        if days_since_joint < 75:  # quest still active or recently completed
                            # Check if quest is still active
                            q1 = self.faction_quests.get(alliance["faction_a"])
                            if q1 and q1.get("type") == "alliance_joint" and not q1.get("completed") and not q1.get("failed"):
                                joint_quest_info = f" | ⚔️ Joint quest active: '{q1['name']}' ({days_since_joint}d)"
                            else:
                                joint_quest_info = f" | ⚔️ Last joint quest: {days_since_joint}d ago"
                lines.append(
                    f"  {color1} {alliance['faction_a']} ↔ {color2} {alliance['faction_b']}: "
                    f"+{alliance['daily_gold']}g, +{alliance['daily_food']}f daily "
                    f"(forged {days_since}d ago, permanent) — quest progress shared 10%{joint_quest_info}"
                )
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


