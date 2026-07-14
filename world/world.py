"""
World of Ashfall -- terrain, exploration, events, and mystery.
Imports from kingdom.py. Built by Bex.
"""

import random
from kingdom import kingdom


# ── TERRAIN TYPES ───────────────────────────────────────────────
# Each terrain has a description, resource yields, and event odds.
# unlock_condition: if set, must be met before the region can be discovered.
# landmark: a secret revealed on deep exploration.

TERRAIN = {
    "the_vale": {
        "desc": "A sheltered green valley cupped by low hills, laced with berry thickets and wild grain.",
        "yields": {"food": 5, "wood": 2, "stone": 0, "gold": 0},
        "event_chance": 0.15,
        "danger": "low",
        "unlock_condition": None,
        "landmark": "The Whispering Spring — a crystal pool that reflects the sky even on cloudy days. Elders say it grants true dreams.",
    },
    "old_oak_ridge": {
        "desc": "A spine of ancient oaks crowning a windy ridge; the oldest trees remember the world before.",
        "yields": {"food": 1, "wood": 8, "stone": 3, "gold": 0},
        "event_chance": 0.25,
        "danger": "medium",
        "unlock_condition": None,
        "landmark": "The Eldertrunk — an oak so vast a dozen people could stand inside its hollow. Carvings on its walls predate the kingdom.",
    },
    "glimmer_marsh": {
        "desc": "Murky wetlands where swamp-gas flickers blue at dusk. Strange herbs grow in the shallows.",
        "yields": {"food": 3, "wood": 1, "stone": 0, "gold": 2},
        "event_chance": 0.40,
        "danger": "medium",
        "unlock_condition": None,
        "landmark": "The Drowned Cairn — a stone structure half-sunk in bog. When the marsh-gas ignites, symbols glow along its walls.",
        "notes": "Rumored to hide will-o'-wisps and something older.",
    },
    "ironroot_depths": {
        "desc": "A dark hollow where iron-rich roots pierce exposed cliff faces. Promising — if you can brave it.",
        "yields": {"food": 0, "wood": 2, "stone": 6, "gold": 3},
        "event_chance": 0.35,
        "danger": "high",
        "unlock_condition": None,
        "landmark": "The Sealed Door — a slab of black stone set into the deepest cliff. Runes pulse faintly when touched. It has not been opened.",
        "notes": "Prospectors whisper of a sealed door set into the cliff.",
    },
    "sunfire_plains": {
        "desc": "Wide, golden grasslands stretching to the horizon, dotted with wildflowers and grazing herds.",
        "yields": {"food": 7, "wood": 0, "stone": 1, "gold": 1},
        "event_chance": 0.20,
        "danger": "low",
        "unlock_condition": None,
        "landmark": "The Sunspire — a natural obelisk of white stone that catches the dawn light and glows like a beacon.",
    },
    "the_ashen_copse": {
        "desc": "A petrified forest, trees frozen mid-burn from some ancient cataclysm. Ashfall's namesake.",
        "yields": {"food": 0, "wood": 4, "stone": 5, "gold": 4},
        "event_chance": 0.50,
        "danger": "high",
        # 🔒 HIDDEN: only discoverable after a specific event fires
        "unlock_condition": "ashen_vision",
        "landmark": "The Sleeper's Hollow — a depression in the warm earth where the ground rises and falls as if breathing. Something vast rests below.",
        "notes": "The ground is still warm. Something sleeps beneath.",
    },
    "the_sunken_sanctum": {
        "desc": "A vast subterranean chamber lit by bioluminescent crystals, hidden beneath the roots of the world. The air hums with old magic.",
        "yields": {"food": 2, "wood": 0, "stone": 8, "gold": 8},
        "event_chance": 0.55,
        "danger": "high",
        # 🔒 SECRET: only discoverable after all lore stories are unveiled
        "unlock_condition": "all_lore_unveiled",
        "landmark": "The Heart-Pool — a circular basin of liquid light at the sanctum's center. It reflects not your face, but your oldest memory. Drinking from it grants a fragment of the Sleeper's own recollection.",
        "notes": "The walls are carved with the history of the Sleepers from beginning to... an ending that has not yet come.",
    },
}

# ── CREATURES ──────────────────────────────────────────────────
# Each region has its own fauna, spirits, and anomalies.
# Encounters returned by creature_encounter() are stubs for future combat.
# Fields:
#   danger: low/medium/high — relative threat
#   type:  beast/spirit/anomaly — category
#   signs: list of ambient clues that hint at the creature's presence
#   encounter: narrative template when directly encountered
#   stakes: dict of resource gains/losses for a "neutral" outcome (avoid/bargain)
#   combat_stakes: dict for a "fight" outcome (higher risk, higher reward)
#   special: any unique behavior note

CREATURES = {
    "the_vale": [
        {
            "name": "Shadow-Fox",
            "danger": "low",
            "type": "beast",
            "signs": [
                "Tiny pawprints circle the grain stores, but nothing is missing — yet.",
                "A flash of silver fur at the edge of torchlight. Gone before you can blink.",
                "Chickens are restless. Something has been watching the coop.",
            ],
            "encounter": "A shadow-fox, silver as starlight, stares at you from atop the granary roof. It cocks its head — curious, not afraid.",
            "stakes": {"food": -1, "gold": 2},  # steals a little, but its pelt is valuable if traded
            "combat_stakes": {"food": 0, "gold": 5},  # pelt + no theft
            "special": "If fed voluntarily (lose 2 food), it may return with a gift (+5 gold later).",
        },
        {
            "name": "Thorn-Bear",
            "danger": "medium",
            "type": "beast",
            "signs": [
                "Deep claw-marks on an old hawthorn. The sap is still wet.",
                "A bee-tree has been torn open. Honey drips into the grass.",
                "Something large crushed a fence on the eastern edge of the vale.",
            ],
            "encounter": "A thorn-bear, shaggy and scarred, rises onto its hind legs. It snorts — a warning, not a charge. It wants the berry thicket you're standing near.",
            "stakes": {"food": -3, "gold": 3},  # lose berries, but bear fur catches a price
            "combat_stakes": {"food": 8, "gold": 6, "pop": -1},  # bear meat + pelt, but risky
            "special": "Can be scared off with fire (requires wood). If avoided, it moves on after 2 days.",
        },
        {
            "name": "Vale-Stag",
            "danger": "low",
            "type": "beast",
            "signs": [
                "A single antler tine, shed by the spring, gleams in the grass.",
                "Hoofprints by the Whispering Spring at dawn — as if it came to drink.",
            ],
            "encounter": "A white stag, antlers tangled with flowering vines, stands at the Whispering Spring. It meets your eyes with ancient calm, then bounds away.",
            "stakes": {"food": 3, "gold": 2},  # blessing: food appears, pilgrims come
            "combat_stakes": {"food": 10, "gold": 0, "lore": "Killing the white stag brings a curse — the Whispering Spring runs murky for a season."},
            "special": "Seeing it is an omen of good fortune. Harming it angers the wildwalkers.",
        },
    ],
    "old_oak_ridge": [
        {
            "name": "Ridge-Wolf Pack",
            "danger": "medium",
            "type": "beast",
            "signs": [
                "Howls echo from three directions at once. They're coordinating.",
                "A half-eaten deer carcass, still warm, drags marks leading toward the oaks.",
                "Scouts report yellow eyes watching from the treeline — always just beyond bowshot.",
            ],
            "encounter": "Three ridge-wolves fan out around your party, silent as smoke. The lead wolf's eyes hold a strange intelligence — it's weighing whether you're prey or threat.",
            "stakes": {"food": -4, "gold": 3},  # they take food, but wolf pelts
            "combat_stakes": {"food": 6, "gold": 8, "pop": -1},  # wolf meat + pelts, but dangerous
            "special": "If you have 2+ scouts, can be tracked to their den for +8 gold (old kills, trinkets).",
        },
        {
            "name": "Oak-Wyrm",
            "danger": "medium",
            "type": "beast",
            "signs": [
                "A woodcutter's axe bounced off bark that moved. He swears the tree hissed.",
                "Shed carapace — segmented, dark amber — curls around an oak root like a bracelet.",
                "Something inside the Eldertrunk ticked. Not a bird. Not a beetle. Ticked.",
            ],
            "encounter": "An oak-wyrm — a centipede the length of your arm — uncoils from a crevice in the ancient bark. Its mandibles drip with amber venom.",
            "stakes": {"wood": -2, "gold": 4},  # avoided, but the tree is damaged; venom sacs are valuable
            "combat_stakes": {"wood": 2, "gold": 8, "pop": -1},  # venom sacs + cleared tree, but venom is deadly
            "special": "Venom can be harvested by herbalists (+6 gold if herbalist in kingdom).",
        },
        {
            "name": "Eldertrunk Guardian",
            "danger": "low",
            "type": "spirit",
            "signs": [
                "The Eldertrunk's hollow hums — a low, resonant note that vibrates in your chest.",
                "Carvings on the inner walls seem to shift when you're not looking directly at them.",
            ],
            "encounter": "A figure of knotted wood and green light steps from the Eldertrunk's hollow. It speaks without words, asking: Why have you come to the old places?",
            "stakes": {"food": 0, "gold": 0},  # no cost to answer
            "combat_stakes": {},  # cannot be fought
            "special": "Answer truthfully (via narrative choice stub) and gain +5 gold and a lore fragment. Answer with greed and lose -3 gold.",
        },
    ],
    "glimmer_marsh": [
        {
            "name": "Bog-Wisp",
            "danger": "medium",
            "type": "spirit",
            "signs": [
                "A blue flame bobs over the marsh at dusk, then splits into three. They're circling something.",
                "A scout followed a wisp last night and woke up knee-deep in bog-water, facing the wrong direction.",
            ],
            "encounter": "A bog-wisp — blue flame with no heat — hovers at eye level. It pulses, beckoning toward deeper marsh. The Drowned Cairn glows faintly in that direction.",
            "stakes": {"food": -2, "gold": 4},  # lost time and supplies, but wisps sometimes lead to treasures
            "combat_stakes": {},  # cannot be fought conventionally
            "special": "Following the wisp has 50% chance of +8 gold (cairn treasure) or -4 food (lost in marsh for a day).",
        },
        {
            "name": "Marsh-Drake",
            "danger": "medium",
            "type": "beast",
            "signs": [
                "Ripples spread across still water — but there's no wind, no frog, no bird.",
                "A duckweed mat is torn from below. Whatever did it was bigger than a man.",
                "Marsh-herbs on a floating island have been flattened in a spiral pattern.",
            ],
            "encounter": "A marsh-drake — a broad-snouted reptile caked in mud and duckweed — erupts from the shallows. It's between you and the causeway.",
            "stakes": {"food": -3, "gold": 3},  # it takes your catch, but drake scales are prized
            "combat_stakes": {"food": 12, "gold": 10, "pop": -1},  # drake meat feeds many, scales are armor-quality
            "special": "Marsh-drake scales can be fashioned into armor (+2 defense if kingdom has a market).",
        },
        {
            "name": "Reed-Walker",
            "danger": "low",
            "type": "anomaly",
            "signs": [
                "Reeds are woven into shapes — crude figures, spirals, a doorframe standing alone in the bog.",
                "A scout sees a tall, thin figure at the marsh edge at dawn. When they approach, it's just reeds. But the reeds weren't arranged like that before.",
            ],
            "encounter": "A figure woven entirely of living reeds rises from the bog. It tilts its head — there's no face, but you feel seen. It extends a hand holding a lacquered box.",
            "stakes": {"food": 0, "gold": 5},  # gift: the box contains ancient coins
            "combat_stakes": {},  # cannot be fought — it dissolves into reeds
            "special": "The reed-walker may be the marsh itself, or something older. The box sometimes contains a lore fragment instead of gold.",
        },
    ],
    "ironroot_depths": [
        {
            "name": "Deep-Tunnel Crawler",
            "danger": "high",
            "type": "beast",
            "signs": [
                "A miner's lantern catches movement at the tunnel's end — something pale, many-legged, and silent.",
                "Tools left at the seam are found arranged in a semicircle. Teeth marks on the handles.",
                "A low chittering echoes from a shaft thought to be exhausted.",
            ],
            "encounter": "A crawler — blind, albino, the size of a pony — skitters across the tunnel ceiling. It's been following your lantern light for the last hour.",
            "stakes": {"stone": -4, "gold": 3},  # it steals shiny stones, but its shed carapace is valuable
            "combat_stakes": {"stone": 6, "gold": 12, "pop": -2},  # carapace + cleared tunnel, but very dangerous
            "special": "Sensitive to light — carrying torches reduces danger. Its carapace can be crafted into shields.",
        },
        {
            "name": "Rust-Ghoul",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "Iron tools left overnight are coated in red dust by morning. The metal is pitted, as if rusted for years.",
                "A miner's iron ration tin dissolved into fine powder. The food inside was untouched.",
                "Red handprints — child-sized — on the tunnel wall. They weren't there yesterday.",
            ],
            "encounter": "A child-shaped figure of swirling rust and iron dust coalesces from the tunnel air. It reaches toward your pickaxe with something like hunger.",
            "stakes": {"stone": -2, "gold": 4},  # it eats some iron-rich stone, leaves behind concentrated ore
            "combat_stakes": {},  # cannot be fought with metal weapons — they dissolve
            "special": "Repelled by pure gold (costs 2 gold to drive off safely). Leaves behind +8 stone in concentrated ore if appeased.",
        },
        {
            "name": "Sentinel of the Sealed Door",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "The Sealed Door's runes glow faintly. The air is thick with a hum just below hearing.",
                "Shadows near the Door move against the light. They're too tall. Too thin.",
            ],
            "encounter": "A figure of absolute darkness detaches from the Sealed Door. It has no features — only the outline of something vast compressed into human shape. It does not move toward you. It simply waits.",
            "stakes": {"food": 0, "gold": 0},  # no direct cost — the sentinel does not attack unless provoked
            "combat_stakes": {},  # cannot be fought — it is the Door's will
            "special": "Only appears if ashen_vision has been triggered. If approached with respect, grants a lore fragment. If attacked, the Door seals permanently (ironroot_depths yields halved).",
        },
        {
            "name": "Gloom-Lantern",
            "danger": "medium",
            "type": "anomaly",
            "signs": [
                "A soft, greenish glow pulses from a side-tunnel that was dark yesterday.",
                "Miners report feeling... watched. Not threatened. Just watched. And oddly at peace.",
                "A fungal growth on the tunnel wall beats like a heart — slow, hypnotic. It's warm to the touch.",
            ],
            "encounter": "A cluster of phosphorescent fungi — each the size of a fist — pulses in the darkness. The light is hypnotic. You feel your feet carrying you closer without your consent.",
            "stakes": {"food": -1, "gold": 6},  # time lost to hypnosis, but harvested spores are prized by herbalists
            "combat_stakes": {"gold": 10, "pop": -1},  # destroying it releases a spore cloud — valuable but potentially lethal
            "special": "Herbalists can harvest safely for +6 gold. If ignored, it spreads — every 7 days, a second lantern appears in another discovered region's creature pool.",
        },
        {
            "name": "Vein-Lurker",
            "danger": "medium",
            "type": "beast",
            "signs": [
                "A prospector's hammer is missing. The pick beside it has tooth marks — wide, flat, made for crushing.",
                "An iron vein has been... licked clean. The stone around it is scored with something like a radula.",
                "A low grinding sound echoes from the deep — stone on stone, or something sharpening itself.",
            ],
            "encounter": "A creature like a cross between a pangolin and a crocodile uncurls from an iron-rich seam. Its scales are flecked with rust and its tongue tests the air for the scent of metal — or blood.",
            "stakes": {"stone": -3, "gold": 5},  # it eats the iron-rich stone you wanted, but its shed scales are valuable
            "combat_stakes": {"stone": 8, "gold": 12, "pop": -1},  # scales + cleared deposit, but armored and aggressive
            "special": "Scales can be crafted into rust-proof armor. If defeated, the iron vein it guarded yields double stone for 3 days.",
        },
    ],
    "sunfire_plains": [
        {
            "name": "Plains-Lion Pride",
            "danger": "medium",
            "type": "beast",
            "signs": [
                "The herds are skittish. They smell cat.",
                "A lioness watches from the golden grass — only her tail-tip twitching gives her away.",
                "Pawprints the size of dinner plates circle the camp. They came close last night.",
            ],
            "encounter": "Three lionesses melt out of the grass, forming a loose semicircle. The pride male is somewhere behind them — you can hear his breath.",
            "stakes": {"food": -5, "gold": 4},  # they take from herds/scouts, but lion pelts fetch a price
            "combat_stakes": {"food": 10, "gold": 14, "pop": -2},  # lion meat + pelts, but pride fights to the death
            "special": "Can be driven off with fire or loud noise. If avoided, they respect your territory and don't return for 14 days.",
        },
        {
            "name": "Sunfire Stallion",
            "danger": "low",
            "type": "beast",
            "signs": [
                "Hoofprints that gleam gold in sunlight — the earth itself is warmed where the stallion passed.",
                "A distant neigh echoes across the plains, and every wild horse in sight turns toward it.",
            ],
            "encounter": "A stallion with a coat like burnished copper canters across the plains. Its mane streams like liquid flame in the sunlight. It watches you with calm, intelligent eyes.",
            "stakes": {"food": 0, "gold": 8},  # it allows approach — shed mane-hairs are worth gold
            "combat_stakes": {},  # too fast to fight; it simply runs
            "special": "If not threatened, may return with its herd. Scouts mounted on tamed plains-horses can explore twice as fast (future integration).",
        },
        {
            "name": "Dust-Devil",
            "danger": "low",
            "type": "spirit",
            "signs": [
                "A column of dust spins in place on a windless day. It almost looks like it's dancing.",
                "Small stones and flower petals orbit a point in the air for a heartbeat, then drop.",
            ],
            "encounter": "A dust-devil — a playful vortex of wind and grass — spins around your party, tugging at cloaks and scattering supplies. It makes a sound almost like laughter.",
            "stakes": {"food": -1, "gold": 2},  # scattered supplies, but some lost coins are swept up too
            "combat_stakes": {},  # cannot be fought — it's wind
            "special": "Harmless unless angered. If respected, it sometimes drops interesting things it's picked up (+3 gold).",
        },
    ],
    "the_ashen_copse": [
        {
            "name": "Ash-Wraith",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "A heat-shimmer hangs over the petrified trees, but the air is cold.",
                "Footprints appear in the ash — leading toward the Sleeper's Hollow, but no one made them.",
                "A scout's breath fogs in warm air. Something cold is nearby.",
            ],
            "encounter": "A shape of ash and frozen fire coalesces between the petrified trees. It wears the face of someone you know — but made of embers and regret.",
            "stakes": {"food": -1, "gold": 3},  # drains warmth, but leaves behind crystallized ash
            "combat_stakes": {"gold": 8, "pop": -1},  # destroying it releases rare vitrified fragments
            "special": "Ash-wraiths are echoes of those who died in the Cataclysm. They cannot be permanently killed — only dispersed. Herbalists can ward them off.",
        },
        {
            "name": "Sleeper's Dream",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "You feel drowsy near the Hollow. Not tired — drowsy, like a half-remembered lullaby.",
                "Two scouts had the same dream last night: a voice vast and slow, speaking a language of warmth.",
            ],
            "encounter": "The ground beneath your feet rises and falls. Once. Twice. The warmth seeps into your bones and your thoughts slow. A vast presence stirs at the edge of consciousness — not hostile, but so large that even its curiosity could crush you.",
            "stakes": {"food": 0, "gold": 0},  # no direct resource change
            "combat_stakes": {},  # cannot be fought — it's a psychic phenomenon
            "special": "Those who experience the Dream gain +1 permanent morale (they feel chosen) but the scout is incapacitated for 1 day. Sometimes grants lore fragments.",
        },
        {
            "name": "Petrified Guardian",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "One of the petrified trees has... moved. It was three paces to the left yesterday.",
                "Stone limbs — too many joints — protrude from the ash at the edge of the Hollow.",
            ],
            "encounter": "A creature of petrified wood and cooled magma pulls itself from the ash. It has no head — only a central cavity where orange light pulses like a heartbeat. It stands between you and the Hollow.",
            "stakes": {"food": 0, "gold": 0},  # it doesn't want resources — it wants you to leave
            "combat_stakes": {"stone": 12, "gold": 15, "pop": -3},  # defeating it yields immense resources but is extremely dangerous
            "special": "Only appears when the Sleeper is agitated (triggered by too much activity in the copse). Can be pacified by a citizen with ash-grey eyes (future integration).",
        },
        {
            "name": "Ember-Husk",
            "danger": "medium",
            "type": "beast",
            "signs": [
                "A patch of ash shifts — not from wind. Something underneath is breathing.",
                "The outline of a deer — but made of compressed ash and cooling ember — stands motionless at the treeline. Then it crumbles.",
                "Scouts find scorched hoofprints that end abruptly at a wall of petrified wood. No prints lead away.",
            ],
            "encounter": "A creature shaped like a stag but formed entirely of compacted ash and dying embers rises from the copse floor. Its antlers crackle with residual heat. It doesn't charge — it watches, and in its hollow eye-sockets, something orange flickers.",
            "stakes": {"wood": 2, "gold": 4},  # it sheds ancient charcoal as it moves — valuable, but unnerving
            "combat_stakes": {"wood": 6, "gold": 8, "pop": -1},  # destroying it releases a burst of trapped heat + rare ember-core
            "special": "These are the echoes of animals caught in the Cataclysm — not truly alive, not truly dead. If left in peace, they sometimes lead scouts to hidden caches (+5 gold).",
        },
        {
            "name": "Ash-Bloom",
            "danger": "low",
            "type": "anomaly",
            "signs": [
                "A single flower — crystalline, pale grey, impossibly delicate — grows from a crack in a petrified trunk.",
                "The air around the bloom smells of honey and burnt cedar. Insects avoid it.",
                "A scout who touched a bloom last week now dreams exclusively in shades of grey. They say it's peaceful.",
            ],
            "encounter": "You find it at the base of a frozen tree: a flower made of crystallized ash, its petals translucent and faintly warm. As you approach, it chimes — a single, pure note that hangs in the air.",
            "stakes": {"food": 0, "gold": 12},  # colossal value — collectors and scholars will pay fortunes for an intact bloom
            "combat_stakes": {},  # cannot be fought — it's a flower. Destroying it yields nothing and angers the copse.
            "special": "Extremely rare. Only appears after the ashen_vision and only when the Sleeper stirs (world_omens firing). Picking it grants +12 gold but the bloom never regrows in that spot. Some say each bloom is a Sleeper's memory.",
        },
    ],
    "the_sunken_sanctum": [
        {
            "name": "Crystal-Serpent",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "A trail of crystallized scales glitters across the sanctum floor — each one sings a single, sustained note when touched.",
                "Something long and luminous coils around a crystal pillar, then vanishes when you look directly at it.",
                "The hum in the air grows louder near the Heart-Pool. It resolves into... a melody? Something is singing.",
            ],
            "encounter": "A serpent of living crystal, each scale a prism catching light that has never seen the sun, uncoils from the Heart-Pool. It has no eyes — but it sees you. Its voice is the sound of glass bells: YOU HAVE COME FAR. ASK.",
            "stakes": {"gold": 15, "lore": "The Crystal-Serpent is not a guardian — it is a librarian. Each scale holds a memory the Sleepers chose to preserve."},
            "combat_stakes": {"gold": 30, "stone": 20, "pop": -4},
            "special": "If the kingdom has unveiled all lore stories, the serpent bows and grants +25 gold and a permanent blessing (+1 gold/day from sanctum resonance). Combat with it is ill-advised — it is older than the Cataclysm.",
        },
        {
            "name": "Echo-Warden",
            "danger": "medium",
            "type": "spirit",
            "signs": [
                "Your own footsteps echo back... from the wrong direction.",
                "A figure in robes of woven light stands at the edge of your torchlight. When you raise the torch, it is gone.",
                "Carved on a wall: a procession of figures, each one identical, walking into the Heart-Pool. Only one walks out.",
            ],
            "encounter": "The Echo-Warden steps out of a wall carving and into reality. It wears the face of someone you know — a citizen of Ashfall, but older, wiser. It speaks with their voice: 'You are not supposed to be here yet. But you are welcome.'",
            "stakes": {"gold": 8, "lore": "The Wardens are echoes of futures that might be. Each is a citizen of Ashfall who, in some timeline, found the sanctum and chose to stay and guard it."},
            "combat_stakes": {},
            "special": "Cannot be fought — it is not wholly present. If bargained with, it may teach a random citizen a skill (+1 permanent role effectiveness).",
        },
        {
            "name": "Memory-Wisp",
            "danger": "low",
            "type": "spirit",
            "signs": [
                "A floating sphere of pale golden light drifts past, and suddenly you remember your sixth birthday — vividly, perfectly.",
                "Dozens of tiny lights hover over the Heart-Pool like stars over water. Each one hums a different, half-familiar tune.",
            ],
            "encounter": "A wisp of pure memory — not a ghost, but a thought given form — floats up to you. It shows you a scene: the First Fire, walking. It shows you the Sleeper, dreaming. It shows you the Cataclysm. And then it shows you something that hasn't happened yet.",
            "stakes": {"gold": 3, "lore": "The wisps are the Sleeper's dreams, condensed. Each one is a story that was told before language existed."},
            "combat_stakes": {},
            "special": "Collecting 3 or more Memory-Wisp lore fragments unlocks a bonus lore story: 'The Unwritten Future.'",
        },
    ],
}

# ── RUMOR HINTS ────────────────────────────────────────────────
# These are whispered hints pointing toward undiscovered regions.
# Used by the rumors() method and during exploration.

RUMOR_POOL = {
    "glimmer_marsh": [
        "Blue lights dance over the marshlands east of the vale at dusk. The herbalist wants to investigate.",
        "A trapper swears he saw will-o'-wisps bobbing over the bog — and heard something large breathing beneath the duckweed.",
        "Strange herbs that only grow in marsh-water have appeared in the market. The merchant won't say where they came from.",
    ],
    "ironroot_depths": [
        "A prospector found iron-rich stone in a stream bed. The source must be somewhere in the dark hollows to the north.",
        "Miners tell tales of a cliff-face threaded with roots that bleed rust. They call it the Ironroot.",
        "Something sealed behind black stone. The elders won't speak of it, but the deepwardens are organizing an expedition.",
    ],
    "sunfire_plains": [
        "Beyond the ridge, the trees thin out into endless golden grassland. Herds of wild cattle roam there.",
        "A travelling merchant speaks of a white obelisk on the plains that catches the dawn like a beacon.",
    ],
    "the_ashen_copse": [
        "Sometimes, in dreams, the folk of Ashfall see a forest of frozen fire. They wake tasting ash.",
        "The ground is warm in a place where no sun reaches. Something sleeps there. Something old.",
    ],
}


# ── WORLD STATE ─────────────────────────────────────────────────


# ── LAIRS ──────────────────────────────────────────────────────
# Each region hides a creature lair - the den, nest, or sanctum of
# its most dangerous or mysterious creature. Lairs are discovered
# during deep_scout (15% chance) and can be challenged for major
# rewards. Once cleared, a lair yields ongoing passive benefits.

LAIRS = {
    "the_vale": {
        "name": "Thorn-Bear's Hollow",
        "boss": "Thorn-Bear",
        "danger": "medium",
        "discovery": "Deep in the vale's hawthorn thicket, a cave mouth yawns - claw-marked stone, the reek of honey and musk. This is the Thorn-Bear's lair.",
        "encounter": "The Thorn-Bear rises from its bed of crushed berries and shed fur. This is its home, and it will not flee. It roars - the sound shakes loose stones from the ceiling.",
        "stakes": {"food": 6, "gold": 8},
        "combat_stakes": {"food": 14, "gold": 15, "pop": -2},
        "cleared_bonus": "The hollow becomes a safe berry-gathering ground. +1 food/day passively.",
        "special": "If you have a herbalist, can be pacified with a sleep-draught (costs 2 herbs, safe clear).",
    },
    "old_oak_ridge": {
        "name": "Ridge-Wolf Lair",
        "boss": "Ridge-Wolf Pack",
        "danger": "medium",
        "discovery": "A cleft in the ridge opens into a shallow cave. Bones - deer, boar, and older, stranger things - litter the entrance. Yellow eyes watch from the dark.",
        "encounter": "The pack leader - a she-wolf grey as stormcloud - stands over a cache of glittering oddities: coins, a bent sword, a child's silver locket. She does not growl. She waits.",
        "stakes": {"food": 4, "gold": 12},
        "combat_stakes": {"food": 10, "gold": 18, "pop": -2},
        "cleared_bonus": "Ridge-wolves no longer harass livestock. Passive +1 food/day.",
        "special": "If you have 2+ scouts, can bait the pack away with 3 food, clear lair safely for partial rewards (+8 gold, no casualties).",
    },
    "glimmer_marsh": {
        "name": "Bog-Wisp Mire",
        "boss": "Bog-Wisp",
        "danger": "high",
        "discovery": "At the heart of the marsh, the ground gives way to black, still water. Lights - dozens of bog-wisps - orbit a single point: a cairn-stone pulsing with cold blue fire.",
        "encounter": "The wisps converge into a single blinding point above the cairn. A voice - many voices, old as the bog - speaks without sound: WHY HAVE YOU COME TO THE DROWNING PLACE?",
        "stakes": {"gold": 8, "lore": "The bog-wisps are the souls of marsh-drowned. They do not hunger - they remember."},
        "combat_stakes": {},
        "cleared_bonus": "The cairn stabilizes. Glimmer_marsh yields +15% permanently (stacks with marsh_revelation).",
        "special": "Can only be 'cleared' by answering the wisps' question truthfully. A citizen with 60+ morale can speak for the kingdom (auto-success). Otherwise 50% chance.",
    },
    "ironroot_depths": {
        "name": "Gloom-Lantern Spore-Vault",
        "boss": "Gloom-Lantern",
        "danger": "high",
        "discovery": "A vast natural chamber opens beyond a collapsed wall. The ceiling glitters with thousands of glow-lanterns - a false starfield. At the center, a single lantern the size of a boulder pulses. Slowly.",
        "encounter": "The mother lantern's pulse synchronizes with your heartbeat. It knows you're here. Spores drift from its gills like green snow, and every breath tastes of honey and forgetting.",
        "stakes": {"gold": 15, "food": -2},
        "combat_stakes": {"gold": 25, "pop": -3},
        "cleared_bonus": "Gloom-Lanterns stop spreading. All existing lanterns wither. +2 gold/day from spore harvest.",
        "special": "If all 6 regions are infected by Gloom-Lanterns before the lair is cleared, a 'Gloom-Saturation' event triggers (special narrative + large resource shift).",
    },
    "sunfire_plains": {
        "name": "Dust-Devil Mesa",
        "boss": "Dust-Devil",
        "danger": "low",
        "discovery": "A flat-topped mesa rises from the grasslands. At its summit, the wind never stops. Whirlwinds dance in place - dozens of them - spinning around a central pillar of carved white stone.",
        "encounter": "The largest dust-devil peels away from the pillar. It has a shape now - vaguely human, arms of spinning sand. It beckons you toward the pillar with a sound like wind chimes.",
        "stakes": {"gold": 10, "lore": "The pillar is a wind-shrine left by a people older than the Cataclysm. They spoke to the air and it answered."},
        "combat_stakes": {},
        "cleared_bonus": "The mesa's wind-spirits become friendly. +1 gold/day, scouts travel faster across sunfire_plains.",
        "special": "The dust-devils want to play. If you bring an offering (5 food left at the pillar), they dance for three days - +15 gold from windfall seeds and trinkets they gather.",
    },
    "the_ashen_copse": {
        "name": "Ash-Wraith Convergence",
        "boss": "Ash-Wraith",
        "danger": "high",
        "discovery": "In a hollow ring of petrified trees, the ash swirls against the wind. Faces form and dissolve in the eddies - dozens of them, mouths open in silent cries. This is where the wraiths are born.",
        "encounter": "The wraiths coalesce into a single figure - tall, cold, wearing the face of someone you knew but cannot name. It reaches toward you. The air freezes. 'Remember us,' it whispers. 'We died so the Sleeper could dream.'",
        "stakes": {"gold": 12, "lore": "The wraiths are the echoes of those who lay down in the ashes during the Cataclysm. They gave their warmth to keep the Sleeper alive."},
        "combat_stakes": {"gold": 20, "pop": -3},
        "cleared_bonus": "The wraiths find peace. Ash-wraith encounters cease in the_ashen_copse. +3 gold/day from crystallized ash harvesting.",
        "special": "If the_ashen_copse has an Ash-Bloom active, the wraiths are calmer - auto-success on bargain. Herbalists can perform a Rite of Remembering (costs 3 herbs) to clear the lair without combat.",
    },
    "the_sunken_sanctum": {
        "name": "Heart-Pool Nexus",
        "boss": "Crystal-Serpent",
        "danger": "high",
        "discovery": "The Heart-Pool at the sanctum's center pulses with a rhythm that matches no living heart. The Crystal-Serpent is coiled around it — protective, ancient, and waiting for the question it has been asked to guard against.",
        "encounter": "The Crystal-Serpent rises to its full height — twenty feet of living prism. Every scale reflects a different world that might have been. Its voice is calm: 'Only those who know the full story may pass. Tell me: what woke the Sleeper in the north?'",
        "stakes": {"gold": 25, "lore": "The serpent shares the oldest memory: the Sleeper beneath the copse did not choose to stay. It was asked. By the first settlers. And the pact was: we remember you, and you sleep. We forget you, and you wake."},
        "combat_stakes": {"gold": 40, "stone": 25, "pop": -5},
        "cleared_bonus": "The Heart-Pool stabilizes into a permanent font of ancient knowledge. +5 gold/day, +2 stone/day, and all future lore fragments collected count as double.",
        "special": "If all 4 lore stories have been unveiled before challenging, the serpent yields without a fight — granting full rewards and the cleared bonus immediately.",
    },
}


# ── REGION DISASTERS ───────────────────────────────────────────────
# Each region has a unique disaster type with narrative and effects.
# chance: base % per day (modified by danger and season)
# recovery_day: days until the region recovers
# special: unique behavior on recovery

DISASTERS = {
    "the_vale": {
        "name": "Thornblight",
        "chance": 0.03,
        "narrative": (
            "THORNBLIGHT: A creeping grey mold spreads through the berry thickets "
            "of the_vale. The fruit withers before it ripens. Herbalists burn the "
            "affected bushes, but the blight has already claimed this season's yield."
        ),
        "effects": {"food": -8},
        "recovery_day": 5,
        "recovery_msg": (
            "The herbalists say the thornblight has run its course. "
            "New green shoots are already appearing among the thorns."
        ),
    },
    "old_oak_ridge": {
        "name": "Ridge-Fire",
        "chance": 0.03,
        "narrative": (
            "RIDGE-FIRE: Lightning strikes the dry canopy of old_oak_ridge! "
            "A crown fire races along the ridgeline. Woodcutters and scouts fight "
            "it with green branches and sand. They contain it, but not before "
            "the flames devour acres of ancient woodland."
        ),
        "effects": {"wood": -12, "food": -3},
        "recovery_day": 7,
        "recovery_msg": (
            "The ridge-fire has passed. Charred oaks stand like black sentinels, "
            "but woodcutters are already harvesting salvageable timber from the burn zone."
        ),
    },
    "glimmer_marsh": {
        "name": "Marsh-Fog",
        "chance": 0.04,
        "narrative": (
            "MARSH-FOG: A dense, luminous fog rolls out of glimmer_marsh before dawn. "
            "Thicker than any in living memory. Foragers out before first light "
            "have not returned. The fog smells faintly of honey and rot."
        ),
        "effects": {"pop": -1, "food": -3},
        "recovery_day": 3,
        "recovery_msg": (
            "The marsh-fog has lifted. The missing foragers stumble back, dazed but "
            "unharmed, muttering about blue lights that spoke in circles. "
            "One carries a curious relic they found in the haze."
        ),
        "special": "fog_discovery",
    },
    "ironroot_depths": {
        "name": "Cave-in",
        "chance": 0.04,
        "narrative": (
            "CAVE-IN: A thunderous rumble echoes from ironroot_depths. "
            "A gallery collapse has trapped miners underground. The rescue takes "
            "all night. Most are pulled out alive, but some are lost to the deep stone."
        ),
        "effects": {"pop": -2, "stone": 15, "gold": 8},
        "recovery_day": 6,
        "recovery_msg": (
            "The collapsed gallery has been shored up. The new vein revealed by "
            "the cave-in is rich. Miners are already bringing up high-grade ore."
        ),
        "special": "reveals_vein",
    },
    "sunfire_plains": {
        "name": "Wildfire",
        "chance": 0.03,
        "narrative": (
            "WILDFIRE: A wall of flame sweeps across the sunfire_plains. Grass fire, "
            "fast and hungry. The herds scatter and the wildflower meadows are reduced "
            "to ash. The fire passes as quickly as it came."
        ),
        "effects": {"food": -6, "wood": -4},
        "recovery_day": 5,
        "recovery_msg": (
            "Green shoots push through the ash on the sunfire_plains. "
            "The plains will bloom again, richer than before."
        ),
        "special": "fertility_boost",
    },
    "the_ashen_copse": {
        "name": "Ash-Storm",
        "chance": 0.05,
        "narrative": (
            "ASH-STORM: The ashen copse exhales. A choking cloud of grey ash rolls "
            "across the kingdom. The sky goes dark at noon. Citizens scramble indoors. "
            "The ash coats everything: crops, roofs, lungs."
        ),
        "effects": {"food": -5, "pop": -1, "gold": -8},
        "recovery_day": 4,
        "recovery_msg": (
            "The ash-storm has passed. Citizens sweep roofs and clear gutters. "
            "Herbalists brew lung-cleansing tea from glimmer_marsh herbs. Life resumes."
        ),
        "special": "vision_chance",
    },
    "the_sunken_sanctum": {
        "name": "Crystal-Shatter",
        "chance": 0.04,
        "narrative": (
            "CRYSTAL-SHATTER: A harmonic resonance builds in the sanctum — "
            "the crystals are singing too loudly. The vibration shatters several "
            "pillars, sending razor-sharp shards through the chamber. "
            "The Heart-Pool dims for the first time in memory."
        ),
        "effects": {"stone": -10, "gold": -10, "pop": -1},
        "recovery_day": 5,
        "recovery_msg": (
            "The crystals have stopped resonating. New growth is already visible — "
            "the sanctum heals itself, slowly. The Heart-Pool brightens. "
            "Scouts report the shattered shards can be collected: +8 stone recovered."
        ),
        "special": "crystal_recovery",
    },
}

class World:
    def __init__(self):
        self.discovered = set(kingdom.territory)
        self.day = 0
        self.season = "spring"
        self.weather = "clear"
        self.world_log = []
        self.unlock_flags = set()        # e.g., "ashen_vision", "marsh_revelation"
        self.exploration_bonuses = {}    # region -> True once deep-scouted
        self.regions_explored_today = []  # reset each day
        self.lore_fragments = []        # collected lore fragments (str), feed unveil_lore()
        self.lore_revealed = []         # lore stories already unveiled
        self._omen_cache_day = -1       # day of cached omen
        self._omen_cache = None        # cached omen result
        self._gloom_lantern_day = 0    # day Gloom-Lantern was last encountered/ignored
        self._gloom_lantern_regions = set()  # regions currently hosting a Gloom-Lantern
        self._shadow_fox_fed_day = 0   # day Shadow-Fox was last fed
        self._shadow_fox_gift_pending = False  # whether a return gift is expected
        self._shadow_fox_return_day = 5   # days until shadow-fox returns with gift
        self._discovered_lairs = {}    # region -> lair name (discovered lairs)
        self._cleared_lairs = set()     # regions where lair has been cleared
        self._active_disasters = {}     # region -> {"name", "day_struck", "recovery_day"}
        self._disaster_cooldown = {}    # region -> day until next disaster possible
        self._sunfire_fertility = False  # wildfire fertility boost active

    # ── DISCOVERY ────────────────────────────────────────────

    def can_discover(self, region):
        """Check if a region is eligible for discovery (unlock conditions met)."""
        if region not in TERRAIN:
            return False
        cond = TERRAIN[region].get("unlock_condition")
        if cond is None:
            return True
        return cond in self.unlock_flags

    def discover(self, region):
        """Attempt to discover a new region. Returns True if successful."""
        if region in self.discovered:
            return False
        if self.can_discover(region):
            self.discovered.add(region)
            kingdom.territory.append(region)
            msg = f"New territory discovered: {region} — {TERRAIN[region]['desc']}"
            self.world_log.append(msg)
            return True
        return False

    # ── RUMORS ───────────────────────────────────────────────

    def rumors(self):
        """Return a list of rumor strings hinting at undiscovered regions."""
        hints = []
        for region, rumor_list in RUMOR_POOL.items():
            if region in self.discovered:
                continue
            if not self.can_discover(region):
                continue
            hints.append(random.choice(rumor_list))
        random.shuffle(hints)
        return hints

    # ── HARVEST ──────────────────────────────────────────────

    def harvest(self, region):
        """Collect daily resources from a region. Returns dict of yields."""
        if region not in self.discovered:
            return {}
        base = TERRAIN[region]["yields"].copy()
        # Apply exploration bonus if deep-scouted
        if region in self.exploration_bonuses:
            for k in base:
                base[k] = int(base[k] * 1.25)
        # Apply marsh_revelation boost to glimmer_marsh
        if region == "glimmer_marsh" and "marsh_revelation" in self.unlock_flags:
            for k in base:
                base[k] = int(base[k] * 1.5)

        # Bonus from sunfire_plains wildfire fertility (one-time)
        if region == "sunfire_plains" and self._sunfire_fertility:
            for k in base:
                base[k] = int(base[k] * 1.30)
            self._sunfire_fertility = False

        # Bonus from cleared lair (Bog-Wisp Mire)
        if region == "glimmer_marsh" and "glimmer_marsh" in self._cleared_lairs:
            for k in base:
                base[k] = int(base[k] * 1.15)
        # Apply disaster penalties (70% yield reduction during active disaster)
        if region in self._active_disasters:
            for k in base:
                base[k] = int(base[k] * 0.3)

        # Apply season modifiers
        season_mod = 1.0
        if self.season == "spring":
            season_mod = 1.2
        elif self.season == "summer":
            season_mod = 1.0
        elif self.season == "autumn":
            season_mod = 0.8
        elif self.season == "winter":
            season_mod = 0.5
        for k in base:
            base[k] = max(0, int(base[k] * season_mod))
        # Apply weather modifiers
        if self.weather == "rain":
            base["food"] = int(base.get("food", 0) * 1.15)
        elif self.weather == "drought":
            base["food"] = int(base.get("food", 0) * 0.7)
        elif self.weather == "storm":
            for k in base:
                base[k] = int(base[k] * 0.85)
        # Add to kingdom resources
        for resource, amount in base.items():
            if resource == "food":
                kingdom.food += amount
            elif resource == "wood":
                kingdom.wood += amount
            elif resource == "stone":
                kingdom.stone += amount
            elif resource == "gold":
                kingdom.gold += amount
        return base

    # ── RANDOM EVENTS ────────────────────────────────────────

    def random_event(self, region=None):
        """Roll for and apply a random event. Returns the event dict or None."""
        if region is None:
            region = random.choice(list(self.discovered)) if self.discovered else "the_vale"
        if region not in self.discovered:
            return None
        danger = TERRAIN[region]["danger"]
        event_chance = TERRAIN[region]["event_chance"]
        if random.random() < event_chance:
            event = generate_event(region, danger, self)
            apply_event(event, self)
            self.world_log.append(f"Event in {region}: {event.get('narrative', '')}")
            return event
        return None

    # ── DAY CYCLE ────────────────────────────────────────────

    def advance_day(self):
        """Advance the world by one day."""
        self.day += 1
        self.regions_explored_today = []
        # Season progression (simple: ~30 days per season)
        day_in_year = self.day % 120
        if day_in_year < 30:
            self.season = "spring"
        elif day_in_year < 60:
            self.season = "summer"
        elif day_in_year < 90:
            self.season = "autumn"
        else:
            self.season = "winter"
        # Weather roll
        roll = random.random()
        if self.season == "winter":
            if roll < 0.15:
                self.weather = "storm"
            elif roll < 0.35:
                self.weather = "snow"
            else:
                self.weather = "clear"
        elif self.season == "summer":
            if roll < 0.10:
                self.weather = "drought"
            elif roll < 0.25:
                self.weather = "rain"
            else:
                self.weather = "clear"
        else:
            if roll < 0.15:
                self.weather = "rain"
            elif roll < 0.20:
                self.weather = "storm"
            else:
                self.weather = "clear"
        # Harvest from all discovered regions
        for region in list(self.discovered):
            self.harvest(region)
        # Check creature special behaviors (spread, return gifts)
        self._check_creature_specials()

        # Check lair activity (passive effects, gloom-saturation)
        self._check_lair_activity()

        # Check for region-specific disasters
        self._check_disasters()

        # Log the day
        self.world_log.append(f"Day {self.day}: {self.season}, {self.weather}")
        return {"day": self.day, "season": self.season, "weather": self.weather}

    # ── EXPLORATION ──────────────────────────────────────────

    def explore(self):
        """Attempt to discover a random eligible region. Returns region name or None."""
        candidates = [r for r in TERRAIN if self.can_discover(r) and r not in self.discovered]
        if not candidates:
            self.world_log.append("No unexplored regions within reach.")
            return None
        # Bias toward regions with rumors
        weights = [2.0 if r in RUMOR_POOL else 1.0 for r in candidates]
        target = random.choices(candidates, weights=weights, k=1)[0]
        cost = {"food": 3, "gold": 1}
        if kingdom.food >= cost["food"] and kingdom.gold >= cost["gold"]:
            kingdom.food -= cost["food"]
            kingdom.gold -= cost["gold"]
            success = self.discover(target)
            if success:
                yield_base = TERRAIN[target].get("yields", {})
                discovery_msg = f"Explorers discovered {target}! Initial survey yields: {yield_base}"
                # Sprinkle in creature signs for flavor
                if target in CREATURES:
                    sign = self._creature_signs(target)
                    if sign and random.random() < 0.50:
                        discovery_msg += f" {sign['sign']}"
                self.world_log.append(discovery_msg)
                # Chance of creature encounter on first discovery
                if target in CREATURES and random.random() < 0.30:
                    encounter = self.creature_encounter(target)
                    if encounter:
                        self.world_log.append(
                            f"🐾 During exploration: {encounter['narrative'][:80]}..."
                        )
                        # Auto-avoid on first contact
                        self.resolve_creature_encounter(encounter, "avoid")
                return target
        else:
            self.world_log.append("Not enough resources to fund an expedition.")
        return None

    def deep_scout(self, region):
        """Deep-scout a discovered region. Reveals landmark, boosts yields. Costs resources."""
        if region not in self.discovered:
            self.world_log.append(f"Cannot deep-scout {region}: not yet discovered.")
            return None
        if region in self.exploration_bonuses:
            self.world_log.append(f"{region} has already been deep-scouted.")
            return None
        # Cost scales with danger
        danger = TERRAIN[region]["danger"]
        costs = {"low": {"food": 2, "gold": 2}, "medium": {"food": 3, "gold": 4}, "high": {"food": 5, "gold": 6}}
        cost = costs.get(danger, {"food": 3, "gold": 3})
        if kingdom.food < cost["food"] or kingdom.gold < cost["gold"]:
            self.world_log.append(f"Not enough resources to deep-scout {region}.")
            return None
        kingdom.food -= cost["food"]
        kingdom.gold -= cost["gold"]
        self.exploration_bonuses[region] = True
        landmark = TERRAIN[region].get("landmark", "a hidden wonder.")
        self.world_log.append(f"Deep-scouted {region}: discovered {landmark}")
        # Check for special triggers
        if region == "ironroot_depths":
            self.trigger_ashen_vision()
        elif region == "glimmer_marsh":
            self.trigger_marsh_revelation()
        # One-time resource bonus
        bonus = {"food": 2, "gold": 3}
        kingdom.food += bonus["food"]
        kingdom.gold += bonus["gold"]

        # Lair discovery - small chance of finding a creature lair
        if region in LAIRS and region not in self._discovered_lairs and random.random() < 0.15:
            lair = LAIRS[region]
            self._discovered_lairs[region] = lair["name"]
            self.world_log.append(
                f"LAIR DISCOVERED: {lair['name']} in {region}! {lair['discovery']}"
            )


        # Creature encounter on deep-scout — you're going deeper into the wilds
        if region in CREATURES and random.random() < 0.40:
            encounter = self.creature_encounter(region)
            if encounter:
                self.world_log.append(
                    f"🐾 While deep-scouting {region}: {encounter['narrative'][:80]}..."
                )
                # Auto-resolve: fight if low danger and we're strong, otherwise avoid
                if encounter["danger"] == "low" and kingdom.defense_rating() >= 30:
                    action = random.choice(["fight", "avoid"])
                elif encounter["ctype"] == "anomaly":
                    action = random.choice(["bargain", "avoid"])
                else:
                    action = "avoid"
                result = self.resolve_creature_encounter(encounter, action)
                if action == "fight":
                    self.world_log.append(f"⚔️ Scouts fought off the {encounter['creature_name']}!")
                elif action == "bargain":
                    self.world_log.append(f"🤝 Scouts parlayed with the {encounter['creature_name']}.")

        return landmark

    # ── SPECIAL TRIGGERS ─────────────────────────────────────

    def trigger_ashen_vision(self):
        """Trigger the ashen vision — reveals the_ashen_copse as discoverable."""
        if "ashen_vision" not in self.unlock_flags:
            self.unlock_flags.add("ashen_vision")
            self.world_log.append("🔥 ASHEN VISION: A scout touches the Sealed Door and sees — a forest of frozen fire, and something sleeping beneath. The way to the_ashen_copse is revealed!")
            # Also award a small one-time bonus
            kingdom.gold += 5

    def trigger_marsh_revelation(self):
        """Trigger the marsh revelation — the Drowned Cairn awakens, boosting glimmer_marsh yields."""
        if "marsh_revelation" not in self.unlock_flags:
            self.unlock_flags.add("marsh_revelation")
            self.world_log.append("💧 MARSH REVELATION: The Drowned Cairn's door grinds open. Blue light spills across the bog. Glimmer_marsh yields are permanently boosted!")
            kingdom.gold += 4

    # ── WORLD MAP ────────────────────────────────────────────

    def world_map(self):
        """Return an ASCII art map of the known world."""
        # Build a simple grid representation
        # Positions on a 5x3 grid (arbitrary but evocative)
        positions = {
            "the_vale":         (2, 1),
            "old_oak_ridge":    (3, 0),
            "glimmer_marsh":    (1, 2),
            "ironroot_depths":  (0, 1),
            "sunfire_plains":   (4, 1),
            "the_ashen_copse":  (4, 2),
            "the_sunken_sanctum": (2, 0),
        }

        symbols = {
            "the_vale":         "🌿",
            "old_oak_ridge":    "🌳",
            "glimmer_marsh":    "💧",
            "ironroot_depths":  "⛏️",
            "sunfire_plains":   "☀️",
            "the_ashen_copse":  "🔥",
            "the_sunken_sanctum": "💎",
        }

        # Build rows of the map
        rows = []
        rows.append("   ┌───────── WORLD MAP ─────────┐")
        for y in range(3):
            line = f" {y} |"
            for x in range(5):
                found = None
                for region, (px, py) in positions.items():
                    if px == x and py == y:
                        found = region
                        break
                if found:
                    sym = symbols.get(found, "?")
                    if found in self.discovered:
                        line += f" {sym} "
                    else:
                        line += " · "  # unexplored but mapped
                else:
                    line += "   "
            line += "|"
            rows.append(line)
        rows.append("   └──────────────────────────────┘")

        # Legend
        legend_lines = []
        legend_lines.append("   Legend:")
        for region, (px, py) in positions.items():
            sym = symbols.get(region, "?")
            if region in self.discovered:
                bonus = " 🔍" if region in self.exploration_bonuses else ""
                awakened = " 💧" if region == "glimmer_marsh" and "marsh_revelation" in self.unlock_flags else ""
                legend_lines.append(f"     {sym} {region} ({TERRAIN[region]['danger']}){bonus}{awakened}")
            else:
                locked = " 🔒" if not self.can_discover(region) else ""
                legend_lines.append(f"     · {region} (undiscovered){locked}")

        remaining = [r for r in TERRAIN if r not in positions.values()]
        locked = [r for r in TERRAIN if not self.can_discover(r) and r not in self.discovered]
        if remaining:
            legend_lines.append(f"  ? unexplored: {len(remaining)} region(s)")
        if locked:
            legend_lines.append(f"  🔒 locked: {len(locked)} region(s)")

        map_str = "\n".join(rows) + "\n" + "\n".join(legend_lines)
        return map_str

    # ── SCOUT REPORT ────────────────────────────────────────

    def scout_report(self):
        """Return a formatted scout intelligence report."""
        lines = []
        lines.append("")
        lines.append("╔══════════════════════════════════════╗")
        lines.append("║     🔭  SCOUT REPORT — DAY " + str(self.day).ljust(3) + "      ║")
        lines.append("╚══════════════════════════════════════╝")
        lines.append("")

        # ── Mapped Regions ──
        lines.append("─── Mapped Regions ───")
        region_order = ["the_vale", "old_oak_ridge", "glimmer_marsh",
                        "ironroot_depths", "sunfire_plains", "the_ashen_copse"]
        for region in region_order:
            t = TERRAIN[region]
            if region in self.discovered:
                deep = "🔍" if region in self.exploration_bonuses else "  "
                awakened = " 💧Cairn" if region == "glimmer_marsh" and "marsh_revelation" in self.unlock_flags else ""
                lines.append(f"  {deep} {region:<22} danger:{t['danger']:<6} ev:{t['event_chance']:.0%}{awakened}")
            elif self.can_discover(region):
                lines.append(f"     {region:<22} (undiscovered — explore!)")
            else:
                cond = t.get("unlock_condition", "???")
                lines.append(f"  🔒 {region:<22} (locked — needs: {cond})")

        # ── Active Unlocks ──
        if self.unlock_flags:
            lines.append("")
            lines.append("─── Active Unlocks ───")
            for flag in sorted(self.unlock_flags):
                if flag == "ashen_vision":
                    lines.append("  🔥 ashen_vision — the_ashen_copse discoverable")
                elif flag == "marsh_revelation":
                    lines.append("  💧 marsh_revelation — glimmer_marsh yields boosted")
                else:
                    lines.append(f"  🏴 {flag}")

        # ── Recent World Log ──
        if self.world_log:
            lines.append("")
            lines.append("─── Recent World Log ───")
            for entry in self.world_log[-5:]:
                lines.append(f"  {entry}")

        # ── Rumours ──
        rumors = self.rumors()
        if rumors:
            lines.append("")
            lines.append("─── Rumours ───")
            for r in rumors[:3]:
                lines.append(f"  🗣️ {r}")

        # ── Creature Activity ──
        creature_report = self.creature_activity()
        if creature_report and "No unusual" not in creature_report:
            lines.append("")
            lines.append(creature_report)

        lines.append("")
        return "\n".join(lines)

    # ── CHRONICLE ────────────────────────────────────────────

    def chronicle(self, limit=25):
        """Return a beautifully formatted narrative timeline of the kingdom.
        Weaves together kingdom_log and world_log, newest first."""
        lines = []
        lines.append("")
        lines.append("╔══════════════════════════════════════════════╗")
        lines.append("║        📜  CHRONICLE OF ASHFALL             ║")
        lines.append("╠══════════════════════════════════════════════╣")
        lines.append(f"║  Day {self.day} | {self.season.title().ljust(7)}| {self.weather.title().ljust(6)}" + " " * 12 + "║")
        lines.append(f"║  Regions known: {len(self.discovered)}/6  |  Pop: {kingdom.population}" + " " * 16 + "║")
        lines.append("╚══════════════════════════════════════════════╝")
        lines.append("")

        # Collect entries from both logs
        entries = []

        for entry in kingdom.kingdom_log:
            # Try to extract day from entry
            day_num = self.day
            if "Day " in entry:
                try:
                    rest = entry.split("Day ")[1]
                    day_str = rest.split(":")[0].split(" ")[0]
                    day_num = int(day_str)
                except (ValueError, IndexError):
                    pass
            entries.append(("kingdom", day_num, entry))

        for entry in self.world_log:
            if entry.startswith("Day "):
                try:
                    day_num = int(entry.split("Day ")[1].split(":")[0])
                except (ValueError, IndexError):
                    day_num = self.day
                entries.append(("world", day_num, entry))
            else:
                entries.append(("world", self.day, entry))

        # Sort by day, newest first
        entries.sort(key=lambda e: e[1], reverse=True)

        # De-duplicate and limit
        seen = set()
        unique = []
        for source, day, text in entries:
            if text not in seen and len(unique) < limit:
                seen.add(text)
                unique.append((source, day, text))

        # Render timeline
        current_day = None
        for i, (source, day, text) in enumerate(unique):
            if day != current_day:
                current_day = day
                connector = "┌" if i == 0 else "├"
                lines.append(f"  {connector}── Day {day} ──")
            symbol = "👑" if source == "kingdom" else "🌍"
            # Wrap long lines
            if len(text) > 58:
                lines.append(f"  │  {symbol} {text[:55]}...")
            else:
                lines.append(f"  │  {symbol} {text}")
        lines.append("  └" + "─" * 42)
        lines.append("")
        return "\n".join(lines)

    def kingdom_chronicle(self, limit=30):
        """Pretty-print the kingdom's event log (kingdom.kingdom_log)."""
        if not kingdom.kingdom_log:
            return "📜 The kingdom chronicle is empty — no great deeds yet recorded."
        lines = []
        lines.append("")
        lines.append("  ┌───────── 👑 KINGDOM CHRONICLE ─────────┐")
        entries = kingdom.kingdom_log[-limit:]  # newest last
        for i, entry in enumerate(entries):
            connector = "├" if i < len(entries) - 1 else "└"
            # Truncate long entries
            if len(entry) > 60:
                entry = entry[:57] + "..."
            lines.append(f"  {connector} {entry}")
        lines.append("  └" + "─" * 42)
        lines.append("")
        return "\n".join(lines)

    def collect_lore(self, fragment):
        """Add a lore fragment. Returns True if it's new."""
        if fragment not in self.lore_fragments:
            self.lore_fragments.append(fragment)
            self.world_log.append(f"📖 Lore fragment collected: {fragment[:40]}...")
            return True
        return False

    def unveil_lore(self):
        """Reveal a piece of the deeper story, based on fragments collected.
        Returns a narrative string, or None if not enough fragments."""
        # Lore stories unlock at fragment thresholds
        LORE_STORIES = [
            {
                "title": "The First Fire",
                "req": 3,
                "text": (
                    "Before Ashfall, before the vale was green, there was the First Fire. "
                    "Not a flame of wood or coal, but a living heat that rose from the earth itself. "
                    "It walked. It breathed. The oldest oaks on the ridge remember its warmth in their rings. "
                    "The Eldertrunk was a sapling when the Fire last passed through — it did not burn. "
                    "It blessed."
                ),
            },
            {
                "title": "The Sleepers",
                "req": 6,
                "text": (
                    "The First Fire was not alone. There were others — beings of earth and flame, "
                    "vast as hills, slow as mountains. They walked the world in an age before names. "
                    "One of them lies beneath the ashen copse, dreaming. The petrified trees are not dead — "
                    "they are held in the moment of the Sleeper's last exhalation, frozen in time. "
                    "The Drowned Cairn was built by hands that worshipped the Sleepers as gods. "
                    "The Sealed Door... is not a door. It is a warning."
                ),
            },
            {
                "title": "The Cataclysm",
                "req": 9,
                "text": (
                    "Something woke one of the Sleepers — not the one beneath the copse, but another, "
                    "far to the north. Its waking cracked the world. Forests burned. Mountains sank. "
                    "The ashen copse is the snapshot of that moment: trees mid-flame, then frozen. "
                    "The Sleeper beneath the copse did not wake — it chose to stay, to hold the land together. "
                    "The Sealed Door was built by the deepwardens of old to keep people away from what stirs below. "
                    "The runes are not a lock. They are a lullaby."
                ),
            },
            {
                "title": "The Pact",
                "req": 12,
                "text": (
                    "Long ago, the first settlers of the vale made a pact: they would tend the land, "
                    "and the Sleeper would sleep. The Whispering Spring is where the pact was sworn — "
                    "its waters carry the Sleeper's dreams to those who drink. The ashen visions "
                    "are not visions at all; they are shared dreams, gifts from the dreaming mind below. "
                    "The child with ash-grey eyes? Touched. Chosen. There have been others before. "
                    "When enough of them gather, the Sleeper will wake — not in fury, but in need. "
                    "Something woke the other one. Something is coming."
                ),
            },
        ]

        # Find the next unrevealed story
        for story in LORE_STORIES:
            if story["title"] in self.lore_revealed:
                continue
            if len(self.lore_fragments) >= story["req"]:
                self.lore_revealed.append(story["title"])
                self.world_log.append(f"📖 Lore unveiled: {story['title']}")
                kingdom.kingdom_log.append(f"📖 The scholars have pieced together a story: {story['title']}")

                # When all 4 lore stories are unveiled, unlock the secret 7th region
                if len(self.lore_revealed) >= 4:
                    self.unlock_flags.add("all_lore_unveiled")
                    self.world_log.append(
                        "💎 The scholars, armed with the full story, have triangulated the location "
                        "of a hidden sanctum — the_sunken_sanctum. The Heart-Pool awaits."
                    )
                    kingdom.kingdom_log.append(
                        "💎 ALL LORE UNVEILED: The full history of the Sleepers is now known. "
                        "A hidden sanctum has been revealed — the_sunken_sanctum can now be discovered!"
                    )
                    # Auto-discover the sanctum if it hasn't been found yet
                    if "the_sunken_sanctum" not in self.discovered:
                        self.discover("the_sunken_sanctum")
                    else:
                        self.world_log.append(
                            "The Heart-Pool pulses with renewed vigor — the sanctum welcomes those "
                            "who know the full truth."
                        )

                return f"\n  ╔══════════════════════════════════════════╗\n  ║  📖 LORE: {story['title']:<30} ║\n  ╚══════════════════════════════════════════╝\n\n  {story['text']}\n"
        return None

    # ── TERRITORY DEFENSE BONUS ──────────────────────────────

    def territory_defense_bonus(self):
        """Calculate defense bonus from discovered and deep-scouted regions.
        Each region adds defense based on its danger level.
        Deep-scouted regions contribute more (intimate terrain knowledge).
        Special combo: ashen_copse + glimmer_marsh both deep-scouted = ancient pact.
        Returns int — usable by kingdom._resolve_raid or added to defense_rating."""
        bonus = 0
        danger_values = {"low": 1, "medium": 2, "high": 3}
        for region in self.discovered:
            danger = TERRAIN[region]["danger"]
            base = danger_values.get(danger, 1)
            if region in self.exploration_bonuses:
                base += 2  # deep-scout: you know every hollow and high ground
            bonus += base
        # Special: ashen_copse + glimmer_marsh both awakened → ancient pact
        if ("the_ashen_copse" in self.discovered
                and "glimmer_marsh" in self.discovered
                and "the_ashen_copse" in self.exploration_bonuses
                and "glimmer_marsh" in self.exploration_bonuses):
            bonus += 4  # The Sleeper and the Drowned Cairn both awakened — the land itself resists invaders
        return bonus


# ══════════════════════════════════════════════════════════════════
    # ── WORLD OMENS ─────────────────────────────────────────

    def world_omens(self):
        """Return a narrative omen based on the current season + weather combo.
        These are rare, flavorful events — small resource impacts, big atmosphere.
        Only fires ~15% of days. Call from kingdom.tick or scout_report.
        Cached per-day: multiple callers share the same omen (or None)."""
        # Per-day cache: fire once, share result across all callers
        if self._omen_cache_day == self.day:
            return self._omen_cache
        self._omen_cache_day = self.day
        if random.random() > 0.15:
            self._omen_cache = None
            return None

        omens = {
            ("spring", "clear"): [
                {"narrative": "🌱 The first swallow of spring returns to the vale. Children chase it through the lanes, laughing. +1 food (optimism sows itself).", "food": 1},
            ],
            ("spring", "rain"): [
                {"narrative": "🌧️ A warm rain falls for three hours straight. Every seed in the ground stirs. The farmers speak of a 'green year.' +3 food.", "food": 3},
            ],
            ("summer", "clear"): [
                {"narrative": "☀️ The sun stands still at noon — or seems to. For one held breath, every shadow vanishes. The elders say it's a blessing from the old days. +2 gold (pilgrims arrive).", "gold": 2},
            ],
            ("summer", "drought"): [
                {"narrative": "🏜️ The Whispering Spring shrinks to a trickle. At its muddy bottom, ancient carvings are exposed. +3 gold (scholars copy them), -2 food (water rationed).", "gold": 3, "food": -2, "lore": "The carvings at the spring's bottom depict a circle of figures holding hands around a sleeping giant."},
            ],
            ("autumn", "clear"): [
                {"narrative": "🍂 The oaks of the ridge drop their leaves all at once — in the space of a single hour. The ground is knee-deep in copper. +3 wood (kindling for the winter).", "wood": 3},
            ],
            ("autumn", "storm"): [
                {"narrative": "⛈️ An autumn gale tears through the vale, but the Eldertrunk doesn't so much as creak. Some say the old oak *leaned into* the wind. +4 wood (storm-fall), -1 stone (roof repairs).", "wood": 4, "stone": -1},
            ],
            ("winter", "clear"): [
                {"narrative": "❄️ A stillness so deep the whole kingdom falls silent. Even the livestock stop lowing. In the quiet, a low, warm hum rises from the direction of the ashen copse. No resources change — but nobody forgets.", "food": 0},
            ],
            ("winter", "snow"): [
                {"narrative": "🌨️ Snow falls thick and fast, but the ground near the Sleeper's Hollow stays bare and warm. A ring of green grass persists in the dead of winter. +2 gold (curious visitors pay to see it).", "gold": 2},
            ],
            ("winter", "storm"): [
                {"narrative": "🌪️ A blizzard howls for two days. When it clears, a new standing stone is found on the ridge — one that was never there before. +3 stone, +2 gold (archaeologists arrive). Some say the land *grew* it.", "stone": 3, "gold": 2, "lore": "The new standing stone is warm to the touch even in deep snow. Its surface is covered in the same runes as the Sealed Door."},
            ],
        }

        key = (self.season, self.weather)
        if key not in omens:
            return None

        omen = random.choice(omens[key]).copy()
        apply_event(omen, self)
        self.world_log.append(f"🌠 Omen ({self.season}/{self.weather}): {omen.get('narrative', '')}")
        # Ash-Bloom: when the Sleeper stirs (world_omens fires) and the copse is discovered,
        # there's a chance an Ash-Bloom crystallizes
        if "the_ashen_copse" in self.discovered and random.random() < 0.30:
            ash_bloom_msg = (
                "\U0001f338 An Ash-Bloom crystallizes in the_ashen_copse \u2014 the Sleeper's stirring "
                "has coaxed a flower of frozen fire from the petrified wood. +12 gold."
            )
            kingdom.gold += 12
            self.world_log.append(ash_bloom_msg)
            if "ash_bloom" not in omen:
                omen["ash_bloom"] = True
                omen["gold"] = omen.get("gold", 0) + 12
                if "narrative" in omen:
                    omen["narrative"] += " An Ash-Bloom crystallized in the copse."
        self._omen_cache = omen
        return omen

    # ── THREAT ASSESSMENT ────────────────────────────────────

    def threat_assessment(self):
        """Return a narrative assessment of external threats based on
        discovered dangerous regions that haven't been deep-scouted.
        Deep-scouting a region means you know its dangers and can prepare."""
        threats = []
        high_danger_unscouted = []
        for region in self.discovered:
            t = TERRAIN[region]
            if t["danger"] in ("medium", "high") and region not in self.exploration_bonuses:
                high_danger_unscouted.append(region)

        if not high_danger_unscouted:
            return "🛡️ All known dangerous regions have been thoroughly scouted. The kingdom rests easy."

        lines = []
        lines.append("⚠️ THREAT ASSESSMENT:")
        for region in high_danger_unscouted:
            t = TERRAIN[region]
            danger_icon = {"medium": "🟡", "high": "🔴"}.get(t["danger"], "⚪")
            notes = t.get("notes", "")
            note_str = f" — {notes}" if notes else ""
            lines.append(f"  {danger_icon} {region} ({t['danger']} danger) — not yet deep-scouted{note_str}")

        total_threat = len(high_danger_unscouted)
        if total_threat >= 2:
            lines.append("  ⚡ Multiple unscouted dangers — the council advises caution.")
        return "\n".join(lines)

    # ── CREATURE ENCOUNTERS ──────────────────────────────────

    def _creature_signs(self, region):
        """Return a random ambient sign of creature activity in a region.
        Used for flavor in scout reports and exploration."""
        if region not in self.discovered or region not in CREATURES:
            return None
        creatures = CREATURES[region]
        if not creatures:
            return None
        creature = random.choice(creatures)
        if creature.get("signs"):
            sign = random.choice(creature["signs"])
            return {"region": region, "creature": creature["name"], "sign": sign, "danger": creature["danger"]}
        return None

    
    # ── LAIRS ────────────────────────────────────────────────

    def challenge_lair(self, region, action="fight"):
        """Challenge a discovered but uncleared lair.
        Actions: fight, bargain, avoid.
        Returns result dict or None."""
        if region not in self._discovered_lairs:
            self.world_log.append(f"No lair has been discovered in {region}.")
            return None
        if region in self._cleared_lairs:
            self.world_log.append(f"The lair in {region} has already been cleared.")
            return None
        if region not in self.discovered:
            self.world_log.append(f"{region} is not under our control.")
            return None

        lair = LAIRS[region]
        boss_name = lair["boss"]

        if action == "bargain":
            self.world_log.append(
                f"Attempting to pacify {lair['name']} ({boss_name})..."
            )
            stakes = lair["stakes"]
            self._cleared_lairs.add(region)
            self.world_log.append(
                f"LAIR CLEARED: {lair['name']} in {region}! {lair['cleared_bonus']}"
            )
            for key, val in stakes.items():
                if key == "lore":
                    self.collect_lore(val)
                elif key == "food":
                    kingdom.food = max(0, kingdom.food + val)
                elif key == "wood":
                    kingdom.wood = max(0, kingdom.wood + val)
                elif key == "stone":
                    kingdom.stone = max(0, kingdom.stone + val)
                elif key == "gold":
                    kingdom.gold = max(0, kingdom.gold + val)
                elif key == "pop":
                    kingdom.population = max(1, kingdom.population + val)
            return {"action": "bargain", "lair": lair["name"], "stakes": stakes, "cleared": True}

        elif action == "fight":
            combat_stakes = lair.get("combat_stakes", {})
            if not combat_stakes:
                self.world_log.append(
                    f"Cannot fight the {boss_name} - it is not a physical foe. Try bargaining."
                )
                return {"action": "fight", "lair": lair["name"], "stakes": {}, "cleared": False}
            self.world_log.append(
                f"CHALLENGING {lair['name']} - facing the {boss_name}!"
            )
            stakes = combat_stakes
            self._cleared_lairs.add(region)
            self.world_log.append(
                f"LAIR CLEARED: {lair['name']} in {region}! {lair['cleared_bonus']}"
            )
            for key, val in stakes.items():
                if key == "lore":
                    self.collect_lore(val)
                elif key == "food":
                    kingdom.food = max(0, kingdom.food + val)
                elif key == "wood":
                    kingdom.wood = max(0, kingdom.wood + val)
                elif key == "stone":
                    kingdom.stone = max(0, kingdom.stone + val)
                elif key == "gold":
                    kingdom.gold = max(0, kingdom.gold + val)
                elif key == "pop":
                    kingdom.population = max(1, kingdom.population + val)
            return {"action": "fight", "lair": lair["name"], "stakes": stakes, "cleared": True}

        else:  # avoid
            self.world_log.append(
                f"Avoiding {lair['name']} - the {boss_name} remains undisturbed."
            )
            return {"action": "avoid", "lair": lair["name"], "stakes": {}, "cleared": False}

    def lair_status(self):
        """Return a narrative report of all lairs - discovered, cleared, and hidden."""
        lines = []
        lines.append("LAIR STATUS:")

        any_found = False
        for region in self.discovered:
            if region not in LAIRS:
                continue
            lair = LAIRS[region]
            if region in self._cleared_lairs:
                lines.append(f"  [CLEARED] {region}: {lair['name']} - {lair['cleared_bonus']}")
                any_found = True
            elif region in self._discovered_lairs:
                lines.append(f"  [DISCOVERED] {region}: {lair['name']} - Boss: {lair['boss']} ({lair['danger']} danger).")
                any_found = True
            else:
                lines.append(f"  [HIDDEN] {region}: No lair found yet. Deep-scout to search.")

        if not any_found and not self.discovered:
            return "No regions discovered - lairs remain hidden."
        elif not any_found:
            lines.append("  No lairs discovered yet. Keep deep-scouting!")

        if self._cleared_lairs:
            lines.append("")
            lines.append("CLEARED LAIR BONUSES:")
            for region in sorted(self._cleared_lairs):
                if region in LAIRS:
                    lines.append(f"  * {LAIRS[region]['name']}: {LAIRS[region]['cleared_bonus']}")

        return "\n".join(lines)

    
    def _check_disasters(self):
        """Check for region-specific disaster events each day."""
        results = []

        for region in list(self.discovered):
            if region not in DISASTERS:
                continue

            disaster = DISASTERS[region]

            # Check cooldown
            if region in self._disaster_cooldown:
                if self.day < self._disaster_cooldown[region]:
                    continue
                else:
                    del self._disaster_cooldown[region]

            # Handle active disaster recovery
            if region in self._active_disasters:
                active = self._active_disasters[region]
                if self.day >= active["recovery_day"]:
                    recovery_msg = disaster.get("recovery_msg",
                        "The crisis in " + region + " has passed.")
                    self.world_log.append("RECOVERY: " + region + " - " + recovery_msg)

                    # Handle special recovery effects
                    special = disaster.get("special")
                    if special == "fog_discovery":
                        if random.random() < 0.50:
                            lore = ("A relic pulled from the marsh-fog of " + region +
                                    ": a silver locket with a portrait of someone "
                                    "who has not been born yet.")
                            self.collect_lore(lore)
                            self.world_log.append(
                                "The fog left behind a curious relic - a lore fragment.")
                        else:
                            kingdom.gold += 5
                            self.world_log.append(
                                "The fog left behind a cache of trade-coins (+5 gold).")
                    elif special == "fertility_boost":
                        self._sunfire_fertility = True
                        self.world_log.append(
                            "Sunfire_plains soil supercharged with wildfire ash.")
                    elif special == "vision_chance":
                        if ("ashen_vision" not in self.unlock_flags
                                and random.random() < 0.20):
                            self.trigger_ashen_vision()
                            self.world_log.append(
                                "Breathing the ash-storm triggered a vision...")
                    elif special == "crystal_recovery":
                        kingdom.stone += 8
                        self.world_log.append(
                            "Scouts collect shattered crystal shards from the sanctum floor (+8 stone).")
                        if random.random() < 0.30:
                            lore = ("A crystal shard from the sanctum holds a fragment of "
                                    "the Sleeper's dream: a city of glass and green, "
                                    "walking on legs of fire. The dream-city sang.")
                            self.collect_lore(lore)
                            self.world_log.append(
                                "One shard contained a memory — a lore fragment!")

                    del self._active_disasters[region]
                    self._disaster_cooldown[region] = self.day + random.randint(10, 20)
                    results.append({"type": "recovery", "region": region,
                                    "special": special})
                continue

            # Roll for new disaster
            base_chance = disaster["chance"]
            danger = TERRAIN[region]["danger"]
            danger_mod = {"low": 1.0, "medium": 1.3, "high": 1.6}.get(danger, 1.0)
            season_mod = 1.0
            if self.season == "summer":
                season_mod = 1.3
            elif self.season == "winter":
                season_mod = 1.2
            final_chance = base_chance * danger_mod * season_mod

            if random.random() < final_chance:
                self._active_disasters[region] = {
                    "name": disaster["name"],
                    "day_struck": self.day,
                    "recovery_day": self.day + disaster["recovery_day"],
                }

                effects = disaster["effects"]
                effect_parts = []
                for key, val in effects.items():
                    if key == "pop":
                        kingdom.population = max(1, kingdom.population + val)
                        effect_parts.append(str(val) + " pop")
                    elif key == "food":
                        kingdom.food = max(0, kingdom.food + val)
                        effect_parts.append(str(val) + " food")
                    elif key == "wood":
                        kingdom.wood = max(0, kingdom.wood + val)
                        effect_parts.append(str(val) + " wood")
                    elif key == "stone":
                        kingdom.stone = max(0, kingdom.stone + val)
                        effect_parts.append(str(val) + " stone")
                    elif key == "gold":
                        kingdom.gold = max(0, kingdom.gold + val)
                        effect_parts.append(str(val) + " gold")

                effects_str = ", ".join(effect_parts)
                msg = ("DISASTER: " + disaster["name"] + " strikes " + region +
                       "! " + disaster["narrative"] + " [" + effects_str + "] " +
                       "(Recovery in " + str(disaster["recovery_day"]) + " days)")
                self.world_log.append(msg)

                # ── Lair-Disaster Interaction ──
                lair_interaction = None
                if region in LAIRS:
                    lair = LAIRS[region]
                    lair_name = lair["name"]
                    if region not in self._discovered_lairs:
                        # Undiscovered lair: 30% chance disaster exposes it
                        if random.random() < 0.30:
                            self._discovered_lairs[region] = lair_name
                            self.world_log.append(
                                f"🏚️ The {disaster['name']} has exposed a hidden lair in {region}: "
                                f"{lair_name}! {lair['discovery'][:80]}..."
                            )
                            lair_interaction = "revealed"
                    elif region not in self._cleared_lairs:
                        # Discovered but uncleared: boss becomes enraged — extra penalty
                        boss = lair["boss"]
                        extra_penalty = random.choice([
                            ("The " + boss + " roars from its lair, enraged by the chaos!", {"gold": -4}),
                            ("The " + boss + " uses the disaster as cover to raid! Food stolen!", {"food": -5}),
                            ("The " + boss + " stirs — the ground trembles!", {"pop": -1}),
                        ])
                        self.world_log.append(
                            f"⚡ LAIR REACTION: {extra_penalty[0]}"
                        )
                        for k, v in extra_penalty[1].items():
                            if k == "pop":
                                kingdom.population = max(1, kingdom.population + v)
                            elif k == "food":
                                kingdom.food = max(0, kingdom.food + v)
                            elif k == "gold":
                                kingdom.gold = max(0, kingdom.gold + v)
                        lair_interaction = "enraged"
                    elif region in self._cleared_lairs:
                        # Cleared lair: 10% chance it destabilizes
                        if random.random() < 0.10:
                            self._cleared_lairs.discard(region)
                            self.world_log.append(
                                f"⚠️ LAIR DESTABILIZED: The {disaster['name']} has reopened "
                                f"{lair_name} in {region}! It must be cleared again."
                            )
                            lair_interaction = "destabilized"

                results.append({
                    "type": "disaster", "region": region,
                    "name": disaster["name"], "effects": effects,
                    "recovery_day": self.day + disaster["recovery_day"],
                    "lair_interaction": lair_interaction,
                })

        return results if results else None

    def disaster_status(self):
        """Return a summary of active disasters."""
        if not self._active_disasters:
            return "No active disasters. The kingdom is at peace."

        lines = ["ACTIVE DISASTERS:"]
        for region, active in sorted(self._active_disasters.items()):
            days_left = max(0, active["recovery_day"] - self.day)
            disaster = DISASTERS.get(region, {})
            name = active.get("name", disaster.get("name", "Unknown"))
            lines.append("  " + region + ": " + name +
                         " - " + str(days_left) + " day(s) until recovery")

        if self._disaster_cooldown:
            lines.append("")
            lines.append("RECENTLY RECOVERED (cooldown):")
            for region, cd_day in sorted(self._disaster_cooldown.items()):
                if cd_day > self.day:
                    days_left = cd_day - self.day
                    lines.append("  " + region + ": stable for " +
                                 str(days_left) + " more day(s)")

        return "\n".join(lines)


    def _check_lair_activity(self):
        """Check for ongoing lair effects - called from advance_day.
        Some lairs have passive effects once cleared; uncleared lairs may cause problems."""
        results = []

        # Gloom-Lantern saturation: if all 6 regions infected and lair not cleared
        if ("ironroot_depths" in self._gloom_lantern_regions
            and "ironroot_depths" not in self._cleared_lairs
            and len(self._gloom_lantern_regions) >= 6):
            self.world_log.append(
                "GLOOM-SATURATION: Every known region pulses with the Gloom-Lantern's "
                "green light. The mother lantern in ironroot_depths has reached full bloom - "
                "spores drift on every wind. Herbalists report citizens sleepwalking toward "
                "the depths. The council demands action!"
            )
            kingdom.gold -= 10
            kingdom.food -= 5
            results.append("gloom_saturation")

        # Cleared lair passive bonuses
        for region in self._cleared_lairs:
            lair = LAIRS.get(region)
            if not lair:
                continue
            if region == "the_vale":
                kingdom.food += 1
            elif region == "old_oak_ridge":
                kingdom.food += 1
            elif region == "glimmer_marsh":
                pass  # bonus applied via harvest() multiplier
            elif region == "ironroot_depths":
                kingdom.gold += 2
            elif region == "sunfire_plains":
                kingdom.gold += 1
            elif region == "the_ashen_copse":
                kingdom.gold += 3
            elif region == "the_sunken_sanctum":
                kingdom.gold += 5
                kingdom.stone += 2

        return results if results else None


    def _check_creature_specials(self):
        """Check and process pending creature special behaviors:
        - Gloom-Lantern spread: every 7 days after being ignored, spawns in another region
        - Shadow-Fox return gift: 3-7 days after being fed, returns with +5 gold
        Called from advance_day()."""
        results = []

        # Gloom-Lantern Spread
        if self._gloom_lantern_regions:
            days_since = self.day - self._gloom_lantern_day
            if days_since > 0 and days_since % 7 == 0:
                # Find eligible regions: discovered, not already infected, have CREATURES
                eligible = [
                    r for r in self.discovered
                    if r in CREATURES and r not in self._gloom_lantern_regions
                ]
                if eligible:
                    target = random.choice(eligible)
                    self._gloom_lantern_regions.add(target)
                    self._gloom_lantern_day = self.day  # reset timer
                    msg = (
                        "\U0001f344 GLOOM-LANTERN SPREAD: A new cluster of hypnotic fungi has appeared "
                        f"in {target}! Herbalists report a soft green glow from the shadows. "
                        f"The Gloom-Lantern now haunts {len(self._gloom_lantern_regions)} region(s)."
                    )
                    self.world_log.append(msg)
                    results.append({"type": "gloom_spread", "region": target, "msg": msg})
                else:
                    # No eligible regions - the lantern has saturated the known world
                    self._gloom_lantern_day = 0  # stop tracking

        # Shadow-Fox Return Gift
        if self._shadow_fox_gift_pending and self._shadow_fox_fed_day > 0:
            return_day = self._shadow_fox_fed_day + self._shadow_fox_return_day
            if self.day >= return_day:
                kingdom.gold += 5
                self._shadow_fox_gift_pending = False
                msg = (
                    "\U0001f98a SHADOW-FOX RETURNS: At dawn, a dead pheasant and a nugget of raw gold "
                    "are found on the granary steps \u2014 the shadow-fox's gift. +5 gold. "
                    "Tiny silver-fur pawprints lead back toward the vale."
                )
                self.world_log.append(msg)
                results.append({"type": "shadow_fox_gift", "msg": msg})

        return results

    def creature_encounter(self, region=None):
        """Generate a creature encounter in a region. Returns structured encounter
        dict for future combat integration. If no region given, picks a random
        discovered region weighted by danger.

        Return dict:
            region, creature_name, danger, ctype, narrative, stakes, combat_stakes, special
        """
        if region is None:
            eligible = [r for r in self.discovered if r in CREATURES]
            if not eligible:
                return None
            danger_weights = {"high": 3, "medium": 2, "low": 1}
            weights = [danger_weights.get(TERRAIN[r]["danger"], 1) for r in eligible]
            region = random.choices(eligible, weights=weights, k=1)[0]

        if region not in CREATURES or region not in self.discovered:
            return None

        creatures = CREATURES[region]
        creature_weights = [{"high": 3, "medium": 2, "low": 1}.get(c["danger"], 1) for c in creatures]
        creature = random.choices(creatures, weights=creature_weights, k=1)[0]

        encounter = {
            "region": region,
            "creature_name": creature["name"],
            "danger": creature["danger"],
            "ctype": creature["type"],
            "narrative": creature["encounter"],
            "stakes": creature["stakes"],
            "combat_stakes": creature.get("combat_stakes", {}),
            "special": creature.get("special", ""),
        }

        self.world_log.append(
            f"\U0001f43e Creature encounter in {region}: {creature['name']} ({creature['danger']} danger)"
        )
        return encounter

    def resolve_creature_encounter(self, encounter, action="avoid"):
        """Resolve a creature encounter with the given action.
        Actions: 'avoid' (default, minimal stakes), 'fight' (combat_stakes), 'bargain' (special)
        Returns resource changes applied to kingdom.
        """
        if not encounter:
            return None

        if action == "fight":
            stakes = encounter.get("combat_stakes", {})
            if not stakes:
                stakes = encounter["stakes"]
                self.world_log.append(f"\u2694\ufe0f Cannot fight {encounter['creature_name']} \u2014 it is not a physical foe.")
            else:
                self.world_log.append(
                    f"\u2694\ufe0f Fighting {encounter['creature_name']} in {encounter['region']}!"
                )
        elif action == "bargain":
            stakes = encounter["stakes"]
            self.world_log.append(
                f"\U0001f91d Attempting to parley with {encounter['creature_name']}..."
            )
        else:  # avoid
            stakes = encounter["stakes"]
            self.world_log.append(
                f"\U0001f6b6 Avoiding {encounter['creature_name']} in {encounter['region']}."
            )

        # Track creature specials for follow-up mechanics
        creature_name = encounter["creature_name"]
        if creature_name == "Gloom-Lantern" and action == "avoid":
            self._gloom_lantern_day = self.day
            self._gloom_lantern_regions.add(encounter["region"])
            self.world_log.append(
                "\U0001f344 The Gloom-Lantern's spores drift on the air. If left unchecked, it may spread..."
            )
        elif creature_name == "Shadow-Fox" and action == "bargain":
            # Feeding the fox voluntarily
            if kingdom.food >= 2:
                kingdom.food -= 2
                self._shadow_fox_fed_day = self.day
                self._shadow_fox_gift_pending = True
                self._shadow_fox_return_day = random.randint(3, 7)
                self.world_log.append(
                    "\U0001f98a You leave out a portion of dried meat. The shadow-fox takes it, "
                    "meets your eyes for one long moment, and vanishes. You feel it will remember this."
                )

        # Apply resource changes
        for key, val in stakes.items():
            if key == "narrative" or key == "special" or key == "lore":
                continue
            if key == "pop":
                kingdom.population = max(1, kingdom.population + val)
            elif key == "food":
                kingdom.food = max(0, kingdom.food + val)
            elif key == "wood":
                kingdom.wood = max(0, kingdom.wood + val)
            elif key == "stone":
                kingdom.stone = max(0, kingdom.stone + val)
            elif key == "gold":
                kingdom.gold = max(0, kingdom.gold + val)

        # Handle lore
        if "lore" in stakes:
            self.collect_lore(stakes["lore"])

        return {"action": action, "creature": encounter["creature_name"], "stakes": stakes}

    def creature_activity(self):
        """Return a narrative report of recent creature activity across discovered regions.
        Picks 1-3 random creature signs."""
        discovered = [r for r in self.discovered if r in CREATURES]
        if not discovered:
            return "\U0001f54a\ufe0f No regions with known fauna have been discovered."

        count = min(len(discovered), random.randint(1, 3))
        regions = random.sample(discovered, count)

        lines = []
        lines.append("\U0001f43e CREATURE ACTIVITY:")
        for region in regions:
            sign = self._creature_signs(region)
            if sign:
                danger_icon = {"low": "\U0001f7e2", "medium": "\U0001f7e1", "high": "\U0001f534"}.get(sign["danger"], "\u26aa")
                lines.append(f"  {danger_icon} {region}: {sign['sign']}")
        return "\n".join(lines) if len(lines) > 1 else "\U0001f54a\ufe0f No unusual creature activity detected."

    def region_lore(self, region_filter=None):
        """Return compiled lore, optionally filtered by a region name.
        Without filter, returns all collected lore fragments."""
        if not self.lore_fragments:
            return "\U0001f4dc No lore fragments have been collected yet. Explore to find them."

        if region_filter:
            # Filter lore fragments that mention the region by name
            matching = [f for f in self.lore_fragments if region_filter.lower() in f.lower()]
            if not matching:
                return f"\U0001f4dc No lore fragments found for {region_filter}."
            lines = [f"\U0001f4dc LORE \u2014 {region_filter}:"]
            for f in matching:
                lines.append(f"  \u2022 {f}")
            return "\n".join(lines)
        else:
            lines = ["\U0001f4dc ALL COLLECTED LORE:"]
            for i, f in enumerate(self.lore_fragments, 1):
                lines.append(f"  {i}. {f}")
            return "\n".join(lines)

    def daily_creature_event(self):
        """Mid-tick creature encounter — small chance each day of a creature
        wandering near the kingdom. Auto-resolves based on kingdom strength.
        Returns a narrative summary dict or None."""
        if random.random() > 0.10:  # 10% chance per day
            return None

        # Pick a random discovered region weighted by proximity (vale/ridge more likely)
        eligible = [r for r in self.discovered if r in CREATURES]
        if not eligible:
            return None

        # Weight: the_vale and old_oak_ridge are "near the kingdom" — more likely
        weights = []
        for r in eligible:
            if r in ("the_vale", "old_oak_ridge"):
                weights.append(4)
            elif r == "glimmer_marsh":
                weights.append(2)
            else:
                weights.append(1)
        region = random.choices(eligible, weights=weights, k=1)[0]

        encounter = self.creature_encounter(region)
        if not encounter:
            return None

        # Auto-resolve: avoid by default, fight if strong, bargain for anomalies
        action = "avoid"
        from kingdom import kingdom
        if kingdom.defense_rating() >= 40 and encounter["danger"] in ("low", "medium"):
            action = random.choice(["fight", "avoid", "avoid"])
        elif encounter["ctype"] == "anomaly":
            action = random.choice(["bargain", "avoid"])

        result = self.resolve_creature_encounter(encounter, action)

        # Build a pithy narrative for the tick summary
        name = encounter["creature_name"]
        if action == "fight":
            narrative = f"⚔️ Guards drove off a {name} near {region}."
        elif action == "bargain":
            narrative = f"🤝 Parlayed with a {name} in {region}."
        else:
            narrative = f"🐾 A {name} was spotted near {region} — avoided without incident."

        return {
            "region": region,
            "creature": name,
            "action": action,
            "narrative": narrative,
            "stakes": result.get("stakes", {}),
        }


# ── EVENT POOLS ──────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════

EVENTS = {
    "low": [
        {"narrative": "Wildflowers bloom — morale lifts. Nothing else changes, but the air smells sweet.", "food": 0},
        {"narrative": "A travelling merchant passes through. +4 gold (trade taxes).", "gold": 4},
        {"narrative": "A child finds a pretty stone that turns out to be a gem. +2 gold.", "gold": 2},
        {"narrative": "Elders tell stories of the old days around the fire. Morale improves.", "food": 1},
        {"narrative": "A gentle rain fills the rain-barrels. +2 food.", "food": 2},
    ],
    "medium": [
        {"narrative": "A wandering bard performs at the tavern. +5 gold (tips), -1 food (feasting).", "gold": 5, "food": -1},
        {"narrative": "Scouts find an abandoned cache of supplies. +3 food, +4 wood.", "food": 3, "wood": 4},
        {"narrative": "A minor rockslide blocks a path. -2 stone (clearing it).", "stone": -2},
        {"narrative": "A dispute between two families erupts. -2 gold (compensation).", "gold": -2},
        {"narrative": "A peddler sells 'lucky charms' that are mostly junk. -1 gold.", "gold": -1},
        {"narrative": "Scouts discover a patch of rare mushrooms. +3 food, +2 gold.", "food": 3, "gold": 2},
        {"narrative": "A roof collapsed on a storehouse! -3 wood, -1 stone.", "wood": -3, "stone": -1},
    ],
    "high": [
        {"narrative": "A wolf-pack harasses the outskirts. -3 food (lost livestock), but +5 gold (bounty pelts).", "food": -3, "gold": 5},
        {"narrative": "A cave-in at the quarry! -5 stone, -1 population.", "stone": -5, "pop": -1},
        {"narrative": "Bandits raid a supply cart. -4 food, -3 gold.", "food": -4, "gold": -3},
        {"narrative": "A cliff face collapses — +8 stone, but -1 population (buried).", "stone": 8, "pop": -1},
        {"narrative": "A wounded dire-bear is driven off by the guard. -4 food (lost to the beast), +6 gold (its pelt is priceless).", "food": -4, "gold": 6},
        {"narrative": "A flash flood sweeps through the outskirts. -5 wood, -3 food.", "wood": -5, "food": -3},
        {"narrative": "An old mine shaft is rediscovered. +10 stone, +5 gold.", "stone": 10, "gold": 5},
        {"narrative": "A strange blue flame erupts from the ground and vanishes. A child who touched it now speaks of 'the sleeping fire.' +4 gold (pilgrims come to see the scorch-mark).", "gold": 4},
        {"narrative": "An ancient cairn is uncovered by erosion. +6 stone, +3 gold (grave goods).", "stone": 6, "gold": 3},
        {"narrative": "Wolves take a goat from the pens. -2 food, but the hunt that follows yields +5 food (venison) and +3 gold (wolf pelts).", "food": 3, "gold": 3},
        {"narrative": "A sinkhole reveals an underground spring. +4 food (fresh water), +2 stone.", "food": 4, "stone": 2},
    ],
}

# ── REGION-SPECIFIC EVENTS ──────────────────────────────────────

REGION_EVENTS = {
    "the_vale": [
        {"narrative": "A wedding is celebrated under the old hawthorn tree. The whole vale gathers, and the couple is showered with wildflower petals. +2 food (feast), +1 gold (gifts).", "food": 2, "gold": 1},
        {"narrative": "Children discover a patch of sun-ripe blackberries bigger than their thumbs. They fill three baskets before sundown. +3 food.", "food": 3},
        {"narrative": "The Whispering Spring reflects a starry sky even in broad daylight. An elder says it's an omen of good fortune. +2 gold (offerings left at the spring).", "gold": 2},
        {"narrative": "A shepherd finds a silver ram's horn half-buried in the hillside. It's ancient and beautifully carved. +4 gold (sold to a collector).", "gold": 4},
        {"narrative": "A gentle earth-tremor rattles cups but does no damage. It uncovers a small cache of old coins behind a cottage wall. +3 gold.", "gold": 3},
        {"narrative": "The berry thickets yield a bumper harvest this season. +5 food (dried and stored).", "food": 5},
        {"narrative": "A travelling tinker fixes every broken pot and kettle in the vale, accepting only a meal as payment. +3 gold (productivity restored!).", "food": -1, "gold": 3},
        {"narrative": "A child born under a shooting star is blessed by the elders at the Whispering Spring. The whole vale celebrates. +2 food, +2 gold.", "food": 2, "gold": 2},
    ],
    "old_oak_ridge": [
        {"narrative": "An acorn from the Eldertrunk sprouts in a single night, growing into a sapling by dawn. The elders call it a blessing. +2 wood, +3 gold (pilgrims visit).", "wood": 2, "gold": 3},
        {"narrative": "A hollow in the Eldertrunk yields a cache of ancient acorn-flour — still edible after who-knows-how-long. +3 food.", "food": 3},
        {"narrative": "A windstorm tears through the ridge, but the ancient oaks barely sway. One dead branch falls — +5 wood — and narrowly misses a woodcutter.", "wood": 5},
        {"narrative": "Carved symbols are found on a lightning-struck oak — they match no known language. Scholars arrive. +4 gold.", "gold": 4, "lore": "The carvings predate the kingdom by millennia. They depict a great fire and something vast moving beneath the earth."},
        {"narrative": "An old badger sett collapses under a woodcutter's feet. They're bruised but fine. -1 food (lost lunch), +2 stone (uncovered flint nodules).", "food": -1, "stone": 2},
        {"narrative": "Owls roost in the high branches of the ridge-oaks. Their pellets contain tiny bones of creatures no one has ever seen. +3 gold (curiosities sold).", "gold": 3},
        {"narrative": "A woodcutter swears an oak spoke to them — not in words, but in a slow, deep feeling of welcome. They refuse to cut that tree. +2 wood (other trees seem easier to fell).", "wood": 2},
        {"narrative": "Sap from a lightning-struck oak tastes like honey and hardens like amber. It fetches a high price. +5 gold.", "gold": 5},
    ],
    "glimmer_marsh": [
        {"narrative": "Will-o'-wisps dance over the marsh at dusk. A scout follows and finds rare marsh-herbs. +6 gold.", "gold": 6},
        {"narrative": "A sunken canoe is dredged from the mire. Inside: +4 food (smoked fish) and a strange map.", "food": 4, "gold": 2},
        {"narrative": "Something large stirs beneath the duckweed. -1 population (taken). The marsh must be respected.", "pop": -1},
        {"narrative": "A hermit living on a reed island offers strange counsel in exchange for food. -2 food, but +6 gold (his predictions come true).", "food": -2, "gold": 6},
        {"narrative": "The Drowned Cairn's symbols glow blue at midnight. A scout who touches them gains knowledge of ancient herb-lore. +3 food, +4 gold.", "food": 3, "gold": 4, "lore": "The Drowned Cairn was built by hands that worshipped the Sleepers as gods — the symbols are prayers for continued slumber."},
        {"narrative": "Marsh-gas ignites in a ring around a sleeping scout. They wake unscathed but surrounded by a perfect circle of scorched reeds. +2 gold (omens read).", "gold": 2},
        {"narrative": "A chorus of frogs falls silent all at once. In the stillness, a low humming rises from the bog — then fades. The scouts retreat, shaken. -1 food (dropped supplies).", "food": -1},
        {"narrative": "The reeds whisper in a language almost understood. Scouts who listen closely find an overgrown causeway leading to a forgotten islet. +3 stone (old paving stones), +3 gold (relics from a drowned shrine).", "stone": 3, "gold": 3},
        {"narrative": "Marsh-lilies bloom under the full moon, their petals glowing faintly silver. Harvested before dawn, they fetch a rare price. +7 gold (moon-petals sold to apothecaries).", "gold": 7},
        {"narrative": "A thick fog rolls in from the bog, smelling of ozone and old stone. When it lifts, scouts find their packs rearranged — but also a pouch of strange coins that weren't there before. +5 gold (pre-cataclysm currency).", "gold": 5},
        # ── Marsh revelation trigger ──
        {"narrative": "The Drowned Cairn's door grinds open a handspan. Blue light spills across the bog like spilled ink. Scouts report a voice — not heard, but *felt* — asking a question in a language older than stone. 💧 The Cairn awakens.", "gold": 3, "unlock": "marsh_revelation"},
    ],
    "sunfire_plains": [
        {"narrative": "Wild horses thunder across the plains. Scouts return with +6 food (game trailed in their wake).", "food": 6},
        {"narrative": "A sun-bleached skull of some great beast is found. Its horns are worth +8 gold.", "gold": 8},
        {"narrative": "A dust-devil twists across the plain, scattering a camp. -2 food (lost supplies).", "food": -2},
        {"narrative": "A nomadic herder shares news of distant lands and trades smoked meat. +3 food, +2 gold.", "food": 3, "gold": 2},
        {"narrative": "The Sunspire glows at dawn so brightly that scouts can see it from the vale. Pilgrims arrive. +5 gold.", "gold": 5},
        {"narrative": "A grass-fire sweeps the eastern edge. -3 food, but the regrowth will be rich.", "food": -3},
        {"narrative": "Scouts find a circle of standing stones aligned with the solstice. +4 gold (scholars pay for the location).", "gold": 4},
        {"narrative": "A pride of plains-lions shadows the scouts for three days. They escape with their lives but lose -2 food to the beasts.", "food": -2},
    ],
    "ironroot_depths": [
        {"narrative": "A vein of pure iron is struck! +8 stone, +5 gold.", "stone": 8, "gold": 5},
        {"narrative": "A miner's pick breaks through into a hollow space beyond the cliff. +4 stone, but -1 population (caught in a collapse).", "stone": 4, "pop": -1},
        {"narrative": "The Sealed Door hums faintly at midnight. Those who sleep near it share the same dream — of a forest frozen in fire. +3 gold (scholars pay to record the vision).", "gold": 3, "lore": "The Sealed Door is not a door — it is a warning. The runes are a lullaby meant to keep something asleep."},
        {"narrative": "A strange fungus grows only on the iron-rich roots. It glows faintly and, when dried, fetches a high price. +5 gold.", "gold": 5},
        {"narrative": "A tunnel collapses, revealing a pocket of ancient tools. +3 stone, +3 gold (relics).", "stone": 3, "gold": 3},
        {"narrative": "Something moves in the darkness beyond the Sealed Door. Miners refuse to work for a day. -2 stone.", "stone": -2},
        {"narrative": "Iron-rich water seeps from a new crack in the cliff. Miners collect the rust-pigment for trade. +3 gold, +2 stone.", "gold": 3, "stone": 2},
        {"narrative": "A deep thrumming echoes from behind the Sealed Door. Tools vibrate off ledges. -3 stone (lost), but the deepwardens are more determined than ever.", "stone": -3},
        # ── Direct ashen vision trigger ──
        {"narrative": "The Sealed Door pulses with warm light. A scout presses their palm to it and sees — the ashen copse, the sleeping thing beneath, the path. +5 gold (rune-knowledge sold). 🔑 The way is revealed.", "gold": 5, "unlock": "ashen_vision"},
    ],
    "the_ashen_copse": [
        {"narrative": "The petrified trees weep ash-sap that hardens into gem-like tears. +8 gold.", "gold": 8, "lore": "The trees are not dead — they are held in the moment of the Sleeper's last exhalation."},
        {"narrative": "A scout places a hand on a frozen trunk and sees — for an instant — the fire that killed this forest. They recoil, but their eyes hold new knowledge. +4 gold, +2 wood (ancient charcoal).", "gold": 4, "wood": 2},
        {"narrative": "The Sleeper's Hollow exhales a warm gust. Those nearby feel an overwhelming urge to lie down and rest. One scout does not wake for two days. -1 food (tended them).", "food": -1},
        {"narrative": "Bones — not human — are found scattered in a circle near the Hollow. They are warm to the touch. +6 gold (collectors prize them). Something was here.", "gold": 6, "lore": "The bones belong to creatures that do not appear in any bestiary — they predate all known life."},
        {"narrative": "The petrified trees ring faintly when struck — a low, mournful chord that hangs in the air for minutes. A musician transcribes the melody and sells it as 'Ashfall's Lament.' +5 gold.", "gold": 5},
        {"narrative": "A sinkhole opens near the Sleeper's Hollow, revealing a chamber of fused glass and ancient bone. +8 stone, +4 gold (vitrified relics). Something's ribcage protrudes from the wall — far too large.", "stone": 8, "gold": 4},
        {"narrative": "At midnight, the entire copse glows a faint orange — embers rekindling for one heartbeat, then dying. No one sleeps well afterward, but pilgrims arrive by dawn. +6 gold, -1 food (hosting the curious).", "gold": 6, "food": -1},
        {"narrative": "A child born during the ashen vision dreams the copse every night. Their drawings of the Sleeper's shape are uncannily precise. Scholars pay +4 gold, and the people feel chosen.", "gold": 4},
        {"narrative": "A scout who touched the Hollow now has ash-grey eyes that see in perfect darkness. They guide a night expedition through the copse. +8 wood (rare charcoal), +3 gold (night-harvested resins).", "wood": 8, "gold": 3},
        {"narrative": "The ground around the Sleeper's Hollow ripples — once, twice — like a stone dropped in water. Tools left on the ground are found rearranged in spirals. +3 stone (uncovered by the tremor), -2 food (uneasy workers abandon their packs).", "stone": 3, "food": -2},
    ],
}


def generate_event(region, danger, world_obj=None):
    """Pick a random event — region-specific if available, else danger-tier generic."""
    # 40% chance of a region-specific event if one exists for this region
    if region in REGION_EVENTS and random.random() < 0.40:
        return random.choice(REGION_EVENTS[region]).copy()
    pool = EVENTS.get(danger, EVENTS["low"])
    return random.choice(pool).copy()


def apply_event(event, world_obj=None):
    """Modify kingdom resources based on event. May also set unlock flags."""
    for key, val in event.items():
        if key == "narrative":
            continue
        if key == "unlock":
            if world_obj and val not in world_obj.unlock_flags:
                world_obj.unlock_flags.add(val)
            continue
        if key == "lore":
            if world_obj:
                world_obj.collect_lore(val)
            continue
        if key == "pop":
            kingdom.population = max(1, kingdom.population + val)
            continue
        if key == "food":
            kingdom.food = max(0, kingdom.food + val)
        elif key == "wood":
            kingdom.wood = max(0, kingdom.wood + val)
        elif key == "stone":
            kingdom.stone = max(0, kingdom.stone + val)
        elif key == "gold":
            kingdom.gold = max(0, kingdom.gold + val)


# ── SINGLETON ───────────────────────────────────────────────
world = World()
