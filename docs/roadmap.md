# rogi — Roadmap

One of three docs on **rogi**, a terminal recreation of MS-DOS *Rogue* in Python and curses. This page: what's missing, ranked by how much it'd change play. See also: [Features](features.md) · [Ruleset](ruleset.md)

Gaps against the classic *Rogue* feature set and the current code. The codebase itself has no open `TODO` markers — these are external observations, not in-repo notes.

- [x] ~~**Traps**~~ — implemented: dart, bear, sleeping gas, confusion gas, teleport, and trap door, hidden until sprung or found with `s` (search). See [Ruleset](ruleset.md#traps).
- [x] ~~**Wands & staffs**~~ — implemented as a single unified item kind: striking, confusion, sleep, teleport away, and polymorph, zapped with `z` in a chosen direction. See [Ruleset](ruleset.md#wands).
- [x] ~~**Rings**~~ — implemented: two worn slots (`P`/`R`), five effects (protection, add strength, regeneration, slow digestion, searching). See [Ruleset](ruleset.md#rings).

1. **Cursed items** — enchantment values can go negative, but nothing stops a cursed weapon, armor, or ring from being removed once worn/put on.
2. **Combat-table fidelity** — the README already flags the to-hit formula as a simplified stand-in for the original's exact tables — worth a call on whether closer fidelity matters for the project's goals.
3. **Monster special abilities** — species like Rattlesnake (poison bite), Vampire (drain), Leprechaun (steal gold and flee), and Nymph (steal item and teleport) exist by name and stats only; confirm whether special-attack behavior is implemented elsewhere, and add it if not.
4. **Difficulty tuning** — no playtesting notes found. The XP curve and depth-weighted spawn selection (`_pick_species_index`) would benefit from a documented tuning pass.
5. **Automated tests** — no `tests/` directory. Dice rolls, hit-chance clamping, and hunger thresholds are strong candidates for unit tests.
6. **Packaging** — `windows-curses` is a manual install step in the README — could move into a `requirements.txt` or `pyproject.toml`.
7. **Screenshot freshness** — `rogi.png` should be checked against the current UI periodically — screenshots drift from code over time.

---

Part of a three-page series on [cndrbrbr/rogi](https://github.com/cndrbrbr/rogi), compiled 2026-08-15. See also: [Features](features.md) · [Ruleset](ruleset.md).
