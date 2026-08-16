# rogi — Features

One of three docs on **rogi**, a terminal recreation of MS-DOS *Rogue* in Python and curses. This page: everything the game does. See also: [Ruleset](ruleset.md) · [Roadmap](roadmap.md)

The codebase is complete as of this writing — no stub functions, no `TODO` markers found in `rogue/*.py`. Every system below is implemented and playable.

| | |
|---|---|
| **Depths** | 26 |
| **Species A–Z** | 26 |
| **Potions** | 9 |
| **Scrolls** | 8 |
| **Weapons** | 6 |
| **Armors** | 8 |
| **Wands** | 5 |
| **Rings** | 5 |

## Procedural dungeons

A 3×3 grid of cells, each getting a randomly sized/positioned room. Rooms are connected with a randomized spanning tree over the 3×3 grid graph (plus a chance of extra edges for loops), and corridors are carved as L-shaped paths through doors punched through facing room walls. (`rogue/dungeon.py`)

## Room-based visibility

Matches the original's room-based lighting rather than modern raycast FOV — standing in a room lights the whole room; standing in a corridor lights only your immediate surroundings. Seen-but-dark tiles are remembered and drawn dim. (`rogue/dungeon.py: Level.visible_from`)

## Turn-based loop

Every turn-consuming action triggers hunger decay, confusion/blindness countdowns, natural regen, the monster AI pass, and the dog's AI pass, in that fixed order, then checks for player death. (`rogue/game.py: Game._end_turn`)

## Combat

A simplified to-hit/damage model (percent chance to hit, capped 5–95%) rather than the original's exact tables. See [Ruleset](ruleset.md#combat) for the formula. (`rogue/combat.py`)

## Weapons & armor

Six weapons, eight armors, each with dice damage or AC values and an optional (initially hidden) `+`/`−` enchantment.

## Potions & scrolls

Nine potion effects, eight scroll effects. Colors and titles are shuffled onto effects fresh each game (`make_appearance_maps`) — "blue potion" means something different every playthrough until identified by use or a scroll of identify. (`rogue/items.py`)

## Wands

Five effects (striking, confusion, sleep, teleport away, polymorph) covering both "wands" and "staffs" as one unified item kind, each with random charges and a hidden material name until zapped. Press `z`, pick a wand, then a direction — the bolt hits the first monster in a straight line. See [Ruleset](ruleset.md#wands) for the full effect table.

## Rings

Five passive effects, two worn at once (protection, add strength, regeneration, slow digestion, searching), identified by wearing them. Put on with `P`, remove with `R`. See [Ruleset](ruleset.md#rings) for the full effect table.

## Traps

Six trap types (dart, bear, sleeping gas, confusion gas, teleport, trap door), hidden on the map until sprung or found by searching. See [Ruleset](ruleset.md#traps) for the full effect table.

## Hunger clock

Starts at 2000, warns at 300 ("hungry") and 150 ("weak"), then ticks starvation damage every 3 turns once it hits zero.

## Companion dog

Spawns next to you at game start and follows you (including through stairs). While you're standing still it roams freely around the room you're in rather than sitting fixed at your side; the instant you move, it drops the wandering and starts closing the gap. Stand next to it and drop a food item (`d`) to feed it — it grows from a small `d` into a big `D` and will fight monsters that come near it. Unkillable by design (no hp tracked), to keep it a simple companion rather than another thing to manage. (`rogue/entities.py: Dog`, `rogue/game.py: Game._dog_turn`)

## 26-letter bestiary

One species per letter A–Z, danger scaling roughly with letter, with spawn selection (`Game._pick_species_index`) weighting toward species near the current dungeon depth. Full table in the [Ruleset](ruleset.md#bestiary). (`rogue/monsters_data.py`)

## Permadeath, one save slot

`Game.save()`/`Game.load()` pickle the whole game state to `save.dat`. That file is deleted on both death and victory — there is no reloading past either.

---

Part of a three-page series on [cndrbrbr/rogi](https://github.com/cndrbrbr/rogi), compiled 2026-08-15. See also: [Ruleset](ruleset.md) · [Roadmap](roadmap.md).
