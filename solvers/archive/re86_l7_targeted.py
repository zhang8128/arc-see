"""Targeted compact-state BFS for specific end-states on L7.

Goal: find minimum depth for each sprite to reach required coverage state.
- C (37x19 wide): cover 4 c8 targets. State (0, 9, h=6, v=9, color=8).
- A (19x19 cross): cover 3 c11 targets. State (33, 30, h=18, v=12, color=11).
- B (13x13 frame): cover 2 c9 targets. State (39, 18, w=19, h=7, color=9).
"""
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
        if 0 in s.pixels: return s


def active_color(s):
    cs = [int(c) for c in s.pixels.flatten() if c != -1 and c != 0]
    if not cs: return -1
    return Counter(cs).most_common(1)[0][0]


def arm_pats(s):
    px = s.pixels
    row_counts = [sum(1 for c in row if c != -1) for row in px]
    h_row = row_counts.index(max(row_counts))
    col_counts = [sum(1 for row in px if row[c] != -1) for c in range(s.width)]
    v_col = col_counts.index(max(col_counts))
    return h_row, v_col


TARGETS = [
    (9, 9, 8), (3, 15, 8), (36, 15, 8), (9, 27, 8),
    (57, 18, 9), (39, 24, 9),
    (45, 30, 11), (39, 48, 11), (51, 48, 11),
]


def covered(s, targets):
    """Strict: sprite pixel at target position must equal target color.
    Active marker 0 and transparent -1 do NOT count as coverage."""
    cov = set()
    px = s.pixels
    for tx, ty, tc in targets:
        dx, dy = tx - s._x, ty - s._y
        if 0 <= dx < s.width and 0 <= dy < s.height:
            if int(px[dy, dx]) == tc:
                cov.add((tx, ty, tc))
    return cov


def bfs_find_coverage(start_g, switches, is_frame, target_color, target_cov_size,
                     time_limit=600, depth_cap=60):
    """BFS until finding any state that covers target_cov_size targets of target_color."""
    start = copy.deepcopy(start_g)
    for _ in range(switches):
        start.perform_action(ActionInput(id=GameAction.ACTION5))

    s0 = active_sprite(start)
    print(f'  start {s0._name}')

    def key(s):
        col = active_color(s)
        if is_frame:
            return (s._x, s._y, s.width, s.height, col)
        h, v = arm_pats(s)
        return (s._x, s._y, h, v, col)

    seen = {key(s0): 0}
    q = deque([(start, [])])
    best_found = None
    best_depth = float('inf')
    t0 = time.time()
    exp = 0
    last_print = 0

    while q:
        if time.time() - t0 > time_limit:
            print(f'  TIMEOUT at exp={exp}')
            break
        g, seq = q.popleft()
        depth = len(seq)
        s = active_sprite(g)

        # Check coverage
        cov = covered(s, TARGETS)
        cov_of_color = [t for t in cov if t[2] == target_color]
        if len(cov_of_color) >= target_cov_size:
            if depth < best_depth:
                best_depth = depth
                best_found = (depth, list(seq), frozenset(cov))
                print(f'  FOUND d={depth} cov={len(cov_of_color)} {sorted(cov_of_color)}')
                # Keep looking for shorter after finding first; actually BFS depth is monotonic
                return best_found

        if depth >= depth_cap: continue
        if time.time() - last_print > 30:
            print(f'  ..exp={exp} depth={depth} q={len(q)}')
            last_print = time.time()

        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            s2 = active_sprite(g2)
            k = key(s2)
            if k in seen and seen[k] <= depth + 1:
                continue
            seen[k] = depth + 1
            q.append((g2, seq + [a]))
            exp += 1

    print(f'  exhausted: exp={exp} states={len(seen)}')
    return best_found


def main():
    g = new_game_at_l7()

    print('=== A (19x19 cross) → 3 c11 ===')
    A_result = bfs_find_coverage(g, 0, False, 11, 3, time_limit=300, depth_cap=50)

    print('\n=== B (13x13 frame) → 2 c9 ===')
    B_result = bfs_find_coverage(g, 1, True, 9, 2, time_limit=300, depth_cap=50)

    print('\n=== C (37x19 wide) → 4 c8 ===')
    C_result = bfs_find_coverage(g, 2, False, 8, 4, time_limit=600, depth_cap=60)

    print('\n=== SUMMARY ===')
    for name, r in [('A', A_result), ('B', B_result), ('C', C_result)]:
        if r:
            d, seq, cov = r
            print(f'  {name}: d={d} cov={sorted(cov)}')
            print(f'    seq={seq}')
        else:
            print(f'  {name}: NOT FOUND')

    if A_result and B_result and C_result:
        total = A_result[0] + B_result[0] + C_result[0] + 2  # 2 switches
        print(f'\n  TOTAL: {total} actions (baseline 328)')


if __name__ == '__main__':
    main()
