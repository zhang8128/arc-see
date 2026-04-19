"""Pure-Python simulator for SU15 mechanics. Replicates the engine's click
behavior so search can run 100x faster than going through the engine."""

# Sprite size by kind index (from engine source)
SPRITE_SIZE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 7, 6: 8, 7: 9, 8: 10}
MAX_KIND = 8
RADIUS = 8
RADIUS_SQ = RADIUS * RADIUS
FRAME_W = 64
FRAME_H = 64
PLAY_Y_MIN = 10  # gnexwlqinp
PLAY_Y_MAX = 63  # ncfmodluov (exclusive upper for click; inclusive for clamp)


def bbox_dist_sq(fruit, cx, cy):
    """Euclidean dist squared from (cx,cy) to nearest point of fruit's bbox."""
    k, x, y = fruit
    w = h = SPRITE_SIZE[k]
    # Closest pt on bbox [x..x+w-1, y..y+h-1] to (cx, cy)
    px = x if cx < x else (x + w - 1 if cx > x + w - 1 else cx)
    py = y if cy < y else (y + h - 1 if cy > y + h - 1 else cy)
    dx = cx - px
    dy = cy - py
    return dx * dx + dy * dy


def clamp_position(k, cx, cy):
    """Given a fruit kind k and a desired center (cx, cy), return the clamped
    top-left (x, y) such that the sprite stays in playable bounds."""
    w = h = SPRITE_SIZE[k]
    x = cx - w // 2
    y = cy - h // 2
    if x < 0:
        x = 0
    if x > FRAME_W - w:
        x = FRAME_W - w
    if y < PLAY_Y_MIN:
        y = PLAY_Y_MIN
    if y > PLAY_Y_MAX:
        y = PLAY_Y_MAX
    if y > FRAME_H - h:
        y = FRAME_H - h
    return x, y


def bbox_overlap(a, b):
    ka, xa, ya = a
    kb, xb, yb = b
    wa = SPRITE_SIZE[ka]
    wb = SPRITE_SIZE[kb]
    if xa + wa <= xb:
        return False
    if xb + wb <= xa:
        return False
    if ya + wa <= yb:
        return False
    if yb + wb <= ya:
        return False
    return True


def click(fruits, cx, cy):
    """Apply a click to a tuple of fruits. Returns (new_fruits, info).
    info: 'invalid' | 'no_op' | 'move' | 'merge' | 'mixed_lost'
    fruits: tuple of (kind, x, y)
    """
    # Validate click position (engine: y must satisfy gnexwlqinp - 1 < y < ncfmodluov)
    if cx < 0 or cx >= FRAME_W:
        return fruits, 'invalid'
    if cy <= PLAY_Y_MIN - 1 or cy >= PLAY_Y_MAX:
        return fruits, 'invalid'

    # Find in-range fruits
    in_range = []
    rest = []
    for f in fruits:
        if bbox_dist_sq(f, cx, cy) <= RADIUS_SQ:
            in_range.append(f)
        else:
            rest.append(f)

    if not in_range:
        return fruits, 'no_op'

    # Move all in-range fruits to (cx, cy), with frame clamping
    moved = []
    for k, _, _ in in_range:
        nx, ny = clamp_position(k, cx, cy)
        moved.append((k, nx, ny))

    new_fruits = list(rest)

    # If only 1 in-range, just move (no merge processing)
    if len(in_range) == 1:
        new_fruits.extend(moved)
        return tuple(new_fruits), 'move'

    # Build merge groups via bbox overlap (union-find)
    n = len(moved)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        pi, pj = find(i), find(j)
        if pi != pj:
            parent[pj] = pi

    for i in range(n):
        for j in range(i + 1, n):
            if bbox_overlap(moved[i], moved[j]):
                union(i, j)

    groups = {}
    for i, f in enumerate(moved):
        r = find(i)
        groups.setdefault(r, []).append(f)

    info = 'move'
    for group in groups.values():
        if len(group) < 2:
            new_fruits.extend(group)
            continue
        kinds = set(f[0] for f in group)
        if len(kinds) > 1:
            # Mixed kinds: flash → all removed
            info = 'mixed_lost'
            continue
        kind = next(iter(kinds))
        if kind >= MAX_KIND:
            # Max kind merged → all removed (delivery via 8+8)
            info = 'merge'
            continue
        # Promote: new sprite of kind+1 at avg center
        avg_cx = sum(f[1] + SPRITE_SIZE[f[0]] // 2 for f in group) // len(group)
        avg_cy = sum(f[2] + SPRITE_SIZE[f[0]] // 2 for f in group) // len(group)
        new_kind = kind + 1
        nx, ny = clamp_position(new_kind, avg_cx, avg_cy)
        new_fruits.append((new_kind, nx, ny))
        info = 'merge'

    return tuple(new_fruits), info


def is_won(fruits, goal_rect_or_list, goal_spec):
    """Check if goal_spec is satisfied: counts of fruit kinds in any goal area match exactly.
    goal_rect_or_list can be a single (gx,gy,gw,gh) or a list of them."""
    if goal_rect_or_list and isinstance(goal_rect_or_list[0], (int,)):
        goals = [goal_rect_or_list]
    else:
        goals = goal_rect_or_list
    counts = {}
    for k, x, y in fruits:
        w = SPRITE_SIZE[k]
        cx = x + w // 2
        cy = y + w // 2
        for gx, gy, gw, gh in goals:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                counts[k] = counts.get(k, 0) + 1
                break
    for rk, rc in goal_spec:
        if counts.get(rk, 0) != rc:
            return False
    return True


def state_key(fruits):
    return tuple(sorted(fruits))


def initial_state_from_engine(level_idx):
    """Extract initial fruits and goal from the engine for a given level."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('su15_engine', 'environment_files/su15/4c352900/su15.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    g = mod.Su15()
    g.set_level(level_idx)

    fruits = []
    for s in g.current_level.get_sprites_by_tag('fruit'):
        try:
            kind = int(s.name)
        except ValueError:
            kind = -1
        fruits.append((kind, s.x, s.y))

    goals = g.current_level.get_sprites_by_tag('goal')
    goal_rect = (goals[0].x, goals[0].y, goals[0].width, goals[0].height) if goals else None

    raw_spec = g.reqbygadvzmjired
    if raw_spec is None or not raw_spec:
        gspec = []
    elif isinstance(raw_spec[0], (list, tuple)):
        gspec = []
        for k, c in raw_spec:
            try:
                gspec.append((int(k), int(c)))
            except ValueError:
                pass
    else:
        try:
            gspec = [(int(raw_spec[0]), int(raw_spec[1]))]
        except ValueError:
            gspec = []

    return tuple(fruits), goal_rect, gspec
