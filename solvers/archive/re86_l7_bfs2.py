"""Compact-state BFS for L7 single-sprite paths.

State key:
  - Cross sprite: (name, x, y, h_pat_row, v_pat_col, dominant_color)
  - Frame sprite: (name, x, y, width, height, dominant_color)

Much smaller state space → full BFS enumeration possible.
"""
import importlib.util, sys, copy, time
from collections import deque
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sol_spec = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(sol_spec)
sol_spec.loader.exec_module(sol)


def new_game_at_l7():
    g = mod.Re86()
    g.set_level(0)
    for lvl in range(1, 7):
        for a in sol.SOLUTIONS[lvl]:
            g.perform_action(ActionInput(id=getattr(GameAction, a)))
    return g


def players(g):
    lvl = g._levels[g._current_level_index]
    return [s for s in lvl._sprites if 'vfaeucgcyr' in s._tags]


def active_sprite(g):
    for s in players(g):
        if 0 in s.pixels:
            return s


def active_color(s):
    from collections import Counter
    cs = [int(c) for c in s.pixels.flatten() if c != -1 and c != 0]
    if not cs: return -1
    return Counter(cs).most_common(1)[0][0]


def arm_pats(s):
    """Cross: find horiz-arm pattern row and vert-arm pattern col."""
    px = s.pixels
    row_counts = [sum(1 for c in row if c != -1) for row in px]
    h_row = row_counts.index(max(row_counts))
    col_counts = [sum(1 for row in px if row[c] != -1) for c in range(s.width)]
    v_col = col_counts.index(max(col_counts))
    return h_row, v_col


def state_key(s, is_frame):
    col = active_color(s)
    if is_frame:
        return (s._x, s._y, s.width, s.height, col)
    h, v = arm_pats(s)
    return (s._x, s._y, h, v, col)


TARGETS = [
    (9, 9, 8), (3, 15, 8), (36, 15, 8), (9, 27, 8),
    (57, 18, 9), (39, 24, 9),
    (45, 30, 11), (39, 48, 11), (51, 48, 11),
]


def covered(s, targets):
    col = active_color(s)
    cov = set()
    px = s.pixels
    for tx, ty, tc in targets:
        if tc != col: continue
        dx, dy = tx - s._x, ty - s._y
        if 0 <= dx < s.width and 0 <= dy < s.height:
            if int(px[dy, dx]) not in (-1,):
                cov.add((tx, ty, tc))
    return cov


def search_sprite(g_start, switches, is_frame, time_limit=180, depth_cap=40):
    start = copy.deepcopy(g_start)
    for _ in range(switches):
        start.perform_action(ActionInput(id=GameAction.ACTION5))

    s0 = active_sprite(start)
    k0 = state_key(s0, is_frame)
    print(f'  start {s0._name} key={k0}')

    seen = {k0: 0}
    q = deque([(start, [])])
    best_cov = {}  # frozenset(targets) -> (depth, seq)
    t0 = time.time()
    expansions = 0
    max_reached = 0

    while q:
        if time.time() - t0 > time_limit:
            print(f'  TIMEOUT')
            break
        g, seq = q.popleft()
        depth = len(seq)
        max_reached = max(max_reached, depth)

        s = active_sprite(g)
        cov = covered(s, TARGETS)
        if cov:
            key = frozenset(cov)
            if key not in best_cov or best_cov[key][0] > depth:
                best_cov[key] = (depth, list(seq))

        if depth >= depth_cap:
            continue

        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            s2 = active_sprite(g2)
            k = state_key(s2, is_frame)
            if k in seen and seen[k] <= depth + 1:
                continue
            seen[k] = depth + 1
            q.append((g2, seq + [a]))
            expansions += 1

    print(f'  exp={expansions} depth_max={max_reached} states={len(seen)} cov_sets={len(best_cov)} {time.time()-t0:.1f}s')
    return best_cov


def main():
    g = new_game_at_l7()

    for name, sw, is_f, depth, t in [
        ('A 19x19 cross', 0, False, 35, 240),
        ('B 13x13 frame', 1, True, 35, 240),
        ('C 37x19 wide', 2, False, 35, 240),
    ]:
        print(f'\n=== {name} ===')
        best = search_sprite(g, sw, is_f, time_limit=t, depth_cap=depth)
        items = sorted(best.items(), key=lambda kv: (-len(kv[0]), kv[1][0]))
        for key, (d, seq) in items[:8]:
            cs = sorted(key)
            print(f'  d={d} cov={len(cs)} {cs}')


if __name__ == '__main__':
    main()
