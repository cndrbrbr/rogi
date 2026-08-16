import random
from . import config as cfg

WALL_H = "-"
WALL_V = "|"
FLOOR = "."
CORRIDOR = "#"
DOOR = "+"
STAIRS_DOWN = ">"
STAIRS_UP = "<"
VOID = " "
TRAP = "^"

WALKABLE = {FLOOR, CORRIDOR, DOOR, STAIRS_DOWN, STAIRS_UP}

TRAP_KEYS = ["dart", "bear", "gas_sleep", "gas_confusion", "teleport", "trapdoor"]
TRAP_NAMES = {
    "dart": "dart trap",
    "bear": "bear trap",
    "gas_sleep": "sleeping gas trap",
    "gas_confusion": "confusion gas trap",
    "teleport": "teleport trap",
    "trapdoor": "trap door",
}


class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def contains(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def interior_points(self):
        pts = []
        for yy in range(self.y + 1, self.y + self.h - 1):
            for xx in range(self.x + 1, self.x + self.w - 1):
                pts.append((xx, yy))
        return pts

    def random_interior(self):
        return random.choice(self.interior_points())


class Level:
    def __init__(self, depth):
        self.depth = depth
        self.grid = [[VOID for _ in range(cfg.MAP_W)] for _ in range(cfg.MAP_H)]
        self.rooms = []
        self.doors = set()
        self.monsters = []
        self.items = {}  # (x,y) -> list[Item]
        self.traps = {}  # (x,y) -> trap key, hidden until sprung or found by searching
        self.known_traps = set()  # (x,y) traps the player has seen
        self.stairs_down = None
        self.stairs_up = None
        self.discovered = set()

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__.setdefault("traps", {})
        self.__dict__.setdefault("known_traps", set())

    def tile(self, x, y):
        if 0 <= x < cfg.MAP_W and 0 <= y < cfg.MAP_H:
            return self.grid[y][x]
        return VOID

    def set_tile(self, x, y, ch):
        self.grid[y][x] = ch

    def is_walkable(self, x, y):
        return self.tile(x, y) in WALKABLE

    def room_at(self, x, y):
        for r in self.rooms:
            if r.contains(x, y):
                return r
        return None

    def visible_from(self, x, y):
        room = self.room_at(x, y)
        if room is not None:
            vis = set()
            for yy in range(room.y, room.y + room.h):
                for xx in range(room.x, room.x + room.w):
                    vis.add((xx, yy))
            return vis
        vis = {(x, y)}
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if self.tile(nx, ny) != VOID:
                vis.add((nx, ny))
        return vis

    def update_discovered(self, x, y):
        newly = self.visible_from(x, y)
        self.discovered |= newly
        return newly

    def random_open_tile(self, avoid=None):
        avoid = avoid or set()
        while True:
            room = random.choice(self.rooms)
            pt = room.random_interior()
            if pt not in avoid:
                return pt


def _cell_bounds(cx, cy):
    cw = cfg.MAP_W // cfg.GRID_COLS
    ch = cfg.MAP_H // cfg.GRID_ROWS
    x0 = cx * cw
    y0 = cy * ch
    w = cw if cx < cfg.GRID_COLS - 1 else cfg.MAP_W - x0
    h = ch if cy < cfg.GRID_ROWS - 1 else cfg.MAP_H - y0
    return x0, y0, w, h


def _make_room(cx, cy):
    x0, y0, cw, ch = _cell_bounds(cx, cy)
    min_w, min_h = 4, 4
    max_w = max(min_w, cw - 2)
    max_h = max(min_h, ch - 2)
    w = random.randint(min_w, max_w)
    h = random.randint(min_h, max_h)
    x = x0 + random.randint(1, max(1, cw - w - 1))
    y = y0 + random.randint(1, max(1, ch - h - 1))
    return Room(x, y, w, h)


def _draw_room(level, room):
    x, y, w, h = room.x, room.y, room.w, room.h
    for xx in range(x, x + w):
        level.set_tile(xx, y, WALL_H)
        level.set_tile(xx, y + h - 1, WALL_H)
    for yy in range(y, y + h):
        level.set_tile(x, yy, WALL_V)
        level.set_tile(x + w - 1, yy, WALL_V)
    for yy in range(y + 1, y + h - 1):
        for xx in range(x + 1, x + w - 1):
            level.set_tile(xx, yy, FLOOR)


def _carve_path(level, x1, y1, x2, y2):
    x, y = x1, y1
    while x != x2:
        if level.tile(x, y) == VOID:
            level.set_tile(x, y, CORRIDOR)
        x += 1 if x2 > x else -1
    while y != y2:
        if level.tile(x, y) == VOID:
            level.set_tile(x, y, CORRIDOR)
        y += 1 if y2 > y else -1
    if level.tile(x2, y2) == VOID:
        level.set_tile(x2, y2, CORRIDOR)


def _connect(level, rooms, cellA, cellB):
    roomA = rooms[cellA]
    roomB = rooms[cellB]
    ax, ay, aw, ah = roomA.x, roomA.y, roomA.w, roomA.h
    bx, by, bw, bh = roomB.x, roomB.y, roomB.w, roomB.h

    if cellA[1] == cellB[1]:  # same row -> horizontal neighbors
        left, right = (roomA, roomB) if ax < bx else (roomB, roomA)
        doorA = (left.x + left.w - 1, random.randint(left.y + 1, left.y + left.h - 2))
        doorB = (right.x, random.randint(right.y + 1, right.y + right.h - 2))
        midx = (doorA[0] + doorB[0]) // 2
        _carve_path(level, doorA[0] + 1, doorA[1], midx, doorA[1])
        _carve_path(level, midx, doorA[1], midx, doorB[1])
        _carve_path(level, midx, doorB[1], doorB[0] - 1, doorB[1])
    else:  # vertical neighbors
        top, bottom = (roomA, roomB) if ay < by else (roomB, roomA)
        doorA = (random.randint(top.x + 1, top.x + top.w - 2), top.y + top.h - 1)
        doorB = (random.randint(bottom.x + 1, bottom.x + bottom.w - 2), bottom.y)
        midy = (doorA[1] + doorB[1]) // 2
        _carve_path(level, doorA[0], doorA[1] + 1, doorA[0], midy)
        _carve_path(level, doorA[0], midy, doorB[0], midy)
        _carve_path(level, doorB[0], midy, doorB[0], doorB[1] - 1)

    level.set_tile(*doorA, DOOR)
    level.set_tile(*doorB, DOOR)
    level.doors.add(doorA)
    level.doors.add(doorB)


def _grid_edges():
    edges = []
    for cy in range(cfg.GRID_ROWS):
        for cx in range(cfg.GRID_COLS):
            if cx + 1 < cfg.GRID_COLS:
                edges.append(((cx, cy), (cx + 1, cy)))
            if cy + 1 < cfg.GRID_ROWS:
                edges.append(((cx, cy), (cx, cy + 1)))
    return edges


def _spanning_tree_edges():
    cells = [(cx, cy) for cy in range(cfg.GRID_ROWS) for cx in range(cfg.GRID_COLS)]
    random.shuffle(cells)
    connected = {cells[0]}
    remaining = set(cells[1:])
    all_edges = _grid_edges()
    tree = []
    while remaining:
        random.shuffle(all_edges)
        progressed = False
        for a, b in all_edges:
            if a in connected and b not in connected:
                tree.append((a, b))
                connected.add(b)
                remaining.discard(b)
                progressed = True
                break
            if b in connected and a not in connected:
                tree.append((a, b))
                connected.add(a)
                remaining.discard(a)
                progressed = True
                break
        if not progressed:
            break
    return tree


def generate_level(depth):
    level = Level(depth)
    rooms = {}
    for cy in range(cfg.GRID_ROWS):
        for cx in range(cfg.GRID_COLS):
            room = _make_room(cx, cy)
            rooms[(cx, cy)] = room
            level.rooms.append(room)
            _draw_room(level, room)

    edges = _spanning_tree_edges()
    for a, b in _grid_edges():
        if (a, b) in edges or (b, a) in edges:
            continue
        if random.random() < 0.25:
            edges.append((a, b))

    for a, b in edges:
        _connect(level, rooms, a, b)

    up_room = random.choice(level.rooms)
    down_room = random.choice([r for r in level.rooms if r is not up_room])
    level.stairs_up = up_room.random_interior()
    level.stairs_down = down_room.random_interior()
    level.set_tile(level.stairs_up[0], level.stairs_up[1], STAIRS_UP)
    level.set_tile(level.stairs_down[0], level.stairs_down[1], STAIRS_DOWN)

    return level
