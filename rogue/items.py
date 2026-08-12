import random

WEAPONS = [
    dict(key="dagger", name="Dagger", dmg_dice="1d4", value=2),
    dict(key="short_sword", name="Short Sword", dmg_dice="1d6", value=10),
    dict(key="mace", name="Mace", dmg_dice="2d4", value=8),
    dict(key="long_sword", name="Long Sword", dmg_dice="1d8", value=15),
    dict(key="spear", name="Spear", dmg_dice="1d8", value=5),
    dict(key="two_handed_sword", name="Two-Handed Sword", dmg_dice="3d6", value=30),
]

ARMORS = [
    dict(key="leather", name="Leather Armor", base_ac=8, value=5),
    dict(key="studded_leather", name="Studded Leather Armor", base_ac=7, value=15),
    dict(key="ring_mail", name="Ring Mail", base_ac=7, value=20),
    dict(key="scale_mail", name="Scale Mail", base_ac=6, value=30),
    dict(key="chain_mail", name="Chain Mail", base_ac=5, value=60),
    dict(key="banded_mail", name="Banded Mail", base_ac=4, value=90),
    dict(key="splint_mail", name="Splint Mail", base_ac=4, value=100),
    dict(key="plate_mail", name="Plate Mail", base_ac=3, value=150),
]

POTION_KEYS = [
    "healing", "extra_healing", "poison", "strength", "restore_strength",
    "confusion", "blindness", "paralysis", "detect_monsters",
]
POTION_NAMES = {
    "healing": "Potion of Healing",
    "extra_healing": "Potion of Extra Healing",
    "poison": "Potion of Poison",
    "strength": "Potion of Strength",
    "restore_strength": "Potion of Restore Strength",
    "confusion": "Potion of Confusion",
    "blindness": "Potion of Blindness",
    "paralysis": "Potion of Paralysis",
    "detect_monsters": "Potion of Detect Monsters",
}
POTION_COLORS = [
    "red", "blue", "green", "clear", "fizzy", "murky", "smoky",
    "pink", "purple", "orange", "yellow", "milky", "violet",
]

SCROLL_KEYS = [
    "identify", "enchant_weapon", "enchant_armor", "teleportation",
    "magic_mapping", "aggravate_monsters", "sleep", "scare_monster",
]
SCROLL_NAMES = {
    "identify": "Scroll of Identify",
    "enchant_weapon": "Scroll of Enchant Weapon",
    "enchant_armor": "Scroll of Enchant Armor",
    "teleportation": "Scroll of Teleportation",
    "magic_mapping": "Scroll of Magic Mapping",
    "aggravate_monsters": "Scroll of Aggravate Monsters",
    "sleep": "Scroll of Sleep",
    "scare_monster": "Scroll of Scare Monster",
}
_SYLLABLES = ["xyzzy", "zelgo", "mer", "flum", "quor", "gna", "vex", "thra", "poc", "lum", "ith", "dun"]

FOODS = [
    dict(key="ration", name="Ration of Food", nutrition_dice="1d600+1500"),
    dict(key="mango", name="Mango Fruit", nutrition_dice="1d300+500"),
]


def make_appearance_maps():
    colors = POTION_COLORS[:]
    random.shuffle(colors)
    potion_map = {key: colors[i] for i, key in enumerate(POTION_KEYS)}

    scroll_map = {}
    used_titles = set()
    for key in SCROLL_KEYS:
        while True:
            title = " ".join(random.choice(_SYLLABLES) for _ in range(random.randint(2, 3))).upper()
            if title not in used_titles:
                used_titles.add(title)
                scroll_map[key] = title
                break
    return potion_map, scroll_map


class Item:
    def __init__(self, kind, key, letter=None):
        self.kind = kind
        self.key = key
        self.letter = letter
        self.plus = 0
        self.identified = kind not in ("potion", "scroll")
        self.quantity = 1

        if kind == "weapon":
            data = next(w for w in WEAPONS if w["key"] == key)
            self.base_name = data["name"]
            self.dmg_dice = data["dmg_dice"]
            self.value = data["value"]
        elif kind == "armor":
            data = next(a for a in ARMORS if a["key"] == key)
            self.base_name = data["name"]
            self.base_ac = data["base_ac"]
            self.value = data["value"]
        elif kind == "potion":
            self.base_name = POTION_NAMES[key]
        elif kind == "scroll":
            self.base_name = SCROLL_NAMES[key]
        elif kind == "food":
            data = next(f for f in FOODS if f["key"] == key)
            self.base_name = data["name"]
            self.nutrition_dice = data["nutrition_dice"]
        elif kind == "gold":
            self.base_name = "Gold Pieces"

    def display_name(self, game):
        if self.kind == "weapon":
            sign = f"+{self.plus}" if self.plus >= 0 else str(self.plus)
            return f"{sign} {self.base_name}" if self.identified else self.base_name
        if self.kind == "armor":
            sign = f"+{self.plus}" if self.plus >= 0 else str(self.plus)
            return f"{sign} {self.base_name}" if self.identified else self.base_name
        if self.kind == "potion":
            if self.identified:
                return self.base_name
            return f"{game.potion_appearance[self.key]} potion"
        if self.kind == "scroll":
            if self.identified:
                return self.base_name
            return f'scroll titled "{game.scroll_appearance[self.key]}"'
        if self.kind == "food":
            return self.base_name
        if self.kind == "gold":
            return f"{self.quantity} gold pieces"
        return self.base_name

    def symbol(self):
        return {
            "weapon": ")",
            "armor": "[",
            "potion": "!",
            "scroll": "?",
            "food": "%",
            "gold": "*",
        }[self.kind]


def random_item(depth):
    roll = random.random()
    if roll < 0.28:
        key = random.choice(WEAPONS)["key"]
        item = Item("weapon", key)
        if random.random() < 0.2:
            item.plus = random.choice([-1, 1, 1, 2])
            item.identified = False
        return item
    if roll < 0.46:
        key = random.choice(ARMORS)["key"]
        item = Item("armor", key)
        if random.random() < 0.2:
            item.plus = random.choice([-1, 1, 1, 2])
            item.identified = False
        return item
    if roll < 0.68:
        return Item("potion", random.choice(POTION_KEYS))
    if roll < 0.86:
        return Item("scroll", random.choice(SCROLL_KEYS))
    if roll < 0.94:
        return Item("food", random.choice(FOODS)["key"])
    item = Item("gold", "gold")
    from .combat import roll_dice
    item.quantity = roll_dice("2d10") * depth
    return item
