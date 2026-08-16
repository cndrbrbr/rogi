# rogi — Roadmap

One of three docs on **rogi**, a terminal recreation of MS-DOS *Rogue* in Python and curses. This page: what's missing, ranked by how much it'd change play. See also: [Features](features.md) · [Ruleset](ruleset.md)

Gaps against the classic *Rogue* feature set and the current code. The codebase itself has no open `TODO` markers — these are external observations, not in-repo notes.

- [x] ~~**Traps**~~ — implemented: dart, bear, sleeping gas, confusion gas, teleport, and trap door, hidden until sprung or found with `s` (search). See [Ruleset](ruleset.md#traps).

1. **Wands & staffs** — a fourth item category from the original is missing; only weapon/armor/potion/scroll/food/gold exist.
2. **Rings** — no ring equipment slot or ring-of-* effects.
3. **Cursed items** — enchantment values can go negative, but nothing stops a cursed weapon or armor from being removed once worn.
4. **Combat-table fidelity** — the README already flags the to-hit formula as a simplified stand-in for the original's exact tables — worth a call on whether closer fidelity matters for the project's goals.
5. **Monster special abilities** — species like Rattlesnake (poison bite), Vampire (drain), Leprechaun (steal gold and flee), and Nymph (steal item and teleport) exist by name and stats only; confirm whether special-attack behavior is implemented elsewhere, and add it if not.
6. **Difficulty tuning** — no playtesting notes found. The XP curve and depth-weighted spawn selection (`_pick_species_index`) would benefit from a documented tuning pass.
7. **Automated tests** — no `tests/` directory. Dice rolls, hit-chance clamping, and hunger thresholds are strong candidates for unit tests.
8. **Packaging** — `windows-curses` is a manual install step in the README — could move into a `requirements.txt` or `pyproject.toml`.
9. **Screenshot freshness** — `rogi.png` should be checked against the current UI periodically — screenshots drift from code over time.

---

Part of a three-page series on [cndrbrbr/rogi](https://github.com/cndrbrbr/rogi), compiled 2026-08-15. See also: [Features](features.md) · [Ruleset](ruleset.md).
