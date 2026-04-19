"""Trace: take sprite A to (9, 24) 16x10 c6 and see if it can move DOWN freely."""
import importlib.util, sys, copy
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


def show(s, label=''):
    from collections import Counter
    cs = [int(c) for c in s.pixels.flatten() if c != -1 and c != 0]
    col = Counter(cs).most_common(1)[0][0] if cs else -1
    print(f'[{label}] pos=({s._x},{s._y}) {s.width}x{s.height} color={col}')


# BFS found A reaching 16x10 c6 at (9, 24) at depth ~19.
# From the earlier partial output, need to reproduce.
# Easier: search forward to find ANY path to 16x10 c6 at (9, 24), then show it, then continue DOWN.

import time
from collections import deque, Counter

def active_color(s):
    cs = [int(c) for c in s.pixels.flatten() if c != -1 and c != 0]
    if not cs: return -1
    return Counter(cs).most_common(1)[0][0]


def state_key(s):
    return (s._x, s._y, s.width, s.height, active_color(s))


def find_path_to(g_start, target_key, depth_cap=40, time_limit=120):
    seen = {state_key(active_sprite(g_start)): (0, [])}
    q = deque([(g_start, [])])
    t0 = time.time()
    while q:
        if time.time() - t0 > time_limit: break
        g, seq = q.popleft()
        depth = len(seq)
        s = active_sprite(g)
        if state_key(s) == target_key:
            return seq
        if depth >= depth_cap: continue
        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            s2 = active_sprite(g2)
            k = state_key(s2)
            if k in seen and seen[k][0] <= depth + 1: continue
            seen[k] = (depth + 1, seq + [a])
            q.append((g2, seq + [a]))
    return None


g = new_game_at_l8()
target = (9, 24, 16, 10, 6)
print(f'Finding path to {target}...')
path = find_path_to(copy.deepcopy(g), target, depth_cap=30, time_limit=120)
if path is None:
    print('NOT REACHABLE within depth 30')
else:
    print(f'Found at depth {len(path)}')
    # Replay
    g2 = copy.deepcopy(g)
    for a in path:
        g2.perform_action(ActionInput(id=getattr(GameAction, a)))
    s = active_sprite(g2)
    show(s, 'arrived')

    # Try moving DOWN step by step toward (9, 45)
    print('\nTry DOWN moves toward (9, 45):')
    for i in range(10):
        prev = (s._x, s._y, s.width, s.height, active_color(s))
        g2.perform_action(ActionInput(id=GameAction.ACTION2))
        s = active_sprite(g2)
        cur = (s._x, s._y, s.width, s.height, active_color(s))
        changed = '' if prev == cur else ' CHANGED'
        print(f'  D{i+1}: {prev} → {cur}{changed}')
