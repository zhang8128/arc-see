"""SU15 engine-based beam solver — uses the real engine (slower per click but
correct for L4+ which has enemies). Uses kind-aware heuristic from sim solver."""
import importlib.util, copy, time
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
BASELINES = [18, 28, 50, 151, 18, 31, 50, 179, 41]
RADIUS = 8


def fresh(level_idx, prefix_solutions=None):
    """Build engine state at start of `level_idx` by playing previous level solutions.
    prefix_solutions: dict mapping str(level_idx) -> click list, must cover [0..level_idx-1]."""
    g = mod.Su15()
    if level_idx == 0 or prefix_solutions is None:
        g.set_level(level_idx)
        return g
    # Natural progression
    for prev in range(level_idx):
        clicks = prefix_solutions.get(str(prev))
        if clicks is None:
            # Fall back to direct set_level
            g.set_level(level_idx)
            return g
        for (cx, cy) in clicks:
            g.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))
    return g


def fruits_kxy(g):
    """List of (kind, x, y, w, h) for each fruit."""
    out = []
    for s in g.current_level.get_sprites_by_tag('fruit'):
        try:
            k = int(s.name)
        except ValueError:
            k = -1
        out.append((k, s.x, s.y, s.width, s.height))
    return out


def enemies_xy(g):
    out = []
    for s in g.current_level.get_sprites_by_tag('enemy'):
        out.append((s.x, s.y, s.width, s.height))
    return out


def goal_areas(g):
    return [(s.x, s.y, s.width, s.height) for s in g.current_level.get_sprites_by_tag('goal')]


def goal_spec(g):
    data = g.reqbygadvzmjired
    if data is None or not data:
        return [], []
    fruit_spec, enemy_spec = [], []
    if isinstance(data[0], (list, tuple)):
        for k, c in data:
            try:
                fruit_spec.append((int(k), int(c)))
            except (ValueError, TypeError):
                enemy_spec.append((str(k), int(c)))
    else:
        try:
            fruit_spec.append((int(data[0]), int(data[1])))
        except ValueError:
            enemy_spec.append((str(data[0]), int(data[1])))
    return fruit_spec, enemy_spec


def state_key(g):
    fr = tuple(sorted((s.name, s.x, s.y) for s in g.current_level.get_sprites_by_tag('fruit')))
    en = tuple(sorted((s.x, s.y) for s in g.current_level.get_sprites_by_tag('enemy')))
    return fr + ('|',) + en


def clamp_click(x, y):
    return max(0, min(63, x)), max(10, min(62, y))


def candidate_clicks(g):
    """Tight set: 4 cardinal max-step + goal cells in range + same-kind merge per fruit."""
    fruits = fruits_kxy(g)
    goals = goal_areas(g)
    pts = set()
    DIRS = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
    for i, (k, x, y, w, h) in enumerate(fruits):
        cx, cy = x + w // 2, y + h // 2
        for dx, dy in DIRS:
            pts.add(clamp_click(cx + dx * (RADIUS - 1), cy + dy * (RADIUS - 1)))
        for gx, gy, gw, gh in goals:
            gcx, gcy = gx + gw // 2, gy + gh // 2
            ddx, ddy = gcx - cx, gcy - cy
            mag = max(abs(ddx), abs(ddy), 1)
            step = min(mag, RADIUS - 1)
            if step > 0:
                pts.add(clamp_click(cx + round(ddx * step / mag), cy + round(ddy * step / mag)))
            # Goal area cells in close range
            if (gcx - cx) ** 2 + (gcy - cy) ** 2 <= (RADIUS + 1) ** 2:
                pts.add(clamp_click(gcx, gcy))
        for j, (ok, ox, oy, ow, oh) in enumerate(fruits):
            if i >= j or ok != k:
                continue
            ocx, ocy = ox + ow // 2, oy + oh // 2
            pts.add(clamp_click((cx + ocx) // 2, (cy + ocy) // 2))
            ddx, ddy = ocx - cx, ocy - cy
            mag = max(abs(ddx), abs(ddy), 1)
            step = min(mag, RADIUS - 1)
            if step > 0:
                pts.add(clamp_click(cx + round(ddx * step / mag), cy + round(ddy * step / mag)))
    return pts


def heuristic(g, goals, fruit_spec):
    fruits = fruits_kxy(g)
    n = len(fruits)
    if n == 0:
        return 10000

    in_goal = {}
    out_pos_by_kind = {}
    for k, x, y, w, h in fruits:
        cx = x + w // 2
        cy = y + h // 2
        in_g = False
        for gx, gy, gw, gh in goals:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                in_g = True
                break
        if in_g:
            in_goal[k] = in_goal.get(k, 0) + 1
        else:
            out_pos_by_kind.setdefault(k, []).append((cx, cy))

    max_kind = max((rk for rk, _ in fruit_spec), default=0)
    needed = [0] * (max_kind + 2)
    for rk, rc in fruit_spec:
        have = in_goal.get(rk, 0)
        needed[rk] += max(0, rc - have)

    score = 0
    have_by_kind = {k: len(positions) for k, positions in out_pos_by_kind.items()}
    for k in range(max_kind, 0, -1):
        req = needed[k]
        available = have_by_kind.get(k, 0)
        used = min(req, available)
        req -= used
        needed[k - 1] += req * 2
        score += req * 40

    if needed[0] > have_by_kind.get(0, 0):
        score += (needed[0] - have_by_kind.get(0, 0)) * 500

    score += n * 15

    for k, positions in out_pos_by_kind.items():
        if k > max_kind:
            score += len(positions) * 10
            continue
        if len(positions) >= 2:
            n_pos = len(positions)
            pairs = []
            for i in range(n_pos):
                for j in range(i + 1, n_pos):
                    d = abs(positions[i][0] - positions[j][0]) + abs(positions[i][1] - positions[j][1])
                    pairs.append((d, i, j))
            pairs.sort()
            used = set()
            for d, i, j in pairs:
                if i in used or j in used:
                    continue
                clicks = max(1, (d - 12) // 14 + 1)
                score += clicks * 6
                used.add(i)
                used.add(j)
            score += (n_pos - len(used)) * 30

    for k, positions in out_pos_by_kind.items():
        if k == max_kind:
            for cx, cy in positions:
                # Distance to nearest goal area
                dist = 1e9
                for gx, gy, gw, gh in goals:
                    dx = max(gx - cx, 0, cx - (gx + gw - 1))
                    dy = max(gy - cy, 0, cy - (gy + gh - 1))
                    d = abs(dx) + abs(dy)
                    if d < dist:
                        dist = d
                score += max(1, (dist - 1) // 7 + 1) * 5

    return int(score)


def try_click(g, x, y, level_idx):
    g2 = copy.deepcopy(g)
    try:
        g2.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))
    except Exception:
        return None, False, True
    won = g2._current_level_index > level_idx or g2._state.name == "WIN"
    dead = g2._state.name == "GAME_OVER"
    return g2, won, dead


def beam_solve_engine(level_idx, beam_width=120, max_depth=300, max_time=1500, verbose=True, prefix_solutions=None):
    g0 = fresh(level_idx, prefix_solutions)
    n0 = len(fruits_kxy(g0))
    goals = goal_areas(g0)
    fspec, espec = goal_spec(g0)
    if verbose:
        print(f"L{level_idx + 1}: {n0} fruits, fspec={fspec}, espec={espec}, baseline={BASELINES[level_idx]}", flush=True)

    h0 = heuristic(g0, goals, fspec)
    beam = [(g0, [], h0)]
    seen = {state_key(g0): 0}
    t0 = time.time()
    last_print = t0

    for depth in range(max_depth):
        now = time.time()
        if now - t0 > max_time:
            print(f"  TIMEOUT at depth {depth} ({now-t0:.0f}s)", flush=True)
            return None
        if now - last_print > 5.0:
            print(f"  d={depth} beam={len(beam)} best_h={beam[0][2] if beam else None} seen={len(seen)} t={now-t0:.0f}s", flush=True)
            last_print = now

        next_beam = []
        for (g, path, _) in beam:
            for (cx, cy) in candidate_clicks(g):
                g2, won, dead = try_click(g, cx, cy, level_idx)
                if dead or g2 is None:
                    continue
                if won:
                    result = path + [(cx, cy)]
                    print(f"  FOUND! depth={depth + 1} clicks={len(result)} (t={time.time()-t0:.1f}s)", flush=True)
                    return result
                key = state_key(g2)
                new_depth = len(path) + 1
                if key in seen and seen[key] <= new_depth:
                    continue
                seen[key] = new_depth
                h = heuristic(g2, goals, fspec)
                next_beam.append((g2, path + [(cx, cy)], h))

        if not next_beam:
            print(f"  STUCK at depth {depth}", flush=True)
            return None

        next_beam.sort(key=lambda t: t[2])
        beam = next_beam[:beam_width]

    print(f"  EXHAUSTED max_depth={max_depth}", flush=True)
    return None


if __name__ == "__main__":
    import sys, json, os
    lvl = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    # Load existing solutions to chain through
    existing = {}
    path = 'solutions/su15_solutions.json'
    if os.path.exists(path):
        with open(path) as f:
            existing = json.load(f)
    # Verify all prior levels exist
    for prev in range(lvl):
        if str(prev) not in existing:
            print(f"ERROR: missing solution for L{prev+1} — solve previous levels first")
            sys.exit(1)
    p = beam_solve_engine(lvl, prefix_solutions=existing)
    if p:
        print(f"L{lvl+1}: {len(p)} clicks vs baseline {BASELINES[lvl]}")
        existing[str(lvl)] = p
        with open(path, 'w') as f:
            json.dump(existing, f, indent=2)
        print(f"Saved L{lvl+1} to {path}")
