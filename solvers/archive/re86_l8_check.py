"""Check which (shape, color) combinations are reachable on L8 for each sprite."""
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


def run_bfs(g_start, switches, depth_cap=60, time_limit=300):
    start = copy.deepcopy(g_start)
    for _ in range(switches):
        start.perform_action(ActionInput(id=GameAction.ACTION5))
    s0 = active_sprite(start)
    seen = {state_key(s0): (0, [])}
    q = deque([(start, [])])
    t0 = time.time()
    while q:
        if time.time() - t0 > time_limit: break
        g, seq = q.popleft()
        depth = len(seq)
        if depth >= depth_cap: continue
        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            s2 = active_sprite(g2)
            k = state_key(s2)
            if k in seen and seen[k][0] <= depth + 1: continue
            seen[k] = (depth + 1, seq + [a])
            q.append((g2, seq + [a]))
    return seen


def main():
    g = new_game_at_l8()
    for label, sw in [('A', 0), ('B', 1)]:
        print(f'\n=== {label} ===')
        seen = run_bfs(g, sw, depth_cap=60, time_limit=300)
        print(f'  reachable states: {len(seen)}')

        # Group by (shape, color)
        by_shape_color = {}
        for (x, y, w, h, c), (d, _) in seen.items():
            key = (w, h, c)
            if key not in by_shape_color or by_shape_color[key][0] > d:
                by_shape_color[key] = (d, (x, y))

        # Filter for 16x10 color 6 and 7x19 color 11
        interesting = [
            (16, 10, 6), (10, 16, 6), (13, 13, 6),
            (7, 19, 11), (19, 7, 11), (13, 13, 11),
        ]
        for key in interesting:
            if key in by_shape_color:
                d, pos = by_shape_color[key]
                print(f'  shape {key}: found at d={d} pos={pos}')
            else:
                print(f'  shape {key}: NOT REACHABLE')

        # Find all reachable (x, y) with 16x10 color 6
        print(f'  all (x,y) with 16x10 c6:')
        states_16x10_c6 = [(x, y, d) for (x, y, w, h, c), (d, _) in seen.items() if w==16 and h==10 and c==6]
        for x, y, d in sorted(states_16x10_c6, key=lambda t: t[2])[:20]:
            print(f'    ({x},{y}) d={d}')

        print(f'  all (x,y) with 7x19 c11:')
        states = [(x, y, d) for (x, y, w, h, c), (d, _) in seen.items() if w==7 and h==19 and c==11]
        for x, y, d in sorted(states, key=lambda t: t[2])[:20]:
            print(f'    ({x},{y}) d={d}')


if __name__ == '__main__':
    main()
