"""Deeper BFS for L8 — search specifically for the required end-states."""
import importlib.util, sys, copy, time
from collections import deque, Counter
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sol_spec = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(sol_spec)
sol_spec.loader.exec_module(sol)


def new_game_at_l8():
    g = mod.Re86()
    g.set_level(0)
    for lvl in range(1, 8):
        for a in sol.SOLUTIONS[lvl]:
            g.perform_action(ActionInput(id=getattr(GameAction, a)))
    return g


def players(g):
    lvl = g._levels[g._current_level_index]
    return [s for s in lvl._sprites if 'vfaeucgcyr' in s._tags]


def active_sprite(g):
    for s in players(g):
        if 0 in s.pixels: return s


def active_color(s):
    cs = [int(c) for c in s.pixels.flatten() if c != -1 and c != 0]
    if not cs: return -1
    return Counter(cs).most_common(1)[0][0]


def state_key(s):
    return (s._x, s._y, s.width, s.height, active_color(s))


TARGETS = [
    (6, 45, 6), (21, 45, 6), (6, 54, 6), (21, 54, 6),
    (9, 39, 11), (15, 39, 11), (9, 57, 11), (15, 57, 11),
]


def covered(s, targets):
    cov = set()
    px = s.pixels
    for tx, ty, tc in targets:
        dx, dy = tx - s._x, ty - s._y
        if 0 <= dx < s.width and 0 <= dy < s.height:
            if int(px[dy, dx]) == tc:
                cov.add((tx, ty, tc))
    return cov


def bfs_find_cov(g_start, switches, target_color, target_cov_size,
                 depth_cap=100, time_limit=600):
    start = copy.deepcopy(g_start)
    for _ in range(switches):
        start.perform_action(ActionInput(id=GameAction.ACTION5))
    s0 = active_sprite(start)
    print(f'  start {s0._name} initial_color={active_color(s0)}')

    seen = {state_key(s0): 0}
    q = deque([(start, [])])
    best = None
    best_depth = float('inf')
    partial = {}  # frozenset -> (depth, seq)
    t0 = time.time()
    exp = 0
    last = 0
    while q:
        if time.time() - t0 > time_limit:
            print(f'  TIMEOUT exp={exp} states={len(seen)}')
            break
        g, seq = q.popleft()
        depth = len(seq)
        s = active_sprite(g)
        cov = covered(s, TARGETS)
        cov_col = [t for t in cov if t[2] == target_color]
        if len(cov_col) >= 1:
            key = frozenset(cov_col)
            if key not in partial or partial[key][0] > depth:
                partial[key] = (depth, list(seq))
        if len(cov_col) >= target_cov_size:
            if depth < best_depth:
                best_depth = depth
                best = (depth, list(seq), frozenset(cov))
                print(f'  FOUND d={depth}')
                return best
        if depth >= depth_cap: continue
        if time.time() - last > 30:
            max_depth = max((len(p[1]) for p in partial.values()), default=0)
            print(f'  ..exp={exp} depth={depth} states={len(seen)} partials={len(partial)} best_partial_size={max(len(k) for k in partial) if partial else 0}')
            last = time.time()
        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            s2 = active_sprite(g2)
            k = state_key(s2)
            if k in seen: continue
            seen[k] = depth + 1
            q.append((g2, seq + [a]))
            exp += 1
    print(f'  DONE exp={exp} states={len(seen)}')
    # Show best partials
    items = sorted(partial.items(), key=lambda kv: (-len(kv[0]), kv[1][0]))
    for key, (d, seq) in items[:6]:
        print(f'    d={d} cov={len(key)} {sorted(key)}')
    return best


def main():
    g = new_game_at_l8()
    print('=== A → 4 c6 ===')
    A = bfs_find_cov(g, 0, 6, 4, depth_cap=100, time_limit=600)
    print('\n=== B → 4 c11 ===')
    B = bfs_find_cov(g, 1, 11, 4, depth_cap=100, time_limit=600)
    if A and B:
        print(f'\nTotal: {A[0] + B[0] + 1} (baseline 221)')
        print(f'\nA_SEQ = {A[1]}')
        print(f'\nB_SEQ = {B[1]}')


if __name__ == '__main__':
    main()
