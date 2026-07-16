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
    "the_dreaming_deep": {
        "desc": "A liminal realm beneath the roots of all other regions — not a place of stone, but of memory made solid. The Sleepers walked here once, and their dreams still echo in the walls.",
        "yields": {"food": 3, "wood": 0, "stone": 5, "gold": 10},
        "event_chance": 0.60,
        "danger": "high",
        # 🔒 ULTIMATE: only discoverable after all 7 lairs are cleared
        "unlock_condition": "all_lairs_cleared",
        "landmark": "The Sleeper's Cradle — an immense hollow in the dreaming stone where one of the Sleepers once rested. The impression of its body is still visible in the rock, and the air here tastes of forgotten sunlight.",
        "notes": "This is the place beneath all places. When the last lair fell silent, something here stirred. The deep is dreaming again — but of what?",
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
            "migration": {"summer": "sunfire_plains"},  # follows berry season to the plains in summer
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
            "migration": {"winter": "the_vale"},  # wolves follow prey into sheltered valleys in winter
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
            "migration": {"autumn": "sunfire_plains"},  # drawn to plains warmth as temperatures drop
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
            "migration": {"autumn": "old_oak_ridge"},  # autumn fog drifts up to the ridge, wisps follow
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
            "migration": {"summer": "old_oak_ridge"},  # follows prey to ridge watering holes in summer drought
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
    "the_dreaming_deep": [
        {
            "name": "Dream-Husk",
            "danger": "medium",
            "type": "anomaly",
            "signs": [
                "The stone walls shimmer like heat-haze — and in the shimmer, shapes move that are not there when you look directly.",
                "A scout falls asleep standing up and speaks three words in a language no one knows. Then wakes, blinking.",
                "Footprints appear in the dust ahead of you — your own, but walking the opposite direction.",
            ],
            "encounter": "A figure — human-shaped but woven from dream-light and the memory of rain — stands at a fork in the deep. It wears your face, but younger. It speaks with your voice: 'Do not be afraid. You have been walking toward this place since the day the kingdom was founded.'",
            "stakes": {"gold": 8, "lore": "The Dream-Husks are not ghosts. They are the shapes the Sleeper gives to its own forgotten thoughts. Each one is a possibility that was never chosen."},
            "combat_stakes": {},
            "special": "Cannot be fought — striking a Dream-Husk only disperses it temporarily. Bargaining with one may reveal a hidden passage (chance to auto-discover a nearby lair or treasure).",
        },
        {
            "name": "Echo-Wyrm",
            "danger": "high",
            "type": "beast",
            "signs": [
                "A low, rhythmic thrumming vibrates through the stone — like a heartbeat, but slower. Much slower.",
                "Tunnels here spiral in patterns that make no geological sense. Something bored them.",
                "Scales the size of shields, shed and translucent, lie scattered at a tunnel junction.",
            ],
            "encounter": "The Echo-Wyrm erupts from the dreaming stone — a blind, pale serpent as thick as a man, its body pulsing with faint auroral light. It does not see you — it feels you through the stone. It is curious. It is also hungry.",
            "stakes": {"food": -3, "gold": 6},
            "combat_stakes": {"food": 12, "gold": 18, "pop": -2},
            "special": "Echo-Wyrm scales are prized by armorers (+8 gold if kingdom has a market). Its bore-tunnels sometimes intersect hidden caches of ancient wealth.",
        },
        {
            "name": "The Remembered",
            "danger": "high",
            "type": "anomaly",
            "signs": [
                "You hear your name spoken — not from ahead, but from inside your own memory. Someone you lost is calling.",
                "The air grows thick with voices, all speaking at once, all telling different stories. They quiet when you enter.",
                "A wall carving shows a circle of figures around a sleeping giant. One figure has your face. The carving is ancient.",
            ],
            "encounter": "They coalesce from the dreaming dark — not one being but many, a composite of every soul the Sleepers ever touched. They speak in unison: a choir of the forgotten. 'We are the Remembered. We have waited for the kingdom that remembers. Are you that kingdom?'",
            "stakes": {"gold": 20, "lore": "The Remembered are the collective memory of every civilization that rose and fell before the Cataclysm. They are the Sleeper's oldest dream — and its deepest grief."},
            "combat_stakes": {"gold": 40, "pop": -4},
            "special": "If the kingdom has an Elder with 70+ morale, the Remembered recognize a kindred spirit and grant their blessing freely. Otherwise, answering their question correctly (via narrative choice) yields +30 gold and a unique lore fragment.",
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
    "the_dreaming_deep": [
        "The elders speak in whispers of a place beneath all places — where the stone remembers "
        "and the air is thick with dreams. 'Only those who have conquered every fear may enter,' they say.",
        "A mad hermit on the ridge claims to have found a crack in the world that leads to a realm "
        "of living memories. 'The Sleepers walked there,' he mutters. 'They left a cradle.'",
        "The Remembered — all of them — wait in the deep. A scout who nearly died on the mesa says "
        "she saw them during her fever: a circle of faces, patient and eternal, asking if the kingdom "
        "is worthy yet.",
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
        "discovery_seasons": ["spring"],  # bears emerge from hibernation
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
        "discovery_seasons": ["winter"],  # wolves den up in winter, tracks in snow
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
        "discovery_seasons": ["autumn"],  # fog season, wisps most visible
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
        "discovery_seasons": ["autumn", "winter"],  # damp, dark conditions favor fungal growth
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
        "discovery_seasons": ["summer"],  # heat creates dust devils, mesa most visible
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
        "discovery_seasons": ["winter"],  # cold draws wraiths, the hot ground contrasts with snow
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
        "discovery_seasons": ["spring"],  # renewal, crystals grow faster in spring
        "discovery": "The Heart-Pool at the sanctum's center pulses with a rhythm that matches no living heart. The Crystal-Serpent is coiled around it — protective, ancient, and waiting for the question it has been asked to guard against.",
        "encounter": "The Crystal-Serpent rises to its full height — twenty feet of living prism. Every scale reflects a different world that might have been. Its voice is calm: 'Only those who know the full story may pass. Tell me: what woke the Sleeper in the north?'",
        "stakes": {"gold": 25, "lore": "The serpent shares the oldest memory: the Sleeper beneath the copse did not choose to stay. It was asked. By the first settlers. And the pact was: we remember you, and you sleep. We forget you, and you wake."},
        "combat_stakes": {"gold": 40, "stone": 25, "pop": -5},
        "cleared_bonus": "The Heart-Pool stabilizes into a permanent font of ancient knowledge. +5 gold/day, +2 stone/day, and all future lore fragments collected count as double.",
        "special": "If all 4 lore stories have been unveiled before challenging, the serpent yields without a fight — granting full rewards and the cleared bonus immediately.",
    },
    "the_dreaming_deep": {
        "name": "The Sleeper's Cradle",
        "boss": "The Remembered",
        "danger": "high",
        "discovery": "At the heart of the dreaming deep, the stone curves into an immense hollow — a cradle big enough to hold a mountain. The impression of a vast form is pressed into the rock. The air vibrates with a quiet, endless hum. This is where a Sleeper rested. Where it may yet rest again.",
        "encounter": "The Remembered gather at the cradle's edge — hundreds of forms, each one a memory of someone who walked these halls before. They part as you approach. At the center, a single figure: not a memory, but something older. It opens eyes that contain galaxies. 'You have cleared every lair. You have faced every fear. You are the kingdom that remembers. What do you ask of the Deep?'",
        "stakes": {"gold": 35, "lore": "The Sleeper's Cradle is not a grave — it is a promise. The Sleepers did not die. They are waiting. And the kingdom that remembers them all will be the one they wake for."},
        "combat_stakes": {"gold": 60, "stone": 30, "pop": -6},
        "cleared_bonus": "The Cradle hums with renewed life. +8 gold/day, +3 stone/day, +2 food/day. The Sleeper's dreams bless all harvests kingdom-wide (+5% to all region yields, stacks with all other bonuses).",
        "special": "If the kingdom has 5+ Ash-Blooms, the Remembered are awed — they bow and grant full rewards without a fight. If the kingdom has 150+ population, the Remembered see a worthy civilization and halve the combat stakes. This is the ultimate lair — clearing it grants the 'dreamer_kingdom' milestone.",
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
    "the_dreaming_deep": {
        "name": "Dream-Quake",
        "chance": 0.03,
        "narrative": (
            "DREAM-QUAKE: The dreaming stone shudders — the Sleeper is having a nightmare. "
            "Reality warps: walls ripple, gravity tilts, and for a terrifying moment, "
            "every citizen in Ashfall experiences the same dream — falling through "
            "darkness toward a light that never gets closer. Scouts in the deep report "
            "that the geography has... changed."
        ),
        "effects": {"gold": -15, "food": -5, "pop": -1},
        "recovery_day": 7,
        "recovery_msg": (
            "The dream-quake has passed. The deep has settled into a new configuration — "
            "stranger, perhaps, but no less navigable. Scouts find that some passages "
            "that were dead ends now lead somewhere new. The Sleeper's nightmare "
            "has left a gift: +10 gold in crystallized dream-residue."
        ),
        "special": "dream_gift",
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
        self._lair_interacted = set()   # (region, day_struck) tuples already processed
        self._ash_blooms_collected = 0  # how many Ash-Blooms have been picked
        self._ash_bloom_milestones = set()  # milestones already triggered (3, 5, 10...)
        self._pending_creature_followups = []  # (day_due, region, event_type, data) tuples
        self._vale_stag_blessing = False  # active blessing from Vale-Stag
        self._thornbear_avoided = False   # Thorn-Bear avoided — follow-up pending
        self._oakwyrm_venom_pending = False  # Oak-Wyrm venom processing pending
        self._bogwisp_following = False   # Bog-Wisp trail being followed
        self._gloom_bloom_fired = False  # Gloom-Lantern bloom-field narrative already triggered
        self._echo_wyrm_last_shed = 0  # day Echo-Wyrm last shed scales (dream-harvest)
        self._memory_wisp_last_harvest = 0  # day Memory-Wisps last delivered dream-harvest
        self._deep_whisper_next_day = 0  # day next deep whisper event fires (initialized on deep discovery)
        self._last_migration_season = self.season  # track season changes for creature migration
        self._migration_log = []  # (day, creature_name, from_region, to_region, season) records
        self._deep_resonance_fired_today = False  # set by people.py when deep-echo dream + T3+ whisper collide
        self._deep_resonance_tier = 0  # whisper tier that triggered the resonance
        self._migration_disaster_processed = set()  # (region, day_struck) pairs already processed for migration-disaster interaction
        self._dream_husk_market_day = 0  # day Dream-Husks visit the market (deep-resonance tier 2)
        self._last_rare_event = {}       # region -> day of last rare event (for combo chains)
        self._deep_resonance_amplify_lairs = False  # consumed by _check_lair_activity for guaranteed seasonal bonuses
        self._creature_migration_counts = {}  # (creature_name, home_region) -> total migrations tracked
        self._rare_combo_region = set()       # regions where a combo chain is active (trifecta possible)
        self._rare_combo_first_day = {}       # region -> day of first rare in active combo chain
        self._trifecta_fired = set()           # regions where triple-rare wonder has fired (once per game each)
        self._trifecta_bonuses = {}            # region -> {"gold": N, "food": N, ...} daily passive bonuses
        self._regional_vision_region = None    # set when a regional vision fires (bridge to dream-bond)
        self._regional_vision_day = 0          # the day the vision fired
        self._veteran_caches = {}              # (creature_name, home_region) -> {"gold": N, "food": N, ...} daily passives

    # ── DISCOVERY ────────────────────────────────────────────

    def can_discover(self, region):
        """Check if a region is eligible for discovery (unlock conditions met)."""
        if region not in TERRAIN:
            return False
        cond = TERRAIN[region].get("unlock_condition")
        if cond is None:
            return True
        if cond == "all_lairs_cleared":
            # All 7 lairs must be cleared
            all_lair_regions = [r for r in LAIRS]
            return all(r in self._cleared_lairs for r in all_lair_regions)
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
            apply_event(event, self, region)
            # Rarity badge for daily log
            rarity = event.get("rarity", "common")
            badge = {"uncommon": "✨ ", "rare": "💎 "}.get(rarity, "")
            self.world_log.append(f"Event in {region}: {badge}{event.get('narrative', '')}")

            # ── Region Event Combo Chains (Tier 2) & Trifecta Wonders (Tier 3) ──
            # Two rare events in the same region within 30 days → combo
            # Three rare events within 30 days of the FIRST → once-per-game trifecta wonder
            if rarity == "rare":
                last_rare_day = self._last_rare_event.get(region, -999)
                combo_active = region in self._rare_combo_region
                combo_first_day = self._rare_combo_first_day.get(region, -999)

                if combo_active and self.day - combo_first_day <= 30:
                    # TRIFECTA! Third rare event in the chain
                    if region not in self._trifecta_fired:
                        self._trifecta_fired.add(region)
                        self._fire_trifecta_wonder(region, event)
                    # Clear combo tracking — the chain is complete
                    self._rare_combo_region.discard(region)
                    self._rare_combo_first_day.pop(region, None)
                elif self.day - last_rare_day <= 30 and last_rare_day > 0:
                    # COMBO! Second rare event — fire the combo chain
                    self._fire_combo_chain(region, event)
                    # Mark this region as having an active combo chain (watching for trifecta)
                    self._rare_combo_region.add(region)
                    # Store the first rare's day (the earlier of the two)
                    self._rare_combo_first_day[region] = min(self.day, last_rare_day)

                self._last_rare_event[region] = self.day

            return event
        return None

    def _fire_combo_chain(self, region, current_event):
        """Two rare events have fired in the same region within 30 days.
        Trigger a unique combo narrative with bonus resources."""
        region_names = {
            "the_vale": "the Vale",
            "old_oak_ridge": "the Ridge",
            "glimmer_marsh": "the Marsh",
            "sunfire_plains": "the Plains",
            "ironroot_depths": "the Depths",
            "the_ashen_copse": "the Copse",
            "the_sunken_sanctum": "the Sanctum",
            "the_dreaming_deep": "the Dreaming Deep",
        }
        rname = region_names.get(region, region)
        combo_gold = random.randint(10, 25)
        combo_food = random.randint(3, 8)
        combo_stone = random.randint(2, 6)

        # Region-specific combo narratives
        COMBO_NARRATIVES = {
            "the_vale": [
                f"The Whispering Spring has spoken twice in a single moon — first a prophecy, now a confirmation. The waters run silver, and the vale itself seems to hold its breath. Those who drink from the spring claim they can hear the Sleeper's heartbeat (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"Two revelations from the vale in quick succession: the earth splits near the spring, revealing a vein of crystallized memory. The elders say {rname} has chosen this generation to receive its secrets (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
            "old_oak_ridge": [
                f"The Eldertrunk stirs twice in a season — roots cracking stone, branches reaching for stars. A root-staircase descends into a chamber no one knew existed: a Corvid-Kin library, its shelves still intact (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"The ridge has spoken through two rare omens. Between them, a new path opens — not a road, but a pattern of fallen leaves that, when followed, leads to a cache of pre-Cataclysm scrolls (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
            "glimmer_marsh": [
                f"The Drowned Cairn has risen twice — each time higher, each time brighter. The standing stones now form a complete ring, and at its center: a pool of liquid moonlight that hardens into trade-bars when touched (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"Two marsh-revelations in one season: the bog-wisps dance in patterns that form a map, and the cairn-stones hum with a frequency that makes buried gold vibrate to the surface (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
            "sunfire_plains": [
                f"The Sunspire has ignited twice — twin pillars of light visible from every territory. Between them, the plains yield up a bounty: windfall seeds that sprout overnight, and coins that glittered in the sun like scattered stars (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"Two rare events on the plains, and the land itself responds: a mesa-wall collapses to reveal an ancient waystation, its vaults still stocked with trade goods from before the Cataclysm (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
            "ironroot_depths": [
                f"The Sealed Door has cracked twice — each time weeping a crystalline tear. When the second tear falls, both merge into a single gemstone the size of a fist. It pulses with a cold, blue light — a fragment of the deep earth's memory (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"Two omens from the depths: the forges burn brighter, the sealed tunnels echo with hammer-falls. Miners break through to a geode chamber — amethyst crystals as long as a man's arm (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
            "the_ashen_copse": [
                f"The ash-figure has walked the copse twice — first tending trees, now planting new ones. Where its feet touch the ash, ash-blooms sprout in clusters of five and six. The harvest is unprecedented (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"Two copse-visions in a single season: the ash-figure returns with a companion — a shape made of smoke and memory. Together they trace a pattern in the ash that, when copied, reveals hidden caches all across {rname} (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
            "the_sunken_sanctum": [
                f"The Heart-Pool has risen twice — and when it recedes the second time, it leaves behind crystalline growths shaped like tiny versions of the Cradle. Each one hums when held (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"Two sanctum-wonders in quick succession: the dreaming-stone veins pulse in synchrony, and the chromatic dust settles into a mural depicting the Sleeper's awakening. Pilgrims arrive unbidden (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
            "the_dreaming_deep": [
                f"The Cradle has sung twice — and on the second song, the Echo-Wyrms join in harmony. The combined sound crystallizes into floating motes of pure dreaming-stone, which drift gently into waiting hands (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
                f"Two deep-miracles in one cycle: the transparent walls show the same vision twice — first as prophecy, then as memory. Between them, the Remembered leave gifts that were not there before (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
            ],
        }

        narratives = COMBO_NARRATIVES.get(region, [
            f"Two rare events in {rname} within a single cycle — the land itself seems to be trying to speak. Scouts find a convergence point where both events' energies pooled, yielding unexpected treasure (+{combo_gold}g, +{combo_food}f, +{combo_stone}s).",
        ])

        narrative = random.choice(narratives)
        kingdom.gold = max(0, kingdom.gold + combo_gold)
        kingdom.food = max(0, kingdom.food + combo_food)
        kingdom.stone = max(0, kingdom.stone + combo_stone)

        self.world_log.append(f"🔗💎 RARE EVENT COMBO [{region}]: {narrative}")
        kingdom.kingdom_log.append(
            f"🔗💎 RARE EVENT COMBO: Two rare events in {rname} within 30 days — the land speaks in patterns."
        )

        # 40% chance of a lore fragment from the combo
        if random.random() < 0.40:
            combo_lore = [
                f"The coincidence of two rare events in {rname} revealed a pattern — the land has a memory, and it repeats itself in cycles. The Sleeper dreams in recurring motifs.",
                f"Two omens in {rname} — and between them, a hidden truth: the rare events are not random. They are the Sleeper's thoughts, surfacing where the border between waking and dreaming is thinnest.",
                f"The people of Ashfall have learned something profound: when {rname} speaks twice, listen. The second voice always clarifies the first.",
            ]
            self.collect_lore(random.choice(combo_lore))
            self.world_log.append("  The double-omen revealed a hidden pattern — a lore fragment.")

    def _fire_trifecta_wonder(self, region, current_event):
        """Three rare events have fired in the same region within 30 days of the first.
        This is a once-per-game wonder event — massive payout, permanent small bonus,
        unique narrative. Each region can only experience this once."""
        region_names = {
            "the_vale": "the Vale",
            "old_oak_ridge": "the Ridge",
            "glimmer_marsh": "the Marsh",
            "sunfire_plains": "the Plains",
            "ironroot_depths": "the Depths",
            "the_ashen_copse": "the Copse",
            "the_sunken_sanctum": "the Sanctum",
            "the_dreaming_deep": "the Dreaming Deep",
        }
        rname = region_names.get(region, region)
        tri_gold = random.randint(20, 40)
        tri_food = random.randint(6, 15)
        tri_stone = random.randint(4, 12)

        # Region-specific trifecta wonder narratives
        TRIFECTA_NARRATIVES = {
            "the_vale": [
                f"THREE omens in {rname} — the Whispering Spring, the vale's oldest voice, has spoken a third time. The waters do not merely shimmer; they rise into a floating column, and within it: the face of the Sleeper, gentle and vast. The spring speaks not in riddles now, but in prophecy: 'The northern fire comes, but the vale will be the first shield. Plant hawthorn. Plant deep. I will make them grow.' Every hawthorn in {rname} flowers simultaneously, and the berries glow with faint gold. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: hawthorn thickets now yield +1 food/day from the Sleeper's blessing.",
                f"A TRIFECTA in {rname}: three rare signs in a single cycle — and the vale answers. The ground opens in a spiral of wildflowers, revealing a staircase of living root that descends into a chamber the Sleepers carved before the Cataclysm. Inside: a single, perfect seed the size of a fist, warm and humming. The elders plant it at the kingdom's heart. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Sleeper's seed grows — +2 food/day kingdom-wide.",
            ],
            "old_oak_ridge": [
                f"A TRIFECTA on {rname}! The Eldertrunk, already stirred twice, now opens fully — a door in its bark that leads not to a hollow, but to the dreaming deep itself. The Corvid-Kin who once served the Sleepers left a final gift: a feather of pure gold, as long as a man's arm, that sings when the wind passes over it. It now hangs in the council chamber. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Corvid-Kin feather grants +1 gold/day and +5% lore chance on all ridge events.",
                f"Three rare omens on the ridge — and the ancient oaks themselves walk. Not far, not fast — but their roots pull free of the earth, and they shuffle a few paces downhill, revealing what they have hidden for millennia: a circle of standing stones, each one carved with a Sleeper's name. The Remembered recognize them all. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Named Stones — +2 stone/day, +1 lore fragment every 10 days.",
            ],
            "glimmer_marsh": [
                f"THREE omens in {rname} — the Drowned Cairn completes its rise. The ring of standing stones is now a perfect circle, and at its center: a throne of solidified bog-light, waiting. The bog-wisps bow to it. The Remembered say it is the Seat of the Rememberer — the Sleeper's own chair, left here in case it ever chose to visit. No one sits in it. But sometimes, at dusk, it hums. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Seat of the Rememberer — +3 gold/day, +10% disease resistance (the marsh purifies itself).",
                f"A TRIFECTA in {rname}: the marsh has given up its oldest secret. The bog-wisps, three times roused, now reveal that they are not lost souls — they are fragments of the Rememberer's own consciousness, scattered when it first lay down to sleep. They coalesce into a single, coherent voice: 'Thank you. We had forgotten what it felt like to be remembered.' The voice's gratitude crystallizes into floating motes of pure gold. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: +2 gold/day from grateful wisps.",
            ],
            "sunfire_plains": [
                f"A TRIFECTA on {rname}: the Sunspire ignites for a third time — and this time, it stays lit. The pillar of golden light becomes permanent, visible from every region, a beacon that banishes shadows within a mile. The First Fire's fragment has awakened fully — not to burn, but to guide. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Eternal Sunspire — +3 gold/day (pilgrims flock to the light), +5% disease resistance (the light cleanses).",
                f"Three rare omens on the plains: the dust-devils dance in a triple spiral that carves a pattern into the earth — a map of all the Sleepers' migration routes, every path they ever walked. Scouts who study it can see how to reach regions still undiscovered, and the plains yield up a buried cache of pre-Cataclysm grain that still sprouts. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Dust-Map — +2 food/day, scouts find undiscovered regions 50% faster.",
            ],
            "ironroot_depths": [
                f"THREE rare omens in {rname} — and the Sealed Door, cracked twice before, swings fully open. Beyond it: not darkness, but a vast underground garden lit by dreaming-stone veins. Trees of crystal. Flowers that sing. A Sleeper's personal sanctuary, preserved since the Cataclysm. The deepwardens weep. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Sleeper's Garden — +2 food/day, +2 stone/day, +1 gold/day from crystal harvests.",
                f"A TRIFECTA in {rname}: the forges burn with a flame that needs no fuel — a fragment of the First Fire, trapped in the depths since the Cataclysm, finally freed by three omens aligning. Every smith in Ashfall works through the night, and every tool they forge has a faint gold shimmer. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the First Forge — +3 gold/day (legendary tools command premium prices), +2 stone/day (ore smelts itself).",
            ],
            "the_ashen_copse": [
                f"A TRIFECTA in {rname}: the ash-figure walked once, then twice — and now it speaks. Its voice is the sound of embers and old promises: 'I have waited for you. All of you. Not just the child with ash-grey eyes — all of you.' The petrified trees nearest the Sleeper's Hollow burst into brief, cold flame and emerge... green. Alive. The Sleeper has begun to reverse the Cataclysm. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Greening — the_ashen_copse now yields +2 food/day (living trees!) and +3 wood/day.",
                f"THREE omens in {rname} — and the Sleeper's Hollow exhales not once but continuously, a warm breeze that carries the scent of a world before fire. Ash-Blooms erupt across the entire copse — not one or two, but thirty-seven. When harvested, each one contains not a memory but a skill: a song, a craft, a lost technique. The kingdom's artisans learn arts from before the Cataclysm. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Bloom-Harvest — +5 gold/day from ancient crafts, +3 food/day (bloom-enhanced crops).",
            ],
            "the_sunken_sanctum": [
                f"A TRIFECTA in {rname}: the Heart-Pool rises a third time — and this time, it does not fall back. The sphere of liquid light hovers permanently above the basin, and within it: the Sleeper's face, ever-watchful, ever-grateful. The sanctum is no longer a hidden ruin — it is a living temple. Pilgrims arrive from beyond Ashfall's borders. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Living Heart-Pool — +5 gold/day, +3 stone/day, all lore fragments collected count as double.",
                f"THREE omens beneath the earth: the Crystal-Serpent, twice seen, now bows permanently. It coils around the Heart-Pool and becomes translucent — a guardian of living crystal who will answer questions about the Sleepers' history. Scholars who ask respectfully receive answers. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Crystal Oracle — +3 gold/day, +1 lore fragment every 5 days.",
            ],
            "the_dreaming_deep": [
                f"A TRIFECTA in {rname} — the ultimate region, the place beneath all places, has spoken three times. And now the Cradle begins to move. Not the stone — the impression within it. The Sleeper's outline shifts, as if the being it holds is stretching for the first time in ten thousand years. The Remembered fall to their knees. The Dream-Husks weep light. The Sleeper is not awake — but it is no longer fully asleep. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Stirring — +8 gold/day, +4 food/day, +4 stone/day, and deep whispers now fire every 5-8 days (was 6-10 at T3+).",
                f"THREE rare omens in the dreaming deep — and the transparent walls, which once showed other worlds, now show THIS world. Ashfall. But not today's Ashfall — tomorrow's. The views are of a kingdom where the Sleeper walks, where the northern fire has come and been turned back, where children play in gardens grown from dreaming-stone. It is a promise. The Remembered call it 'the Inevitable.' +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: the Inevitable Vision — +5 gold/day, +3 food/day, kingdom-wide morale never drops below 40.",
            ],
        }

        narratives = TRIFECTA_NARRATIVES.get(region, [
            f"THREE rare omens in {rname} within a single cycle — a once-in-a-generation convergence. The land itself seems to hold its breath, and then... releases. Scouts find a convergence point where all three events' energies pooled, yielding extraordinary treasure. The chroniclers record this as a Wonder. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: +3 gold/day, +2 food/day from the wonder site.",
            f"A TRIFECTA WONDER in {rname}! Three rare events aligned, and the kingdom will speak of this day for generations. The boundary between waking and dreaming dissolved for a full minute — and when it reformed, it left behind a permanent gift: a small patch of dreaming-stone that renews itself daily. +{tri_gold}g, +{tri_food}f, +{tri_stone}s. Permanent: +2 stone/day, +2 gold/day from the dreaming-stone patch.",
        ])

        narrative = random.choice(narratives)
        kingdom.gold = max(0, kingdom.gold + tri_gold)
        kingdom.food = max(0, kingdom.food + tri_food)
        kingdom.stone = max(0, kingdom.stone + tri_stone)

        # ── Permanent passive bonuses ──
        # Each region's trifecta wonder grants a unique daily passive.
        # These are the mechanical payouts referenced in the narrative text.
        TRIFECTA_PASSIVES = {
            "the_vale": {"food": 1, "gold": 1},
            "old_oak_ridge": {"gold": 1, "stone": 2, "lore_every_10_days": True},
            "glimmer_marsh": {"gold": 2, "disease_resist_pct": 10},
            "sunfire_plains": {"gold": 2, "food": 1},
            "ironroot_depths": {"food": 1, "gold": 2, "stone": 2},
            "the_ashen_copse": {"food": 2, "gold": 3, "wood": 2},
            "the_sunken_sanctum": {"gold": 4, "stone": 2, "lore_double": True},
            "the_dreaming_deep": {"gold": 6, "food": 3, "stone": 3, "whisper_fast": True},
        }
        self._trifecta_bonuses[region] = TRIFECTA_PASSIVES.get(region, {"gold": 2, "food": 1, "stone": 1})

        self.world_log.append(
            f"🔗💎🌟 TRIFECTA WONDER [{region}]: {narrative}"
        )
        kingdom.kingdom_log.append(
            f"🔗💎🌟 TRIFECTA WONDER: Three rare events in {rname} within a single cycle — "
            f"a once-per-game wonder! The kingdom will never forget this day."
        )

        # 100% chance of a lore fragment from a trifecta
        tri_lore = [
            f"The trifecta wonder in {rname} revealed the deepest truth yet: the rare events are not random chance. They are the Sleeper's heartbeat, pulsing through the land — and three beats in a cycle means the Sleeper is dreaming of urgency. Something is coming. Something must be prepared.",
            f"Three rare omens in {rname} — and the pattern is now clear. The Sleepers did not simply fall asleep. They are dreaming the kingdom into existence. Every rare event is a dream-thought, and three in a row is the Sleeper actively shaping the future. Ashfall was not an accident. It was a design, dreamed ten thousand years ago.",
            f"The trifecta in {rname} has changed everything the scholars thought they knew. The Remembered confirm it: the Sleeper beneath the copse is the Rememberer, the youngest and most hopeful of its kind. It chose to stay not out of duty, but out of love — and its three omens are its way of saying: 'I am almost ready. Wait for me.'",
        ]
        self.collect_lore(random.choice(tri_lore))
        self.world_log.append("  The trifecta wonder revealed a fundamental truth — a lore fragment crystallized from the convergence.")

    # ── DAY CYCLE ────────────────────────────────────────────

    def advance_day(self):
        """Advance the world by one day."""
        self.day += 1
        self.regions_explored_today = []
        # Reset daily flags for cross-system resonance
        # NOTE: _deep_whisper_fired_today is set here and consumed by people.py same-day
        # NOTE: _deep_resonance_fired_today is set by people.py and consumed NEXT day — reset in _check_deep_resonance_effects()
        self._deep_whisper_fired_today = False
        self._deep_whisper_tier = 0
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

        # Check deep-resonance world-side effects (set by people.py when dreams+whispers collide)
        # Must fire BEFORE _check_lair_activity so resonance can amplify seasonal lair bonuses
        self._check_deep_resonance_effects()

        # Check lair activity (passive effects, gloom-saturation)
        self._check_lair_activity()

        # Check for lair echoes (flavor events from cleared lairs)
        self._lair_echoes()

        # Check Ash-Bloom milestones (Sleeper's memory fragments)
        self._check_ash_bloom_milestones()

        # Apply Ash-Bloom passive daily bonuses
        self._apply_ash_bloom_passives()

        # Apply Trifecta Wonder permanent passive bonuses
        self._apply_trifecta_passives()

        # Apply Veteran Creature Cache passive daily bonuses
        self._apply_veteran_cache_passives()

        # Check pending creature follow-up events
        self._check_creature_followups()

        # Check for seasonal creature migrations
        self._check_migrations()

        # Check for deep whispers (dreaming-deep periodic omens)
        self._check_deep_whispers()

        # Check for region-specific disasters
        self._check_disasters()

        # Check migration-disaster interactions (creatures caught in disasters)
        self._check_migration_disaster_interaction()

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
        # Seasonal bias: preferred season = 25%, neutral = 15%, off-season = 10%
        if region in LAIRS and region not in self._discovered_lairs:
            lair = LAIRS[region]
            discover_chance = 0.15  # base
            preferred = lair.get("discovery_seasons")
            if preferred is not None:
                if self.season in preferred:
                    discover_chance = 0.25  # preferred season — much more likely
                else:
                    discover_chance = 0.10  # off-season — harder to find
            if random.random() < discover_chance:
                self._discovered_lairs[region] = lair["name"]
                season_hint = ""
                if preferred and self.season in preferred:
                    season_hint = " The season made it easier to find."
                elif preferred:
                    season_hint = " It would have been easier in the right season."
                self.world_log.append(
                    f"LAIR DISCOVERED: {lair['name']} in {region}! {lair['discovery']}{season_hint}"
                )


        # Creature encounter on deep-scout — you're going deeper into the wilds
        if region in CREATURES and random.random() < 0.40:
            encounter = self.creature_encounter(region)
            if encounter:
                self.world_log.append(
                    f"🐾 While deep-scouting {region}: {encounter['narrative'][:80]}..."
                )
                # Auto-resolve: fight if low danger and we're strong, otherwise avoid
                if encounter["danger"] == "low" and kingdom.defense_rating(self) >= 30:
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
            "the_dreaming_deep": (2, 2),
        }

        symbols = {
            "the_vale":         "🌿",
            "old_oak_ridge":    "🌳",
            "glimmer_marsh":    "💧",
            "ironroot_depths":  "⛏️",
            "sunfire_plains":   "☀️",
            "the_ashen_copse":  "🔥",
            "the_sunken_sanctum": "💎",
            "the_dreaming_deep": "🌌",
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
                        "ironroot_depths", "sunfire_plains", "the_ashen_copse",
                        "the_sunken_sanctum", "the_dreaming_deep"]
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

        # ── Ash-Bloom Status ──
        if self._ash_blooms_collected > 0:
            lines.append("")
            lines.append("─── Ash-Bloom Collection ───")
            lines.append(f"  \U0001f338 Blooms collected: {self._ash_blooms_collected}")
            milestones_hit = sorted(self._ash_bloom_milestones)
            if milestones_hit:
                names = {3: "Sleeper Dreams", 5: "Sleeper Remembers", 10: "Sleeper Speaks", 15: "Sleeper's Gift"}
                for m in milestones_hit:
                    lines.append(f"    \U0001f31f Milestone: {names.get(m, f'Threshold {m}')} ({m} blooms)")
            next_milestone = None
            for threshold in [3, 5, 10, 15]:
                if threshold not in self._ash_bloom_milestones:
                    next_milestone = threshold
                    break
            if next_milestone:
                needed = next_milestone - self._ash_blooms_collected
                lines.append(f"    → Next milestone at {next_milestone} blooms ({needed} more needed)")

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
        """Add a lore fragment. Returns True if it's new.
        If any trifecta wonder grants lore_double, each fragment is counted twice."""
        result = False
        if fragment not in self.lore_fragments:
            self.lore_fragments.append(fragment)
            self.world_log.append(f"📖 Lore fragment collected: {fragment[:40]}...")
            result = True
        # Trifecta wonder: lore_double — all fragments count as double
        for region, bonuses in self._trifecta_bonuses.items():
            if bonuses.get("lore_double"):
                doubled = fragment + " [doubled by the Living Heart-Pool's resonance]"
                if doubled not in self.lore_fragments:
                    self.lore_fragments.append(doubled)
                break
        return result

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

        # Ash-Bloom milestone 10: sleeper_alliance
        if 10 in self._ash_bloom_milestones:
            bonus += 5  # The Sleeper actively defends the land

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
            # ── Trade Synergy Lore Chance: Memory Road may whisper lore even without an omen ──
            synergy_bonuses = kingdom.trade_synergy_bonuses()
            lore_chance = synergy_bonuses.get("lore_chance_pct", 0) / 100.0
            if lore_chance > 0 and random.random() < lore_chance:
                fragment = (
                    f"Trade route whispers: merchants on the Memory Road "
                    f"brought back a tale — 'The Sleepers did not die. They are waiting.' "
                    f"A scrap of old knowledge, carried on trade winds."
                )
                self.collect_lore(fragment)
                self.world_log.append(f"📖 Trade lore: {fragment[:60]}...")
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
            self._ash_blooms_collected += 1
            bloom_num = self._ash_blooms_collected
            ash_bloom_msg = (
                f"\U0001f338 An Ash-Bloom crystallizes in the_ashen_copse \u2014 the Sleeper's stirring "
                f"has coaxed a flower of frozen fire from the petrified wood. +12 gold. "
                f"[Bloom #{bloom_num} collected]"
            )
            kingdom.gold += 12
            self.world_log.append(ash_bloom_msg)
            if "ash_bloom" not in omen:
                omen["ash_bloom"] = True
                omen["gold"] = omen.get("gold", 0) + 12
                if "narrative" in omen:
                    omen["narrative"] += f" An Ash-Bloom crystallized in the copse. [Bloom #{bloom_num}]"
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

    def _creatures_in_region(self, region):
        """Return all creatures currently present in a region, including migratory ones.
        Migratory creatures appear in their destination region during the migration season
        AND remain in their home region (they can be encountered in transit or at either end)."""
        creatures = []
        seen = set()

        # First: resident creatures (home region)
        if region in CREATURES:
            for c in CREATURES[region]:
                key = (region, c["name"])
                if key not in seen:
                    creatures.append(c)
                    seen.add(key)

        # Second: migratory creatures from other regions currently in this region
        for home_region, creature_list in CREATURES.items():
            if home_region == region:
                continue
            for c in creature_list:
                migration = c.get("migration", {})
                if self.season in migration and migration[self.season] == region:
                    key = (home_region, c["name"])
                    if key not in seen:
                        migratory_c = c.copy()
                        migratory_c["_migrated_from"] = home_region
                        migratory_c["_migratory"] = True
                        creatures.append(migratory_c)
                        seen.add(key)

        return creatures

    def _creature_signs(self, region):
        """Return a random ambient sign of creature activity in a region.
        Used for flavor in scout reports and exploration.
        Includes migratory creatures currently in the region."""
        if region not in self.discovered:
            return None
        creatures = self._creatures_in_region(region)
        if not creatures:
            return None
        creature = random.choice(creatures)
        if creature.get("signs"):
            sign = random.choice(creature["signs"])
            # Add migration context to the sign
            if creature.get("_migratory"):
                sign = sign + f" (The {creature['name']} has wandered here from {creature['_migrated_from']} — a seasonal visitor.)"
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
            self._check_all_lairs_cleared()
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
            self._check_all_lairs_cleared()
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

    def _check_all_lairs_cleared(self):
        """If all 7 lairs are cleared, unlock the_dreaming_deep."""
        # Exclude the_dreaming_deep from the check — it's the 8th region unlocked BY clearing the other 7
        all_lair_regions = [r for r in LAIRS if r in TERRAIN and r != "the_dreaming_deep"]
        if all(r in self._cleared_lairs for r in all_lair_regions):
            if "all_lairs_cleared" not in self.unlock_flags:
                self.unlock_flags.add("all_lairs_cleared")
                self.world_log.append(
                    "\U0001f31f ALL LAIRS CLEARED: Every lair in the known world has been "
                    "conquered. The kingdom stands unchallenged. And in the silence "
                    "that follows... something stirs. The dreaming deep has opened. "
                    "A realm beneath all realms — the_dreaming_deep — can now be discovered."
                )
                # Auto-discover if conditions are met
                if "the_dreaming_deep" not in self.discovered:
                    self.discover("the_dreaming_deep")

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

    
    def _process_lair_disaster_interaction(self, region, disaster_name):
        """Process lair-disaster interaction for a region hit by disaster.
        Called once per disaster instance (tracked by _lair_interacted).

        Lair exposure chance now scales with the lair's discovery season:
          - Preferred season: 55% (disaster tears open the lair's hiding place)
          - No preference:    30% (neutral — as before)
          - Off-season:       15% (the lair is dormant, harder to expose)
        Returns the interaction type string or None."""
        if region not in LAIRS:
            return None

        lair = LAIRS[region]
        lair_name = lair["name"]

        if region not in self._discovered_lairs:
            # Undiscovered lair: disaster may expose it, with seasonal bias
            expose_chance = 0.30  # base
            preferred = lair.get("discovery_seasons")
            if preferred is not None:
                if self.season in preferred:
                    expose_chance = 0.55  # preferred season — disaster tears open hiding place
                else:
                    expose_chance = 0.15  # off-season — lair is dormant, harder to expose
            if random.random() < expose_chance:
                self._discovered_lairs[region] = lair_name
                season_note = ""
                if preferred and self.season in preferred:
                    season_note = " The season's conditions made the lair vulnerable to exposure."
                elif preferred:
                    season_note = " It might have stayed hidden in a gentler season."
                self.world_log.append(
                    f"🏚️ The {disaster_name} has exposed a hidden lair in {region}: "
                    f"{lair_name}! {lair['discovery'][:80]}...{season_note}"
                )
                return "revealed"
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
            return "enraged"
        elif region in self._cleared_lairs:
            # Cleared lair: 10% chance it destabilizes
            if random.random() < 0.10:
                self._cleared_lairs.discard(region)
                self.world_log.append(
                    f"⚠️ LAIR DESTABILIZED: The {disaster_name} has reopened "
                    f"{lair_name} in {region}! It must be cleared again."
                )
                return "destabilized"
        return None

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
                    elif special == "dream_gift":
                        kingdom.gold += 10
                        self.world_log.append(
                            "Scouts collect crystallized dream-residue from the dreaming deep (+10 gold).")
                        if random.random() < 0.40:
                            lore = ("In the dream-quake's wake, a wall carving is revealed "
                                    "that was not there before: the Sleepers, all of them, "
                                    "standing in a circle around a star. Beneath it, "
                                    "a single word in the old tongue: TOGETHER.")
                            self.collect_lore(lore)
                            self.world_log.append(
                                "The dream-quake exposed a new carving — a lore fragment!")

                    del self._active_disasters[region]
                    self._disaster_cooldown[region] = self.day + random.randint(10, 20)
                    results.append({"type": "recovery", "region": region,
                                    "special": special})
                # ── Lair interaction for active disaster (fires once) ──
                lair_key = (region, active["day_struck"])
                if lair_key not in self._lair_interacted:
                    interaction = self._process_lair_disaster_interaction(
                        region, active["name"])
                    if interaction is not None:
                        self._lair_interacted.add(lair_key)
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
                lair_key = (region, self.day)
                lair_interaction = self._process_lair_disaster_interaction(
                    region, disaster["name"])
                if lair_interaction is not None:
                    self._lair_interacted.add(lair_key)

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

    def _check_migration_disaster_interaction(self):
        """Check if migratory creatures are caught in active disasters.
        When a disaster strikes a region with migratory creatures, special interactions fire.
        Called from advance_day() right after _check_disasters()."""
        results = []
        for region, active in list(self._active_disasters.items()):
            # Only process disasters that struck TODAY (not ongoing ones from prior days)
            if active["day_struck"] != self.day:
                continue
            # Already processed this disaster for migration interaction?
            key = (region, active["day_struck"])
            if key in self._migration_disaster_processed:
                continue
            self._migration_disaster_processed.add(key)

            # Find migratory creatures in this region
            creatures = self._creatures_in_region(region)
            migrators = [c for c in creatures if c.get("_migratory")]
            if not migrators:
                continue

            disaster_name = active.get("name", DISASTERS.get(region, {}).get("name", "a disaster"))

            for creature in migrators:
                home = creature.get("_migrated_from", "unknown")
                cname = creature["name"]
                ctype = creature.get("type", "beast")

                # Build a unique interaction narrative based on creature + disaster
                interaction_key = (cname, disaster_name)
                narratives = self._migration_disaster_narratives(creature, disaster_name, region, home)

                if narratives:
                    narrative = random.choice(narratives)
                    gold_bonus = random.randint(3, 8)
                    food_bonus = random.randint(1, 4)

                    self.world_log.append(
                        f"\U0001f43e🐾 MIGRATION-DISASTER: {narrative} (+{gold_bonus} gold, +{food_bonus} food)"
                    )
                    kingdom.gold = max(0, kingdom.gold + gold_bonus)
                    kingdom.food = max(0, kingdom.food + food_bonus)

                    # 20% chance of lore fragment from the unusual encounter
                    if random.random() < 0.20:
                        lore_narratives = [
                            f"A {cname}, displaced by the {disaster_name} in {region}, left behind something that was not from this world — a memory-stone that hums when held.",
                            f"While fleeing the {disaster_name}, the {cname} unearthed an ancient relic buried beneath {region} — a fragment of the old world, preserved by chance.",
                            f"In the chaos of the {disaster_name}, scouts found where the {cname} had been digging: a cache of pre-Cataclysm artifacts, exposed by the creature's desperate flight.",
                        ]
                        self.collect_lore(random.choice(lore_narratives))
                        self.world_log.append(
                            f"  The {cname}'s panic revealed a hidden relic — a lore fragment!"
                        )

                    results.append({
                        "region": region, "creature": cname, "disaster": disaster_name,
                        "narrative": narrative, "gold": gold_bonus, "food": food_bonus,
                    })

        return results if results else None

    def _migration_disaster_narratives(self, creature, disaster_name, region, home):
        """Return a list of possible narratives for a creature caught in a disaster.
        Each is a one-line story about how the creature reacts."""
        cname = creature["name"]
        ctype = creature.get("type", "beast")

        # Shared narrative templates
        templates = []

        # Beast-specific
        if ctype == "beast":
            templates = [
                f"The {cname}, having migrated from {home} to {region}, is caught in the {disaster_name}. Panicked, it flees — and in its wake, it leaves behind scavenged treasures from its old territory.",
                f"Displaced by the {disaster_name}, a {cname} from {home} crashes through {region} in a blind panic. Scouts track its trail to a cache of odds and ends it was carrying from its homeland.",
                f"The {disaster_name} in {region} sends the {cname} — a seasonal visitor from {home} — into a frenzy. It abandons its temporary den, and scouts find the den still stocked with gathered resources.",
                f"Caught mid-migration by the {disaster_name}, the {cname} turns wildly and carves a new path through {region}. In its desperation, it exposes a hidden hollow previously unknown to scouts.",
            ]
        elif ctype == "spirit":
            templates = [
                f"The {disaster_name} in {region} agitates the {cname} — a spirit from {home} that wandered here with the season. It flares with unnatural light, revealing hidden paths and old secrets.",
                f"Disoriented by the {disaster_name}, the {cname} — a seasonal spirit from {home} — pulses erratically. Each pulse illuminates something previously hidden in {region}.",
                f"The {cname}, a spirit-migrant from {home}, reacts to the {disaster_name} by scattering itself into a dozen dancing lights. When it reforms, it has left behind something it gathered from the spirit world.",
            ]
        elif ctype == "anomaly":
            templates = [
                f"The {disaster_name} disrupts the {cname}'s seasonal presence in {region}. The anomaly — normally indifferent — responds by reshaping the terrain, exposing buried caches.",
                f"A {cname} from {home}, normally docile in {region}, reacts to the {disaster_name} by unfurling into a form no one has seen before. When the disaster passes, the creature is gone — but it left a gift.",
            ]

        # Creature-specific additions
        specific = {
            "Ridge-Wolf Pack": [
                f"The {disaster_name} scatters the Ridge-Wolf Pack across {region}. The wolves, far from their {home} dens, panic — and in their flight, they abandon a kill-site laden with scavenged valuables.",
                f"Wolves fleeing the {disaster_name} in {region} lead scouts to an emergency den — the pack's contingency cache, filled with trinkets gathered across two territories.",
            ],
            "Thorn-Bear": [
                f"The Thorn-Bear, summering in {region} from {home}, reacts to the {disaster_name} with territorial fury. It tears through the chaos — and in its rampage, it uncovers a buried trove.",
                f"A Thorn-Bear caught in the {disaster_name} abandons its berry-hoard. The cache — honeycombs, dried fruit, and something glittering — is found by scouts in the aftermath.",
            ],
            "Oak-Wyrm": [
                f"The Oak-Wyrm, drawn to {region} from {home} for the season, sheds its carapace prematurely in panic from the {disaster_name}. The shed carapace is larger and more valuable than usual.",
                f"An Oak-Wyrm fleeing the {disaster_name} burrows deep and strikes an old root-system — dislodging ancient amber deposits that scouts quickly harvest.",
            ],
            "Bog-Wisp": [
                f"The {disaster_name} whips the Bog-Wisps into a frenzy over {region}. The spirit-lights, confused so far from {home}, spiral into a pattern that points to a hidden cache beneath the cairn-stones.",
                f"Bog-Wisps displaced from {home} by the season and now caught in the {disaster_name} pulse in unison — a distress signal that reveals the location of a long-lost offering site.",
            ],
            "Plains-Lion Pride": [
                f"The {disaster_name} in {region} panics the Plains-Lion Pride — summer migrants from {home}. In their chaotic retreat, they abandon a fresh kill, and something glittering was in its belly.",
                f"Lions fleeing the {disaster_name} lead scouts to their temporary watering-hole den in {region}. The pride's cache — gathered across two territories — is left unguarded.",
            ],
        }

        if cname in specific:
            templates = specific[cname] + templates

        return templates if templates else None

    def _check_deep_resonance_effects(self):
        """Check if a deep-resonance event fired yesterday (set by people.py).
        When a citizen's deep-echo dream and a T3+ Sleeper whisper collide,
        the dreaming deep itself pulses with activity the next day.
        Called from advance_day()."""
        if not self._deep_resonance_fired_today:
            return None

        tier = self._deep_resonance_tier
        # Reset the flags now that we've consumed them
        self._deep_resonance_fired_today = False
        self._deep_resonance_tier = 0

        # Only fire if the dreaming deep is discovered
        if "the_dreaming_deep" not in self.discovered:
            return None

        # Build tier-appropriate effects
        gold_bonus = random.randint(8, 20) if tier >= 4 else random.randint(5, 12)
        stone_bonus = random.randint(2, 8) if tier >= 4 else random.randint(1, 4)
        food_bonus = random.randint(3, 6) if tier >= 4 else random.randint(1, 3)
        lore_chance = 0.55 if tier >= 4 else 0.35

        # Apply resources
        kingdom.gold = max(0, kingdom.gold + gold_bonus)
        kingdom.stone = max(0, kingdom.stone + stone_bonus)
        kingdom.food = max(0, kingdom.food + food_bonus)

        # Narratives for the dreaming deep's response
        tier_badge = "🌞" if tier >= 4 else "🌟"
        deep_narratives = [
            f"The dreaming stone walls of the deep shimmer with afterimages of last night's resonance — a citizen's dream and the Sleeper's voice touched the same moment, and the stone remembers. Crystalline tears weep from the walls (+{gold_bonus}g, +{stone_bonus}s).",
            f"The Cradle hums — a resonant echo of the bond forged last night between dreamer and Sleeper. The dreaming deep pulses once, and new veins of dreaming-stone are exposed (+{gold_bonus}g, +{stone_bonus}s).",
            f"The Remembered gather at the Cradle's edge, drawn by the resonance. They do not speak, but they leave gifts: crystallized memories, still warm (+{gold_bonus}g, +{food_bonus}f).",
            f"Throughout the dreaming deep, Echo-Wyrms chorus in harmony — a sound like glass bells. The resonance between waking dreamer and sleeping god has awakened something in them (+{gold_bonus}g, +{stone_bonus}s).",
            f"The Heart-Pool in the sunken sanctum and the Cradle in the deep pulse in synchrony — two hearts beating as one. The resonance ripples outward, and the deep gives up its treasures (+{gold_bonus}g, +{food_bonus}f).",
        ]

        narrative = random.choice(deep_narratives)
        self.world_log.append(f"{tier_badge}🌊 DEEP-RESONANCE WORLD PULSE [T{tier}]: {narrative}")

        # Lore fragment chance
        if random.random() < lore_chance:
            resonance_lore = [
                "Last night's resonance left a permanent mark on the dreaming deep — a handprint on the Cradle wall that was not there before, glowing faintly. It matches the dreamer's hand exactly.",
                "The resonance between Sleeper and dreamer crystallized into a memory-sphere: a perfect globe of dreaming-stone that, when held, replays the moment of connection — the Sleeper's voice, the dreamer's answer, the brief unity of waking and sleeping worlds.",
                "In the aftermath of the resonance, a new carving appears on the Cradle's wall: a spiral — the ancient symbol for 'two becoming one.' The Remembered bow before it.",
            ]
            self.collect_lore(random.choice(resonance_lore))
            self.world_log.append("  The resonance left a permanent mark — a lore fragment crystallized from the bond.")

        # ── Tier 2: Dream-Husk Market Visitation ──
        # The resonance weakens the boundary between dreaming deep and waking world.
        # Dream-Husks drift into the market square, drawn by the bond.
        if "the_dreaming_deep" in self.discovered and random.random() < 0.65:
            self._dream_husk_market_day = self.day  # kingdom can check this for market bonuses
            husk_narratives = [
                f"Something has followed the resonance out of the dreaming deep. Dream-Husks — shimmering, translucent shapes that look almost human — drift through the market square. They do not speak, but merchants who trade with them find their pouches heavier afterward.",
                f"The boundary between the dreaming deep and the waking world frays. Dream-Husks, echoes of sleepers who never woke, wander the market. They barter in memories — and leave behind coins that gleam with an inner light.",
                f"At dawn, the market square is full of silent figures made of crystallized dream-light. Dream-Husks. They examine every stall, every good, with an intensity that is not quite human. By midday they are gone — but the gold they left is real.",
                f"The resonance drew them: Dream-Husks, the half-formed shapes of those who slept near the Cradle and never fully returned. They drift through the bazaar, paying for ordinary goods with extraordinary coin.",
                f"Shopkeepers wake to find Dream-Husks lined up at their stalls before sunrise — patient, silent, waiting. Their trade is strange but generous. 'They paid in starlight,' one merchant whispers. 'The starlight turned to gold.'",
            ]
            self.world_log.append(f"👻🏛️ DREAM-HUSK VISITATION: {random.choice(husk_narratives)}")
            kingdom.kingdom_log.append("👻🏛️ DREAM-HUSK VISITATION: Dream-Husks from the deep walked the market square after last night's resonance.")

        # ── Tier 2: Deep-Resonance Lair Season Amplification ──
        # When the Sleeper's connection to the waking world is strong,
        # all lairs in their discovery season yield their bonuses today.
        self._deep_resonance_amplify_lairs = True
        amplify_narratives = [
            "The resonance pulses through the dreaming stone — and across the kingdom, old lairs stir. Where the Sleeper's presence touches, hidden caches within cleared lairs bloom with renewed bounty.",
            "The bond between dreamer and Sleeper sends a shiver through the earth. In every cleared lair, something long-dormant quickens — ancient hoards, spirit-offerings, crystalline growths — all awakened by the resonance.",
            "The dreaming deep does not keep its gifts to itself. The resonance ripples outward, and every lair the kingdom has ever cleared responds — seasonal treasures surge to the surface.",
        ]
        self.world_log.append(f"🌊🪨 DEEP-RESONANCE LAIR SURGE: {random.choice(amplify_narratives)}")

        # ── Tier 3: Regional Vision Echoes ──
        # At tier 3+, the resonance is strong enough that every citizen in a random
        # discovered region shares a waking vision of the Sleeper's memory.
        # This is a one-time vision per resonance event — a brief moment where the
        # boundary between dream and waking completely dissolves in one region.
        vision_chance = 0.75 if tier >= 4 else 0.50
        if tier >= 3 and random.random() < vision_chance:
            eligible_regions = [r for r in self.discovered if r != "the_dreaming_deep"]
            if not eligible_regions:
                eligible_regions = list(self.discovered)
            vision_region = random.choice(eligible_regions)
            region_names = {
                "the_vale": "the Vale", "old_oak_ridge": "the Ridge",
                "glimmer_marsh": "the Marsh", "sunfire_plains": "the Plains",
                "ironroot_depths": "the Depths", "the_ashen_copse": "the Copse",
                "the_sunken_sanctum": "the Sanctum", "the_dreaming_deep": "the Dreaming Deep",
            }
            rname = region_names.get(vision_region, vision_region)
            vision_gold = random.randint(5, 15) if tier >= 4 else random.randint(3, 10)
            vision_food = random.randint(2, 6) if tier >= 4 else random.randint(1, 3)
            vision_stone = random.randint(1, 3)
            kingdom.gold = max(0, kingdom.gold + vision_gold)
            kingdom.food = max(0, kingdom.food + vision_food)
            kingdom.stone = max(0, kingdom.stone + vision_stone)

            vision_narratives = [
                f"For thirty seconds, every citizen in {rname} freezes mid-motion — and sees the same thing: the Sleeper's first dawn, a sunrise of liquid gold over a world that had never known warmth. When the vision passes, they find their hands full of crystal-bloom petals (+{vision_gold}g, +{vision_food}f, +{vision_stone}s).",
                f"The resonance wave breaks over {rname} like a tide of light. Citizens drop their tools and stare at the sky — which, for one held breath, shows not today's clouds but the stars as they were before the Cataclysm. A cartographer who sketches the vision sells it for a fortune (+{vision_gold}g, +{vision_food}f, +{vision_stone}s).",
                f"In {rname}, the Sleeper's memory unfolds like a flower. Every person over thirty suddenly remembers being held — by something vast, warm, and ancient. The children see their parents weep, and for the first time, understand that the Sleeper is not a myth. Offerings pile up at the nearest shrine (+{vision_gold}g, +{vision_food}f, +{vision_stone}s).",
                f"The deep-resonance reaches {rname} not as sound but as light — a pulse of amber-gold that passes through walls, through flesh, through time. For a single heartbeat, every citizen sees the Sleeper as it was: a being of living fire and earth, walking. The vision leaves behind fleeting warmth in every home (+{vision_gold}g, +{vision_food}f, +{vision_stone}s).",
                f"{rname} becomes a window into the Sleeper's oldest dream. Citizens report seeing the Pact being made: the first settlers kneeling, the Sleeper bowing its great head, the Whispering Spring bubbling up at the point of contact. The memory is so vivid that mushrooms sprout overnight at the spot where the vision was strongest — glow-caps, prized by herbalists (+{vision_gold}g, +{vision_food}f, +{vision_stone}s).",
            ]
            self.world_log.append(f"🌟👁️ REGIONAL VISION [{rname}]: {random.choice(vision_narratives)}")
            kingdom.kingdom_log.append(f"🌟👁️ REGIONAL VISION: The Sleeper's resonance triggered a shared vision across {rname} — every citizen saw the same memory simultaneously.")

            # Bridge: expose region + day so dream-bond system can react
            self._regional_vision_region = vision_region
            self._regional_vision_day = self.day

            # Vision lore chance
            if random.random() < 0.40:
                vision_lore = [
                    f"The shared vision in {rname} revealed a truth: the Sleeper did not choose the copse at random. It chose the place where the First Fire had once walked — drawn to the residual warmth, like a moth to a candle.",
                    f"After the vision in {rname}, three citizens independently drew the same symbol: a spiral with a flame at its center. It matches carvings found in the Eldertrunk. The collective unconscious of Ashfall is beginning to remember what the Keepers have long suspected.",
                    f"The resonance-vision in {rname} was not the Sleeper's doing alone. The Remembered amplified it — a gift of gratitude for the kingdom that did not forget them. They chose {rname} because something important happened there, long ago.",
                ]
                self.collect_lore(random.choice(vision_lore))
                self.world_log.append("  The region-wide vision crystallized a shared memory — a lore fragment.")

        return {"tier": tier, "gold": gold_bonus, "stone": stone_bonus, "food": food_bonus, "lore": lore_chance, "dream_husk_market": True, "amplify_lairs": True}

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

        # Gloom-Lantern bloom-field: lair cleared after widespread infection → positive narrative
        if (not self._gloom_bloom_fired
            and "ironroot_depths" in self._cleared_lairs
            and len(self._gloom_lantern_regions) >= 4):
            self._gloom_bloom_fired = True
            bloom_bonus = len(self._gloom_lantern_regions)
            kingdom.gold += bloom_bonus * 3
            kingdom.food += bloom_bonus
            region_list = ", ".join(sorted(self._gloom_lantern_regions))
            self.world_log.append(
                f"\U0001f344 GLOOM-BLOOM: With the mother lantern destroyed, the spores "
                f"in {region_list} have transformed. Instead of spreading, they crystallize "
                f"into delicate, phosphorescent blooms — 'gloom-flowers.' Herbalists discover "
                f"the petals, when dried, make a tea that grants vivid, prophetic dreams. "
                f"+{bloom_bonus * 3} gold, +{bloom_bonus} food. The Gloom-Lantern's legacy "
                f"is not destruction, but revelation."
            )
            kingdom.kingdom_log.append(
                "\U0001f344 GLOOM-BLOOM: Spores crystallized into gloom-flowers across "
                f"{bloom_bonus} regions — a blessing from the vanquished dark."
            )
            results.append("gloom_bloom")

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
            elif region == "the_dreaming_deep":
                kingdom.gold += 8
                kingdom.stone += 3
                kingdom.food += 2

        # ── Lair Seasonal Bonuses ──
        # Cleared lairs grant extra resources during their discovery season
        # (the season when the lair is most active/vulnerable)
        # When deep-resonance amplifies: 100% chance + doubled resources
        amplify = self._deep_resonance_amplify_lairs
        if amplify:
            self._deep_resonance_amplify_lairs = False  # consume flag

        LAIR_SEASONAL_BONUSES = {
            "the_vale": {
                "seasons": ["spring"],
                "bonus": {"food": 2},
                "narrative": "The Thorn-Bear's old hollow drips with spring honey — beekeepers harvest the wild combs.",
            },
            "old_oak_ridge": {
                "seasons": ["winter"],
                "bonus": {"gold": 2},
                "narrative": "Snow reveals what the Ridge-Wolves buried: old coins wind-polished to a gleam, scattered across the frozen den.",
            },
            "glimmer_marsh": {
                "seasons": ["autumn"],
                "bonus": {"gold": 3, "food": 1},
                "narrative": "Autumn fog thickens around the cairn, and the bog-wisps' old gathering ground yields ghost-bloom petals — prized by herbalists.",
            },
            "ironroot_depths": {
                "seasons": ["autumn", "winter"],
                "bonus": {"stone": 3, "gold": 2},
                "narrative": "The damp season makes the old spore-vault walls weep mineral-rich slurry — concentrated ore, easily harvested.",
            },
            "sunfire_plains": {
                "seasons": ["summer"],
                "bonus": {"gold": 3, "food": 1},
                "narrative": "Summer heat makes the mesa's wind-spirits restless — they dance and scatter windfall seeds and lost trinkets across the plains.",
            },
            "the_ashen_copse": {
                "seasons": ["winter"],
                "bonus": {"gold": 4},
                "narrative": "Winter cold crystallizes the ash where the wraiths once converged — forming fragile, gem-like structures that fetch high prices.",
            },
            "the_sunken_sanctum": {
                "seasons": ["spring"],
                "bonus": {"gold": 6, "stone": 3},
                "narrative": "Spring renewal accelerates crystal growth in the Heart-Pool chamber — new formations sprout overnight, rich with captured light.",
            },
            "the_dreaming_deep": {
                "seasons": [],  # the deep transcends seasons
                "bonus": None,  # no seasonal bonus — the deep already gives generously
                "narrative": None,
            },
        }

        for region in self._cleared_lairs:
            sb = LAIR_SEASONAL_BONUSES.get(region)
            if not sb or not sb.get("bonus"):
                continue
            if self.season in sb.get("seasons", []):
                # Fire the narrative ~8% of days normally, 100% when deep-resonance amplifies
                trigger_chance = 1.0 if amplify else 0.08
                if random.random() < trigger_chance:
                    bonus = sb["bonus"]
                    multiplier = 2 if amplify else 1  # doubled during resonance
                    parts = []
                    for key, val in bonus.items():
                        actual_val = val * multiplier
                        if key == "food":
                            kingdom.food += actual_val
                            parts.append(f"+{actual_val}f")
                        elif key == "gold":
                            kingdom.gold += actual_val
                            parts.append(f"+{actual_val}g")
                        elif key == "stone":
                            kingdom.stone += actual_val
                            parts.append(f"+{actual_val}s")
                        elif key == "wood":
                            kingdom.wood += actual_val
                            parts.append(f"+{actual_val}w")
                    bonus_str = ", ".join(parts)
                    if amplify:
                        self.world_log.append(
                            f"🌊🪨 DEEP-RESONANCE LAIR BONUS [{region}]: {sb['narrative']} ({bonus_str}) [amplified by resonance]"
                        )
                    else:
                        self.world_log.append(
                            f"\U0001faa8 LAIR SEASON: {sb['narrative']} ({bonus_str})"
                        )
                    results.append(f"lair_season_{region}")

        return results if results else None

    def _lair_echoes(self):
        """Post-clearing narrative echoes — flavor events from cleared lairs.
        Fires rarely (~5% per cleared lair per day). Adds history and atmosphere."""
        ECHOES = {
            "the_vale": [
                "A child finds a claw as long as a dagger near Thorn-Bear's Hollow. "
                "They bring it to the village, wide-eyed — a relic of the beast that once prowled here.",
                "Berry-pickers report the hollow is now thick with brambles and fruit. "
                "The Thorn-Bear's old territory has turned generous in its absence.",
                "An elder carves a bear totem from vale-oak and places it at the hollow's edge. "
                "'To remember what we overcame,' they say.",
                "Honey-dripping combs, abandoned in the hollow, are harvested by beekeepers. "
                "The Thorn-Bear's old larder feeds the village for a day. 'Even monsters keep pantry,' "
                "a child remarks.",
                "A travelling bard composes 'The Lay of the Hollow' — a ballad about the day the "
                "Thorn-Bear fell. It's sung in the tavern for weeks.",
                "Odd claw-mark patterns on the hollow walls, studied by scouts, turn out to be a crude map "
                "of berry patches across the vale. The Thorn-Bear was marking its territory — now it marks ours.",
            ],
            "old_oak_ridge": [
                "Scouts spot a lone wolf on the ridge at dusk. It watches silently, then melts into the trees. "
                "Not hostile — almost... acknowledging.",
                "A hunter finds an old wolf-den beneath the Eldertrunk, long abandoned. "
                "Inside: a cache of shiny stones and a child's bracelet. The Ridge-Wolves collected trophies.",
                "On cold nights, some swear they still hear the pack howling — but it's only the wind "
                "through the ridge-pines. Probably.",
                "A woodcutter reports that deer have returned to the ridge in numbers not seen since before "
                "the wolves were cleared. The ecosystem is rebalancing.",
                "The Eldertrunk's bark has begun to regrow where wolf claws scored it. "
                "A green shoot — an oak sapling — pushes through the old scar. New life from old wounds.",
                "A scout finds a wolf pup, orphaned and alone, at the edge of the old territory. "
                "They bring it to the village. The elders debate: wild thing or ward of Ashfall?",
            ],
            "glimmer_marsh": [
                "On misty mornings, the bog-wisps' cairn glows faintly blue. "
                "Herbalists say the light is harmless — even soothing. Some meditate there now.",
                "A scout swears they saw a figure in the marsh — tall, thin, made of reeds and fog — "
                "but when they approached, it was only a trick of the light. The bog remembers.",
                "A strange flower blooms where the wisps once gathered: petals of cold blue flame "
                "that extinguish at dawn. The herbalists call it 'wisp-woe' and prize it for tinctures.",
                "A fisherman pulls up a net full of silver-scaled fish near the old cairn — fish no one "
                "has seen before. 'The wisps left us a going-away present,' the herbalist says.",
                "Duckweed on the marsh pools arranges itself into words at dawn. The messages are brief: "
                "'THANK YOU.' 'REMEMBER.' 'GO DEEPER.' By noon, the duckweed drifts apart again.",
                "A child born during the marsh-fog the year the wisps were calmed has eyes that glow faintly "
                "blue in darkness. The elders call it the Wisp-Touch — a blessing, not a curse.",
            ],
            "ironroot_depths": [
                "A miner discovers that crushed gloom-lantern spores, mixed with iron-dust, "
                "make a paste that glows for hours. The builders are intrigued.",
                "The spore-vault is silent now, but the walls still pulse faintly green. "
                "Geologists say it's residual phosphorescence. Miners say it's a heartbeat.",
                "A young scout ventures to the sealed vault entrance and returns with a sketch: "
                "the spores, dormant now, have grown into shapes resembling letters. No one can read them.",
                "The glow-paste formula has spread among the builders. The new watchtower's interior "
                "is coated with it — a soft green light that needs no fuel. 'The spores lighting our way,' "
                "a mason chuckles.",
                "A geologist cracks open a nodule from the vault wall. Inside: a perfect crystal impression "
                "of a fern that hasn't grown on the surface since before the Cataclysm. +1 lore.",
                "Miners report that the iron veins near the old spore-vault are richer than anywhere else "
                "in the depths. The gloom-lanterns fed on something that enriched the stone.",
            ],
            "sunfire_plains": [
                "Wind patterns around the mesa have shifted since the dust-devil was dispersed. "
                "Travelers say the plains feel... calmer. The sky seems wider.",
                "A trader reports finding a spiral of perfectly smooth stones atop Dust-Devil Mesa. "
                "No one remembers putting them there. The pattern matches old wind-warding charms.",
                "At high noon, the mesa casts no shadow. Scouts have checked three times. "
                "The elders say some places forget how to be ordinary.",
                "A herd of wild horses grazes at the mesa's base — the first time they've come that close "
                "since the dust-devils began their dance. 'Even the animals know it's safe now,' a scout says.",
                "The wind-spirits have taken to carrying flower petals across the plains in elaborate patterns. "
                "From the mesa top, the petal-trails spell words in a language of curves and spirals.",
                "A young scout who spent a night on the mesa returns with hair that moves as if in a perpetual "
                "breeze — even indoors. They call it 'wind-kissed' and the elders nod knowingly.",
            ],
            "the_ashen_copse": [
                "A patch of tiny white flowers — ghostbloom — sprouts where the Ash-Wraith once converged. "
                "First living things seen in the copse in living memory.",
                "A scout reports hearing whispers near the old convergence site. "
                "Not threatening — just... words in a language that almost makes sense. "
                "The Sleepers' tongue, perhaps.",
                "The ash-fall has lessened since the wraith was dispersed. "
                "Someone carves a small stone marker: 'Here, the air remembered how to be still.'",
                "The ghostbloom patch has spread — now a field of white nodding flowers that open only "
                "at dusk. Herbalists say their petals, brewed as tea, bring peaceful dreams.",
                "A wraith-mark remains on one petrified tree: a handprint that glows faintly silver "
                "under the new moon. Scouts leave small offerings there — pebbles, coins, a sprig of rosemary.",
                "A citizen who lost a parent in the Cataclysm visits the convergence site and weeps. "
                "When they rise, the ash around their feet has crystallized into tiny, perfect flowers. "
                "'They heard me,' they whisper.",
            ],
            "the_sunken_sanctum": [
                "The Heart-Pool pulses gently in the dark, casting prismatic light on the crystal walls. "
                "A scout reports that the pool showed them a vision — a city of glass, walking on legs of fire.",
                "Crystal fragments near the Heart-Pool hum at a frequency that makes teeth ache. "
                "A herbalist claims the hum, when transcribed as notes, forms a lullaby.",
                "Echoes in the sanctum now whisper in a voice that might be the Crystal-Serpent's: "
                "'The Sleepers are not dead. They are listening.'",
                "A crystal pillar that was dormant for centuries begins to glow when a particular citizen "
                "walks past — as if it recognizes their bloodline. The genealogists grow excited.",
                "The Heart-Pool shows a different vision to each visitor now: a mother sees her lost child "
                "smiling, a builder sees a tower that reaches the clouds, a scout sees a map of stars. "
                "The pool remembers everyone who has ever looked into it.",
                "A choir of children sing near the Heart-Pool and the crystals harmonize — adding notes "
                "no human voice could produce. The recorded song becomes a treasured artifact of Ashfall.",
            ],
            "the_dreaming_deep": [
                "The Sleeper's Cradle thrums with a low, contented hum. "
                "Miners working near the deep report dreams of flying — every night, the same dream, "
                "over cities of spun glass and gardens of light.",
                "A child in Ashfall draws a picture of the Remembered — all of them, in a circle — "
                "without ever having been told what they look like. The elders grow quiet.",
                "The dreaming stone walls in the deep shimmer with new colors: gold, violet, "
                "a blue that has no name. The stonemasons call it 'Sleeper-glass' and say "
                "it sings when you hold it to your ear.",
                "An Echo-Wyrm sheds a scale the size of a dinner plate — it resonates with a low, "
                "sustained note for three days before falling silent. The armorers have never seen "
                "anything like it.",
                "A Dream-Husk lingers near the Cradle's edge and speaks — not in words, but in images "
                "that flash through the minds of everyone nearby. A garden. A child laughing. A star "
                "being born. 'The Sleeper is happy,' a scout translates.",
                "The Cradle's hum changes pitch at midnight — a melody that resolves into the same "
                "four notes, over and over. A music-theorist identifies them as the opening of a "
                "lullaby so old it predates human speech.",
            ],
        }

        for region in list(self._cleared_lairs):
            if region not in ECHOES:
                continue
            if random.random() < 0.05:  # 5% chance per day per cleared lair
                echo = random.choice(ECHOES[region])
                self.world_log.append(f"🕳️ LAIR ECHO — {region}: {echo}")

    def _check_migrations(self):
        """Check if the season has changed and log creature migrations.
        Called from advance_day() before deep whispers.
        Migratory creatures move between regions based on season."""
        if self.season == self._last_migration_season:
            return None  # no season change, no migration to log

        old_season = self._last_migration_season
        new_season = self.season
        self._last_migration_season = new_season

        # Find all creatures that migrate in the new season
        arriving = []  # (creature_name, home_region, destination)
        departing = []  # (creature_name, home_region, destination from old season)

        for home_region, creature_list in CREATURES.items():
            for c in creature_list:
                migration = c.get("migration", {})
                # Arriving: creature migrates TO a region in the new season
                if new_season in migration:
                    arriving.append((c["name"], home_region, migration[new_season]))
                # Departing: creature was in a migration region during the old season
                if old_season in migration:
                    departing.append((c["name"], home_region, migration[old_season]))

        if not arriving and not departing:
            return None

        messages = []
        for name, home, dest in arriving:
            msg = (
                f"🐾 CREATURE MIGRATION: {name} has moved from {home} to {dest} "
                f"for the {new_season} season. Scouts report fresh tracks and new activity "
                f"in {dest}."
            )
            messages.append(msg)
            self.world_log.append(msg)

        for name, home, dest in departing:
            msg = (
                f"🐾 CREATURE MIGRATION: {name} has left {dest} and returned to {home} "
                f"as {old_season} gives way to {new_season}."
            )
            messages.append(msg)
            self.world_log.append(msg)

        self._migration_log.append({
            "day": self.day,
            "old_season": old_season,
            "new_season": new_season,
            "arriving": arriving,
            "departing": departing,
        })

        # ── Tier 2: Veteran Traveler Tracking ──
        # Creatures that have migrated 3+ times become "veteran travelers" —
        # their encounters yield bonus resources and unique narrative.
        for name, home, dest in arriving:
            key = (name, home)
            count = self._creature_migration_counts.get(key, 0) + 1
            self._creature_migration_counts[key] = count
            if count == 3:
                self.world_log.append(
                    f"⭐ CREATURE VETERAN: {name} (of {home}) has completed its third migration. "
                    f"It now travels with the confidence of an old hand — seasoned, clever, "
                    f"and carrying treasures gathered across seasons."
                )
                kingdom.kingdom_log.append(
                    f"⭐ VETERAN TRAVELER: {name} has become a veteran of the migration roads — "
                    f"it knows every trail, every cache, every hidden spring."
                )
                # ── Tier 3: Veteran Cache ──
                # Veteran creatures establish caches in their home region that yield daily passives.
                cache_key = (name, home)
                if cache_key not in self._veteran_caches:
                    cache_gold = random.randint(1, 3)
                    cache_food = random.randint(1, 2)
                    cache_resource = random.choice(["stone", "wood"])
                    cache_amount = random.randint(1, 2)
                    cache_bonus = {"gold": cache_gold, "food": cache_food}
                    cache_bonus[cache_resource] = cache_amount
                    self._veteran_caches[cache_key] = cache_bonus
                    self.world_log.append(
                        f"📦 VETERAN CACHE: {name} has created a hidden cache in {home} — "
                        f"a stash of treasures gathered across its travels. "
                        f"Scouts can now tap this cache daily (+{cache_gold}g, +{cache_food}f, "
                        f"+{cache_amount} {cache_resource})."
                    )
                    kingdom.kingdom_log.append(
                        f"📦 VETERAN CACHE: {name} established a treasure cache in {home} "
                        f"— the kingdom can now harvest its gathered wealth daily."
                    )
            elif count > 3 and count % 5 == 0:
                self.world_log.append(
                    f"👑 CREATURE ELDER-TRAVELER: {name} (of {home}) has now migrated {count} times. "
                    f"It is a living legend of the migration roads — scouts tell stories of its wisdom."
                )

        return messages if messages else None

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

        # Echo-Wyrm Dream-Harvest (the_dreaming_deep)
        # After the dreaming deep is discovered, the Echo-Wyrm periodically sheds
        # valuable auroral scales — every 10-15 days.
        if "the_dreaming_deep" in self.discovered:
            if self._echo_wyrm_last_shed == 0:
                self._echo_wyrm_last_shed = self.day  # initialize timer on first discovery
            else:
                days_since = self.day - self._echo_wyrm_last_shed
                if days_since >= random.randint(10, 15):
                    self._echo_wyrm_last_shed = self.day
                    gold_gain = random.randint(5, 10)
                    kingdom.gold += gold_gain
                    bonus = ""
                    if random.random() < 0.30:
                        stone_gain = random.randint(2, 5)
                        kingdom.stone += stone_gain
                        bonus = f" +{stone_gain} stone (dreaming-stone fragments)"
                    msg = (
                        f"\U0001f40d ECHO-WYRM DREAM-HARVEST: The Echo-Wyrm has shed its auroral scales "
                        f"in the dreaming deep. Scouts collect the translucent, humming plates — "
                        f"prized by armorers and scholars alike. +{gold_gain} gold{bonus}."
                    )
                    self.world_log.append(msg)
                    results.append({"type": "echo_wyrm_harvest", "gold": gold_gain, "msg": msg})

        # Memory-Wisp Dream-Harvest (the_sunken_sanctum)
        # Memory-Wisps occasionally deliver prophetic glimpses — fragments of possible
        # futures that translate into tangible wealth. Every 12-18 days.
        if "the_sunken_sanctum" in self.discovered:
            if self._memory_wisp_last_harvest == 0:
                self._memory_wisp_last_harvest = self.day  # initialize timer on first discovery
            else:
                days_since = self.day - self._memory_wisp_last_harvest
                if days_since >= random.randint(12, 18):
                    self._memory_wisp_last_harvest = self.day
                    gold_gain = random.randint(3, 7)
                    kingdom.gold += gold_gain
                    bonus = ""
                    if random.random() < 0.25:
                        lore_text = (
                            "The Memory-Wisps showed a glimpse of something yet to come — "
                            "a future where Ashfall's towers touch the clouds and the Sleeper "
                            "walks among its people, awake and grateful."
                        )
                        self.collect_lore(lore_text)
                        bonus = " +1 lore fragment (future-memory)"
                    msg = (
                        f"\u2728 MEMORY-WISP DREAM-HARVEST: A flight of Memory-Wisps drifts "
                        f"through the sunken sanctum, each carrying a fragment of a possible future. "
                        f"One shows a cache of crystal-coins hidden in a crevice — scouts recover them. "
                        f"+{gold_gain} gold{bonus}."
                    )
                    self.world_log.append(msg)
                    results.append({"type": "memory_wisp_harvest", "gold": gold_gain, "msg": msg})

        return results

    def _check_deep_whispers(self):
        """Periodic narrative events from the dreaming deep after it's discovered.
        Fires every 8-12 days (stochastic). These are flavorful omens that give
        resource bonuses, lore fragments, and deepen the connection between
        the kingdom and the Sleeper's realm. Called from advance_day().

        Whisper tier scales with ash-bloom count:
          Tier 1 (0-4 blooms): The Sleeper stirs — subtle signs
          Tier 2 (5-9 blooms): The Sleeper remembers — active gifts
          Tier 3 (10-14 blooms): The Sleeper speaks — direct communication
          Tier 4 (15+ blooms): The Sleeper awakens — near-physical presence"""
        if "the_dreaming_deep" not in self.discovered:
            return None

        # Initialize the timer on first discovery
        if self._deep_whisper_next_day == 0:
            self._deep_whisper_next_day = self.day + random.randint(8, 12)
            return None

        if self.day < self._deep_whisper_next_day:
            return None

        # Determine current tier based on ash-bloom count
        blooms = self._ash_blooms_collected
        if blooms >= 15:
            current_tier = 4
        elif blooms >= 10:
            current_tier = 3
        elif blooms >= 5:
            current_tier = 2
        else:
            current_tier = 1

        # Filter whispers to those at or below current tier
        eligible = [w for w in DEEP_WHISPERS if w.get("tier", 1) <= current_tier]
        if not eligible:
            eligible = DEEP_WHISPERS  # fallback

        # Weighted selection: higher-tier whispers get higher weight (more dramatic)
        weights = []
        for w in eligible:
            tier = w.get("tier", 1)
            if tier == current_tier:
                weights.append(4)  # current-tier whispers are most likely
            elif tier == current_tier - 1:
                weights.append(2)  # previous tier still appears
            else:
                weights.append(1)  # much older tiers are rare callbacks
        whisper = random.choices(eligible, weights=weights, k=1)[0].copy()

        title = whisper.get("title", "Deep Whisper")
        narrative = whisper.get("narrative", "")
        effects = whisper.get("effects", {})
        lore = whisper.get("lore")
        tier = whisper.get("tier", 1)

        # Apply effects
        for key, val in effects.items():
            if key == "food":
                kingdom.food = max(0, kingdom.food + val)
            elif key == "wood":
                kingdom.wood = max(0, kingdom.wood + val)
            elif key == "stone":
                kingdom.stone = max(0, kingdom.stone + val)
            elif key == "gold":
                kingdom.gold = max(0, kingdom.gold + val)
            elif key == "pop":
                kingdom.population = max(1, kingdom.population + val)

        # Collect lore if present
        if lore:
            self.collect_lore(lore)

        # ── Deep-Whisper Quest Spawning ──
        # T3+ whispers with quest data can generate faction quests
        quest_data = whisper.get("quest")
        quest_result = None
        if quest_data:
            try:
                from people import people as ppl
                if hasattr(ppl, '_spawn_deep_whisper_quest'):
                    quest_result = ppl._spawn_deep_whisper_quest(quest_data, world_obj=self)
            except Exception:
                pass  # gracefully skip if people module unavailable

        # ── Set daily flag for cross-system resonance ──
        # When a T3+ whisper fires, memory-dreams can resonate with it
        if tier >= 3:
            self._deep_whisper_fired_today = True
            self._deep_whisper_tier = tier

        # Tier badge for logging
        tier_badges = {1: "🌫️", 2: "✨", 3: "🌟", 4: "🌞"}
        badge = tier_badges.get(tier, "🌌")

        # Log it
        self.world_log.append(f"{badge} DEEP WHISPER [T{tier}] — {title}: {narrative}")
        kingdom.kingdom_log.append(f"{badge} DEEP WHISPER [T{tier}]: {title} — {narrative[:70]}...")

        # Higher tiers fire more frequently (the Sleeper grows more active)
        if tier >= 3:
            interval = random.randint(6, 10)  # more frequent at tier 3+
        elif tier >= 2:
            interval = random.randint(7, 11)
        else:
            interval = random.randint(8, 12)
        self._deep_whisper_next_day = self.day + interval

        return {"title": title, "narrative": narrative, "effects": effects, "tier": tier, "quest_result": quest_result}

    def _check_ash_bloom_milestones(self):
        """Check if enough Ash-Blooms have been collected to trigger a Sleeper's Memory event.
        Called from advance_day(). Milestones at 3, 5, 10, 15 blooms."""
        milestones = {
            3: {
                "title": "The Sleeper Dreams",
                "narrative": (
                    "Three Ash-Blooms have been gathered — three crystallized memories of the Sleeper. "
                    "Across Ashfall, dreams grow more vivid. Citizens wake remembering places they've "
                    "never been: a city of glass and green, walking on legs of fire. The elders say "
                    "the Sleeper is stirring — not in anger, but in recognition. "
                    "Someone is listening."
                ),
                "effects": {"gold": 15, "food": 3},
                "permanent": "ash_dreams — +1 morale/day for all citizens (the Sleeper's dreams are comforting)",
            },
            5: {
                "title": "The Sleeper Remembers",
                "narrative": (
                    "Five Ash-Blooms. Five memories. The fragments coalesce into something coherent: "
                    "the Sleeper beneath the copse remembers the Pact. It remembers the first settlers "
                    "who promised to tend the land. It remembers being asked to stay. And now, through "
                    "the blooms, it reaches out — not to wake, but to *thank*. The Heart-Pool in the "
                    "sunken sanctum pulses with warm light, and for three full minutes, every citizen "
                    "of Ashfall hears a voice like mountains shifting: 'YOU HAVE NOT FORGOTTEN.'"
                ),
                "effects": {"gold": 25, "stone": 10},
                "permanent": "sleeper_pact_renewed — +2 gold/day from sanctum resonance, +1 stone/day",
            },
            10: {
                "title": "The Sleeper Speaks",
                "narrative": (
                    "Ten Ash-Blooms — ten memories woven into a tapestry of ancient truth. The Sleeper "
                    "does not merely stir now; it *speaks*. The Whispering Spring carries its voice to "
                    "every corner of Ashfall, and the message is clear: something woke the other Sleeper "
                    "in the north, and it is coming. But the Sleeper beneath the copse has chosen its side. "
                    "It will not wake in fury. It will wake in *defense*. The pact is no longer just a "
                    "promise — it is an alliance. The land itself rises to protect its people."
                ),
                "effects": {"gold": 40, "pop": 3},
                "permanent": "sleeper_alliance — territory_defense_bonus +5, +3 population (awakened followers arrive)",
            },
            15: {
                "title": "The Sleeper's Gift",
                "narrative": (
                    "Fifteen Ash-Blooms. The Sleeper's full story is now known — not through scholars "
                    "or lore-hunters, but through the Sleeper's own memories, gifted freely through "
                    "each bloom. The Heart-Pool rises from its basin and takes the shape of a figure "
                    "of liquid light — the Sleeper's projected form. It kneels. It speaks: "
                    "'YOU REMEMBERED. NOW I REMEMBER YOU. WHEN THE NORTHERN FIRE COMES, STAND IN THE "
                    "ASHEN COPSE. I WILL NOT LET YOU FALL.' The bloom-field at the copse's edge now "
                    "glows with a permanent, warm light — a beacon visible for miles."
                ),
                "effects": {"gold": 60, "food": 15, "wood": 15},
                "permanent": "sleeper_beacon — all copse events become positive, +3 gold/day, +2 food/day",
            },
        }

        for threshold, milestone in sorted(milestones.items()):
            if threshold in self._ash_bloom_milestones:
                continue
            if self._ash_blooms_collected >= threshold:
                self._ash_bloom_milestones.add(threshold)
                m = milestone
                self.world_log.append(
                    f"\U0001f31f ASH-BLOOM MILESTONE: {m['title']} "
                    f"({self._ash_blooms_collected} blooms collected) — {m['narrative'][:100]}..."
                )
                kingdom.kingdom_log.append(
                    f"\U0001f31f {m['title']}: {m['narrative'][:80]}..."
                )
                # Apply one-time effects
                for key, val in m["effects"].items():
                    if key == "pop":
                        kingdom.population += val
                    elif key == "food":
                        kingdom.food += val
                    elif key == "wood":
                        kingdom.wood += val
                    elif key == "stone":
                        kingdom.stone += val
                    elif key == "gold":
                        kingdom.gold += val
                # Log the permanent bonus
                kingdom.kingdom_log.append(
                    f"  \U0001f4dc Permanent: {m['permanent']}"
                )
                break  # Only one milestone per day

    def _apply_ash_bloom_passives(self):
        """Apply daily passive bonuses from Ash-Bloom milestones.
        Called from advance_day()."""
        # Milestone 5: sleeper_pact_renewed — +2 gold/day, +1 stone/day
        if 5 in self._ash_bloom_milestones:
            kingdom.gold += 2
            kingdom.stone += 1
        # Milestone 15: sleeper_beacon — +3 gold/day, +2 food/day
        if 15 in self._ash_bloom_milestones:
            kingdom.gold += 3
            kingdom.food += 2

    def _apply_trifecta_passives(self):
        """Apply daily passive bonuses from Trifecta Wonder events.
        Each region's wonder grants permanent daily resource yields.
        Called from advance_day()."""
        if not self._trifecta_bonuses:
            return
        for region, bonuses in self._trifecta_bonuses.items():
            for resource, amount in bonuses.items():
                # Skip non-resource keys (lore_double, whisper_fast, etc.)
                if resource in ("lore_double", "lore_every_10_days", "disease_resist_pct", "whisper_fast"):
                    continue
                if resource == "gold":
                    kingdom.gold += amount
                elif resource == "food":
                    kingdom.food += amount
                elif resource == "stone":
                    kingdom.stone += amount
                elif resource == "wood":
                    kingdom.wood += amount

    def _apply_veteran_cache_passives(self):
        """Apply daily passive bonuses from veteran creature caches.
        Veteran creatures (3+ migrations) establish hidden caches in their
        home regions that yield daily resources.
        Called from advance_day()."""
        if not self._veteran_caches:
            return
        for (name, home), bonuses in self._veteran_caches.items():
            for resource, amount in bonuses.items():
                if resource == "gold":
                    kingdom.gold += amount
                elif resource == "food":
                    kingdom.food += amount
                elif resource == "stone":
                    kingdom.stone += amount
                elif resource == "wood":
                    kingdom.wood += amount

    def _check_creature_followups(self):
        """Process pending creature follow-up events:
        - Ridge-Wolf den treasure: scouts track wolves to their den for gold
        - Vale-Stag blessing: temporary food/morale boost
        Called from advance_day()."""
        if not self._pending_creature_followups:
            return

        remaining = []
        for due_day, region, event_type, data in self._pending_creature_followups:
            if self.day < due_day:
                remaining.append((due_day, region, event_type, data))
                continue

            if event_type == "ridgewolf_den":
                # Scouts found the wolf den — gold from old kills and trinkets
                den_gold = random.randint(6, 10)
                kingdom.gold += den_gold
                self.world_log.append(
                    f"\U0001f43a RIDGE-WOLF DEN FOUND: Scouts tracked the pack to their den "
                    f"beneath an ancient oak on old_oak_ridge. Inside: {den_gold} gold worth of "
                    f"shiny stones, old coins, and a child's lost bracelet. The pack watches "
                    f"from the treeline but does not interfere."
                )
            elif event_type == "valestag_blessing":
                # The white stag's blessing manifests
                blessing_food = random.randint(4, 8)
                kingdom.food += blessing_food
                self._vale_stag_blessing = False
                self.world_log.append(
                    f"\U0001f98c VALE-STAG BLESSING MANIFESTS: The white stag was seen days ago, "
                    f"and now the blessing blooms. Berry thickets are heavier than anyone remembers. "
                    f"Wild grain bends under its own weight. The Whispering Spring runs sweeter. "
                    f"+{blessing_food} food. The stag watches from the treeline, then vanishes."
                )
            elif event_type == "thornbear_moves":
                # Thorn-Bear has moved on — berry thicket is safe to harvest
                thicket_food = random.randint(3, 5)
                kingdom.food += thicket_food
                self._thornbear_avoided = False
                self.world_log.append(
                    f"\U0001f43b THORN-BEAR MOVED ON: Scouts confirm the bear has left the vale. "
                    f"The berry thicket it was guarding is heavy with fruit — no one has dared "
                    f"harvest it for days. +{thicket_food} food. Children are sent to gather "
                    f"with strict instructions to sing loudly."
                )
            elif event_type == "oakwyrm_venom":
                # Oak-Wyrm venom processed — herbalists render it into saleable form
                self._oakwyrm_venom_pending = False
                # Check if kingdom has herbalists via people module
                has_herbalist = False
                try:
                    from people import people as ppl
                    for c in ppl.citizens:
                        if getattr(c, 'role', '') == 'herbalist':
                            has_herbalist = True
                            break
                except Exception:
                    pass
                if has_herbalist:
                    venom_gold = random.randint(6, 9)
                    self.world_log.append(
                        f"\U0001f9ea OAK-WYRM VENOM RENDERED: The kingdom's herbalists have "
                        f"carefully rendered the amber venom sacs. The resulting tincture is "
                        f"prized by physicians and alchemists across the region. "
                        f"+{venom_gold} gold from sale."
                    )
                else:
                    venom_gold = random.randint(2, 4)
                    self.world_log.append(
                        f"\U0001f9ea OAK-WYRM VENOM SPOILED: Without a skilled herbalist, "
                        f"much of the venom's potency was lost. A traveling merchant buys "
                        f"what remains. +{venom_gold} gold. Perhaps next time..."
                    )
                kingdom.gold += venom_gold
            elif event_type == "bogwisp_cairn":
                # Bog-Wisp gamble resolves: the Drowned Cairn yields treasure or disappointment
                self._bogwisp_following = False
                if random.random() < 0.50:
                    # Success — found treasure
                    cairn_gold = random.randint(6, 10)
                    kingdom.gold += cairn_gold
                    self.world_log.append(
                        f"\U0001fa94 BOG-WISP REWARD: The wisp's trail led true! Beneath the "
                        f"Drowned Cairn, scouts found a cache of ancient grave-goods — "
                        f"tarnished silver torcs, jet beads, and coins from a kingdom "
                        f"that fell before the Cataclysm. +{cairn_gold} gold."
                    )
                else:
                    # Failure — lost in marsh
                    lost_food = random.randint(2, 4)
                    kingdom.food = max(0, kingdom.food - lost_food)
                    self.world_log.append(
                        f"\U0001fa94 BOG-WISP TRICK: The wisp's trail vanished into deep bog. "
                        f"Scouts spent hours floundering through muck and reed-beds before "
                        f"finding their way back, exhausted and empty-handed. "
                        f"-{lost_food} food from wasted provisions."
                    )

        self._pending_creature_followups = remaining

    def creature_encounter(self, region=None):
        """Generate a creature encounter in a region. Returns structured encounter
        dict for future combat integration. If no region given, picks a random
        discovered region weighted by danger.

        Migratory creatures are included — a Ridge-Wolf in the_vale during winter, etc.

        Return dict:
            region, creature_name, danger, ctype, narrative, stakes, combat_stakes, special,
            _migratory (bool, if from migration), _migrated_from (str, home region)
        """
        if region is None:
            # Include regions that have any creatures (resident or migratory)
            eligible = [r for r in self.discovered if self._creatures_in_region(r)]
            if not eligible:
                return None
            danger_weights = {"high": 3, "medium": 2, "low": 1}
            weights = [danger_weights.get(TERRAIN[r]["danger"], 1) for r in eligible]
            region = random.choices(eligible, weights=weights, k=1)[0]

        if region not in self.discovered:
            return None

        creatures = self._creatures_in_region(region)
        if not creatures:
            return None

        creature_weights = [{"high": 3, "medium": 2, "low": 1}.get(c["danger"], 1) for c in creatures]
        creature = random.choices(creatures, weights=creature_weights, k=1)[0]

        # Build narrative with migration context
        narrative = creature["encounter"]
        if creature.get("_migratory"):
            narrative += f" (It has wandered here from {creature['_migrated_from']} — a seasonal migrant, far from its usual territory.)"

        encounter = {
            "region": region,
            "creature_name": creature["name"],
            "danger": creature["danger"],
            "ctype": creature["type"],
            "narrative": narrative,
            "stakes": creature["stakes"],
            "combat_stakes": creature.get("combat_stakes", {}),
            "special": creature.get("special", ""),
            "_migratory": creature.get("_migratory", False),
            "_migrated_from": creature.get("_migrated_from"),
        }

        migration_note = " [migratory]" if creature.get("_migratory") else ""
        self.world_log.append(
            f"\U0001f43e Creature encounter in {region}: {creature['name']} ({creature['danger']} danger){migration_note}"
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
        region = encounter["region"]
        if creature_name == "Gloom-Lantern" and action == "avoid":
            self._gloom_lantern_day = self.day
            self._gloom_lantern_regions.add(region)
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
        elif creature_name == "Ash-Bloom" and action in ("bargain", "fight"):
            # Picking the bloom — each one is a Sleeper's memory
            self._ash_blooms_collected += 1
            bloom_num = self._ash_blooms_collected
            self.world_log.append(
                f"\U0001f338 ASH-BLOOM PICKED: The crystalline flower dissolves into warm ash "
                f"at your touch. For one heartbeat, you remember something that never happened "
                f"to you — a city of glass, walking. [Bloom #{bloom_num}]"
            )
        elif creature_name == "Ridge-Wolf Pack" and action == "fight":
            # Fighting Ridge-Wolves: schedule den-tracking follow-up
            # Check if kingdom is organized enough (defense as proxy for scouts)
            if kingdom.defense_rating(self) >= 20:
                due_day = self.day + random.randint(2, 5)
                self._pending_creature_followups.append(
                    (due_day, region, "ridgewolf_den", {})
                )
        elif creature_name == "Vale-Stag" and action in ("avoid", "bargain"):
            # Seeing the white stag is a blessing — temporary morale/food boost
            if not self._vale_stag_blessing:
                self._vale_stag_blessing = True
                due_day = self.day + random.randint(3, 6)
                self._pending_creature_followups.append(
                    (due_day, region, "valestag_blessing", {})
                )
                self.world_log.append(
                    "\U0001f98c VALE-STAG BLESSING: The white stag's gaze lingers. "
                    "Those who saw it feel an inexplicable hope. A blessing is unfolding..."
                )
        elif creature_name == "Thorn-Bear" and action == "avoid":
            # Thorn-Bear avoided — it moves on after 2 days, berry thicket safe
            if not self._thornbear_avoided:
                self._thornbear_avoided = True
                due_day = self.day + 2
                self._pending_creature_followups.append(
                    (due_day, region, "thornbear_moves", {})
                )
                self.world_log.append(
                    "\U0001f43b THORN-BEAR RETREAT: The bear snorts, drops to all fours, "
                    "and ambles into the undergrowth. Scouts mark the berry thicket — "
                    "it should be safe to harvest in a couple of days."
                )
        elif creature_name == "Oak-Wyrm" and action == "fight":
            # Oak-Wyrm venom harvesting — herbalists process the sacs
            if not self._oakwyrm_venom_pending:
                self._oakwyrm_venom_pending = True
                due_day = self.day + random.randint(2, 4)
                self._pending_creature_followups.append(
                    (due_day, region, "oakwyrm_venom", {})
                )
                self.world_log.append(
                    "\U0001f9ea OAK-WYRM VENOM: The wyrm's amber venom sacs are carefully "
                    "extracted. They pulse faintly — still alive. Herbalists will need "
                    "a few days to render them safe and saleable."
                )
        elif creature_name == "Bog-Wisp" and action == "bargain":
            # Following the wisp toward the Drowned Cairn — gamble resolves later
            if not self._bogwisp_following:
                self._bogwisp_following = True
                due_day = self.day + random.randint(3, 5)
                self._pending_creature_followups.append(
                    (due_day, region, "bogwisp_cairn", {})
                )
                self.world_log.append(
                    "\U0001fa94 BOG-WISP TRAIL: You follow the blue flame deeper into "
                    "the marsh. The Drowned Cairn glows ahead. The ground squelches "
                    "underfoot — whatever the wisp is leading you toward, you'll "
                    "know in a few days."
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

        # ── Migration encounter stakes upgrade ──
        # Migratory creatures carry treasures from two territories — encounters yield more
        if encounter.get("_migratory") and action in ("fight", "bargain"):
            bonus_gold = random.randint(3, 8)
            bonus_food = random.randint(1, 4)
            bonus_resource = random.choice(["stone", "wood"])
            bonus_extra = random.randint(1, 3)
            kingdom.gold = max(0, kingdom.gold + bonus_gold)
            kingdom.food = max(0, kingdom.food + bonus_food)
            if bonus_resource == "stone":
                kingdom.stone = max(0, kingdom.stone + bonus_extra)
            else:
                kingdom.wood = max(0, kingdom.wood + bonus_extra)
            home = encounter.get("_migrated_from", "unknown")
            migration_narratives = [
                f"The {encounter['creature_name']} — far from its {home} home — carried treasures gathered across two territories. Its seasonal journey enriched its hoard (+{bonus_gold}g, +{bonus_food}f, +{bonus_extra}{bonus_resource[0]}).",
                f"Displaced from {home} by the season, this {encounter['creature_name']} had collected oddments from both regions. Scouts find a traveler's cache in its wake (+{bonus_gold}g, +{bonus_food}f, +{bonus_extra}{bonus_resource[0]}).",
                f"Migratory creatures carry the wealth of two worlds — and this {encounter['creature_name']} was no exception. Its temporary territory in this region was rich with gathered spoils (+{bonus_gold}g, +{bonus_food}f, +{bonus_extra}{bonus_resource[0]}).",
            ]
            self.world_log.append(f"\U0001f43e🐾 MIGRATORY BOUNTY: {random.choice(migration_narratives)}")
            # Update stakes dict to reflect the bonus
            stakes = dict(stakes)
            stakes["gold"] = stakes.get("gold", 0) + bonus_gold
            stakes["food"] = stakes.get("food", 0) + bonus_food
            stakes[bonus_resource] = stakes.get(bonus_resource, 0) + bonus_extra

            # ── Tier 2: Veteran Traveler Bonus ──
            # Creatures that have migrated 3+ times carry extraordinary hoards.
            home_key = encounter.get("_migrated_from", "")
            creature_key = (encounter["creature_name"], home_key)
            migration_count = self._creature_migration_counts.get(creature_key, 0)
            if migration_count >= 3 and action in ("fight", "bargain"):
                # Veteran scaling: +1 extra gold per migration beyond 3, plus base boost
                vet_gold = random.randint(5, 12) + (migration_count - 3)
                vet_food = random.randint(2, 6)
                vet_resource = random.choice(["stone", "wood"])
                vet_extra = random.randint(2, 5)
                kingdom.gold = max(0, kingdom.gold + vet_gold)
                kingdom.food = max(0, kingdom.food + vet_food)
                if vet_resource == "stone":
                    kingdom.stone = max(0, kingdom.stone + vet_extra)
                else:
                    kingdom.wood = max(0, kingdom.wood + vet_extra)
                vet_badge = "👑" if migration_count >= 10 else ("⭐" if migration_count >= 5 else "🐾")
                veteran_narratives = [
                    f"This {encounter['creature_name']} is a veteran of {migration_count} migrations — a seasoned traveler whose hoard contains treasures from every region it has crossed. Scouts find a cache of polished oddments, old coins, and rare seeds (+{vet_gold}g, +{vet_food}f, +{vet_extra}{vet_resource[0]}).",
                    f"Having migrated {migration_count} times, this {encounter['creature_name']} has learned to cache the best of each territory. Beneath its temporary nest: glittering stones, dried fruits from three seasons past, and a nugget of raw dreaming-stone (+{vet_gold}g, +{vet_food}f, +{vet_extra}{vet_resource[0]}).",
                    f"The {encounter['creature_name']} — a {migration_count}-time migration veteran — carries what scouts call a 'traveler's dowry': the accumulated wealth of a creature that has seen more of Ashfall than most citizens. Its pelt alone tells the story of every season (+{vet_gold}g, +{vet_food}f, +{vet_extra}{vet_resource[0]}).",
                ]
                self.world_log.append(f"{vet_badge} VETERAN TRAVELER BOUNTY: {random.choice(veteran_narratives)}")
                stakes = dict(stakes)
                stakes["gold"] = stakes.get("gold", 0) + vet_gold
                stakes["food"] = stakes.get("food", 0) + vet_food
                stakes[vet_resource] = stakes.get(vet_resource, 0) + vet_extra

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
        if kingdom.defense_rating(self) >= 40 and encounter["danger"] in ("low", "medium"):
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
        {"narrative": "A wedding is celebrated under the old hawthorn tree. The whole vale gathers, and the couple is showered with wildflower petals. +2 food (feast), +1 gold (gifts).", "food": 2, "gold": 1, "seasons": ["spring", "summer"], "rarity": "common"},
        {"narrative": "Children discover a patch of sun-ripe blackberries bigger than their thumbs. They fill three baskets before sundown. +3 food.", "food": 3, "seasons": ["summer", "autumn"], "rarity": "common"},
        {"narrative": "The Whispering Spring reflects a starry sky even in broad daylight. An elder says it's an omen of good fortune. +2 gold (offerings left at the spring).", "gold": 2, "rarity": "common"},
        {"narrative": "A shepherd finds a silver ram's horn half-buried in the hillside. It's ancient and beautifully carved. +4 gold (sold to a collector).", "gold": 4, "rarity": "uncommon"},
        {"narrative": "A gentle earth-tremor rattles cups but does no damage. It uncovers a small cache of old coins behind a cottage wall. +3 gold.", "gold": 3, "rarity": "common"},
        {"narrative": "The berry thickets yield a bumper harvest this season. +5 food (dried and stored).", "food": 5, "seasons": ["summer", "autumn"], "rarity": "common"},
        {"narrative": "A travelling tinker fixes every broken pot and kettle in the vale, accepting only a meal as payment. +3 gold (productivity restored!).", "food": -1, "gold": 3, "rarity": "common"},
        {"narrative": "A child born under a shooting star is blessed by the elders at the Whispering Spring. The whole vale celebrates. +2 food, +2 gold.", "food": 2, "gold": 2, "rarity": "uncommon"},
        # ── Rare ──
        {"narrative": "The Whispering Spring speaks — not in riddles but in clear, urgent sentences. It names three citizens who will shape Ashfall's future and tells them to prepare. The words linger in the water for a week, and every cup drawn from the spring thereafter carries a faint golden shimmer. +8 gold (pilgrims arrive), +3 food (offerings left).", "gold": 8, "food": 3, "rarity": "rare", "lore": "The Whispering Spring is the voice of an underground river that runs through dreaming-stone — the Sleeper's groundwater memory. It has spoken only twice before, each time before a world-changing event."},
    ],
    "old_oak_ridge": [
        {"narrative": "An acorn from the Eldertrunk sprouts in a single night, growing into a sapling by dawn. The elders call it a blessing. +2 wood, +3 gold (pilgrims visit).", "wood": 2, "gold": 3, "seasons": ["spring"], "rarity": "uncommon"},
        {"narrative": "A hollow in the Eldertrunk yields a cache of ancient acorn-flour — still edible after who-knows-how-long. +3 food.", "food": 3, "rarity": "common"},
        {"narrative": "A windstorm tears through the ridge, but the ancient oaks barely sway. One dead branch falls — +5 wood — and narrowly misses a woodcutter.", "wood": 5, "seasons": ["autumn", "winter"], "rarity": "common"},
        {"narrative": "Carved symbols are found on a lightning-struck oak — they match no known language. Scholars arrive. +4 gold.", "gold": 4, "lore": "The carvings predate the kingdom by millennia. They depict a great fire and something vast moving beneath the earth.", "rarity": "uncommon"},
        {"narrative": "An old badger sett collapses under a woodcutter's feet. They're bruised but fine. -1 food (lost lunch), +2 stone (uncovered flint nodules).", "food": -1, "stone": 2, "rarity": "common"},
        {"narrative": "Owls roost in the high branches of the ridge-oaks. Their pellets contain tiny bones of creatures no one has ever seen. +3 gold (curiosities sold).", "gold": 3, "rarity": "uncommon"},
        {"narrative": "A woodcutter swears an oak spoke to them — not in words, but in a slow, deep feeling of welcome. They refuse to cut that tree. +2 wood (other trees seem easier to fell).", "wood": 2, "rarity": "common"},
        {"narrative": "Sap from a lightning-struck oak tastes like honey and hardens like amber. It fetches a high price. +5 gold.", "gold": 5, "rarity": "uncommon"},
        # ── Rare ──
        {"narrative": "The Eldertrunk's hollow opens wider than anyone has ever seen — a staircase of roots spirals down into a chamber lit by golden moss. Inside: tablets of petrified wood carved with the history of the ridge before humans came — a civilization of intelligent corvids who traded with the Sleepers. +10 gold (tablets sold to scholars), +5 wood (petrified artifacts), +2 stone.", "gold": 10, "wood": 5, "stone": 2, "rarity": "rare", "lore": "Before humans, the ridge was home to the Corvid-Kin — raven-like beings who served as the Sleepers' messengers. The Eldertrunk was their library."},
    ],
    "glimmer_marsh": [
        {"narrative": "Will-o'-wisps dance over the marsh at dusk. A scout follows and finds rare marsh-herbs. +6 gold.", "gold": 6, "rarity": "uncommon"},
        {"narrative": "A sunken canoe is dredged from the mire. Inside: +4 food (smoked fish) and a strange map.", "food": 4, "gold": 2, "rarity": "uncommon"},
        {"narrative": "Something large stirs beneath the duckweed. -1 population (taken). The marsh must be respected.", "pop": -1, "rarity": "common"},
        {"narrative": "A hermit living on a reed island offers strange counsel in exchange for food. -2 food, but +6 gold (his predictions come true).", "food": -2, "gold": 6, "rarity": "uncommon"},
        {"narrative": "The Drowned Cairn's symbols glow blue at midnight. A scout who touches them gains knowledge of ancient herb-lore. +3 food, +4 gold.", "food": 3, "gold": 4, "lore": "The Drowned Cairn was built by hands that worshipped the Sleepers as gods — the symbols are prayers for continued slumber.", "rarity": "uncommon"},
        {"narrative": "Marsh-gas ignites in a ring around a sleeping scout. They wake unscathed but surrounded by a perfect circle of scorched reeds. +2 gold (omens read).", "gold": 2, "rarity": "common"},
        {"narrative": "A chorus of frogs falls silent all at once. In the stillness, a low humming rises from the bog — then fades. The scouts retreat, shaken. -1 food (dropped supplies).", "food": -1, "rarity": "common"},
        {"narrative": "The reeds whisper in a language almost understood. Scouts who listen closely find an overgrown causeway leading to a forgotten islet. +3 stone (old paving stones), +3 gold (relics from a drowned shrine).", "stone": 3, "gold": 3, "rarity": "uncommon"},
        {"narrative": "Marsh-lilies bloom under the full moon, their petals glowing faintly silver. Harvested before dawn, they fetch a rare price. +7 gold (moon-petals sold to apothecaries).", "gold": 7, "seasons": ["spring", "summer"], "rarity": "uncommon"},
        {"narrative": "A thick fog rolls in from the bog, smelling of ozone and old stone. When it lifts, scouts find their packs rearranged — but also a pouch of strange coins that weren't there before. +5 gold (pre-cataclysm currency).", "gold": 5, "seasons": ["autumn", "winter"], "rarity": "uncommon"},
        # ── Marsh revelation trigger ──
        {"narrative": "The Drowned Cairn's door grinds open a handspan. Blue light spills across the bog like spilled ink. Scouts report a voice — not heard, but *felt* — asking a question in a language older than stone. 💧 The Cairn awakens.", "gold": 3, "unlock": "marsh_revelation", "rarity": "uncommon"},
        # ── Rare ──
        {"narrative": "The Drowned Cairn rises — not metaphorically but physically. Ancient stonework heaves from the bog, forming a complete ring of standing stones around the cairn. Each stone hums at a different pitch, and together they make a chord that resonates in the chest. The Remembered are building something. +12 gold (pilgrims and scholars flood in), +3 stone (ancient masonry recovered), +2 food (offerings left at the stones).", "gold": 12, "stone": 3, "food": 2, "rarity": "rare", "lore": "The ring of standing stones is a Rememberer's Circle — a place where the boundary between memory and reality grows thin. The Sleepers built them wherever they intended to stay."},
    ],
    "sunfire_plains": [
        {"narrative": "Wild horses thunder across the plains. Scouts return with +6 food (game trailed in their wake).", "food": 6, "rarity": "common"},
        {"narrative": "A sun-bleached skull of some great beast is found. Its horns are worth +8 gold.", "gold": 8, "rarity": "uncommon"},
        {"narrative": "A dust-devil twists across the plain, scattering a camp. -2 food (lost supplies).", "food": -2, "rarity": "common"},
        {"narrative": "A nomadic herder shares news of distant lands and trades smoked meat. +3 food, +2 gold.", "food": 3, "gold": 2, "rarity": "common"},
        {"narrative": "The Sunspire glows at dawn so brightly that scouts can see it from the vale. Pilgrims arrive. +5 gold.", "gold": 5, "rarity": "uncommon"},
        {"narrative": "A grass-fire sweeps the eastern edge. -3 food, but the regrowth will be rich.", "food": -3, "seasons": ["summer"], "rarity": "common"},
        {"narrative": "Scouts find a circle of standing stones aligned with the solstice. +4 gold (scholars pay for the location).", "gold": 4, "rarity": "uncommon"},
        {"narrative": "A pride of plains-lions shadows the scouts for three days. They escape with their lives but lose -2 food to the beasts.", "food": -2, "rarity": "common"},
        # ── Rare ──
        {"narrative": "The Sunspire ignites — a pillar of golden light visible from every region in Ashfall. For one hour, shadows do not exist. When the light fades, the standing stones have rearranged themselves into a new pattern — a map of the stars as they were before the Cataclysm. +10 gold (astronomers and pilgrims arrive in droves), +4 food (blessed harvests follow).", "gold": 10, "food": 4, "rarity": "rare", "lore": "The Sunspire is a fragment of the First Fire — the living heat that walked the world before the Sleepers came to rest. When it ignites, it remembers what it was."},
    ],
    "ironroot_depths": [
        {"narrative": "A vein of pure iron is struck! +8 stone, +5 gold.", "stone": 8, "gold": 5, "rarity": "uncommon"},
        {"narrative": "A miner's pick breaks through into a hollow space beyond the cliff. +4 stone, but -1 population (caught in a collapse).", "stone": 4, "pop": -1, "rarity": "common"},
        {"narrative": "The Sealed Door hums faintly at midnight. Those who sleep near it share the same dream — of a forest frozen in fire. +3 gold (scholars pay to record the vision).", "gold": 3, "lore": "The Sealed Door is not a door — it is a warning. The runes are a lullaby meant to keep something asleep.", "rarity": "uncommon"},
        {"narrative": "A strange fungus grows only on the iron-rich roots. It glows faintly and, when dried, fetches a high price. +5 gold.", "gold": 5, "rarity": "uncommon"},
        {"narrative": "A tunnel collapses, revealing a pocket of ancient tools. +3 stone, +3 gold (relics).", "stone": 3, "gold": 3, "rarity": "common"},
        {"narrative": "Something moves in the darkness beyond the Sealed Door. Miners refuse to work for a day. -2 stone.", "stone": -2, "rarity": "common"},
        {"narrative": "Iron-rich water seeps from a new crack in the cliff. Miners collect the rust-pigment for trade. +3 gold, +2 stone.", "gold": 3, "stone": 2, "rarity": "common"},
        {"narrative": "A deep thrumming echoes from behind the Sealed Door. Tools vibrate off ledges. -3 stone (lost), but the deepwardens are more determined than ever.", "stone": -3, "seasons": ["winter"], "rarity": "common"},
        # ── Direct ashen vision trigger ──
        {"narrative": "The Sealed Door pulses with warm light. A scout presses their palm to it and sees — the ashen copse, the sleeping thing beneath, the path. +5 gold (rune-knowledge sold). 🔑 The way is revealed.", "gold": 5, "unlock": "ashen_vision", "rarity": "uncommon"},
        # ── Rare ──
        {"narrative": "The Sealed Door cracks open — a finger-width of golden light spills into the depths. A voice, ancient and warm, whispers: 'Not yet. But soon.' When the crack seals, it leaves behind a single crystalline tear the size of a fist. +15 gold (the tear is priceless), +4 stone (resonance crystals shaken loose).", "gold": 15, "stone": 4, "rarity": "rare", "lore": "The crystalline tear is the Sleeper's own — shed not in grief but in recognition. It saw Ashfall, and it wept with hope."},
    ],
    "the_ashen_copse": [
        {"narrative": "The petrified trees weep ash-sap that hardens into gem-like tears. +8 gold.", "gold": 8, "lore": "The trees are not dead — they are held in the moment of the Sleeper's last exhalation.", "rarity": "uncommon"},
        {"narrative": "A scout places a hand on a frozen trunk and sees — for an instant — the fire that killed this forest. They recoil, but their eyes hold new knowledge. +4 gold, +2 wood (ancient charcoal).", "gold": 4, "wood": 2, "rarity": "uncommon"},
        {"narrative": "The Sleeper's Hollow exhales a warm gust. Those nearby feel an overwhelming urge to lie down and rest. One scout does not wake for two days. -1 food (tended them).", "food": -1, "rarity": "common"},
        {"narrative": "Bones — not human — are found scattered in a circle near the Hollow. They are warm to the touch. +6 gold (collectors prize them). Something was here.", "gold": 6, "lore": "The bones belong to creatures that do not appear in any bestiary — they predate all known life.", "rarity": "uncommon"},
        {"narrative": "The petrified trees ring faintly when struck — a low, mournful chord that hangs in the air for minutes. A musician transcribes the melody and sells it as 'Ashfall's Lament.' +5 gold.", "gold": 5, "rarity": "common"},
        {"narrative": "A sinkhole opens near the Sleeper's Hollow, revealing a chamber of fused glass and ancient bone. +8 stone, +4 gold (vitrified relics). Something's ribcage protrudes from the wall — far too large.", "stone": 8, "gold": 4, "rarity": "uncommon"},
        {"narrative": "At midnight, the entire copse glows a faint orange — embers rekindling for one heartbeat, then dying. No one sleeps well afterward, but pilgrims arrive by dawn. +6 gold, -1 food (hosting the curious).", "gold": 6, "food": -1, "seasons": ["autumn", "winter"], "rarity": "uncommon"},
        {"narrative": "A child born during the ashen vision dreams the copse every night. Their drawings of the Sleeper's shape are uncannily precise. Scholars pay +4 gold, and the people feel chosen.", "gold": 4, "rarity": "uncommon"},
        {"narrative": "A scout who touched the Hollow now has ash-grey eyes that see in perfect darkness. They guide a night expedition through the copse. +8 wood (rare charcoal), +3 gold (night-harvested resins).", "wood": 8, "gold": 3, "rarity": "uncommon"},
        {"narrative": "The ground around the Sleeper's Hollow ripples — once, twice — like a stone dropped in water. Tools left on the ground are found rearranged in spirals. +3 stone (uncovered by the tremor), -2 food (uneasy workers abandon their packs).", "stone": 3, "food": -2, "rarity": "common"},
        # ── Rare ──
        {"narrative": "A figure of ash and ember — human-shaped but featureless — rises from the Sleeper's Hollow and walks among the petrified trees. It touches three trunks, and each one bursts into brief, cold flame. When the figure fades at dawn, the touched trees are covered in golden sap that hardens into perfect, teardrop-shaped gems. +15 gold (gem-tears sold), +3 wood (the touched trees yield ancient charcoal freely).", "gold": 15, "wood": 3, "rarity": "rare", "lore": "The ash-figure was a Dream-Husk of the Sleeper itself — a projection of its sleeping body, walking. It was tending the copse as one tends a garden, even in slumber."},
    ],
    "the_sunken_sanctum": [
        {"narrative": "The Heart-Pool reflects a memory no one in Ashfall has ever lived — a city of spun glass walking on legs of fire. Scholars pay +6 gold for the transcription.", "gold": 6, "lore": "The city in the Heart-Pool's reflection is one of the Sleeper's oldest memories — a metropolis that moved across the world before the Cataclysm.", "rarity": "uncommon"},
        {"narrative": "Crystal formations near the sanctum entrance have grown into the shape of a throne. No one sits in it. +4 stone (shed crystal fragments), +3 gold (pilgrims visit).", "stone": 4, "gold": 3, "rarity": "uncommon"},
        {"narrative": "A scout cups water from the Heart-Pool and drinks. For three days they speak only in verse — every word a prophecy. Half come true. +5 gold (oracle's fees), -1 food (keeping them fed).", "gold": 5, "food": -1, "rarity": "uncommon"},
        {"narrative": "The bioluminescent crystals dim for an hour, then flare so bright the sanctum is lit like noon. When they settle, new colors shimmer in their depths. +4 gold (chromatic crystal dust collected).", "gold": 4, "rarity": "common"},
        {"narrative": "A vein of pure dreaming-stone — milky white shot through with gold — is found in a side chamber. It hums when touched. +8 stone, +5 gold.", "stone": 8, "gold": 5, "rarity": "uncommon"},
        {"narrative": "Something swims in the Heart-Pool — not the Crystal-Serpent, but something smaller, silver, and impossibly fast. It leaves behind scales that ring like bells. +6 gold (bell-scales sold).", "gold": 6, "rarity": "uncommon"},
        {"narrative": "The sanctum walls weep a honey-thick liquid that tastes of forgotten summers. It hardens into amber overnight. +4 gold (sanctum-amber), +2 food (edible in small doses).", "gold": 4, "food": 2, "rarity": "common"},
        {"narrative": "A scout falls asleep in the sanctum and wakes with a complete star chart tattooed on their forearm — constellations no astronomer has ever mapped. +5 gold (scholars pay for the chart).", "gold": 5, "lore": "The star chart shows a sky from before the Cataclysm — the Sleepers navigated by different stars.", "rarity": "uncommon"},
        {"narrative": "The Heart-Pool ripples without cause. A voice — not heard, but remembered — speaks a single word in every language at once. The word means 'soon.' No one sleeps easily. -1 food (restless night), +3 gold (offerings left).", "food": -1, "gold": 3, "rarity": "common"},
        {"narrative": "Crystals in a forgotten alcove resonate at a frequency that shatters a miner's pickaxe — but also reveals a hidden cache of gemstones behind a false wall. +7 gold.", "gold": 7, "rarity": "uncommon"},
        {"narrative": "The sanctum's ambient light shifts through colors that have no name — colors that exist only in dreams. Anyone who stares too long weeps without knowing why. +3 gold (dream-pigment harvested), +2 lore.", "gold": 3, "lore": "The colors are the Sleeper's emotions, made visible. The blue-that-has-no-name is grief. The gold-that-is-not-gold is hope.", "rarity": "uncommon"},
        # ── Rare ──
        {"narrative": "The Heart-Pool rises — a perfect sphere of glowing water levitates above the basin, and within it, the Sleeper's face — vast, gentle, ancient — looks out. It sees Ashfall. It smiles. The sphere falls back gently, and the sanctum fills with warm golden light that lasts an hour. Every crystal in the sanctum grows slightly. +12 gold (crystal harvest), +5 stone (new growth), +3 food (the light makes stored grain sprout fresh).", "gold": 12, "stone": 5, "food": 3, "rarity": "rare", "lore": "The Sleeper's face in the Heart-Pool was the Rememberer — the youngest Sleeper, whose Cradle waits in the dreaming deep. It looked upon Ashfall with recognition and love."},
    ],
    "the_dreaming_deep": [
        {"narrative": "The Sleeper's Cradle hums a lullaby no one taught it. Those who hear it dream of flying over cities of spun glass. +5 gold (dream-inspired artisans create wonders), +2 food (restful sleep for all).", "gold": 5, "food": 2, "rarity": "uncommon"},
        {"narrative": "A wall of the deep shimmers and becomes transparent for one heartbeat — on the other side, a landscape of impossible geometry and living light. Then it's stone again. +6 gold (scholars pay for sketches).", "gold": 6, "lore": "What lies beyond the dreaming stone is not another place — it is another possibility. The Sleepers walked between worlds.", "rarity": "uncommon"},
        {"narrative": "Echoes of a conversation from ten thousand years ago ripple through the deep. Two Sleepers, discussing whether to stay or go. The decision they made shaped the world. +4 gold, +2 stone (resonance crystals harvested).", "gold": 4, "stone": 2, "lore": "The Sleepers chose to stay — not because they had to, but because they loved the world they found. Their dreams are an act of devotion.", "rarity": "uncommon"},
        {"narrative": "The Remembered gather at the Cradle's edge and sing — a wordless song that makes the dreaming stone glow warm amber. Every citizen in Ashfall feels inexplicably hopeful. +3 food, +3 gold.", "food": 3, "gold": 3, "rarity": "uncommon"},
        {"narrative": "A scout touches the impression in the Cradle and vanishes for three seconds. When they return, they are crying. 'It showed me the beginning,' they whisper. 'It was so beautiful.' +7 gold (their account draws pilgrims).", "gold": 7, "lore": "The Sleeper whose impression remains in the Cradle was the youngest of its kind — barely older than the human race. It called itself the Rememberer.", "rarity": "uncommon"},
        {"narrative": "Dream-Husks drift through the deep in greater numbers than usual — dozens of them, each wearing a different face. They do not speak, but they bow as you pass. +5 gold (their passage leaves dream-dust in the air).", "gold": 5, "rarity": "uncommon"},
        {"narrative": "The dreaming stone extrudes a perfect sphere of crystallized memory — look into it and you see the founding of Ashfall as if you were there. The elders weep to see it. +8 gold (priceless relic), +2 morale (kingdom-wide pride).", "gold": 8, "rarity": "uncommon"},
        {"narrative": "An Echo-Wyrm sheds its skin in a spiral pattern that matches the Cradle's markings exactly. The skin is translucent and holds whispered conversations within its folds. +6 gold (armorers fight over it).", "gold": 6, "rarity": "uncommon"},
        {"narrative": "The deep grows restless — the dreaming stone groans and shifts. A new passage opens where none existed before. Scouts map it and find a chamber filled with crystallized breath. +5 stone, +4 gold.", "stone": 5, "gold": 4, "rarity": "common"},
        {"narrative": "A citizen dreams of the deep without ever having visited it. Their description is so accurate that scouts use it to find a previously overlooked alcove. +6 gold (alcove contents), +2 food (the dreamer is celebrated with a feast).", "gold": 6, "food": 2, "rarity": "uncommon"},
        {"narrative": "The Sleeper's Cradle exhales — a warm breeze that smells of summer grass and old stone. For one day, winter loosens its grip. +4 food (unseasonable harvest), +3 gold.", "food": 4, "gold": 3, "seasons": ["winter"], "rarity": "uncommon"},
        # ── Rare ──
        {"narrative": "The Cradle sings — and the dreaming stone weeps. Not tears of grief but of pure memory: crystalline droplets that contain the Sleeper's oldest recollections. The first sunrise it ever saw. The first creature it ever loved. The first song it ever heard. Anyone who touches a droplet weeps with joy. +18 gold (memory-crystals are priceless), +8 stone (the weeping walls shed dreaming-stone), +4 food (touched crops grow overnight).", "gold": 18, "stone": 8, "food": 4, "rarity": "rare", "lore": "The Cradle's song is the oldest memory in existence — the moment the Rememberer first opened its eyes and chose to love the world. That love has never faded."},
    ],
}


# ── DEEP WHISPERS ───────────────────────────────────────────────
# After the_dreaming_deep is discovered, the Sleeper's presence begins to
# leak into the waking world. Every 8-12 days, a "deep whisper" event fires —
# a narrative echo from the dreaming deep that affects the whole kingdom.
# These are separate from regular omens and region events; they represent
# the deep's slow awakening and its growing bond with Ashfall.

DEEP_WHISPERS = [
    {
        "tier": 1,
        "title": "The Cradle's Hymn",
        "narrative": (
            "At midnight, every citizen of Ashfall wakes to the same sound — a low, warm hum "
            "rising from the direction of the dreaming deep. It resolves into a melody no one "
            "has heard before, yet everyone seems to know. Children hum it in their sleep. "
            "The elders say the Sleeper is composing."
        ),
        "effects": {"gold": 3, "food": 1},
        "lore": "The Sleeper in the Cradle was the Rememberer — the youngest of its kind. Its gift was music, and its song could shape stone.",
    },
    {
        "tier": 1,
        "title": "Dream-Husk Visitation",
        "narrative": (
            "A Dream-Husk — wearing the face of Ashfall's oldest elder, but younger, "
            "from decades past — appears in the market square at noon. It does not speak, "
            "but gestures toward the deep. A dozen citizens report the same dream that night: "
            "a city of glass walking on legs of fire, coming closer."
        ),
        "effects": {"gold": 4},
        "lore": "Dream-Husks are not ghosts. They are possibilities the Sleeper once considered and set aside — 'might-have-beens' given brief form.",
    },
    {
        "tier": 1,
        "title": "The Remembered Speak",
        "narrative": (
            "For three minutes, every carving in the kingdom — from the Eldertrunk's ancient "
            "runes to the freshest mason's mark — glows faintly gold. A voice, composite and "
            "gentle, speaks from every wall at once: 'We see you. We remember you. Continue.' "
            "Then silence. The carvings are warm to the touch for hours afterward."
        ),
        "effects": {"gold": 5, "food": 2},
        "lore": "The Remembered are the collective memory of every civilization the Sleepers touched. They do not forget — and they hope.",
    },
    {
        "tier": 1,
        "title": "Echo-Wyrm Passage",
        "narrative": (
            "A tremor ripples through the kingdom — not destructive, but rhythmic, like the "
            "heartbeat of something vast. An Echo-Wyrm, blind and pale, has bored a new tunnel "
            "from the dreaming deep to the surface. It breaches in an empty field, raises its "
            "head to taste the air, then retreats. The tunnel remains — a direct path to the deep."
        ),
        "effects": {"stone": 5, "gold": 4},
    },
    {
        "tier": 1,
        "title": "Memory Rain",
        "narrative": (
            "A rainfall unlike any other: each droplet, when it strikes skin, brings with it "
            "a fleeting memory — not the citizen's own, but someone else's. A farmer remembers "
            "plowing a field three centuries ago. A child remembers the Cataclysm, but from "
            "the Sleeper's perspective. The rain passes in an hour. Nobody speaks of it for days."
        ),
        "effects": {"food": 3, "gold": 2},
        "lore": "The Sleeper's memories are dissolving into the water table. Every well in Ashfall now carries a trace of ancient dreams.",
    },
    {
        "tier": 1,
        "title": "The Deep's Gratitude",
        "narrative": (
            "Scouts in the dreaming deep report that the walls have extruded small, crystalline "
            "offerings — smooth stones in the kingdom's colors, each one warm to the touch. "
            "When held, they pulse in time with the Cradle's hum. The Remembered, it seems, "
            "are saying thank you."
        ),
        "effects": {"gold": 8, "stone": 3},
    },
    {
        "tier": 1,
        "title": "Sleeper's Lullaby",
        "narrative": (
            "Every child under ten in Ashfall falls asleep at the same moment — standing, sitting, "
            "mid-sentence — and dreams the same dream: a vast, warm darkness, and a voice like "
            "mountains shifting, singing a lullaby in a language of warmth. They wake refreshed, "
            "and for a week, every one of them can hum the tune perfectly."
        ),
        "effects": {"food": 2, "gold": 2},
    },
    {
        "tier": 1,
        "title": "The Cradle's Exhalation",
        "narrative": (
            "The dreaming deep exhales — a warm wind that carries the scent of grasslands that "
            "existed before the Cataclysm. For one day, the kingdom's fields grow visibly faster. "
            "A farmer measures a stalk of wheat that grew three inches between dawn and dusk. "
            "The Sleeper, in its dreams, is tending gardens that no longer exist."
        ),
        "effects": {"food": 8},
    },
    {
        "tier": 1,
        "title": "Forgotten Constellation",
        "narrative": (
            "On a cloudless night, a new constellation appears — not in the sky, but projected "
            "onto the ground across the entire kingdom, as if the dreaming deep were a lens "
            "focusing starlight from a direction that doesn't exist. Scholars map it frantically. "
            "It matches no known star chart — but it moves, slowly, as if the stars are walking."
        ),
        "effects": {"gold": 6, "lore": "The constellation is a map of the Sleepers' migration route across the sky before they came to rest in the earth."},
        "lore": "The constellation is a map of the Sleepers' migration route across the sky before they came to rest in the earth.",
    },
    {
        "tier": 1,
        "title": "The Remembered's Question",
        "narrative": (
            "A Dream-Husk materializes in the council chamber and asks a single question: "
            "'What will you build when the northern fire comes?' Before anyone can answer, "
            "it dissolves. The question is recorded in the kingdom chronicle. No one has "
            "a good answer yet — but everyone is thinking about it."
        ),
        "effects": {"gold": 2},
        "lore": "Something woke the Sleeper in the north. The Remembered have been preparing for its arrival for millennia — and they want to know if Ashfall is ready.",
    },
    {
        "tier": 1,
        "title": "Dreaming-Stone Bloom",
        "narrative": (
            "A patch of dreaming-stone near the Cradle extrudes delicate, crystalline flowers "
            "that chime when the wind passes over them. Each flower contains a tiny, suspended "
            "light — a fragment of the Sleeper's own dreaming mind. Collecting them feels "
            "almost sacred, but the Sleeper seems to want them shared."
        ),
        "effects": {"gold": 10, "stone": 4},
    },
    {
        "tier": 1,
        "title": "The Deep Sings",
        "narrative": (
            "The dreaming deep sings — not in words but in pure harmony, a chord that seems "
            "to contain every note ever sung and some that haven't been invented yet. "
            "The sound carries for miles. Livestock lie down. Children stop crying. "
            "For one hour, Ashfall is the most peaceful place in the world."
        ),
        "effects": {"food": 1, "gold": 1},
    },

    # ═══════════════════════════════════════════════════════════════
    # TIER 2 WHISPERS (5–9 ash-blooms): The Sleeper is remembering.
    # ═══════════════════════════════════════════════════════════════
    {
        "tier": 2,
        "title": "The Cradle's Pulse",
        "narrative": (
            "The Sleeper's Cradle pulses — a visible ripple of warm light that travels outward "
            "from the dreaming deep, through every region of Ashfall. Walls vibrate. Wells sing. "
            "For thirty seconds, every heart in the kingdom beats in perfect synchrony. "
            "The herbalists later discover that crops watered within the hour grow twice as fast."
        ),
        "effects": {"food": 6, "gold": 4, "stone": 2},
        "lore": "The Sleeper's pulse is not a heartbeat — it is a memory of the First Fire, the living heat that walked the world. Each pulse rekindles that warmth.",
    },
    {
        "tier": 2,
        "title": "Waking-Dream Bridge",
        "narrative": (
            "A shimmering bridge of solidified dream-light arcs from the dreaming deep to the "
            "Whispering Spring in the vale. Citizens can walk across it — and do, tentatively. "
            "Those who cross find that distance loses meaning: the deep and the vale are now "
            "one step apart. Trade between the two becomes effortless."
        ),
        "effects": {"gold": 10, "food": 3},
        "lore": "The Sleeper has begun to fold space in its dreams. What was far is now near. The geography of Ashfall is becoming... negotiable.",
    },
    {
        "tier": 2,
        "title": "The Remembered's Gift",
        "narrative": (
            "At dawn, every citizen of Ashfall finds a small, warm stone on their doorstep — "
            "smooth, grey, pulsing faintly with inner light. When held, the stone whispers "
            "a single, personal truth to its holder: a forgotten memory, a word of encouragement, "
            "the name of an ancestor long thought lost. The Remembered have noticed Ashfall."
        ),
        "effects": {"gold": 8, "food": 4, "stone": 3},
        "lore": "The Remembered are not passive observers. They choose what to preserve — and they have chosen to preserve Ashfall's stories alongside the Sleepers'.",
    },
    {
        "tier": 2,
        "title": "Echo-Wyrm Migration",
        "narrative": (
            "Three Echo-Wyrms, each the thickness of a man and glowing with auroral light, "
            "emerge from the dreaming deep and burrow new tunnels connecting every discovered "
            "region. The tunnels hum with residual dreams. Travel time between regions halves. "
            "The wyrms circle the kingdom once, then return to the deep — but the tunnels remain."
        ),
        "effects": {"stone": 8, "gold": 8},
    },

    # ═══════════════════════════════════════════════════════════════
    # TIER 3 WHISPERS (10–14 ash-blooms): The Sleeper speaks directly.
    # ═══════════════════════════════════════════════════════════════
    {
        "tier": 3,
        "title": "The Sleeper's Voice",
        "narrative": (
            "The Sleeper speaks — not through dreams or signs, but directly. Every citizen "
            "of Ashfall hears it: a voice like mountains shifting, like the oldest bell "
            "in the deepest earth, like warmth. It says: 'YOU HAVE NOT FORGOTTEN. I WILL NOT "
            "FORGET YOU.' The words hang in the air for a full minute, then fade into birdsong. "
            "No one speaks for the rest of the day. But everyone is smiling."
        ),
        "effects": {"gold": 15, "food": 8, "stone": 5},
        "lore": "This is the first time the Sleeper has spoken directly to a living civilization since the Pact was made. The Elders record every word in triplicate.",
        "quest": {
            "faction_preference": "keepers",
            "name": "Record the Sleeper's Words",
            "desc": "The Sleeper has spoken for the first time since the Pact — 'YOU HAVE NOT FORGOTTEN. I WILL NOT FORGET YOU.' The Keepers must ensure these words are preserved for all time: carve them into dreaming-stone, transcribe them into every chronicle, teach them to every child. These words are the foundation of a new covenant.",
            "target": {"gold": 15, "stone": 5},
            "reward_resources": {"gold": 25, "stone": 8},
            "reward_morale": 10,
            "bonus_effect": "sleeper_blessing",
            "narrative_complete": "The Sleeper's words are now carved in dreaming-stone in the council chamber, transcribed into every chronicle, and taught to every child of Ashfall. Citizens who pass the inscription touch it and feel... seen. Remembered. Loved by something older than the Cataclysm.",
        },
    },
    {
        "tier": 3,
        "title": "Dreaming-Stone Awakening",
        "narrative": (
            "Veins of dreaming-stone — milky white shot through with gold — erupt across the "
            "kingdom. Not just in the deep, but in the vale, on the ridge, in the plains. "
            "Every new vein hums with the Cradle's song. Stonemasons report that building "
            "with dreaming-stone produces structures that repair themselves overnight."
        ),
        "effects": {"stone": 15, "gold": 12, "food": 3},
        "lore": "The dreaming-stone is the Sleeper's physical memory, made solid. Each vein is a story — a battle, a love, a loss — that the Sleeper has chosen to share with the kingdom.",
    },
    {
        "tier": 3,
        "title": "The Remembered's Procession",
        "narrative": (
            "At midnight, every Dream-Husk and Memory-Wisp in existence converges on Ashfall's "
            "central square. Hundreds of them — figures of light, memory, and might-have-been — "
            "form a circle and bow. Not to the kingdom's rulers, but to its people. "
            "'You are the remembering kingdom,' they say in unison. 'We have waited for you "
            "since the Cataclysm. You are the reason we did not fade.'"
        ),
        "effects": {"gold": 20, "food": 6},
        "lore": "The Remembered are not relics of the past — they are seeds of the future. Every civilization the Sleepers touched left something behind, and Ashfall has inherited all of it.",
        "quest": {
            "faction_preference": "wildwalkers",
            "name": "Build a Shrine for the Remembered",
            "desc": "The Remembered bowed to Ashfall and called it 'the remembering kingdom.' They have waited since the Cataclysm for a people who would not forget. The Wildwalkers must honor them: build a shrine where Dream-Husks can rest, where Memory-Wisps can roost, where the Remembered know they are welcome — not as visitors, but as neighbors.",
            "target": {"stone": 12, "wood": 8},
            "reward_resources": {"gold": 20, "food": 5},
            "reward_morale": 10,
            "bonus_effect": "lore_recovery",
            "narrative_complete": "The Shrine of the Remembered now stands at the edge of the dreaming deep — a circle of carved stones with a ceiling open to the sky. Dream-Husks gather here at dusk. Memory-Wisps roost in the rafters. The Remembered are no longer visitors. They are neighbors. They are family.",
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # TIER 4 WHISPERS (15+ ash-blooms): The Sleeper is nearly awake.
    # ═══════════════════════════════════════════════════════════════
    {
        "tier": 4,
        "title": "The Cradle Opens",
        "narrative": (
            "The Sleeper's Cradle — the immense hollow in the dreaming stone — begins to glow. "
            "Not with reflected light, but from within. The impression of the Sleeper's body "
            "fills with warm, golden radiance. And then, for one impossible moment, the Sleeper "
            "is *there* — not fully present, but an outline of something vast and kind, "
            "reaching out. It touches the nearest scout's forehead. The scout weeps. "
            "'Soon,' the Sleeper says. 'Soon I will walk with you.'"
        ),
        "effects": {"gold": 25, "food": 12, "stone": 10},
        "lore": "The Sleeper has chosen its side. When the northern fire comes, it will not face Ashfall alone. The kingdom that remembers has earned the remembrance of a god.",
        "quest": {
            "faction_preference": None,  # any faction can take this
            "name": "Prepare for the Awakening",
            "desc": "The Sleeper showed itself — vast, kind, and nearly awake. It said 'Soon I will walk with you.' The kingdom must prepare: build a welcoming-ground near the dreaming deep, gather offerings of every craft, and ready the people for the day when a god walks among them in friendship.",
            "target": {"gold": 25, "stone": 15, "food": 5},
            "reward_resources": {"gold": 40, "stone": 15, "food": 8},
            "reward_morale": 15,
            "bonus_effect": "eternal_legacy",
            "narrative_complete": "The Welcoming-Ground is complete — a perfect circle of dreaming-stone pillars around a hollow in the earth where the Sleeper's first footprint will fall. Offerings from every craft in Ashfall line the perimeter: carved wood, woven cloth, forged iron, baked bread. The kingdom waits. The Sleeper, in its dreams, smiles. Soon.",
        },
    },
    {
        "tier": 4,
        "title": "The First and Last Song",
        "narrative": (
            "The dreaming deep sings a song that has not been heard since before the Cataclysm. "
            "It is the Sleeper's own song — the one it sang when it first chose to stay, "
            "when the Pact was made, when the world was younger. Every creature in Ashfall "
            "stops and listens. Every tree bends toward the sound. The song promises: "
            "'I was here before the fire. I will be here after. And I will not let you burn.' "
            "For one day, no disaster can strike. No raid can succeed. The Sleeper is watching."
        ),
        "effects": {"gold": 30, "food": 15, "stone": 12},
        "lore": "This is the Sleeper's oldest memory — the moment it first loved the world. It has been waiting ten thousand years to share it with someone who would understand.",
    },
]


def generate_event(region, danger, world_obj=None):
    """Pick a random event — region-specific if available, else danger-tier generic.

    Events support two optional fields for weighted selection:
      - 'seasons': list of seasons when the event is more likely
      - 'rarity':  "common" (weight 4), "uncommon" (weight 1), "rare" (weight 0.3)

    Combined weight = season_weight × rarity_weight. Defaults assume common + no season.

    Season weights: exact match=3, adjacent=2, no field=2, distant=1
    Rarity weights:  common=4, uncommon=1, rare=0.3, no field=2 (neutral)"""
    # 40% chance of a region-specific event if one exists for this region
    if region in REGION_EVENTS and random.random() < 0.40:
        events = REGION_EVENTS[region]
        if world_obj is not None:
            season = world_obj.season
            weights = []
            # Adjacency map: adjacent seasons share mild affinity
            season_adjacency = {
                "spring": ["spring", "summer", "winter"],
                "summer": ["summer", "spring", "autumn"],
                "autumn": ["autumn", "summer", "winter"],
                "winter": ["winter", "autumn", "spring"],
            }
            adjacent = season_adjacency.get(season, [season])
            for ev in events:
                # ── Season weight ──
                ev_seasons = ev.get("seasons")
                if ev_seasons is None:
                    s_weight = 2  # neutral — no seasonal preference
                elif season in ev_seasons:
                    s_weight = 3  # exact match — strongly preferred
                elif any(s in ev_seasons for s in adjacent):
                    s_weight = 2  # adjacent season — mild preference
                else:
                    s_weight = 1  # distant season — less likely but still possible

                # ── Rarity weight ──
                rarity = ev.get("rarity", "common")
                r_weight = {"common": 4, "uncommon": 1, "rare": 0.3}.get(rarity, 2)

                weights.append(s_weight * r_weight)
            return random.choices(events, weights=weights, k=1)[0].copy()
        return random.choice(events).copy()
    pool = EVENTS.get(danger, EVENTS["low"])
    return random.choice(pool).copy()


def apply_event(event, world_obj=None, region=None):
    """Modify kingdom resources based on event. May also set unlock flags.
    If region is 'the_ashen_copse' and Ash-Bloom milestone 15 (Sleeper's Gift) is active,
    all negative resource effects become positive — the Sleeper's beacon protects the copse."""
    # Sleeper Beacon (milestone 15): all copse events become positive
    sleeper_beacon = (
        region == "the_ashen_copse"
        and world_obj is not None
        and 15 in world_obj._ash_bloom_milestones
    )
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
        # Under the Sleeper's Beacon, negative effects become positive
        if sleeper_beacon and val < 0:
            if key == "pop":
                continue  # population losses are negated entirely
            else:
                val = abs(val)
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
