"""G50T L7: open BFS that tries ACTION5 at various points.

State key includes engine fingerprint to allow ghost-awareness.
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


def state_key(g):
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    doors_t = tuple((d.x, d.y, bool(d.dijhfchobv)) for d in eng.uwxkstolmf)
    sws = tuple(getattr(h, 'dijhfchobv', None) for h in eng.hamayflsib)
    # ghosts: (spawn_pos, path_remaining_len)
    ghosts = tuple(sorted((k.x, k.y) for k in eng.rloltuowth))
    ghost_lens = tuple(sorted(len(v) for v in eng.rloltuowth.values()))
    counter = eng.rlazdofsxb
    return ((p.x, p.y), doors_t, sws, ghosts, ghost_lens, counter)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 6


def main():
    max_depth = 70
    g0 = fresh()
    start = state_key(g0)
    seen = {start: []}
    q = deque([(start, [])])
    best = None
    actions = ['U', 'D', 'L', 'R', 'ACTION5']
    iters = 0
    while q:
        key, path = q.popleft()
        iters += 1
        if iters % 100000 == 0:
            print(f"  iter {iters}, queue {len(q)}, depth {len(path)}")
        if best and len(path) >= len(best):
            continue
        if len(path) > max_depth:
            continue
        for name in actions:
            # Skip redundant ACTION5 (don't chain them wastefully)
            if name == 'ACTION5' and path and path[-1] == 'ACTION5':
                continue
            g2 = fresh()
            apply(g2, path + [name])
            if is_win(g2):
                full = path + [name]
                if not best or len(full) < len(best):
                    best = full
                    print(f"  WIN at {len(full)} actions!")
                break
            new_key = state_key(g2)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))

    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"\nBEST: {len(best)} actions (baseline 67)")
        print(f"  {''.join(to_letter.get(a, '?') for a in best)}")
        print(f"  {best}")
    else:
        print(f"\nNo win in depth {max_depth}. States explored: {len(seen)}")


if __name__ == "__main__":
    main()
