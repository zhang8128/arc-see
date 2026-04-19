"""SU15 simulator v2 — adds enemy logic.

Mechanics implemented:
- Click vacuums in-range fruits and kind-1 enemies toward click point (4 ticks)
- Each tick, enemies NOT vacuumed and NOT in cooldown move 1 step (or 2 for kind-3)
  toward closest fruit (sign-based Chebyshev movement)
- After move, check enemy-fruit overlap; on collision, fruit downgrades 1 kind and
  enemy enters cooldown (~2 clicks)
- After 4 ticks, in-range fruits merge (if same kind, upgrade; mixed kind, all removed)
- Win = goal data spec satisfied: counts of fruit kinds AND enemy kinds in goal area
"""
SPRITE_SIZE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 7, 6: 8, 7: 9, 8: 10}
ENEMY_W = 5
ENEMY_H = 4  # all enemies are 5 wide x 4 tall
MAX_KIND = 8
RADIUS = 8
RADIUS_SQ = RADIUS * RADIUS
FRAME_W = 64
FRAME_H = 64
PLAY_Y_MIN = 10
PLAY_Y_MAX = 63
TICKS = 4
VACUUM_STEP = 4  # stqbquzms = 4 px per tick toward click
COOLDOWN_AFTER_HIT = 9  # bjetwxoaq + djoqfdlzu + 1


def bbox_dist_sq(x, y, w, h, cx, cy):
    px = x if cx < x else (x + w - 1 if cx > x + w - 1 else cx)
    py = y if cy < y else (y + h - 1 if cy > y + h - 1 else cy)
    dx = cx - px
    dy = cy - py
    return dx * dx + dy * dy


def clamp_fruit_pos(k, cx, cy):
    w = h = SPRITE_SIZE[k]
    x = cx - w // 2
    y = cy - h // 2
    if x < 0:
        x = 0
    if x > FRAME_W - w:
        x = FRAME_W - w
    if y < PLAY_Y_MIN:
        y = PLAY_Y_MIN
    if y > FRAME_H - h:
        y = FRAME_H - h
    return x, y


def clamp_enemy_pos(x, y):
    if x < 0:
        x = 0
    if x > FRAME_W - ENEMY_W:
        x = FRAME_W - ENEMY_W
    if y < PLAY_Y_MIN:
        y = PLAY_Y_MIN
    if y > FRAME_H - ENEMY_H:
        y = FRAME_H - ENEMY_H
    return x, y


def bbox_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    if x1 + w1 <= x2:
        return False
    if x2 + w2 <= x1:
        return False
    if y1 + h1 <= y2:
        return False
    if y2 + h2 <= y1:
        return False
    return True


# State representation:
# fruits: tuple of (kind, x, y)
# enemies: tuple of (kind_int, x, y, cooldown)  -- kind_int 1, 2, or 3
# returns (new_fruits, new_enemies, info)


def click(state, cx, cy):
    fruits, enemies = state

    # Validate click
    if cx < 0 or cx >= FRAME_W:
        return state, 'invalid'
    if cy <= PLAY_Y_MIN - 1 or cy >= PLAY_Y_MAX:
        return state, 'invalid'

    # Find in-range fruits
    fruits_list = list(fruits)
    enemies_list = list(enemies)

    in_range_fruit_idx = []
    for i, (k, x, y) in enumerate(fruits_list):
        w = SPRITE_SIZE[k]
        if bbox_dist_sq(x, y, w, w, cx, cy) <= RADIUS_SQ:
            in_range_fruit_idx.append(i)

    # Find in-range enemies (kind 1 = chase logic differs, but all are in range)
    in_range_enemy_idx = []
    for i, (ek, ex, ey, cd) in enumerate(enemies_list):
        if bbox_dist_sq(ex, ey, ENEMY_W, ENEMY_H, cx, cy) <= RADIUS_SQ:
            if ek == 1:  # only kind 1 enemies are vacuumable
                in_range_enemy_idx.append(i)

    # Note: even when no vacuum targets are in range, the engine still runs the
    # 4-tick loop — enemies chase, cooldowns decrement, collisions happen. So we
    # mark info='no_op' but keep executing the tick loop with empty in_range lists.
    info = 'click' if (in_range_fruit_idx or in_range_enemy_idx) else 'no_op'
    in_range_fruit_set = set(in_range_fruit_idx)
    in_range_enemy_set = set(in_range_enemy_idx)

    # Precompute chase direction once per click for non-vacuumed non-cooldown enemies.
    # Engine does not re-aim per tick — direction is sign-based delta to nearest fruit
    # at click time, applied for all 4 ticks. This matters when an enemy's x or y
    # matches its target at click time (delta sign becomes 0) but it should keep moving
    # in the originally chosen direction.
    chase_dir = {}
    for ei, (ek, ex, ey, cd) in enumerate(enemies_list):
        if ei in in_range_enemy_set or cd > 0:
            continue
        ecx = ex + ENEMY_W // 2
        ecy = ey + ENEMY_H // 2
        best_d2 = None
        best_target = None
        for fk, fx, fy in fruits_list:
            fw = SPRITE_SIZE[fk]
            fcx = fx + fw // 2
            fcy = fy + fw // 2
            dd = (fcx - ecx) ** 2 + (fcy - ecy) ** 2
            if best_d2 is None or dd < best_d2:
                best_d2 = dd
                best_target = (fcx, fcy)
        if best_target is None:
            continue
        tx, ty = best_target
        speed = 2 if ek == 3 else 1
        sx = 0
        sy = 0
        if tx > ecx:
            sx = speed
        elif tx < ecx:
            sx = -speed
        if ty > ecy:
            sy = speed
        elif ty < ecy:
            sy = -speed
        chase_dir[ei] = (sx, sy)

    # Compute per-tick integer step for vacuumed kind-1 enemies.
    # Engine quantizes: round(unit_vector * VACUUM_SPEED) is the integer (dx, dy)
    # applied each tick. Direction is frozen at click time — no per-tick re-aim.
    # Float accumulation (old approach) drifts visibly when a component is small
    # (e.g., uvx*speed = 0.48 accumulates to +2 over 4 ticks but engine stays at 0).
    VACUUM_SPEED = 3.4  # stqbquzms * 0.85
    enemy_int_step = {}
    for ei in in_range_enemy_idx:
        ek, x, y, cd = enemies_list[ei]
        ecx = x + ENEMY_W // 2
        ecy = y + ENEMY_H // 2
        vdx = cx - ecx
        vdy = cy - ecy
        mag_sq = vdx * vdx + vdy * vdy
        if mag_sq > 0:
            mag = mag_sq ** 0.5
            sx = int(round(vdx / mag * VACUUM_SPEED))
            sy = int(round(vdy / mag * VACUUM_SPEED))
        else:
            sx, sy = 0, 0
        enemy_int_step[ei] = (sx, sy)

    # Run 4 ticks: each tick moves in-range fruits/enemies up to 4 px toward click,
    # then non-vacuumed enemies move 1 step toward their closest fruit, then collisions.
    downed = set()  # fruit indices downed (hit by enemy)
    downed_enemies = set()  # enemy indices removed (via merge)
    for tick in range(TICKS):
        # Move in-range fruits toward click (capped step)
        for i in in_range_fruit_idx:
            k, x, y = fruits_list[i]
            w = SPRITE_SIZE[k]
            scx = x + w // 2
            scy = y + w // 2
            dx = cx - scx
            dy = cy - scy
            sx = max(-VACUUM_STEP, min(VACUUM_STEP, dx))
            sy = max(-VACUUM_STEP, min(VACUUM_STEP, dy))
            new_scx = scx + sx
            new_scy = scy + sy
            nx, ny = clamp_fruit_pos(k, new_scx, new_scy)
            fruits_list[i] = (k, nx, ny)

        # Move in-range kind-1 enemies using integer step per tick
        for i in in_range_enemy_idx:
            if i in downed_enemies:
                continue
            ek, x, y, cd = enemies_list[i]
            sx, sy = enemy_int_step[i]
            nx, ny = clamp_enemy_pos(x + sx, y + sy)
            enemies_list[i] = (ek, nx, ny, cd)

        # Check per-tick enemy-enemy bbox overlap among vacuumed enemies → merge
        active_vacuumed = [i for i in in_range_enemy_idx if i not in downed_enemies]
        n_av = len(active_vacuumed)
        if n_av >= 2:
            parent_e = {i: i for i in active_vacuumed}

            def find_e(i):
                while parent_e[i] != i:
                    parent_e[i] = parent_e[parent_e[i]]
                    i = parent_e[i]
                return i

            for a_i in range(n_av):
                i1 = active_vacuumed[a_i]
                k1, x1, y1, _ = enemies_list[i1]
                for a_j in range(a_i + 1, n_av):
                    i2 = active_vacuumed[a_j]
                    k2, x2, y2, _ = enemies_list[i2]
                    if bbox_overlap(x1, y1, ENEMY_W, ENEMY_H, x2, y2, ENEMY_W, ENEMY_H):
                        r1 = find_e(i1)
                        r2 = find_e(i2)
                        if r1 != r2:
                            parent_e[r2] = r1

            groups_v = {}
            for i in active_vacuumed:
                r = find_e(i)
                groups_v.setdefault(r, []).append(i)

            for grp in groups_v.values():
                if len(grp) < 2:
                    continue
                kinds = set(enemies_list[i][0] for i in grp)
                if len(kinds) > 1:
                    for i in grp:
                        downed_enemies.add(i)
                    continue
                kind = next(iter(kinds))
                if kind >= 3:
                    for i in grp:
                        downed_enemies.add(i)
                    continue
                avg_x = sum(enemies_list[i][1] + ENEMY_W // 2 for i in grp) // len(grp)
                avg_y = sum(enemies_list[i][2] + ENEMY_H // 2 for i in grp) // len(grp)
                new_kind = kind + 1
                nx = avg_x - ENEMY_W // 2
                ny = avg_y - ENEMY_H // 2
                nx, ny = clamp_enemy_pos(nx, ny)
                leader = grp[0]
                enemies_list[leader] = (new_kind, nx, ny, 0)
                for other in grp[1:]:
                    downed_enemies.add(other)

        # Decrement cooldowns
        for i, (ek, ex, ey, cd) in enumerate(enemies_list):
            if cd > 0:
                enemies_list[i] = (ek, ex, ey, cd - 1)

        # Apply frozen chase direction for non-vacuumed, non-cooldown enemies
        for ei in chase_dir:
            ek, ex, ey, cd = enemies_list[ei]
            if cd > 0:
                continue
            sx, sy = chase_dir[ei]
            new_x, new_y = clamp_enemy_pos(ex + sx, ey + sy)
            enemies_list[ei] = (ek, new_x, new_y, cd)

        # Check enemy-fruit collisions for non-vacuumed, non-cooldown enemies
        for ei, (ek, ex, ey, cd) in enumerate(enemies_list):
            if ei in in_range_enemy_set:
                continue
            if cd > 0:
                continue
            for fi, (fk, fx, fy) in enumerate(fruits_list):
                if fi in downed:
                    continue
                fw = SPRITE_SIZE[fk]
                if bbox_overlap(ex, ey, ENEMY_W, ENEMY_H, fx, fy, fw, fw):
                    new_kind = max(0, fk - 1)
                    if new_kind == 0 and fk == 0:
                        downed.add(fi)
                    else:
                        ncx = fx + fw // 2
                        ncy = fy + fw // 2
                        nx, ny = clamp_fruit_pos(new_kind, ncx, ncy)
                        fruits_list[fi] = (new_kind, nx, ny)
                        downed.add(fi)
                    enemies_list[ei] = (ek, ex, ey, COOLDOWN_AFTER_HIT)
                    break

    # Filter out downed enemies (merged during ticks)
    if downed_enemies:
        enemies_list = [e for i, e in enumerate(enemies_list) if i not in downed_enemies]

    # Now run merge logic on the in-range fruits (those at click point)
    if len(in_range_fruit_idx) >= 2:
        # All in-range fruits are at the click point (after vacuum)
        # Build groups via bbox overlap
        moved = [(fruits_list[i][0], fruits_list[i][1], fruits_list[i][2]) for i in in_range_fruit_idx]
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
            ki, xi, yi = moved[i]
            wi = SPRITE_SIZE[ki]
            for j in range(i + 1, n):
                kj, xj, yj = moved[j]
                wj = SPRITE_SIZE[kj]
                if bbox_overlap(xi, yi, wi, wi, xj, yj, wj, wj):
                    union(i, j)

        groups = {}
        for i in range(n):
            r = find(i)
            groups.setdefault(r, []).append(i)

        new_in_range = []  # post-merge fruits replacing in-range list
        kept_indices = set()
        for grp in groups.values():
            if len(grp) < 2:
                kept_indices.add(grp[0])
                new_in_range.append(moved[grp[0]])
                continue
            kinds = set(moved[i][0] for i in grp)
            if len(kinds) > 1:
                # Mixed → all removed
                continue
            kind = next(iter(kinds))
            if kind >= MAX_KIND:
                continue  # max kind merged → removed
            avg_cx = sum(moved[i][1] + SPRITE_SIZE[moved[i][0]] // 2 for i in grp) // len(grp)
            avg_cy = sum(moved[i][2] + SPRITE_SIZE[moved[i][0]] // 2 for i in grp) // len(grp)
            new_kind = kind + 1
            nx, ny = clamp_fruit_pos(new_kind, avg_cx, avg_cy)
            new_in_range.append((new_kind, nx, ny))

        # Replace in_range fruits with merge results
        new_fruits = []
        for i, f in enumerate(fruits_list):
            if i in in_range_fruit_set:
                continue
            new_fruits.append(f)
        new_fruits.extend(new_in_range)
        fruits_list = new_fruits

    return (tuple(fruits_list), tuple(enemies_list)), info


def is_won(state, goal_rects, goal_spec_fruits, goal_spec_enemies):
    """Check spec satisfaction. goal_rects: list of (gx,gy,gw,gh).
    goal_spec_fruits: list of (kind_int, count). goal_spec_enemies: list of (kind_int, count)."""
    fruits, enemies = state
    fruit_counts = {}
    enemy_counts = {}
    for k, x, y in fruits:
        w = SPRITE_SIZE[k]
        cx = x + w // 2
        cy = y + w // 2
        for gx, gy, gw, gh in goal_rects:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                fruit_counts[k] = fruit_counts.get(k, 0) + 1
                break
    for ek, ex, ey, cd in enemies:
        cx = ex + ENEMY_W // 2
        cy = ey + ENEMY_H // 2
        for gx, gy, gw, gh in goal_rects:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                enemy_counts[ek] = enemy_counts.get(ek, 0) + 1
                break
    for rk, rc in goal_spec_fruits:
        if fruit_counts.get(rk, 0) != rc:
            return False
    for rk, rc in goal_spec_enemies:
        if enemy_counts.get(rk, 0) != rc:
            return False
    return True


def state_key(state):
    fruits, enemies = state
    # Use only kind/x/y for enemies (ignore cooldown for state matching)
    return (tuple(sorted(fruits)), tuple(sorted((e[0], e[1], e[2]) for e in enemies)))


def initial_state_from_engine(level_idx, prefix_solutions=None):
    """Get initial state by either set_level (if no prefix) or chained progression."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('su15_engine', 'environment_files/su15/4c352900/su15.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from arcengine import GameAction, ActionInput

    g = mod.Su15()
    if prefix_solutions and level_idx > 0:
        for prev in range(level_idx):
            clicks = prefix_solutions.get(str(prev))
            if clicks is None:
                g.set_level(level_idx)
                break
            for (cx, cy) in clicks:
                g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    else:
        g.set_level(level_idx)

    fruits = []
    for s in g.current_level.get_sprites_by_tag('fruit'):
        try:
            kind = int(s.name)
        except ValueError:
            kind = -1
        fruits.append((kind, s.x, s.y))

    enemies = []
    all_tags = g.current_level.get_all_tags()
    for tag, ek in (('enemy', 1), ('enemy2', 2), ('enemy3', 3)):
        if tag not in all_tags:
            continue
        for s in g.current_level.get_sprites_by_tag(tag):
            enemies.append((ek, s.x, s.y, 0))

    goal_rects = [(s.x, s.y, s.width, s.height) for s in g.current_level.get_sprites_by_tag('goal')]

    raw = g.reqbygadvzmjired
    fspec, espec = [], []
    if raw:
        if isinstance(raw[0], (list, tuple)):
            for k, c in raw:
                try:
                    fspec.append((int(k), int(c)))
                except (ValueError, TypeError):
                    # Enemy kind name → enemy_kind_int
                    if k == 'vnjbdkorwc':
                        espec.append((1, int(c)))
                    elif k == 'yckgseirmu':
                        espec.append((2, int(c)))
                    elif k == 'vptxjilzzk':
                        espec.append((3, int(c)))
        else:
            try:
                fspec.append((int(raw[0]), int(raw[1])))
            except (ValueError, TypeError):
                pass

    state = (tuple(fruits), tuple(enemies))
    return state, goal_rects, fspec, espec
