# rogi — Ruleset

One of three docs on **rogi**, a terminal recreation of MS-DOS *Rogue* in Python and curses. This page: mechanics as actually implemented, including the full A–Z bestiary. See also: [Features](features.md) · [Roadmap](roadmap.md)

## Core stats

| Stat | Value |
|---|---|
| Start HP | 12 |
| Start Strength | 16 |
| Start Hunger | 2000 |
| "Hungry" warning | ≤ 300 |
| "Weak" warning | ≤ 150 |
| Starvation damage interval | every 3 turns |
| Natural regen interval | every 20 turns |
| XP to next level | level² × 15 |
| HP gained per level | 1d8 |
| Max depth | 26 |

## Combat

```
# hit chance, clamped 5–95%
hit% = 45 + atk_bonus × 5 − defender_AC × 4

# damage on a hit, minimum 1
dmg  = max(1, roll(weapon_dice) + (STR − 16) ÷ 3)

# player attack bonus
atk_bonus = character_level + weapon_plus
```

Armor AC is `base_ac − armor_plus` — lower is better, matching the original's inverted AC direction. Bare-handed damage is `1d3`.

## Items

### Drop odds

| Roll | Odds |
|---|---|
| Weapon | 28% |
| Armor | 18% |
| Potion | 22% |
| Scroll | 18% |
| Food | 8% |
| Gold | 6% |

20% of dropped weapons and armor carry a random enchantment (`−1, +1, +1, +2`) and spawn unidentified. Gold quantity is `2d10 × dungeon depth`. Potion colors and scroll titles are shuffled fresh each game.

## Status effects

| Source | Effect | Duration / result |
|---|---|---|
| Potion of Confusion | Confused | 1d10+10 turns |
| Potion of Blindness | Blind | 1d10+10 turns |
| Potion of Paralysis | Paralyzed | 1d6+3 turns |
| Scroll of Sleep | Paralyzed | 1d10+5 turns |
| Scroll of Scare Monster | Sleeps monsters within 3 tiles | — |
| Scroll of Aggravate Monsters | Wakes every monster on the level | — |
| Potion / Scroll of Detect / Mapping | Reveals monster tiles or full layout | — |

## Win & lose

**Win** — carry the Amulet of Yendor from wherever it's found back up to dungeon level 1.

**Lose** — HP reaches 0, from combat or starvation. Permadeath — the save file is deleted immediately.

## Bestiary

All 26 species, A to Z, from `rogue/monsters_data.py`.

| Ltr | Name | HP dice | Atk dice | AC | Atk bonus | XP | Mean | Erratic | Stationary |
|---|---|---|---|---|---|---|---|---|---|
| A | Aquator | 3d8 | 1d2 | 2 | 3 | 20 | | | |
| B | Bat | 1d8 | 1d2 | 8 | 1 | 2 | | ✓ | |
| C | Centaur | 4d8 | 1d6 | 4 | 4 | 25 | | | |
| D | Dragon | 10d8 | 3d10 | −1 | 9 | 5000 | ✓ | | |
| E | Emu | 1d8 | 1d2 | 7 | 1 | 2 | ✓ | | |
| F | Flytrap | 8d8 | 1d2 | 3 | 3 | 80 | ✓ | | ✓ |
| G | Gnome | 1d8 | 1d6 | 5 | 2 | 8 | | | |
| H | Hobgoblin | 1d8 | 1d8 | 5 | 3 | 3 | ✓ | | |
| I | Icky Thing | 1d8 | 1d2 | 9 | 1 | 1 | | ✓ | |
| J | Jackal | 1d8 | 1d2 | 7 | 1 | 2 | ✓ | | |
| K | Kobold | 1d8 | 1d4 | 7 | 2 | 1 | ✓ | | |
| L | Leprechaun | 3d8 | 1d1 | 8 | 2 | 10 | | ✓ | |
| M | Medusa | 8d8 | 3d4 | 2 | 6 | 200 | ✓ | | |
| N | Nymph | 3d8 | 1d1 | 9 | 0 | 37 | | ✓ | |
| O | Orc | 1d8 | 1d8 | 6 | 3 | 5 | ✓ | | |
| P | Phantom | 8d8 | 4d4 | 3 | 5 | 120 | ✓ | ✓ | |
| Q | Quagga | 3d8 | 1d5 | 3 | 4 | 15 | ✓ | | |
| R | Rattlesnake | 2d8 | 1d3 | 3 | 3 | 9 | ✓ | | |
| S | Spider | 2d8 | 1d3 | 4 | 3 | 20 | ✓ | ✓ | |
| T | Troll | 6d8 | 4d6 | 4 | 6 | 120 | ✓ | | |
| U | Ur-Vile | 7d8 | 3d6 | 2 | 6 | 190 | ✓ | ✓ | |
| V | Vampire | 8d8 | 3d6 | 1 | 7 | 350 | ✓ | | |
| W | Wraith | 5d8 | 1d6 | 4 | 5 | 55 | ✓ | | |
| X | Xorn | 7d8 | 3d4 | 0 | 6 | 100 | ✓ | | |
| Y | Yeti | 4d8 | 2d6 | 6 | 4 | 50 | ✓ | | |
| Z | Zombie | 2d8 | 2d3 | 8 | 2 | 6 | ✓ | | |

---

Part of a three-page series on [cndrbrbr/rogi](https://github.com/cndrbrbr/rogi), compiled 2026-08-15. See also: [Features](features.md) · [Roadmap](roadmap.md).
