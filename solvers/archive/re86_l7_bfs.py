"""BFS for single-sprite coverage on L7.

Uses the engine as simulator: deepcopy per expansion.
State key = (active_sprite_index, pixel_hash, x, y).
Other sprites don't move when only pressing ACTION1-4.
"""
import importlib.util, sys, copy, hashlib, time
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


def state_key(g):
    s = active_sprite(g)
    return (s._name, s._x, s._y, s.pixels.tobytes())


def active_color(s):
    """Dominant non-(-1, 0) color in sprite."""
    from collections import Counter
    cs = [int(c) for c in s.pixels.flatten() if c != -1 and c != 0]
    if not cs: return None
    return Counter(cs).most_common(1)[0][0]


def covered_targets(s, targets):
    """Which targets does this sprite cover at its current state?"""
    col = active_color(s)
    if col is None: return set(), None
    cov = set()
    px = s.pixels
    for tx, ty, tc in targets:
        if tc != col: continue
        dx, dy = tx - s._x, ty - s._y
        if 0 <= dx < s.width and 0 <= dy < s.height:
            if int(px[dy, dx]) not in (-1,):
                cov.add((tx, ty, tc))
    return cov, col


TARGETS = [
    (9, 9, 8), (3, 15, 8), (36, 15, 8), (9, 27, 8),
    (57, 18, 9), (39, 24, 9),
    (45, 30, 11), (39, 48, 11), (51, 48, 11),
]


def search_sprite(initial_g, switches, max_depth=18, target_mask=None, time_limit=60):
    """BFS over a single sprite's moves (no switch).
    Returns dict: frozenset(covered targets) -> (depth, action_seq).
    """
    # First apply switches to pick sprite
    start = copy.deepcopy(initial_g)
    for _ in range(switches):
        start.perform_action(ActionInput(id=GameAction.ACTION5))

    start_s = active_sprite(start)
    print(f'  Searching from {start_s._name} pos=({start_s._x},{start_s._y})')

    best = {}  # frozenset(targets) -> (depth, seq)
    seen = {state_key(start): 0}
    q = deque([(start, [])])
    t0 = time.time()
    expansions = 0

    while q:
        if time.time() - t0 > time_limit:
            print(f'  TIMEOUT at {expansions} expansions, depth ~{len(seq) if q else "?"}')
            break
        g, seq = q.popleft()
        depth = len(seq)

        # Record coverage
        s = active_sprite(g)
        cov, col = covered_targets(s, TARGETS)
        if cov:
            key = frozenset(cov)
            if key not in best or best[key][0] > depth:
                best[key] = (depth, list(seq))

        if depth >= max_depth:
            continue

        for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            k = state_key(g2)
            if k in seen and seen[k] <= depth + 1:
                continue
            seen[k] = depth + 1
            q.append((g2, seq + [a]))
            expansions += 1

    print(f'  Expanded {expansions} states in {time.time()-t0:.1f}s, {len(best)} unique coverages')
    return best


def main():
    g = new_game_at_l7()

    # Deeper, longer searches
    print('\n=== Sprite A (19x19 cross, initially active) ===')
    best_A = search_sprite(g, switches=0, max_depth=25, time_limit=120)
    show_best(best_A, 'A')

    print('\n=== Sprite B (13x13 frame, morph-capable) ===')
    best_B = search_sprite(g, switches=1, max_depth=25, time_limit=120)
    show_best(best_B, 'B')

    print('\n=== Sprite C (37x19 wide cross) ===')
    best_C = search_sprite(g, switches=2, max_depth=25, time_limit=180)
    show_best(best_C, 'C')


def show_best(best, label):
    if not best:
        print(f'  {label}: no coverages found')
        return
    # Sort by coverage size DESC, then depth ASC
    items = sorted(best.items(), key=lambda kv: (-len(kv[0]), kv[1][0]))
    for key, (depth, seq) in items[:10]:
        cs = sorted(key)
        print(f'  {label}: d={depth} cov={len(cs)} {cs}')


if __name__ == '__main__':
    main()
