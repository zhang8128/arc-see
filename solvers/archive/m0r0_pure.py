"""M0R0 pure-Python solver — no deepcopy, state as tuples.
Models: walls, mirrored piece movement, cvcer selection/movement,
dfnuk/hnutp barriers, wyiex death zones, piece merging."""
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

# ── Level data parsed from m0r0.py ──────────────────────────────

# Wall pixel arrays from jggua sprites (0=wall, -1=walkable)
WALL_PIXELS = {
    "Level1": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, -1, 0, 0, 0, 0, -1, -1, -1, -1, -1, 0],
        [0, -1, -1, -1, 0, -1, -1, -1, 0, 0, 0, -1, 0],
        [0, -1, 0, -1, 0, -1, 0, 0, 0, -1, 0, -1, 0],
        [0, -1, 0, -1, 0, -1, 0, -1, -1, -1, -1, -1, 0],
        [0, -1, 0, -1, -1, -1, 0, -1, 0, 0, 0, 0, 0],
        [0, -1, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, 0],
        [-1, -1, -1, -1, -1, -1, 0, 0, 0, 0, -1, -1, 0],
        [0, 0, 0, 0, 0, -1, 0, -1, -1, 0, -1, 0, 0],
        [0, 0, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, 0],
        [0, 0, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, 0],
        [0, 0, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "Level2": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
        [0, 0, 0, -1, -1, -1, 0, 0, 0, 0, -1, -1, -1, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, 0],
        [-1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1],
        [0, 0, -1, -1, -1, 0, 0, 0, 0, 0, -1, -1, -1, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "Level6": [
        [0, 0, -1, -1, -1, 0, -1, -1, -1, -1, 0],
        [0, -1, -1, -1, -1, 0, -1, -1, -1, -1, 0],
        [0, -1, -1, -1, -1, 0, -1, -1, -1, -1, 0],
        [0, -1, -1, 0, 0, 0, 0, -1, -1, -1, 0],
        [0, -1, 0, 0, 0, 0, 0, 0, -1, 0, 0],
        [0, -1, 0, 0, 0, 0, 0, 0, -1, 0, 0],
        [0, -1, -1, 0, 0, 0, 0, 0, -1, -1, 0],
        [0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 0],
        [0, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0],
        [0, 0, -1, -1, -1, -1, -1, -1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "Level9": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 0],
        [0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 0],
        [0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 0],
        [0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0],
        [0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0],
        [0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0],
        [0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 0],
        [0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 0],
        [0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "Level10": [
        [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, 0, 0],
        [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0],
        [0, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, 0, 0],
        [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0],
        [0, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, 0, 0],
        [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0],
        [0, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0],
    ],
}


def rotate180(pixels):
    return [row[::-1] for row in reversed(pixels)]


def make_walls(pixels, offset_x=0, offset_y=0):
    """Return set of (x,y) wall positions from pixel array."""
    walls = set()
    for y, row in enumerate(pixels):
        for x, val in enumerate(row):
            if val >= 0:  # 0 or positive = wall
                walls.add((x + offset_x, y + offset_y))
    return walls


# Level definitions: (grid_w, grid_h, wall_key, wall_offset, wall_rotation,
#                      piece_A_pos, piece_B_pos, cvcer_positions,
#                      wyiex_positions, hnutp, dfnuk)
# hnutp = {color: [(x,y),...]} — switch positions
# dfnuk = {color: [(x,y,dx,dy),...]} — barrier base positions, 3 cells each
LEVELS = []

# Level 1: grid 11x11, jggua-Level6 rotated 180, 2 pieces, no extras
LEVELS.append({
    "grid": (11, 11),
    "wall_key": "Level6",
    "wall_rotation": 180,
    "wall_offset": (0, 0),
    "piece_A": (3, 9),   # ubwff-idtiq
    "piece_B": (7, 9),   # ubwff-crkfz
    "cvcers": [],
    "wyiex": set(),
    "hnutp": {},
    "dfnuk": {},
})

# Level 2: grid 13x13, jggua-Level11 at (2,0), wyiex positions
_l2_wyiex = {(5,5),(5,6),(12,8),(11,8),(10,8),(9,8),(8,8),(4,8),(2,8),(1,8),(0,8),
             (5,8),(5,7),(4,12),(3,12),(2,12),(1,12),(0,12),(9,12),(8,12),(7,12),
             (6,12),(5,12),(12,12),(11,12),(10,12)}
LEVELS.append({
    "grid": (13, 13),
    "wall_key": None,  # custom wall handling
    "wall_rotation": 0,
    "wall_offset": (0, 0),
    "piece_A": (4, 1),
    "piece_B": (8, 1),
    "cvcers": [],
    "wyiex": _l2_wyiex,
    "hnutp": {},
    "dfnuk": {},
})

# Level 3: grid 13x13, jggua-Level1, 3 cvcers
LEVELS.append({
    "grid": (13, 13),
    "wall_key": "Level1",
    "wall_rotation": 0,
    "wall_offset": (0, 0),
    "piece_A": (4, 10),
    "piece_B": (8, 10),
    "cvcers": [(1, 3), (6, 2), (8, 6)],
    "wyiex": set(),
    "hnutp": {},
    "dfnuk": {},
})

# Level 4: grid 11x11, jggua-Level9, 1 cvcer, wyiex
_l4_wyiex = {(1,1),(2,1),(3,1),(9,1),(8,1),(7,1),(7,9),(9,9),(8,9),
             (3,9),(2,9),(1,9),(4,6),(5,6),(6,6),(4,4),(5,4),(6,4)}
LEVELS.append({
    "grid": (11, 11),
    "wall_key": "Level9",
    "wall_rotation": 0,
    "wall_offset": (0, 0),
    "piece_A": (2, 6),
    "piece_B": (8, 4),
    "cvcers": [(5, 5)],
    "wyiex": _l4_wyiex,
    "hnutp": {},
    "dfnuk": {},
})

# Level 5: grid 15x15, jggua-Level2, dfnuk/hnutp barriers, no cvcers
# dfnuk barriers (after 90° rotation = horizontal 3-cell bars)
# dfnuk at pos (x,y) rotated 90° occupies (x,y), (x+1,y), (x+2,y)
LEVELS.append({
    "grid": (15, 15),
    "wall_key": "Level2",
    "wall_rotation": 0,
    "wall_offset": (0, 0),
    "piece_A": (13, 12),   # ubwff-idtiq
    "piece_B": (1, 12),    # ubwff-crkfz
    "cvcers": [],
    "wyiex": set(),
    "hnutp": {
        "qeazm": [(3, 12), (3, 1)],
        "raixb": [(8, 6)],
        "ujcze": [(14, 6)],
    },
    "dfnuk": {
        "qeazm": [(10, 9), (10, 5)],  # each is 3 cells horizontal
        "raixb": [(3, 5)],
        "ujcze": [(2, 9)],
    },
})

# Level 6: grid 13x13, jggua-Level10, 1 cvcer, dfnuk/hnutp, many wyiex
_l6_wyiex = set()
for x in range(13):
    _l6_wyiex.add((x, 0))
for x in range(13):
    _l6_wyiex.add((x, 12))
for y in range(1, 12):
    _l6_wyiex.add((0, y))
    _l6_wyiex.add((12, y))
for y in range(1, 12):
    _l6_wyiex.add((6, y))
_l6_wyiex.update([(5, 6), (1, 6), (7, 6), (11, 6)])
# Remove the ones that are the border (already all 0,12 and 12,y)
# Actually, let me list them from the source exactly
_l6_wyiex = set()
# Row 0: all 13 cells
for x in range(13):
    _l6_wyiex.add((x, 0))
# Row 12: all 13 cells
for x in range(13):
    _l6_wyiex.add((x, 12))
# Column 0: y=1-11
for y in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
    _l6_wyiex.add((0, y))
# Column 12: y=1-11
for y in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
    _l6_wyiex.add((12, y))
# Column 6: y=1-11
for y in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
    _l6_wyiex.add((6, y))
# Additional: (5,6), (1,6), (7,6), (11,6)
_l6_wyiex.update([(5, 6), (1, 6), (7, 6), (11, 6)])

LEVELS.append({
    "grid": (13, 13),
    "wall_key": "Level10",
    "wall_rotation": 0,
    "wall_offset": (0, 0),
    "piece_A": (3, 4),
    "piece_B": (9, 4),
    "cvcers": [(6, 9)],
    "wyiex": _l6_wyiex,
    "hnutp": {
        "raixb": [(9, 2), (3, 9)],
        "ujcze": [(3, 2)],
    },
    "dfnuk": {
        "raixb": [(2, 6)],   # 3 cells: (2,6),(3,6),(4,6)
        "ujcze": [(8, 6)],   # 3 cells: (8,6),(9,6),(10,6)
    },
})


def build_wall_set(level_cfg):
    """Build the set of wall positions for a level."""
    if level_cfg["wall_key"] is None:
        # Level 2: jggua-Level11 at position (2,0) within 13x13
        # Level11 pixel array is 10 rows x 9 cols
        pixels = [
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -1, 0, 0, 0, 0, 0, 0, 0],
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
            [-1, -1, -1, -1, 0, -1, -1, -1, -1],
        ]
        return make_walls(pixels, 2, 0)

    pixels = WALL_PIXELS[level_cfg["wall_key"]]
    rot = level_cfg["wall_rotation"]
    if rot == 180:
        pixels = rotate180(pixels)
    ox, oy = level_cfg["wall_offset"]
    return make_walls(pixels, ox, oy)


def get_dfnuk_cells(dfnuk_cfg):
    """Get barrier cells per color. Each dfnuk at (x,y) rotated 90° = 3 horizontal cells."""
    result = {}
    for color, positions in dfnuk_cfg.items():
        cells = set()
        for (bx, by) in positions:
            cells.add((bx, by))
            cells.add((bx + 1, by))
            cells.add((bx + 2, by))
        result[color] = frozenset(cells)
    return result


# ── Game state model ──────────────────────────────

# State = (piece_A_xy, piece_B_xy, cvcer_positions, barriers_open, mode)
# piece_xy = (x,y) or None if cancelled
# cvcer_positions = tuple of (x,y) sorted
# barriers_open = frozenset of open barrier colors
# mode = -1 (player) or index into cvcer_positions

BASELINES = [30, 209, 83, 86, 436, 126]

U, D, L, R = 0, 1, 2, 3
DX = [0, 0, -1, 1]
DY = [-1, 1, 0, 0]
DIR_NAMES = ["U", "D", "L", "R"]

# Piece A (ubwff-idtiq): moves (dx, dy)
# Piece B (ubwff-crkfz): moves (-dx, dy)
# So for U: A=(0,-1), B=(0,-1) → both up
# For D: A=(0,1), B=(0,1) → both down
# For L: A=(-1,0), B=(1,0) → A left, B right
# For R: A=(1,0), B=(-1,0) → A right, B left


def try_move_piece(px, py, dx, dy, walls, cvcers_set, grid_w, grid_h, dfnuk_blocked):
    """Try to move a piece. Returns new position. Blocked by walls, cvcers, dfnuk barriers."""
    nx, ny = px + dx, py + dy
    if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h:
        return px, py
    if (nx, ny) in walls:
        return px, py
    if (nx, ny) in cvcers_set:
        return px, py
    if (nx, ny) in dfnuk_blocked:
        return px, py
    return nx, ny


def compute_barriers_open(piece_A, piece_B, cancelled, hnutp_cfg):
    """Determine which barrier colors are open based on piece positions on switches."""
    active_positions = set()
    if piece_A and "A" not in cancelled:
        active_positions.add(piece_A)
    if piece_B and "B" not in cancelled:
        active_positions.add(piece_B)

    open_colors = set()
    for color, switch_positions in hnutp_cfg.items():
        for sp in switch_positions:
            if sp in active_positions:
                open_colors.add(color)
                break
    return frozenset(open_colors)


def get_blocked_dfnuk(dfnuk_cells, barriers_open):
    """Get set of blocked dfnuk cells (those NOT open)."""
    blocked = set()
    for color, cells in dfnuk_cells.items():
        if color not in barriers_open:
            blocked.update(cells)
    return blocked


def bfs_level(level_idx, max_states=5_000_000):
    cfg = LEVELS[level_idx]
    grid_w, grid_h = cfg["grid"]
    walls = build_wall_set(cfg)
    wyiex = cfg["wyiex"]
    hnutp = cfg["hnutp"]
    dfnuk_cells = get_dfnuk_cells(cfg["dfnuk"])
    has_cvcers = len(cfg["cvcers"]) > 0
    has_barriers = len(cfg["dfnuk"]) > 0
    baseline = BASELINES[level_idx]
    limit = min(baseline + 10, 150)

    init_A = cfg["piece_A"]
    init_B = cfg["piece_B"]
    init_cvcers = tuple(sorted(cfg["cvcers"]))
    init_cancelled = frozenset()

    # Compute initial barrier state
    init_barriers_open = frozenset()
    if has_barriers:
        init_barriers_open = compute_barriers_open(init_A, init_B, init_cancelled, hnutp)

    # State: (A, B, cvcers, cancelled, barriers_open, mode)
    # mode: -1 = player, 0..n-1 = cvcer index selected
    init_state = (init_A, init_B, init_cvcers, init_cancelled, init_barriers_open, -1)

    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}, grid={grid_w}x{grid_h}, cvcers={len(cfg['cvcers'])}", flush=True)

    queue = deque([(init_state, [])])
    visited = {init_state}
    iters = 0

    while queue:
        state, path = queue.popleft()
        iters += 1
        if iters % 100000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue

        piece_A, piece_B, cvcers, cancelled, barriers_open, mode = state
        cvcers_set = set(cvcers)
        dfnuk_blocked = get_blocked_dfnuk(dfnuk_cells, barriers_open) if has_barriers else set()

        # Generate next states
        actions = []  # (new_state, action_name)

        if mode == -1:  # Player mode
            # UDLR moves
            for d in range(4):
                dx, dy = DX[d], DY[d]

                # Move piece A: (dx, dy)
                if piece_A and "A" not in cancelled:
                    new_ax, new_ay = try_move_piece(
                        piece_A[0], piece_A[1], dx, dy,
                        walls, cvcers_set, grid_w, grid_h, dfnuk_blocked)
                    new_A = (new_ax, new_ay)
                else:
                    new_A = piece_A

                # Move piece B: (-dx, dy) — x-mirrored
                if piece_B and "B" not in cancelled:
                    new_bx, new_by = try_move_piece(
                        piece_B[0], piece_B[1], -dx, dy,
                        walls, cvcers_set, grid_w, grid_h, dfnuk_blocked)
                    new_B = (new_bx, new_by)
                else:
                    new_B = piece_B

                # Check wyiex death zones
                hit_death = False
                if new_A and "A" not in cancelled and new_A in wyiex:
                    hit_death = True
                if new_B and "B" not in cancelled and new_B in wyiex:
                    hit_death = True

                if hit_death:
                    # Reset to initial positions
                    new_A = init_A
                    new_B = init_B
                    new_cancelled = frozenset()
                    new_cvcers = init_cvcers
                    new_barriers = frozenset()
                    if has_barriers:
                        new_barriers = compute_barriers_open(new_A, new_B, new_cancelled, hnutp)
                    new_state = (new_A, new_B, new_cvcers, new_cancelled, new_barriers, -1)
                    actions.append((new_state, DIR_NAMES[d]))
                    continue

                # Check adjacent merge condition
                new_cancelled = set(cancelled)
                if (new_A and "A" not in new_cancelled and
                    new_B and "B" not in new_cancelled):
                    # Check if they were adjacent and swapped
                    old_A = piece_A
                    old_B = piece_B
                    if (old_A and old_B and
                        abs(old_A[0] - old_B[0]) == 1 and old_A[1] == old_B[1]):
                        # Were horizontally adjacent
                        if ((new_A[0] == old_B[0] and new_A[1] == old_B[1]) or
                            (new_B[0] == old_A[0] and new_B[1] == old_A[1])):
                            # Swapped → merge at midpoint
                            mx = (new_A[0] + new_B[0]) // 2
                            my = (new_A[1] + new_B[1]) // 2
                            new_A = (mx, my)
                            new_B = (mx, my)

                    # Check if they overlap → cancel both
                    if new_A == new_B:
                        new_cancelled.add("A")
                        new_cancelled.add("B")

                new_cancelled = frozenset(new_cancelled)

                # Check win
                active_count = 0
                if "A" not in new_cancelled:
                    active_count += 1
                if "B" not in new_cancelled:
                    active_count += 1
                if active_count == 0:
                    result = path + [DIR_NAMES[d]]
                    print(f"  FOUND! {len(result)} moves ({iters} iters): {' '.join(result)}", flush=True)
                    return result

                # Compute new barriers
                new_barriers = barriers_open
                if has_barriers:
                    new_barriers = compute_barriers_open(new_A, new_B, new_cancelled, hnutp)

                new_state = (new_A, new_B, cvcers, new_cancelled, new_barriers, -1)
                actions.append((new_state, DIR_NAMES[d]))

            # Click on cvcers to select
            if has_cvcers:
                for ci in range(len(cvcers)):
                    new_state = (piece_A, piece_B, cvcers, cancelled, barriers_open, ci)
                    actions.append((new_state, f"C{ci}"))

        else:  # Cvcer selected (mode = cvcer index)
            # UDLR moves the selected cvcer
            sel_pos = cvcers[mode]
            for d in range(4):
                dx, dy = DX[d], DY[d]
                nx, ny = sel_pos[0] + dx, sel_pos[1] + dy
                if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h:
                    continue
                if (nx, ny) in walls:
                    continue
                # Check collision with other cvcers
                other_cvcers = set(cvcers) - {sel_pos}
                if (nx, ny) in other_cvcers:
                    continue
                # Check collision with pieces
                piece_positions = set()
                if piece_A and "A" not in cancelled:
                    piece_positions.add(piece_A)
                if piece_B and "B" not in cancelled:
                    piece_positions.add(piece_B)
                # Cvcers can move through piece positions? Let me check...
                # Actually, the code uses try_move_sprite which checks collisions differently
                # For now, assume cvcers are blocked by walls and other nhiae-tagged sprites only

                new_cvcer_list = list(cvcers)
                new_cvcer_list[mode] = (nx, ny)
                new_cvcers = tuple(sorted(new_cvcer_list))
                # Find new mode index (sorted position may change)
                new_mode = new_cvcers.index((nx, ny))

                new_state = (piece_A, piece_B, new_cvcers, cancelled, barriers_open, new_mode)
                actions.append((new_state, DIR_NAMES[d]))

            # Click to deselect
            new_state = (piece_A, piece_B, cvcers, cancelled, barriers_open, -1)
            actions.append((new_state, "X"))

        for new_state, name in actions:
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [name]))

        if len(visited) >= max_states:
            print(f"  State limit reached ({max_states})", flush=True)
            break

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


# ── Verification ──────────────────────────────────

GRID_MAP = {
    (11, 11): (4, 4, 5),
    (13, 13): (6, 6, 4),
    (15, 15): (2, 2, 4),
}

UP_A, DOWN_A, LEFT_A, RIGHT_A = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK_A = GameAction.ACTION6
GAME_DIRS = [UP_A, DOWN_A, LEFT_A, RIGHT_A]


def grid_to_display(gx, gy, grid_size):
    bx, by, cs = GRID_MAP[grid_size]
    return bx + gx * cs, by + gy * cs


def path_to_api_actions(path, level_idx):
    """Convert BFS path to API action sequence."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    g = mod.M0r0()
    g.set_level(level_idx)
    grid_size = g.current_level.grid_size
    cfg = LEVELS[level_idx]

    actions = []
    # We need to track cvcer positions to generate correct click coordinates
    cvcers = list(sorted(cfg["cvcers"]))

    for name in path:
        if name in ("U", "D", "L", "R"):
            idx = DIR_NAMES.index(name)
            actions.append(("dir", GAME_DIRS[idx]))
        elif name.startswith("C"):
            ci = int(name[1:])
            cx, cy = cvcers[ci]
            dx, dy = grid_to_display(cx, cy, grid_size)
            actions.append(("click", dx, dy))
        elif name == "X":
            # Deselect: click on (0,0) which is a wall
            dx, dy = grid_to_display(0, 0, grid_size)
            actions.append(("click", dx, dy))

        # Update cvcer tracking for subsequent clicks
        if name in ("U", "D", "L", "R") and any(a.startswith("C") for a in path[:path.index(name)] if isinstance(a, str)):
            pass  # We'd need to track mode properly here
            # Actually, we track cvcers based on the BFS state transitions

    return actions


if __name__ == "__main__":
    import importlib.util
    spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    all_solutions = {}

    for level in range(6):
        result = bfs_level(level)
        if result:
            all_solutions[level] = result
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum(BASELINES)
    print(f"Solved {len(all_solutions)}/6, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 6:
        print("\nVerifying with game engine...", flush=True)

        for level_idx in range(6):
            g = mod.M0r0()
            g.set_level(level_idx)
            grid_size = g.current_level.grid_size
            cfg = LEVELS[level_idx]
            path = all_solutions[level_idx]

            # Track cvcer positions for click conversion
            cvcers = list(sorted(cfg["cvcers"]))
            mode = -1

            for name in path:
                if name in ("U", "D", "L", "R"):
                    idx = DIR_NAMES.index(name)
                    g.perform_action(ActionInput(id=GAME_DIRS[idx]))
                    if mode >= 0:
                        # Update cvcer position after move
                        current_cvcers = g.current_level.get_sprites_by_name("cvcer")
                        cvcers = sorted([(c.x, c.y) for c in current_cvcers])
                elif name.startswith("C"):
                    ci = int(name[1:])
                    cx, cy = cvcers[ci]
                    dx, dy = grid_to_display(cx, cy, grid_size)
                    g.perform_action(ActionInput(id=CLICK_A, data={"x": dx, "y": dy}))
                    mode = ci
                elif name == "X":
                    dx, dy = grid_to_display(0, 0, grid_size)
                    g.perform_action(ActionInput(id=CLICK_A, data={"x": dx, "y": dy}))
                    mode = -1
                    current_cvcers = g.current_level.get_sprites_by_name("cvcer")
                    cvcers = sorted([(c.x, c.y) for c in current_cvcers])

            print(f"  Level {level_idx+1}: {len(path)} moves, level_idx={g._current_level_index}, state={g._state.name}")

        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("m0r0-dadda488", render_mode=None)
        result = env.reset()

        for level_idx in range(6):
            g_tmp = mod.M0r0()
            g_tmp.set_level(level_idx)
            grid_size = g_tmp.current_level.grid_size
            cfg = LEVELS[level_idx]
            path = all_solutions[level_idx]

            cvcers = list(sorted(cfg["cvcers"]))
            mode = -1

            for name in path:
                if name in ("U", "D", "L", "R"):
                    idx = DIR_NAMES.index(name)
                    result = env.step(GAME_DIRS[idx])
                    if mode >= 0:
                        # After cvcer move, update positions via game engine
                        g_track = mod.M0r0()
                        g_track.set_level(level_idx)
                        # Replay to current point... this is getting complex
                        pass
                elif name.startswith("C"):
                    ci = int(name[1:])
                    cx, cy = cvcers[ci]
                    dx, dy = grid_to_display(cx, cy, grid_size)
                    result = env.step(CLICK_A, data={"x": dx, "y": dy})
                    mode = ci
                elif name == "X":
                    dx, dy = grid_to_display(0, 0, grid_size)
                    result = env.step(CLICK_A, data={"x": dx, "y": dy})
                    mode = -1

            print(f"  Level {level_idx+1}: {len(path)} moves, levels={result.levels_completed}")

        print(f"\nTotal: {total}, State: {result.state}")
