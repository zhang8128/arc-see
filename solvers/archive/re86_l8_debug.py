"""Explore L8 state space fully and report all coverage options."""
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


def state_key(s):
    return (s._x, s._y, s.width, s.height, active_color(s))


def full_bfs(g_start, switches, time_limit=300, depth_cap=60):
    start = copy.deepcopy(g_start)
    for _ in range(switches):
        start.perform_action(ActionInput(id=GameAction.ACTION5))
    s0 = active_sprite(start)
    print(f'  start {s0._name} key={state_key(s0)}')
    seen = {state_key(s0): 0}
    q = deque([(start, [])])
    best_cov = {}  # frozenset → (depth, seq)
    shapes_seen = set()
    colors_seen = set()
    t0 = time.time()
    exp = 0
    while q:
        if time.time() - t0 > time_limit: break
        g, seq = q.popleft()
        depth = len(seq)
        s = active_sprite(g)
        shapes_seen.add((s.width, s.height))
        colors_seen.add(active_color(s))
        cov = covered(s, TARGETS)
        if cov:
            key = frozenset(cov)
            if key not in best_cov or best_cov[key][0] > depth:
                best_cov[key] = (depth, list(seq))
        if depth >= depth_cap: continue
        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            s2 = active_sprite(g2)
            k = state_key(s2)
            if k in seen and seen[k] <= depth + 1: continue
            seen[k] = depth + 1
            q.append((g2, seq + [a]))
            exp += 1
    print(f'  exp={exp} states={len(seen)} time={time.time()-t0:.1f}s')
    print(f'  shapes reached: {sorted(shapes_seen)}')
    print(f'  colors reached: {sorted(colors_seen)}')
    return best_cov, seen


def main():
    g = new_game_at_l8()

    for name, sw in [('A (frame1)', 0), ('B (frame2)', 1)]:
        print(f'\n=== {name} ===')
        best, seen = full_bfs(g, sw, time_limit=300, depth_cap=60)
        items = sorted(best.items(), key=lambda kv: (-len(kv[0]), kv[1][0]))
        print(f'  top coverages:')
        for key, (d, seq) in items[:12]:
            cs = sorted(key)
            print(f'    d={d} cov={len(cs)} {cs}')


if __name__ == '__main__':
    main()
