"""G50T L6: try 1-ghost solutions. Maybe not all 4 switches needed."""
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
    g.set_level(5)
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
    return g._state.name == "WIN" or g._current_level_index > 5


def solve(prefix, max_ghost_len, label, max_depth=45):
    g = fresh()
    apply(g, prefix)
    print(f"\n=== {label} ({len(prefix)} prefix) ===")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
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
    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"  WIN at {len(best)} actions! seq: {''.join(to_letter.get(a, '?') for a in best)}")
    else:
        print(f"  NO WIN")
    return best


def main():
    # Try ghost on sw[0] only
    solve(list('LLU') + ['ACTION5'], 3, "Ghost on sw[0]")
    # Try ghost on sw[1] only
    solve(list('LLULL') + ['ACTION5'], 5, "Ghost on sw[1]")
    # Try no ghost at all (just walk)
    solve([], 0, "No ghost (walking only)")


if __name__ == "__main__":
    main()
