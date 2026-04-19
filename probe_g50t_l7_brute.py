"""G50T L7: brute BFS with ghost configurations and proper engine state keys.

We track (pos, doors, hamay_press_tuple, teleport_signature) to dedupe states.

Try multiple prefix configurations and pick the best.
"""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTION_NAMES = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}


def fresh():
    g = mod.G50t()
    g.set_level(6)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTION_NAMES[name]
    g.perform_action(ActionInput(id=getattr(GameAction, full)))


def apply(g, seq):
    for a in seq:
        do(g, a)


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def state_key(g, clamp):
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    doors_t = tuple((d.x, d.y, bool(d.dijhfchobv)) for d in eng.uwxkstolmf)
    sws = tuple(getattr(h, 'dijhfchobv', None) for h in eng.hamayflsib)
    return ((p.x, p.y), doors_t, sws, clamp)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 6


def solve(prefix, max_ghost_len, label, max_depth=55):
    g = fresh()
    apply(g, prefix)
    start = state_key(g, 0)
    seen = {start: []}
    q = deque([(start, [])])
    best = None
    while q:
        (_, _, _, _), path = q.popleft()
        if best and len(path) >= len(best):
            continue
        if len(path) > max_depth:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, prefix + path + [name])
            if is_win(g2):
                full = prefix + path + [name]
                if not best or len(full) < len(best):
                    best = full
                break
            clamp = min(len(path) + 1, max_ghost_len)
            new_key = state_key(g2, clamp)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
    print(f"{label}: prefix={len(prefix)} best={len(best) if best else 'NO WIN'}")
    return best


def main():
    SW2 = list('DDL')
    SW3 = list('DDLRUULLUU')
    # Also try a path that latches door[1] via sw[2] first, then reaches sw[3]:
    # (25,25) → sw[2] DDL → step off RR DDLR (back to (25,31))... messy
    # Or just let BFS find creative paths.

    results = []
    results.append(('sw[2]', solve(SW2 + ['ACTION5'], 3, 'ghost sw[2]', 60)))
    results.append(('sw[3]', solve(SW3 + ['ACTION5'], 10, 'ghost sw[3]', 60)))
    results.append(('sw[2]+sw[3]', solve(SW2 + ['ACTION5'] + SW3 + ['ACTION5'], 10, 'sw[2]+sw[3]', 60)))
    results.append(('sw[3]+sw[2]', solve(SW3 + ['ACTION5'] + SW2 + ['ACTION5'], 10, 'sw[3]+sw[2]', 60)))
    results.append(('walking', solve([], 0, 'walking', 50)))

    best = None
    for label, r in results:
        if r and (best is None or len(r) < len(best[1])):
            best = (label, r)
    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"\nBEST: {best[0]}  {len(best[1])} actions (baseline 67)")
        print(f"  {''.join(to_letter.get(a, '?') for a in best[1])}")
        print(f"  {best[1]}")


if __name__ == "__main__":
    main()
