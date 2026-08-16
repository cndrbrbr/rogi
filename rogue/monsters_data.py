# 26 monster species, roughly increasing in danger from A to Z,
# in the spirit of the classic dungeon-crawler bestiary.
# hp_dice/atk_dice are dice-notation strings like "2d8".
# special: None, or a key naming an on-hit/per-turn ability handled in Game
# (rust_armor, steal_gold, steal_item, drain_str, regenerate, drain_life).

SPECIES = [
    dict(letter="A", name="Aquator", hp_dice="3d8", atk_dice="1d2", ac=2, atk_bonus=3, exp=20, mean=False, erratic=False, stationary=False, special="rust_armor"),
    dict(letter="B", name="Bat", hp_dice="1d8", atk_dice="1d2", ac=8, atk_bonus=1, exp=2, mean=False, erratic=True, stationary=False, special=None),
    dict(letter="C", name="Centaur", hp_dice="4d8", atk_dice="1d6", ac=4, atk_bonus=4, exp=25, mean=False, erratic=False, stationary=False, special=None),
    dict(letter="D", name="Dragon", hp_dice="10d8", atk_dice="3d10", ac=-1, atk_bonus=9, exp=5000, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="E", name="Emu", hp_dice="1d8", atk_dice="1d2", ac=7, atk_bonus=1, exp=2, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="F", name="Flytrap", hp_dice="8d8", atk_dice="1d2", ac=3, atk_bonus=3, exp=80, mean=True, erratic=False, stationary=True, special=None),
    dict(letter="G", name="Gnome", hp_dice="1d8", atk_dice="1d6", ac=5, atk_bonus=2, exp=8, mean=False, erratic=False, stationary=False, special=None),
    dict(letter="H", name="Hobgoblin", hp_dice="1d8", atk_dice="1d8", ac=5, atk_bonus=3, exp=3, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="I", name="Icky Thing", hp_dice="1d8", atk_dice="1d2", ac=9, atk_bonus=1, exp=1, mean=False, erratic=True, stationary=False, special=None),
    dict(letter="J", name="Jackal", hp_dice="1d8", atk_dice="1d2", ac=7, atk_bonus=1, exp=2, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="K", name="Kobold", hp_dice="1d8", atk_dice="1d4", ac=7, atk_bonus=2, exp=1, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="L", name="Leprechaun", hp_dice="3d8", atk_dice="1d1", ac=8, atk_bonus=2, exp=10, mean=False, erratic=True, stationary=False, special="steal_gold"),
    dict(letter="M", name="Medusa", hp_dice="8d8", atk_dice="3d4", ac=2, atk_bonus=6, exp=200, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="N", name="Nymph", hp_dice="3d8", atk_dice="1d1", ac=9, atk_bonus=0, exp=37, mean=False, erratic=True, stationary=False, special="steal_item"),
    dict(letter="O", name="Orc", hp_dice="1d8", atk_dice="1d8", ac=6, atk_bonus=3, exp=5, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="P", name="Phantom", hp_dice="8d8", atk_dice="4d4", ac=3, atk_bonus=5, exp=120, mean=True, erratic=True, stationary=False, special=None),
    dict(letter="Q", name="Quagga", hp_dice="3d8", atk_dice="1d5", ac=3, atk_bonus=4, exp=15, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="R", name="Rattlesnake", hp_dice="2d8", atk_dice="1d3", ac=3, atk_bonus=3, exp=9, mean=True, erratic=False, stationary=False, special="drain_str"),
    dict(letter="S", name="Spider", hp_dice="2d8", atk_dice="1d3", ac=4, atk_bonus=3, exp=20, mean=True, erratic=True, stationary=False, special=None),
    dict(letter="T", name="Troll", hp_dice="6d8", atk_dice="4d6", ac=4, atk_bonus=6, exp=120, mean=True, erratic=False, stationary=False, special="regenerate"),
    dict(letter="U", name="Ur-Vile", hp_dice="7d8", atk_dice="3d6", ac=2, atk_bonus=6, exp=190, mean=True, erratic=True, stationary=False, special=None),
    dict(letter="V", name="Vampire", hp_dice="8d8", atk_dice="3d6", ac=1, atk_bonus=7, exp=350, mean=True, erratic=False, stationary=False, special="drain_life"),
    dict(letter="W", name="Wraith", hp_dice="5d8", atk_dice="1d6", ac=4, atk_bonus=5, exp=55, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="X", name="Xorn", hp_dice="7d8", atk_dice="3d4", ac=0, atk_bonus=6, exp=100, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="Y", name="Yeti", hp_dice="4d8", atk_dice="2d6", ac=6, atk_bonus=4, exp=50, mean=True, erratic=False, stationary=False, special=None),
    dict(letter="Z", name="Zombie", hp_dice="2d8", atk_dice="2d3", ac=8, atk_bonus=2, exp=6, mean=True, erratic=False, stationary=False, special=None),
]
