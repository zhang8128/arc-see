"""G50T L7: try all 2-ghost combinations for the 3 reachable switches.

Reachable switches: sw[2]=(19,37), sw[3]=(13,1). sw[0] and sw[1] unreachable directly.
Also possible: 1-ghost solutions with ghost A on each reachable switch.
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


def doors(g):
    return tuple((d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 6


# Reachable switch paths (from walking BFS)
SW2_PATH = list('DDL')         # (25,25) → (19,37)? wait that's (25,25) D (25,31) D (25,37) L (19,37)
SW3_PATH = list('DDLRUULLUU')  # (25,25) → (13,1) — 10 moves


def solve(prefix, max_ghost_len, label, max_depth=60):
    g = fresh()
    apply(g, prefix)
    start = (pos(g), doors(g), 0)
    seen = {start: []}
    q = deque([(start, [])])
    best = None
    while q:
        (p, d, _), path = q.popleft()
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
            new_p = pos(g2)
            new_d = doors(g2)
            new_mc = min(len(path) + 1, max_ghost_len)
            new_key = (new_p, new_d, new_mc)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
    print(f"{label}: prefix={len(prefix)} best={len(best) if best else 'NO WIN'}")
    return best


def main():
    results = []
    # 1-ghost variants
    results.append(('ghost sw[2]', solve(SW2_PATH + ['ACTION5'], len(SW2_PATH), 'ghost sw[2]')))
    results.append(('ghost sw[3]', solve(SW3_PATH + ['ACTION5'], len(SW3_PATH), 'ghost sw[3]')))
    # 2-ghost variants
    results.append(('sw[2] then sw[3]', solve(
        SW2_PATH + ['ACTION5'] + SW3_PATH + ['ACTION5'], max(len(SW2_PATH), len(SW3_PATH)),
        'sw[2] then sw[3]')))
    results.append(('sw[3] then sw[2]', solve(
        SW3_PATH + ['ACTION5'] + SW2_PATH + ['ACTION5'], max(len(SW2_PATH), len(SW3_PATH)),
        'sw[3] then sw[2]')))
    # No ghost
    results.append(('walking', solve([], 0, 'walking')))

    best = None
    for label, r in results:
        if r and (best is None or len(r) < len(best[1])):
            best = (label, r)
    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"\nBEST: {best[0]}  {len(best[1])} actions (baseline 67)")
        print(f"  {''.join(to_letter.get(a, '?') for a in best[1])}")


if __name__ == "__main__":
    main()
