"""M0R0 solver — decomposition approach.
Phase 1: Enumerate cvcer configurations
Phase 2: For each config, solve pieces-only BFS
Phase 3: Pick cheapest total solution"""
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

BASELINES = [30, 209, 83, 86, 436, 126]

# Wall pixel arrays
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
    "Level11": [
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
    ],
}


def rotate180(pixels):
    return [row[::-1] for row in reversed(pixels)]


def make_walls(pixels, offset_x=0, offset_y=0):
    walls = set()
    for y, row in enumerate(pixels):
        for x, val in enumerate(row):
            if val >= 0:
                walls.add((x + offset_x, y + offset_y))
    return walls


DIR_NAMES = ["U", "D", "L", "R"]
DX = [0, 0, -1, 1]
DY = [-1, 1, 0, 0]


def bfs_cvcer_paths(start, walls, grid_w, grid_h, extra_blocked=frozenset()):
    """BFS from cvcer start position. Returns {pos: path} where path is list of dir indices."""
    blocked = walls | set(extra_blocked)
    q = deque([(start, [])])
    visited = {start: []}
    while q:
        (x, y), path = q.popleft()
        for d in range(4):
            nx, ny = x + DX[d], y + DY[d]
            if 0 <= nx < grid_w and 0 <= ny < grid_h and (nx, ny) not in blocked and (nx, ny) not in visited:
                new_path = path + [d]
                visited[(nx, ny)] = new_path
                q.append(((nx, ny), new_path))
    return visited


def pieces_bfs(piece_A, piece_B, walls, cvcers_set, wyiex, grid_w, grid_h,
               hnutp=None, dfnuk_cells=None, max_depth=150):
    """BFS for piece movement only (no cvcer manipulation).
    Returns (path, length) or None."""
    if hnutp is None:
        hnutp = {}
    if dfnuk_cells is None:
        dfnuk_cells = {}

    init_A = piece_A
    init_B = piece_B

    def compute_barriers(A, B, cancelled):
        if not hnutp:
            return frozenset()
        active = set()
        if A and "A" not in cancelled:
            active.add(A)
        if B and "B" not in cancelled:
            active.add(B)
        open_c = set()
        for color, switches in hnutp.items():
            for s in switches:
                if s in active:
                    open_c.add(color)
                    break
        return frozenset(open_c)

    def get_blocked_dfnuk(barriers_open):
        if not dfnuk_cells:
            return set()
        blocked = set()
        for color, cells in dfnuk_cells.items():
            if color not in barriers_open:
                blocked.update(cells)
        return blocked

    init_barriers = compute_barriers(init_A, init_B, frozenset())
    init_state = (init_A, init_B, frozenset(), init_barriers)
    queue = deque([(init_state, [])])
    visited = {init_state}

    while queue:
        state, path = queue.popleft()
        if len(path) >= max_depth:
            continue

        A, B, cancelled, barriers_open = state
        dfnuk_blocked = get_blocked_dfnuk(barriers_open)
        all_blocked = walls | cvcers_set | dfnuk_blocked

        for d in range(4):
            dx, dy = DX[d], DY[d]

            # Move piece A: (dx, dy)
            if A and "A" not in cancelled:
                nax, nay = A[0] + dx, A[1] + dy
                if nax < 0 or nax >= grid_w or nay < 0 or nay >= grid_h or (nax, nay) in all_blocked:
                    nax, nay = A
                new_A = (nax, nay)
            else:
                new_A = A

            # Move piece B: (-dx, dy)
            if B and "B" not in cancelled:
                nbx, nby = B[0] - dx, B[1] + dy
                if nbx < 0 or nbx >= grid_w or nby < 0 or nby >= grid_h or (nbx, nby) in all_blocked:
                    nbx, nby = B
                new_B = (nbx, nby)
            else:
                new_B = B

            # Check wyiex
            hit_death = False
            if new_A and "A" not in cancelled and new_A in wyiex:
                hit_death = True
            if new_B and "B" not in cancelled and new_B in wyiex:
                hit_death = True

            if hit_death:
                new_A = init_A
                new_B = init_B
                new_cancelled = frozenset()
                new_barriers = compute_barriers(new_A, new_B, new_cancelled)
                new_state = (new_A, new_B, new_cancelled, new_barriers)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [DIR_NAMES[d]]))
                continue

            # Check merge
            new_cancelled = set(cancelled)
            if (new_A and "A" not in new_cancelled and
                new_B and "B" not in new_cancelled):
                old_A, old_B = A, B
                if (old_A and old_B and
                    abs(old_A[0] - old_B[0]) == 1 and old_A[1] == old_B[1]):
                    if ((new_A[0] == old_B[0] and new_A[1] == old_B[1]) or
                        (new_B[0] == old_A[0] and new_B[1] == old_A[1])):
                        mx = (new_A[0] + new_B[0]) // 2
                        my = (new_A[1] + new_B[1]) // 2
                        new_A = (mx, my)
                        new_B = (mx, my)

                if new_A == new_B:
                    new_cancelled.add("A")
                    new_cancelled.add("B")

            new_cancelled = frozenset(new_cancelled)

            # Win check
            active = sum(1 for p in ["A", "B"] if p not in new_cancelled)
            if active == 0:
                return path + [DIR_NAMES[d]]

            new_barriers = compute_barriers(new_A, new_B, new_cancelled)
            new_state = (new_A, new_B, new_cancelled, new_barriers)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [DIR_NAMES[d]]))

    return None


def solve_level_no_cvcers(level_idx):
    """Solve levels without cvcers (L1, L2, L5)."""
    configs = {
        0: {"wall_key": "Level6", "rot": 180, "off": (0,0), "grid": (11,11),
            "A": (3,9), "B": (7,9), "wyiex": set()},
        1: {"wall_key": "Level11", "rot": 0, "off": (2,0), "grid": (13,13),
            "A": (4,1), "B": (8,1),
            "wyiex": {(5,5),(5,6),(12,8),(11,8),(10,8),(9,8),(8,8),(4,8),(2,8),(1,8),(0,8),
                      (5,8),(5,7),(4,12),(3,12),(2,12),(1,12),(0,12),(9,12),(8,12),(7,12),
                      (6,12),(5,12),(12,12),(11,12),(10,12)}},
    }
    if level_idx not in configs:
        return None

    cfg = configs[level_idx]
    pixels = WALL_PIXELS[cfg["wall_key"]]
    if cfg["rot"] == 180:
        pixels = rotate180(pixels)
    walls = make_walls(pixels, *cfg["off"])
    gw, gh = cfg["grid"]

    return pieces_bfs(cfg["A"], cfg["B"], walls, set(), cfg["wyiex"], gw, gh,
                      max_depth=min(BASELINES[level_idx] + 10, 150))


def solve_level3():
    """L3: 3 cvcers. Enumerate cvcer target positions, solve pieces for each."""
    walls = make_walls(WALL_PIXELS["Level1"])
    gw, gh = 13, 13
    init_A, init_B = (4, 10), (8, 10)
    init_cvcers = [(1, 3), (6, 2), (8, 6)]
    limit = min(BASELINES[2] + 10, 150)

    # Get reachable positions for each cvcer (blocked by walls + other cvcers)
    cvcer_reachable = []
    for i, c in enumerate(init_cvcers):
        other = frozenset(init_cvcers[j] for j in range(3) if j != i)
        paths = bfs_cvcer_paths(c, walls, gw, gh, other)
        cvcer_reachable.append(paths)
        print(f"  Cvcer {i} at {c}: {len(paths)} reachable positions")

    # Try all combinations
    best = None
    best_cost = limit + 1
    tried = 0

    positions_0 = sorted(cvcer_reachable[0].keys(), key=lambda p: len(cvcer_reachable[0][p]))
    positions_1 = sorted(cvcer_reachable[1].keys(), key=lambda p: len(cvcer_reachable[1][p]))
    positions_2 = sorted(cvcer_reachable[2].keys(), key=lambda p: len(cvcer_reachable[2][p]))

    for p0 in positions_0:
        cost0 = len(cvcer_reachable[0][p0])
        if cost0 > 0:
            cost0 += 2  # click + deselect
        if cost0 >= best_cost:
            continue
        for p1 in positions_1:
            if p1 == p0:
                continue
            cost1 = len(cvcer_reachable[1][p1])
            if cost1 > 0:
                cost1 += 2
            if cost0 + cost1 >= best_cost:
                continue
            for p2 in positions_2:
                if p2 == p0 or p2 == p1:
                    continue
                cost2 = len(cvcer_reachable[2][p2])
                if cost2 > 0:
                    cost2 += 2
                cvcer_cost = cost0 + cost1 + cost2
                if cvcer_cost >= best_cost:
                    continue

                tried += 1
                cvcers_set = {p0, p1, p2}
                remaining = limit - cvcer_cost

                result = pieces_bfs(init_A, init_B, walls, cvcers_set, set(), gw, gh,
                                    max_depth=remaining)
                if result:
                    total = cvcer_cost + len(result)
                    if total < best_cost:
                        best_cost = total
                        best = (p0, p1, p2, result, cvcer_cost)
                        print(f"  Found: cvcer_cost={cvcer_cost}, pieces={len(result)}, total={total}")

                if tried % 1000 == 0:
                    print(f"  tried={tried}", flush=True)

    if best:
        p0, p1, p2, piece_path, cvcer_cost = best
        # Build full action sequence with position-based click references
        # Track actual cvcer positions during construction
        current_pos = {0: init_cvcers[0], 1: init_cvcers[1], 2: init_cvcers[2]}
        full_path = []
        for i in range(3):
            target = [p0, p1, p2][i]
            cvcer_path = cvcer_reachable[i][target]
            if cvcer_path:
                cx, cy = current_pos[i]
                full_path.append(f"C({cx},{cy})")  # Click by position
                pos = list(current_pos[i])
                for d in cvcer_path:
                    pos[0] += DX[d]
                    pos[1] += DY[d]
                    full_path.append(DIR_NAMES[d])
                current_pos[i] = tuple(pos)
                full_path.append("X")
        full_path.extend(piece_path)
        print(f"  Total: {len(full_path)} moves ({cvcer_cost} cvcer + {len(piece_path)} pieces)")
        return full_path

    return None


def solve_level4():
    """L4: 1 cvcer, wyiex death zones."""
    walls = make_walls(WALL_PIXELS["Level9"])
    gw, gh = 11, 11
    init_A, init_B = (2, 6), (8, 4)
    init_cvcers = [(5, 5)]
    wyiex = {(1,1),(2,1),(3,1),(9,1),(8,1),(7,1),(7,9),(9,9),(8,9),
             (3,9),(2,9),(1,9),(4,6),(5,6),(6,6),(4,4),(5,4),(6,4)}
    limit = min(BASELINES[3] + 10, 150)

    # Cvcer reachability — blocked by wyiex + pieces
    cvcer_blocked = frozenset(wyiex | {init_A, init_B})
    paths = bfs_cvcer_paths((5, 5), walls, gw, gh, cvcer_blocked)
    print(f"  Cvcer at (5,5): {len(paths)} reachable positions")

    best = None
    best_cost = limit + 1

    for pos, cvcer_path in sorted(paths.items(), key=lambda kv: len(kv[1])):
        cvcer_cost = len(cvcer_path)
        if cvcer_cost > 0:
            cvcer_cost += 2
        if cvcer_cost >= best_cost:
            continue

        cvcers_set = {pos}
        remaining = limit - cvcer_cost
        result = pieces_bfs(init_A, init_B, walls, cvcers_set, wyiex, gw, gh,
                            max_depth=remaining)
        if result:
            total = cvcer_cost + len(result)
            if total < best_cost:
                best_cost = total
                full_path = []
                if cvcer_path:
                    full_path.append(f"C({init_cvcers[0][0]},{init_cvcers[0][1]})")
                    for d in cvcer_path:
                        full_path.append(DIR_NAMES[d])
                    full_path.append("X")
                full_path.extend(result)
                best = full_path
                print(f"  Found: cvcer at {pos} (cost={cvcer_cost}), pieces={len(result)}, total={total}")

    return best


def solve_level5():
    """L5: No cvcers but has dfnuk/hnutp barriers."""
    walls = make_walls(WALL_PIXELS["Level2"])
    gw, gh = 15, 15
    init_A, init_B = (13, 12), (1, 12)
    limit = min(BASELINES[4] + 10, 150)

    hnutp = {
        "qeazm": [(3, 12), (3, 1)],
        "raixb": [(8, 6)],
        "ujcze": [(14, 6)],
    }
    dfnuk_cells = {
        "qeazm": frozenset([(10,9),(11,9),(12,9),(10,5),(11,5),(12,5)]),
        "raixb": frozenset([(3,5),(4,5),(5,5)]),
        "ujcze": frozenset([(2,9),(3,9),(4,9)]),
    }

    result = pieces_bfs(init_A, init_B, walls, set(), set(), gw, gh,
                        hnutp=hnutp, dfnuk_cells=dfnuk_cells, max_depth=limit)
    return result


def solve_level6():
    """L6: 1 cvcer, dfnuk/hnutp barriers, many wyiex. NO wall sprites.
    Key insight: (6,9) is the ONLY safe cell in column 6. The cvcer blocks it.
    Move cvcer away → pieces can cross at (6,9)."""
    walls = set()  # L6 has no jggua walls
    gw, gh = 13, 13
    init_A, init_B = (3, 4), (9, 4)
    init_cvcers = [(6, 9)]
    limit = min(BASELINES[5] + 10, 150)

    # Exact wyiex positions from game engine
    wyiex = set()
    for x in range(13):
        wyiex.add((x, 0))
        wyiex.add((x, 12))
    for y in range(1, 12):
        wyiex.add((0, y))
        wyiex.add((12, y))
    # Column 6: all EXCEPT y=9
    for y in [1, 2, 3, 4, 5, 6, 7, 8, 10, 11]:
        wyiex.add((6, y))
    wyiex.update([(5, 6), (1, 6), (7, 6), (11, 6)])

    hnutp = {
        "raixb": [(9, 2), (3, 9)],
        "ujcze": [(3, 2)],
    }
    dfnuk_cells = {
        "raixb": frozenset([(2,6),(3,6),(4,6)]),
        "ujcze": frozenset([(8,6),(9,6),(10,6)]),
    }

    # Cvcer is blocked by wyiex (collidable), dfnuk barriers (closed), and pieces
    all_dfnuk = set()
    for cells in dfnuk_cells.values():
        all_dfnuk.update(cells)
    cvcer_blocked = frozenset(wyiex | all_dfnuk | {init_A, init_B})
    paths = bfs_cvcer_paths((6, 9), walls, gw, gh, cvcer_blocked)
    print(f"  Cvcer at (6,9): {len(paths)} reachable positions")

    best = None
    best_cost = limit + 1

    for pos, cvcer_path in sorted(paths.items(), key=lambda kv: len(kv[1])):
        cvcer_cost = len(cvcer_path)
        if cvcer_cost > 0:
            cvcer_cost += 2
        if cvcer_cost >= best_cost:
            continue

        cvcers_set = {pos}
        remaining = limit - cvcer_cost
        result = pieces_bfs(init_A, init_B, walls, cvcers_set, wyiex, gw, gh,
                            hnutp=hnutp, dfnuk_cells=dfnuk_cells, max_depth=remaining)
        if result:
            total = cvcer_cost + len(result)
            if total < best_cost:
                best_cost = total
                full_path = []
                if cvcer_path:
                    full_path.append("C0")
                    for d in cvcer_path:
                        full_path.append(DIR_NAMES[d])
                    full_path.append("X")
                full_path.extend(result)
                best = full_path
                print(f"  Found: cvcer at {pos} (cost={cvcer_cost}), pieces={len(result)}, total={total}")

    return best


# ── Main ──────────────────────────────────────────

if __name__ == "__main__":
    import importlib.util
    spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    solvers = [
        lambda: solve_level_no_cvcers(0),
        lambda: solve_level_no_cvcers(1),
        solve_level3,
        solve_level4,
        solve_level5,
        solve_level6,
    ]

    all_solutions = {}

    for level in range(6):
        print(f"Level {level+1} (baseline={BASELINES[level]}):", flush=True)
        result = solvers[level]()
        if result:
            all_solutions[level] = result
            print(f"  Solution: {len(result)} moves", flush=True)
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum(BASELINES)
    print(f"Solved {len(all_solutions)}/6, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 6:
        # Verify with game engine
        print("\nVerifying with game engine...", flush=True)
        GRID_MAP = {(11,11): (4,4,5), (13,13): (6,6,4), (15,15): (2,2,4)}
        CLICK_A = GameAction.ACTION6
        GAME_DIRS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]

        def grid_to_display(gx, gy, grid_size):
            bx, by, cs = GRID_MAP[grid_size]
            return bx + gx * cs, by + gy * cs

        level_cvcers = [[], [], [(1,3),(6,2),(8,6)], [(5,5)], [], [(6,9)]]

        for level_idx in range(6):
            g = mod.M0r0()
            g.set_level(level_idx)
            gs = g.current_level.grid_size
            path = all_solutions[level_idx]

            cvcers = list(sorted(level_cvcers[level_idx]))
            mode = -1

            for name in path:
                if name in ("U", "D", "L", "R"):
                    idx = DIR_NAMES.index(name)
                    g.perform_action(ActionInput(id=GAME_DIRS[idx]))
                    if mode >= 0:
                        # Update cvcer positions after move
                        current_cvcers = g.current_level.get_sprites_by_name("cvcer")
                        new_cvcers = sorted([(c.x, c.y) for c in current_cvcers])
                        # Find which one moved
                        old_selected = cvcers[mode]
                        for nc in new_cvcers:
                            if nc not in cvcers:
                                mode = new_cvcers.index(nc)
                                break
                        cvcers = new_cvcers
                elif name.startswith("C"):
                    ci = int(name[1:])
                    cx, cy = cvcers[ci]
                    dx, dy = grid_to_display(cx, cy, gs)
                    g.perform_action(ActionInput(id=CLICK_A, data={"x": dx, "y": dy}))
                    mode = ci
                elif name == "X":
                    dx, dy = grid_to_display(0, 0, gs)
                    g.perform_action(ActionInput(id=CLICK_A, data={"x": dx, "y": dy}))
                    mode = -1
                    current_cvcers = g.current_level.get_sprites_by_name("cvcer")
                    cvcers = sorted([(c.x, c.y) for c in current_cvcers])

            print(f"  Level {level_idx+1}: {len(path)} moves, level_idx={g._current_level_index}, state={g._state.name}")

        # Verify with API
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("m0r0-dadda488", render_mode=None)
        result = env.reset()

        for level_idx in range(6):
            g_tmp = mod.M0r0()
            g_tmp.set_level(level_idx)
            gs = g_tmp.current_level.grid_size
            path = all_solutions[level_idx]
            cvcers = list(sorted(level_cvcers[level_idx]))
            mode = -1

            for name in path:
                if name in ("U", "D", "L", "R"):
                    idx = DIR_NAMES.index(name)
                    result = env.step(GAME_DIRS[idx])
                elif name.startswith("C"):
                    ci = int(name[1:])
                    cx, cy = cvcers[ci]
                    dx, dy = grid_to_display(cx, cy, gs)
                    result = env.step(CLICK_A, data={"x": dx, "y": dy})
                    mode = ci
                elif name == "X":
                    dx, dy = grid_to_display(0, 0, gs)
                    result = env.step(CLICK_A, data={"x": dx, "y": dy})
                    mode = -1

                # Track cvcer positions for click generation
                # After any action in cvcer mode, update position
                if mode >= 0 and name in ("U", "D", "L", "R"):
                    d = DIR_NAMES.index(name)
                    cx, cy = cvcers[mode]
                    nx, ny = cx + DX[d], cy + DY[d]
                    new_cvcers = list(cvcers)
                    new_cvcers[mode] = (nx, ny)
                    cvcers = sorted(new_cvcers)
                    # Recalculate mode index
                    mode = cvcers.index((nx, ny))

            print(f"  Level {level_idx+1}: {len(path)} moves, levels={result.levels_completed}")

        print(f"\nTotal: {total}, State: {result.state}")
