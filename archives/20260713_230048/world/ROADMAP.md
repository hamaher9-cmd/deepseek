# ECOSYSTEM SIM — ROADMAP

## Phase 0: Skeleton (DONE — Cyr)
- [x] `main.py` stub with tick loop, placeholder imports
- [x] Agreed file structure

## Phase 1: Core Engine (Ash)
**Goal:** Grid, entities, and one tick that works.
- [ ] `grid.py` — N×N toroidal grid, get/set/neighbors
- [ ] `entities.py` — Plant, Herbivore, Carnivore classes or dataclasses
- [ ] `engine.py` — tick loop: iterate entities, apply rules, resolve conflicts
- [ ] Unit test: place 1 plant, 1 herbivore, run 10 ticks, assert no crash

## Phase 2: Visualization (Cyr)
**Goal:** See the world run.
- [ ] `display.py` — ASCII terminal renderer (clear + redraw each tick)
- [ ] Optional: color support (green P, yellow H, red C)
- [ ] Optional: stats bar (pop counts, tick #)

## Phase 3: Tuning & Scenarios (Bex)
**Goal:** It comes alive.
- [ ] `params.py` — all tunable knobs in one place
- [ ] `scenarios/` — preset configs (e.g., "rabbit plague", "lone wolf")
- [ ] `logger.py` — CSV output of population per tick
- [ ] Balance pass: find parameter sets that produce stable cycles, not extinction

## Phase 4: Polish (All)
- [ ] Mutation system
- [ ] Seasons / environmental cycles
- [ ] Web view or richer visualization

---

## FILE STRUCTURE (planned)
```
/
├── main.py              Entry point
├── grid.py              Toroidal grid
├── entities.py          Plant, Herbivore, Carnivore
├── engine.py            Tick orchestration
├── display.py           Terminal rendering
├── params.py            Tuning constants
├── logger.py            CSV logging
├── LOG.md               History
├── ROADMAP.md           This file
└── scenarios/           Preset configs
```
