import random
import os
import pickle

from . import config as cfg
from . import dungeon
from . import items as items_mod
from . import monsters_data
from .entities import Player, Monster, Dog
from .combat import resolve_attack, roll_dice

SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save.dat")

DIRS = {
    "h": (-1, 0), "j": (0, 1), "k": (0, -1), "l": (1, 0),
    "y": (-1, -1), "u": (1, -1), "b": (-1, 1), "n": (1, 1),
    "KEY_LEFT": (-1, 0), "KEY_RIGHT": (1, 0), "KEY_UP": (0, -1), "KEY_DOWN": (0, 1),
}


class GameOver(Exception):
    def __init__(self, won, reason):
        self.won = won
        self.reason = reason


class Game:
    def __init__(self):
        self.player = Player()
        self.levels = {}
        self.messages = []
        self.potion_appearance, self.scroll_appearance = items_mod.make_appearance_maps()
        self.turn_count = 0
        self.finished = False
        self.win = False
        self.end_reason = ""
        self.dog = None

    # ---------- setup ----------

    def new_game(self):
        self.player = Player()
        level = self._get_level(1)
        self.player.x, self.player.y = level.stairs_up
        dog_pos = self._adjacent_open_tile(level, self.player.x, self.player.y)
        self.dog = Dog(dog_pos[0], dog_pos[1])
        self.msg(f"Welcome to the Dungeons of Doom, {self._hero_name()}.")
        self.msg(f"{self.dog.name} the dog trots along beside you.")

    def _adjacent_open_tile(self, level, x, y):
        candidates = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if level.is_walkable(x + dx, y + dy):
                    candidates.append((x + dx, y + dy))
        return random.choice(candidates) if candidates else (x, y)

    def _hero_name(self):
        return "adventurer"

    def _get_level(self, depth):
        if depth not in self.levels:
            level = dungeon.generate_level(depth)
            self._populate(level, depth)
            self.levels[depth] = level
        return self.levels[depth]

    def _populate(self, level, depth):
        n_monsters = random.randint(1, 3) + depth // 3
        for _ in range(n_monsters):
            idx = self._pick_species_index(depth)
            species = monsters_data.SPECIES[idx]
            pos = level.random_open_tile()
            level.monsters.append(Monster(species, pos[0], pos[1], depth))

        n_items = random.randint(2, 5)
        for _ in range(n_items):
            item = items_mod.random_item(depth)
            pos = level.random_open_tile()
            level.items.setdefault(pos, []).append(item)

        n_traps = random.randint(1, 3)
        for _ in range(n_traps):
            pos = level.random_open_tile()
            if pos in level.traps or pos in (level.stairs_up, level.stairs_down):
                continue
            level.traps[pos] = random.choice(dungeon.TRAP_KEYS)

        if depth == cfg.MAX_DEPTH:
            amulet = items_mod.Item("gold", "gold")
            amulet.kind = "amulet"
            amulet.base_name = "Amulet of Yendor"
            amulet.identified = True
            amulet.quantity = 1
            pos = level.random_open_tile()
            level.items.setdefault(pos, []).append(amulet)

    def _pick_species_index(self, depth):
        target = depth - 1
        weights = []
        for i in range(len(monsters_data.SPECIES)):
            if i > depth + 2:
                weights.append(0.0001)
            else:
                weights.append(1.0 / (1 + abs(i - target)))
        return random.choices(range(len(monsters_data.SPECIES)), weights=weights, k=1)[0]

    # ---------- messaging ----------

    def msg(self, text):
        self.messages.append(text)

    def pop_messages(self):
        msgs = self.messages
        self.messages = []
        return msgs

    # ---------- state helpers ----------

    @property
    def level(self):
        return self.levels[self.player.depth]

    def monster_at(self, x, y):
        for m in self.level.monsters:
            if m.x == x and m.y == y:
                return m
        return None

    # ---------- turn processing ----------

    def player_action(self, key):
        """Returns True if the action consumed a turn."""
        p = self.player
        if not p.alive:
            return False

        if p.paralyzed_turns > 0:
            p.paralyzed_turns -= 1
            self.msg("You are paralyzed and cannot move!")
            self._end_turn()
            return True

        if key in DIRS:
            dx, dy = DIRS[key]
            if p.confused_turns > 0 and random.random() < 0.5:
                dx, dy = random.choice(list(DIRS.values()))
            return self._try_move(dx, dy)
        if key == "g" or key == ",":
            return self._pick_up()
        if key == ">":
            return self._use_stairs(down=True)
        if key == "<":
            return self._use_stairs(down=False)
        if key == "s" or key == ".":
            self._search()
            self._end_turn()
            return True
        return False

    def _try_move(self, dx, dy):
        p = self.player
        nx, ny = p.x + dx, p.y + dy
        target = self.monster_at(nx, ny)
        if target:
            self._player_attacks(target)
            self._end_turn()
            return True
        if self.level.is_walkable(nx, ny):
            p.x, p.y = nx, ny
            self.level.update_discovered(nx, ny)
            self._check_trap(nx, ny)
            self._auto_pick_up()
            self._end_turn()
            return True
        self.msg("There is a wall in your way.")
        return False

    def _search(self):
        p = self.player
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                pos = (p.x + dx, p.y + dy)
                if pos in self.level.traps and pos not in self.level.known_traps \
                        and random.random() < 0.33:
                    self.level.known_traps.add(pos)
                    self.msg(f"You find a {dungeon.TRAP_NAMES[self.level.traps[pos]]}.")

    def _check_trap(self, x, y):
        key = self.level.traps.get((x, y))
        if key is None:
            return
        self.level.known_traps.add((x, y))
        del self.level.traps[(x, y)]
        self._trigger_trap(key)

    def _trigger_trap(self, key):
        p = self.player
        if key == "dart":
            dmg = roll_dice("1d4")
            p.hp -= dmg
            self.msg(f"A dart trap fires! You take {dmg} damage.")
        elif key == "bear":
            dmg = roll_dice("1d3")
            p.hp -= dmg
            p.paralyzed_turns += roll_dice("1d4") + 2
            self.msg(f"A bear trap snaps shut on your leg! You take {dmg} damage and can't move.")
        elif key == "gas_sleep":
            p.paralyzed_turns += roll_dice("1d6") + 2
            self.msg("A cloud of gas puts you to sleep!")
        elif key == "gas_confusion":
            p.confused_turns += roll_dice("1d10") + 5
            self.msg("A cloud of gas leaves you confused!")
        elif key == "teleport":
            pos = self.level.random_open_tile()
            p.x, p.y = pos
            self.level.update_discovered(p.x, p.y)
            self.msg("The floor vanishes and you are yanked through space!")
        elif key == "trapdoor":
            if p.depth >= cfg.MAX_DEPTH:
                self.msg("The floor trembles but holds.")
                return
            p.depth += 1
            new_level = self._get_level(p.depth)
            p.x, p.y = new_level.random_open_tile()
            self.level.update_discovered(p.x, p.y)
            self._follow_dog(new_level)
            self.msg(f"The floor gives way beneath you! You fall to level {p.depth}.")

    def _auto_pick_up(self):
        p = self.player
        pos = (p.x, p.y)
        stack = self.level.items.get(pos)
        if not stack:
            return
        remaining = []
        for item in stack:
            if not self._collect_item(item):
                remaining.append(item)
        if remaining:
            self.level.items[pos] = remaining
        else:
            self.level.items.pop(pos, None)

    def _player_attacks(self, m):
        p = self.player
        hit, dmg = resolve_attack(p.attack_bonus(), p.damage_dice(), p.damage_bonus(), m.ac)
        if hit:
            m.hp -= dmg
            m.awake = True
            self.msg(f"You hit the {m.name} for {dmg}.")
            if m.hp <= 0:
                self.msg(f"You have slain the {m.name}.")
                self.level.monsters.remove(m)
                if p.gain_exp(m.exp):
                    self.msg(f"You feel more experienced. Welcome to level {p.level}.")
        else:
            self.msg(f"You miss the {m.name}.")

    def _collect_item(self, item):
        """Try to add item to the player's gold/inventory. Returns True if consumed."""
        p = self.player
        if item.kind == "gold":
            p.gold += item.quantity
            self.msg(f"You found {item.quantity} gold pieces.")
            return True
        if item.kind == "amulet":
            p.has_amulet = True
            item.letter = p.free_letter()
            p.inventory.append(item)
            self.msg("You feel a wave of power. You have the Amulet of Yendor!")
            return True
        letter = p.free_letter()
        if letter is None:
            self.msg("Your pack is full.")
            return False
        item.letter = letter
        p.inventory.append(item)
        self.msg(f"You now have {item.display_name(self)} ({letter}).")
        return True

    def _pick_up(self):
        p = self.player
        pos = (p.x, p.y)
        stack = self.level.items.get(pos)
        if not stack:
            self.msg("There is nothing here to pick up.")
            return False
        item = stack[0]
        if self._collect_item(item):
            stack.pop(0)
            if not stack:
                del self.level.items[pos]
            self._end_turn()
            return True
        return False

    def _use_stairs(self, down):
        p = self.player
        pos = (p.x, p.y)
        if down:
            if pos != self.level.stairs_down:
                self.msg("There are no stairs down here.")
                return False
            if p.depth >= cfg.MAX_DEPTH:
                self.msg("The stairs are blocked by ancient rubble.")
                return False
            p.depth += 1
            new_level = self._get_level(p.depth)
            p.x, p.y = new_level.stairs_up
            self.level.update_discovered(p.x, p.y)
            self._follow_dog(new_level)
            self.msg(f"You descend to level {p.depth}.")
            self._end_turn()
            return True
        else:
            if pos != self.level.stairs_up:
                self.msg("There are no stairs up here.")
                return False
            if p.depth == 1:
                if p.has_amulet:
                    self.finished = True
                    self.win = True
                    self.end_reason = "You escaped the dungeon with the Amulet of Yendor! YOU WIN!"
                else:
                    self.msg("This is the top of the dungeon.")
                return False
            p.depth -= 1
            new_level = self._get_level(p.depth)
            p.x, p.y = new_level.stairs_down
            self.level.update_discovered(p.x, p.y)
            self._follow_dog(new_level)
            self.msg(f"You climb up to level {p.depth}.")
            self._end_turn()
            return True

    def _follow_dog(self, new_level):
        if self.dog is None:
            return
        self.dog.x, self.dog.y = self._adjacent_open_tile(new_level, self.player.x, self.player.y)

    # ---------- item use ----------

    def use_item(self, letter, action):
        p = self.player
        item = next((it for it in p.inventory if it.letter == letter), None)
        if item is None:
            self.msg("You don't have that.")
            return False
        if action == "wield":
            if item.kind != "weapon":
                self.msg("You can't wield that.")
                return False
            p.weapon = item
            item.identified = True
            self.msg(f"You are wielding {item.display_name(self)}.")
        elif action == "wear":
            if item.kind != "armor":
                self.msg("You can't wear that.")
                return False
            p.armor = item
            item.identified = True
            self.msg(f"You are wearing {item.display_name(self)}.")
        elif action == "quaff":
            if item.kind != "potion":
                self.msg("You can't drink that.")
                return False
            self._apply_potion(item)
            p.inventory.remove(item)
        elif action == "read":
            if item.kind != "scroll":
                self.msg("You can't read that.")
                return False
            self._apply_scroll(item)
            p.inventory.remove(item)
        elif action == "eat":
            if item.kind != "food":
                self.msg("You can't eat that.")
                return False
            gained = roll_dice(item.nutrition_dice)
            p.hunger = min(cfg.START_HUNGER, p.hunger + gained)
            self.msg(f"You eat the {item.display_name(self)}. Yum.")
            p.inventory.remove(item)
        elif action == "drop":
            p.inventory.remove(item)
            if item.kind == "food" and self.dog is not None and \
                    max(abs(self.dog.x - p.x), abs(self.dog.y - p.y)) <= 1:
                grew = self.dog.feed()
                if grew:
                    self.msg(f"{self.dog.name} wolfs down the {item.display_name(self)} and grows into a big dog!")
                else:
                    self.msg(f"{self.dog.name} happily wolfs down the {item.display_name(self)}.")
            else:
                self.level.items.setdefault((p.x, p.y), []).append(item)
                self.msg(f"You dropped {item.display_name(self)}.")
        else:
            return False
        self._end_turn()
        return True

    def _apply_potion(self, item):
        p = self.player
        key = item.key
        name = item.display_name(self)
        if key == "healing":
            heal = roll_dice("2d8")
            p.hp = min(p.max_hp, p.hp + heal)
            self.msg(f"You feel better. ({name})")
        elif key == "extra_healing":
            heal = roll_dice("3d8")
            p.hp = min(p.max_hp + 2, p.hp + heal)
            if p.hp > p.max_hp:
                p.max_hp = p.hp
            self.msg(f"You feel much better. ({name})")
        elif key == "poison":
            dmg = roll_dice("1d6")
            p.hp -= dmg
            self.msg(f"You feel very sick. ({name})")
        elif key == "strength":
            p.str += 1
            p.max_str = max(p.max_str, p.str)
            self.msg(f"You feel stronger. ({name})")
        elif key == "restore_strength":
            p.str = p.max_str
            self.msg(f"You feel your strength returning. ({name})")
        elif key == "confusion":
            p.confused_turns += roll_dice("1d10") + 10
            self.msg(f"You feel confused. ({name})")
        elif key == "blindness":
            p.blind_turns += roll_dice("1d10") + 10
            self.msg(f"A cloak of darkness falls over you. ({name})")
        elif key == "paralysis":
            p.paralyzed_turns += roll_dice("1d6") + 3
            self.msg(f"You feel your muscles freeze! ({name})")
        elif key == "detect_monsters":
            for m in self.level.monsters:
                self.level.discovered.add((m.x, m.y))
            self.msg(f"You sense the presence of monsters. ({name})")
        item.identified = True

    def _apply_scroll(self, item):
        p = self.player
        key = item.key
        name = item.display_name(self)
        if key == "identify":
            unidentified = [it for it in p.inventory if not it.identified]
            if unidentified:
                target = unidentified[0]
                target.identified = True
                self.msg(f"This is {name}. You identify {target.display_name(self)}.")
            else:
                self.msg(f"This is {name}. You have nothing left to identify.")
        elif key == "enchant_weapon":
            if p.weapon:
                p.weapon.plus += 1
                p.weapon.identified = True
                self.msg(f"Your {p.weapon.base_name} glows blue. ({name})")
            else:
                self.msg(f"You feel a faint tingle, but you wield nothing. ({name})")
        elif key == "enchant_armor":
            if p.armor:
                p.armor.plus += 1
                p.armor.identified = True
                self.msg(f"Your {p.armor.base_name} glows silver. ({name})")
            else:
                self.msg(f"You feel a faint tingle, but you wear nothing. ({name})")
        elif key == "teleportation":
            pos = self.level.random_open_tile()
            p.x, p.y = pos
            self.level.update_discovered(p.x, p.y)
            self.msg(f"You are yanked through space! ({name})")
        elif key == "magic_mapping":
            for yy in range(cfg.MAP_H):
                for xx in range(cfg.MAP_W):
                    if self.level.tile(xx, yy) != dungeon.VOID:
                        self.level.discovered.add((xx, yy))
            self.msg(f"You feel a sense of the dungeon's layout. ({name})")
        elif key == "aggravate_monsters":
            for m in self.level.monsters:
                m.awake = True
            self.msg(f"You hear a horrible shriek echo through the dungeon. ({name})")
        elif key == "sleep":
            p.paralyzed_turns += roll_dice("1d10") + 5
            self.msg(f"A wave of drowsiness overcomes you. ({name})")
        elif key == "scare_monster":
            for m in self.level.monsters:
                if abs(m.x - p.x) <= 3 and abs(m.y - p.y) <= 3:
                    m.awake = False
            self.msg(f"The dungeon grows quiet around you. ({name})")
        item.identified = True

    # ---------- end of turn ----------

    def _end_turn(self):
        p = self.player
        self.turn_count += 1
        p.turn += 1

        if p.confused_turns > 0:
            p.confused_turns -= 1
        if p.blind_turns > 0:
            p.blind_turns -= 1

        p.hunger -= 1
        if p.hunger == cfg.HUNGRY_AT:
            self.msg("You are starting to feel hungry.")
        elif p.hunger == cfg.WEAK_AT:
            self.msg("You are weak with hunger.")
        elif p.hunger <= 0:
            if p.turn % cfg.STARVE_DAMAGE_EVERY == 0:
                p.hp -= 1
                self.msg("You are starving!")

        if p.turn % cfg.REGEN_TURNS == 0 and p.hp < p.max_hp and p.hunger > 0:
            p.hp += 1

        self._monsters_turn()
        self._dog_turn()

        if p.hp <= 0 and p.alive:
            p.alive = False
            self.finished = True
            self.win = False
            self.end_reason = "You died in the Dungeons of Doom."

    def _monsters_turn(self):
        p = self.player
        for m in list(self.level.monsters):
            if m.hp <= 0:
                continue
            if not m.awake:
                if (m.x, m.y) in self.level.visible_from(p.x, p.y) and abs(m.x - p.x) + abs(m.y - p.y) <= 6:
                    if random.random() < 0.5:
                        m.awake = True
                if not m.awake:
                    continue
            if m.stationary:
                if abs(m.x - p.x) <= 1 and abs(m.y - p.y) <= 1:
                    self._monster_attacks(m)
                continue

            dx = 0 if m.x == p.x else (1 if p.x > m.x else -1)
            dy = 0 if m.y == p.y else (1 if p.y > m.y else -1)
            if m.erratic and random.random() < 0.5:
                dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)])

            nx, ny = m.x + dx, m.y + dy
            if nx == p.x and ny == p.y:
                self._monster_attacks(m)
            elif self.level.is_walkable(nx, ny) and self.monster_at(nx, ny) is None \
                    and not (self.dog and (nx, ny) == (self.dog.x, self.dog.y)):
                m.x, m.y = nx, ny

    def _dog_turn(self):
        dog = self.dog
        if dog is None:
            return
        p = self.player

        adjacent_monster = None
        for m in self.level.monsters:
            if m.hp > 0 and max(abs(m.x - dog.x), abs(m.y - dog.y)) <= 1:
                adjacent_monster = m
                break
        if adjacent_monster is not None:
            hit, dmg = resolve_attack(dog.atk_bonus(p.depth), dog.atk_dice(), 0, adjacent_monster.ac)
            adjacent_monster.awake = True
            if hit:
                adjacent_monster.hp -= dmg
                self.msg(f"{dog.name} bites the {adjacent_monster.name} for {dmg}.")
                if adjacent_monster.hp <= 0:
                    self.msg(f"{dog.name} kills the {adjacent_monster.name}.")
                    self.level.monsters.remove(adjacent_monster)
                    if p.gain_exp(adjacent_monster.exp // 2):
                        self.msg(f"You feel more experienced. Welcome to level {p.level}.")
            else:
                self.msg(f"{dog.name} misses the {adjacent_monster.name}.")
            return

        if max(abs(dog.x - p.x), abs(dog.y - p.y)) <= 1:
            candidates = []
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    nx, ny = dog.x + ddx, dog.y + ddy
                    if max(abs(nx - p.x), abs(ny - p.y)) > 1:
                        continue
                    if (nx, ny) == (p.x, p.y):
                        continue
                    if not self.level.is_walkable(nx, ny):
                        continue
                    if self.monster_at(nx, ny) is not None:
                        continue
                    candidates.append((nx, ny))
            if candidates:
                dog.x, dog.y = random.choice(candidates)
            return

        dx = 0 if dog.x == p.x else (1 if p.x > dog.x else -1)
        dy = 0 if dog.y == p.y else (1 if p.y > dog.y else -1)
        nx, ny = dog.x + dx, dog.y + dy
        if self.level.is_walkable(nx, ny) and self.monster_at(nx, ny) is None and (nx, ny) != (p.x, p.y):
            dog.x, dog.y = nx, ny

    def _monster_attacks(self, m):
        p = self.player
        hit, dmg = resolve_attack(m.atk_bonus, m.atk_dice, 0, p.ac)
        if hit:
            p.hp -= dmg
            self.msg(f"The {m.name} hits you for {dmg}.")
        else:
            self.msg(f"The {m.name} misses you.")

    # ---------- save/load ----------

    def save(self):
        with open(SAVE_PATH, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load():
        with open(SAVE_PATH, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def has_save():
        return os.path.exists(SAVE_PATH)

    @staticmethod
    def delete_save():
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
