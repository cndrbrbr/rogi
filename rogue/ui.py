import curses

from . import config as cfg
from . import dungeon
from .game import Game, DIRS

COLOR_WALL = 1
COLOR_DOOR = 2
COLOR_STAIRS = 3
COLOR_PLAYER = 4
COLOR_MONSTER = 5
COLOR_ITEM = 6
COLOR_DIM = 7
COLOR_DOG = 8
COLOR_TRAP = 9

ARROW_KEYS = {
    curses.KEY_LEFT: "KEY_LEFT",
    curses.KEY_RIGHT: "KEY_RIGHT",
    curses.KEY_UP: "KEY_UP",
    curses.KEY_DOWN: "KEY_DOWN",
}


def init_colors():
    if not curses.has_colors():
        return False
    curses.start_color()
    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:
        bg = curses.COLOR_BLACK
    curses.init_pair(COLOR_WALL, curses.COLOR_WHITE, bg)
    curses.init_pair(COLOR_DOOR, curses.COLOR_YELLOW, bg)
    curses.init_pair(COLOR_STAIRS, curses.COLOR_CYAN, bg)
    curses.init_pair(COLOR_PLAYER, curses.COLOR_WHITE, bg)
    curses.init_pair(COLOR_MONSTER, curses.COLOR_RED, bg)
    curses.init_pair(COLOR_ITEM, curses.COLOR_GREEN, bg)
    curses.init_pair(COLOR_DIM, curses.COLOR_WHITE, bg)
    curses.init_pair(COLOR_DOG, curses.COLOR_MAGENTA, bg)
    curses.init_pair(COLOR_TRAP, curses.COLOR_RED, bg)
    return True


def _addch_safe(stdscr, y, x, ch, attr=0):
    if 0 <= y < cfg.SCREEN_H and 0 <= x < cfg.SCREEN_W:
        try:
            stdscr.addstr(y, x, ch, attr)
        except curses.error:
            pass


def tile_color(ch, has_color):
    if not has_color:
        return curses.A_NORMAL
    if ch in (dungeon.WALL_H, dungeon.WALL_V):
        return curses.color_pair(COLOR_WALL) | curses.A_DIM
    if ch == dungeon.DOOR:
        return curses.color_pair(COLOR_DOOR)
    if ch in (dungeon.STAIRS_DOWN, dungeon.STAIRS_UP):
        return curses.color_pair(COLOR_STAIRS) | curses.A_BOLD
    if ch in (dungeon.FLOOR, dungeon.CORRIDOR):
        return curses.color_pair(COLOR_DIM) | curses.A_DIM
    if ch == dungeon.TRAP:
        return curses.color_pair(COLOR_TRAP) | curses.A_BOLD
    return curses.A_NORMAL


def render(stdscr, game, has_color):
    stdscr.erase()
    p = game.player
    level = game.level
    visible = level.visible_from(p.x, p.y) if p.blind_turns == 0 else {(p.x, p.y)}
    level.discovered |= visible

    for y in range(cfg.MAP_H):
        for x in range(cfg.MAP_W):
            ch = level.tile(x, y)
            if ch == dungeon.VOID:
                continue
            pos = (x, y)
            base_ch = dungeon.TRAP if pos in level.known_traps else ch
            if pos in visible:
                stack = level.items.get(pos)
                if stack:
                    disp = stack[-1].symbol()
                    attr = curses.color_pair(COLOR_ITEM) if has_color else curses.A_NORMAL
                else:
                    disp = base_ch
                    attr = tile_color(base_ch, has_color)
                _addch_safe(stdscr, cfg.MAP_TOP + y, x, disp, attr)
            elif pos in level.discovered:
                stack = level.items.get(pos)
                disp = stack[-1].symbol() if stack else base_ch
                attr = (curses.color_pair(COLOR_DIM) | curses.A_DIM) if has_color else curses.A_DIM
                _addch_safe(stdscr, cfg.MAP_TOP + y, x, disp, attr)

    for m in level.monsters:
        if (m.x, m.y) in visible:
            attr = curses.color_pair(COLOR_MONSTER) if has_color else curses.A_NORMAL
            _addch_safe(stdscr, cfg.MAP_TOP + m.y, m.x, m.letter, attr)

    dog = game.dog
    if dog is not None and (dog.x, dog.y) in visible:
        attr = (curses.color_pair(COLOR_DOG) | curses.A_BOLD) if has_color else curses.A_BOLD
        _addch_safe(stdscr, cfg.MAP_TOP + dog.y, dog.x, dog.symbol, attr)

    p_attr = (curses.color_pair(COLOR_PLAYER) | curses.A_BOLD) if has_color else curses.A_BOLD
    _addch_safe(stdscr, cfg.MAP_TOP + p.y, p.x, "@", p_attr)

    draw_status(stdscr, game)
    stdscr.move(cfg.MAP_TOP + p.y, p.x)


def draw_status(stdscr, game):
    p = game.player
    hunger_state = ""
    if p.hunger <= 0:
        hunger_state = " Starving"
    elif p.hunger <= cfg.WEAK_AT:
        hunger_state = " Weak"
    elif p.hunger <= cfg.HUNGRY_AT:
        hunger_state = " Hungry"
    status = (
        f"Level: {p.depth}  Gold: {p.gold}  Hp: {max(0,p.hp)}({p.max_hp})  "
        f"Str: {p.str}({p.max_str})  Arm: {p.ac}  Exp: {p.level}/{p.exp}{hunger_state}"
    )
    _addch_safe(stdscr, cfg.STATUS_ROW, 0, status.ljust(cfg.SCREEN_W - 1)[: cfg.SCREEN_W - 1])


def show_messages(stdscr, game):
    msgs = game.pop_messages()
    if not msgs:
        _addch_safe(stdscr, cfg.MSG_ROW, 0, " " * (cfg.SCREEN_W - 1))
        return
    for i, m in enumerate(msgs):
        more = i < len(msgs) - 1
        line = m + (" --More--" if more else "")
        _addch_safe(stdscr, cfg.MSG_ROW, 0, line.ljust(cfg.SCREEN_W - 1)[: cfg.SCREEN_W - 1])
        stdscr.refresh()
        if more:
            stdscr.getch()
    _addch_safe(stdscr, cfg.MSG_ROW, 0, " " * (cfg.SCREEN_W - 1))


def prompt(stdscr, text):
    _addch_safe(stdscr, cfg.MSG_ROW, 0, text.ljust(cfg.SCREEN_W - 1)[: cfg.SCREEN_W - 1])
    stdscr.refresh()


def read_key(stdscr):
    key = stdscr.getch()
    if key in ARROW_KEYS:
        return ARROW_KEYS[key]
    try:
        return chr(key)
    except ValueError:
        return ""


def choose_item(stdscr, game, kind, verb):
    p = game.player
    matches = [it for it in p.inventory if kind is None or it.kind == kind]
    if not matches:
        prompt(stdscr, f"You have nothing to {verb}. (press a key)")
        stdscr.refresh()
        stdscr.getch()
        return None
    stdscr.erase()
    _addch_safe(stdscr, 0, 0, f"{verb.capitalize()} what?")
    for i, it in enumerate(matches):
        _addch_safe(stdscr, i + 1, 0, f"{it.letter}) {it.display_name(game)}")
    stdscr.refresh()
    while True:
        key = read_key(stdscr)
        if key == chr(27):
            return None
        for it in matches:
            if key == it.letter:
                return it.letter


def show_inventory(stdscr, game):
    p = game.player
    stdscr.erase()
    if not p.inventory:
        _addch_safe(stdscr, 0, 0, "Your pack is empty. (press a key)")
    else:
        _addch_safe(stdscr, 0, 0, "Inventory:")
        for i, it in enumerate(p.inventory):
            tag = ""
            if it is p.weapon:
                tag = " (wielded)"
            elif it is p.armor:
                tag = " (worn)"
            _addch_safe(stdscr, i + 1, 0, f"{it.letter}) {it.display_name(game)}{tag}")
        _addch_safe(stdscr, len(p.inventory) + 2, 0, "(press a key to continue)")
    stdscr.refresh()
    stdscr.getch()


HELP_TEXT = [
    "Movement: h/j/k/l/y/u/b/n or arrow keys, bump a monster to attack",
    "Items are picked up automatically by walking over them.",
    "i  show inventory      g  pick up (if you declined earlier)",
    "w  wield a weapon      W  wear armor",
    "q  quaff a potion      r  read a scroll",
    "e  eat food            d  drop an item",
    ">  go down stairs      <  go up stairs",
    "s  search / wait       ?  this help screen",
    "Q  quit the game",
    "",
    "Your dog starts small (d). Drop food (d) while standing next to it",
    "to feed it -- it grows into a big dog (D) that fights for you.",
    "",
    "Traps (^) are hidden until sprung or found. Search (s) nearby tiles",
    "to spot one before you step on it.",
    "",
    "Find the Amulet of Yendor on level 26 and carry it back to level 1 to win.",
    "(press a key to continue)",
]


def show_help(stdscr):
    stdscr.erase()
    for i, line in enumerate(HELP_TEXT):
        _addch_safe(stdscr, i, 0, line)
    stdscr.refresh()
    stdscr.getch()


def confirm(stdscr, text):
    prompt(stdscr, text + " (y/n)")
    stdscr.refresh()
    while True:
        key = read_key(stdscr)
        if key in ("y", "Y"):
            return True
        if key in ("n", "N", chr(27)):
            return False


def end_screen(stdscr, game):
    stdscr.erase()
    lines = [game.end_reason, "", f"You reached dungeon level {game.player.depth}.",
             f"Gold collected: {game.player.gold}", f"Experience level: {game.player.level}",
             "", "(press a key to exit)"]
    for i, line in enumerate(lines):
        _addch_safe(stdscr, i, 0, line)
    stdscr.refresh()
    stdscr.getch()


def main_menu(stdscr):
    stdscr.erase()
    lines = ["ROGUE", "", "A dungeon crawl"]
    if Game.has_save():
        lines += ["", "c) Continue saved game", "n) New game", "Q) Quit"]
    else:
        lines += ["", "n) New game", "Q) Quit"]
    for i, line in enumerate(lines):
        _addch_safe(stdscr, i, 0, line)
    stdscr.refresh()
    while True:
        key = read_key(stdscr)
        if key in ("n", "N"):
            return "new"
        if key in ("c", "C") and Game.has_save():
            return "continue"
        if key in ("q", "Q"):
            return "quit"


def run(stdscr):
    curses.curs_set(1)
    has_color = init_colors()
    stdscr.keypad(True)

    choice = main_menu(stdscr)
    if choice == "quit":
        return
    if choice == "continue":
        try:
            game = Game.load()
        except Exception:
            game = Game()
            game.new_game()
    else:
        Game.delete_save()
        game = Game()
        game.new_game()

    while not game.finished:
        render(stdscr, game, has_color)
        show_messages(stdscr, game)
        stdscr.refresh()
        key = read_key(stdscr)

        if key == "?":
            show_help(stdscr)
            continue
        if key == "i":
            show_inventory(stdscr, game)
            continue
        if key == "Q":
            if confirm(stdscr, "Really quit?"):
                game.save()
                return
            continue
        if key == "w":
            letter = choose_item(stdscr, game, "weapon", "wield")
            if letter:
                game.use_item(letter, "wield")
            continue
        if key == "W":
            letter = choose_item(stdscr, game, "armor", "wear")
            if letter:
                game.use_item(letter, "wear")
            continue
        if key == "q":
            letter = choose_item(stdscr, game, "potion", "quaff")
            if letter:
                game.use_item(letter, "quaff")
            continue
        if key == "r":
            letter = choose_item(stdscr, game, "scroll", "read")
            if letter:
                game.use_item(letter, "read")
            continue
        if key == "e":
            letter = choose_item(stdscr, game, "food", "eat")
            if letter:
                game.use_item(letter, "eat")
            continue
        if key == "d":
            letter = choose_item(stdscr, game, None, "drop")
            if letter:
                game.use_item(letter, "drop")
            continue

        game.player_action(key)

    Game.delete_save()
    render(stdscr, game, has_color)
    end_screen(stdscr, game)
