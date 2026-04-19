"""Targeted BFS for L8 — two frames, each covering 4 targets via morph."""
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
    # Both L8 sprites are frames — use dims + position + color
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


def bfs_find(g_start, switches, target_color, target_cov_size, time_limit=600, depth_cap=60):
    start = copy.deepcopy(g_start)
    for _ in range(switches):
        start.perform_action(ActionInput(id=GameAction.ACTION5))
    s0 = active_sprite(start)
    print(f'  start {s0._name}')
    seen = {state_key(s0): 0}
    q = deque([(start, [])])
    t0 = time.time()
    exp = 0
    last_print = 0
    while q:
        if time.time() - t0 > time_limit:
            print(f'  TIMEOUT exp={exp}')
            return None
        g, seq = q.popleft()
        depth = len(seq)
        s = active_sprite(g)
        cov = covered(s, TARGETS)
        cov_col = [t for t in cov if t[2] == target_color]
        if len(cov_col) >= target_cov_size:
            print(f'  FOUND d={depth} cov={sorted(cov_col)}')
            return (depth, list(seq), frozenset(cov))
        if depth >= depth_cap: continue
        if time.time() - last_print > 30:
            print(f'  ..exp={exp} depth={depth} q={len(q)}')
            last_print = time.time()
        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            s2 = active_sprite(g2)
            k = state_key(s2)
            if k in seen and seen[k] <= depth + 1: continue
            seen[k] = depth + 1
            q.append((g2, seq + [a]))
            exp += 1
    print(f'  exhausted exp={exp}')
    return None


def main():
    g = new_game_at_l8()

    # Sprite A (active): frame color 12, pos (45,42) → should cover 4 c6 via 16×10
    # Sprite B: frame color 10, pos (48,39) → should cover 4 c11 via 7×19
    # Try both assignments.

    print('=== A (active frame 13x13) → 4 c6 ===')
    A6 = bfs_find(g, 0, 6, 4, time_limit=300, depth_cap=60)

    print('\n=== B (second frame) → 4 c11 ===')
    B11 = bfs_find(g, 1, 11, 4, time_limit=300, depth_cap=60)

    print('\n=== SUMMARY ===')
    if A6 and B11:
        total = A6[0] + B11[0] + 1  # 1 switch
        print(f'  A: d={A6[0]}')
        print(f'  B: d={B11[0]}')
        print(f'  TOTAL: {total} actions (baseline 221)')
        print(f'\nA_SEQ = {A6[1]}')
        print(f'B_SEQ = {B11[1]}')


if __name__ == '__main__':
    main()
