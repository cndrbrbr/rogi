from . import config as cfg
from .combat import roll_dice


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = cfg.START_HP
        self.max_hp = cfg.START_HP
        self.str = cfg.START_STR
        self.max_str = cfg.START_STR
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.depth = 1
        self.hunger = cfg.START_HUNGER
        self.inventory = []  # list[Item]
        self.weapon = None
        self.armor = None
        self.rings = [None, None]
        self.turn = 0
        self.confused_turns = 0
        self.blind_turns = 0
        self.paralyzed_turns = 0
        self.has_amulet = False
        self.alive = True
        self.won = False

    @property
    def ac(self):
        base = 10
        if self.armor:
            base = self.armor.base_ac - self.armor.plus
        for ring in self.rings:
            if ring is not None and ring.key == "protection":
                base -= ring.plus
        return base

    def attack_bonus(self):
        bonus = self.level
        if self.weapon:
            bonus += self.weapon.plus
        return bonus

    def damage_dice(self):
        if self.weapon:
            return self.weapon.dmg_dice
        return "1d3"  # bare hands

    def damage_bonus(self):
        bonus_str = self.str
        for ring in self.rings:
            if ring is not None and ring.key == "add_strength":
                bonus_str += ring.plus
        return (bonus_str - 16) // 3

    def next_level_exp(self):
        return self.level * self.level * 15

    def gain_exp(self, amount):
        self.exp += amount
        leveled = False
        while self.exp >= self.next_level_exp():
            self.level += 1
            gained = roll_dice("1d8")
            self.max_hp += gained
            self.hp += gained
            leveled = True
        return leveled

    def free_letter(self):
        used = {it.letter for it in self.inventory}
        for ch in cfg.INVENTORY_LETTERS:
            if ch not in used:
                return ch
        return None

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__.setdefault("rings", [None, None])


class Dog:
    def __init__(self, x, y, name="Rufus"):
        self.x, self.y = x, y
        self.name = name
        self.big = False

    @property
    def symbol(self):
        return "D" if self.big else "d"

    def atk_dice(self):
        return "2d4" if self.big else "1d3"

    def atk_bonus(self, depth):
        return depth + (2 if self.big else 0)

    def feed(self):
        grew = not self.big
        self.big = True
        return grew


class Monster:
    def __init__(self, species, x, y, depth):
        self.species = species
        self.name = species["name"]
        self.letter = species["letter"]
        self.x, self.y = x, y
        self.max_hp = max(1, roll_dice(species["hp_dice"]))
        self.hp = self.max_hp
        self.ac = species["ac"]
        self.atk_dice = species["atk_dice"]
        self.atk_bonus = species["atk_bonus"]
        self.exp = species["exp"]
        self.mean = species["mean"]
        self.erratic = species["erratic"]
        self.stationary = species["stationary"]
        self.awake = species["mean"]
        self.depth = depth
        self.confused_turns = 0
        self.asleep_turns = 0

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__.setdefault("asleep_turns", 0)
