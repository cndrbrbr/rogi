import random
import re

_DICE_RE = re.compile(r"^(\d+)d(\d+)([+-]\d+)?$")


def roll_dice(spec):
    m = _DICE_RE.match(spec.strip())
    if not m:
        return int(spec)
    n, d, bonus = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    return sum(random.randint(1, d) for _ in range(n)) + bonus


def resolve_attack(atk_bonus, dmg_dice, dmg_bonus, defender_ac):
    hit_chance = max(5, min(95, 45 + atk_bonus * 5 - defender_ac * 4))
    roll = random.randint(1, 100)
    hit = roll <= hit_chance
    if not hit:
        return False, 0
    dmg = max(1, roll_dice(dmg_dice) + dmg_bonus)
    return True, dmg
