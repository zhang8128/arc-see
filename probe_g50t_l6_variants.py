"""G50T L6: try ghost variants with slightly different paths to see if any
wins in <48 actions."""
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


def solve(prefix, max_ghost_len, label, max_depth=40):
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
    print(f"{label}: prefix={len(prefix)} result={len(best) if best else 'NO WIN'}")
    return best


def main():
    # Reverse order: ghost B first (longer path to sw[1]) then ghost A (sw[0])
    b1 = solve(list('LLULL') + ['ACTION5'] + list('LLU') + ['ACTION5'], 5,
               "sw[1] then sw[0]")

    # Ghost A only on sw[0] via longer path that gives more pre-reach
    # From (55,31): LLU direct. Any alt? Probably not shorter.
    b2 = solve(list('LLU') + ['ACTION5'] + list('LLULL') + ['ACTION5'], 5,
               "sw[0] then sw[1]")

    # Path via sw[1] that ends at sw[0]: LLULL R R U — wait (31,25)+R=(37,25), +R=(43,25). So LLULLRRU = 8 moves ending at sw[0] but also pressing sw[1] in transit
    b3 = solve(list('LLULLRRU') + ['ACTION5'] + list('LLULL') + ['ACTION5'], 8,
               "ghost A path via sw[1] to sw[0]")

    # Print best
    best = min([b for b in [b1, b2, b3] if b], key=len) if any([b1, b2, b3]) else None
    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"\nBest: {len(best)} actions")
        print(f"  {''.join(to_letter.get(a, '?') for a in best)}")
        print(f"  {best}")


if __name__ == "__main__":
    main()
